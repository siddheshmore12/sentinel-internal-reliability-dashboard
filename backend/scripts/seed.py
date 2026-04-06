import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.models.enums import CheckType, Environment
from app.models.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    """Seed the database with realistic internal services."""
    services = [
        {"name": "Global Payment API", "environment": Environment.PRODUCTION, "url": "https://httpstat.us/200", "check_type": CheckType.HTTP},
        {"name": "Auth Service", "environment": Environment.PRODUCTION, "url": "https://httpstat.us/200", "check_type": CheckType.HTTP},
        {"name": "Search API", "environment": Environment.STAGING, "url": "https://httpstat.us/404", "check_type": CheckType.HTTP},
        {"name": "Notification Worker", "environment": Environment.PRODUCTION, "url": "https://httpstat.us/500", "check_type": CheckType.HTTP},
        {"name": "Analytics DB", "environment": Environment.PRODUCTION, "url": "postgres://localhost", "check_type": CheckType.DATABASE, "maintenance": True},
    ]

    async with AsyncSessionLocal() as session:
        for svc_data in services:
            maintenance = svc_data.pop("maintenance", False)
            svc = Service(**svc_data, maintenance_mode=maintenance)
            session.add(svc)
            
        await session.commit()
    logger.info("Database successfully seeded with realistic internal services.")

if __name__ == "__main__":
    asyncio.run(seed_data())
