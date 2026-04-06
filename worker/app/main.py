import asyncio
import logging
import time

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.metrics import WORKER_RUN_DURATION
from app.core.redis_client import DASHBOARD_SUMMARY_KEY, cache_set
from app.services.dashboard_service import build_dashboard_summary

from worker_app.checker import run_checks_for_all_services

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
settings = get_settings()

async def loop():
    logger.info(f"Starting Sentinel background worker. Polling interval: {settings.HEALTH_CHECK_INTERVAL_SECONDS}s")
    
    while True:
        start_time = time.monotonic()
        
        try:
            # 1. Run all checks and save to Postgres
            await run_checks_for_all_services()
            
            # 2. Re-build and push the dashboard summary to Redis cache
            async with AsyncSessionLocal() as session:
                summary = await build_dashboard_summary(session)
                # Use json dump mode so UUIDs and enums properly encode
                await cache_set(DASHBOARD_SUMMARY_KEY, summary.model_dump(mode="json"))
                logger.debug("Successfully refreshed Redis cache.")
                
            # 3. Log metrics
            duration = time.monotonic() - start_time
            WORKER_RUN_DURATION.observe(duration)
            logger.info(f"Check cycle completed in {duration:.2f}s.")
            
        except Exception as exc:
            logger.error(f"Worker iteration failed: {exc}")
            
        # 4. Sleep until next cycle
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(loop())
