import asyncio
import logging

import httpx

from app.core.config import settings
from app.core.exceptions import OrderArchiveFailedError

logger = logging.getLogger("store-service")


async def archive_session_orders(session_id: int) -> None:
    """Call Order Service to archive orders for a completed session.

    Retries up to 3 times with 1 second interval on failure.
    """
    url = f"{settings.order_service_url}/internal/orders/archive"
    payload = {"session_id": session_id}
    max_retries = 3

    async with httpx.AsyncClient(timeout=5.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Order archive successful for session {session_id}")
                return
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                logger.warning(
                    f"Order archive attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0)

    raise OrderArchiveFailedError()
