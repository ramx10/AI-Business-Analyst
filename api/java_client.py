import logging
from typing import Optional

import httpx

JAVA_BASE_URL = "http://localhost:8081"

logger = logging.getLogger(__name__)


async def record_history(
    user_email: str,
    dataset_name: str,
    row_count: int,
    cleaning_summary: str,
    session_id: str,
    kpi_summary: str = "",
    insights: str = "",
) -> bool:
    """POST a cleaning history entry to the Java Spring Boot backend.

    Falls back gracefully (returns False) if the Java backend is unreachable.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{JAVA_BASE_URL}/api/user/dashboards/history",
                json={
                    "datasetName": dataset_name,
                    "rowCount": row_count,
                    "cleaningSummary": cleaning_summary,
                    "kpiSummary": kpi_summary,
                    "insights": insights,
                },
                headers={"Authorization": f"Bearer {user_email}"},
            )
            if resp.is_success:
                logger.info("History recorded for %s (%s)", user_email, dataset_name)
                return True
            else:
                logger.warning(
                    "Java backend returned %s: %s", resp.status_code, resp.text
                )
                return False
    except Exception as e:
        logger.warning("Failed to record history (Java unavailable): %s", e)
        return False


async def get_history(user_email: str) -> list:
    """GET dashboard history entries from the Java Spring Boot backend."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{JAVA_BASE_URL}/api/user/dashboards/history",
                headers={"Authorization": f"Bearer {user_email}"},
            )
            if resp.is_success:
                return resp.json()
            else:
                logger.warning(
                    "Java backend returned %s: %s", resp.status_code, resp.text
                )
                return []
    except Exception as e:
        logger.warning("Failed to get history (Java unavailable): %s", e)
        return []
