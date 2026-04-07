import asyncio
import logging
import time

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.metrics import WORKER_RUN_DURATION
from app.core.redis_client import DASHBOARD_SUMMARY_KEY, cache_set
from app.services.dashboard_service import build_dashboard_summary
from app.repositories.health_check_repo import HealthCheckRepository
from app.repositories.service_repo import ServiceRepository
from app.strategies.factory import get_strategy

logger = logging.getLogger(__name__)
settings = get_settings()

async def _evaluate_and_store(hc_repo: HealthCheckRepository, service) -> None:
    try:
        strategy = get_strategy(service.check_type)
        result = await strategy.check(service.url)
        
        await hc_repo.create(
            service_id=service.id,
            latency_ms=result.latency_ms,
            status_code=result.status_code,
            status=result.status,
            error_message=result.error_message
        )
        await hc_repo.db.commit()
    except Exception as exc:
        logger.error(f"Failed to check service {service.name}: {exc}")

async def run_checks_for_all_services() -> None:
    async with AsyncSessionLocal() as session:
        service_repo = ServiceRepository(session)
        hc_repo = HealthCheckRepository(session)
        
        services = await service_repo.get_all()
        logger.info(f"Worker initiated check cycle for {len(services)} services.")
        
        tasks = []
        for svc in services:
            tasks.append(_evaluate_and_store(hc_repo, svc))
            
        await asyncio.gather(*tasks)

async def worker_loop() -> None:
    logger.info(f"Starting Sentinel embedded background worker. Polling interval: {settings.HEALTH_CHECK_INTERVAL_SECONDS}s")
    while True:
        start_time = time.monotonic()
        try:
            await run_checks_for_all_services()
            async with AsyncSessionLocal() as session:
                summary = await build_dashboard_summary(session)
                await cache_set(DASHBOARD_SUMMARY_KEY, summary.model_dump(mode="json"))
                logger.debug("Successfully refreshed Redis cache.")
            duration = time.monotonic() - start_time
            WORKER_RUN_DURATION.observe(duration)
        except asyncio.CancelledError:
            logger.info("Worker loop cancelled.")
            raise
        except Exception as exc:
            logger.error(f"Worker iteration failed: {exc}")
            
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL_SECONDS)
