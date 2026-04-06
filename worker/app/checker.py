import asyncio
import logging
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.models.enums import HealthStatus
from app.repositories.health_check_repo import HealthCheckRepository
from app.repositories.service_repo import ServiceRepository
from app.strategies.factory import get_strategy

logger = logging.getLogger(__name__)

async def run_checks_for_all_services() -> None:
    """
    Fetch all active services, orchestrate health checks via the Strategy Pattern,
    and persist the results to PostgreSQL.
    """
    async with AsyncSessionLocal() as session:
        service_repo = ServiceRepository(session)
        hc_repo = HealthCheckRepository(session)
        
        services = await service_repo.get_all()
        logger.info(f"Worker initiated check cycle for {len(services)} services.")
        
        tasks = []
        for svc in services:
            tasks.append(_evaluate_and_store(hc_repo, svc))
            
        await asyncio.gather(*tasks)

async def _evaluate_and_store(hc_repo: HealthCheckRepository, service) -> None:
    try:
        strategy = get_strategy(service.check_type)
        result = await strategy.check(service.url)
        
        # Write to database (HealthCheck log)
        await hc_repo.create(
            service_id=service.id,
            latency_ms=result.latency_ms,
            status_code=result.status_code,
            status=result.status,
            error_message=result.error_message
        )
        
        # In a real system, you'd trigger alerting here if status == DOWN
        # and service.maintenance_mode == False.
        
        await hc_repo.db.commit()
    except Exception as exc:
        logger.error(f"Failed to check service {service.name}: {exc}")
