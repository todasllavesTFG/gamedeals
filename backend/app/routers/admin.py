import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.scheduler import (
    scheduler,
    update_cheapshark_prices,
    update_steam_prices,
    update_fanatical_prices,
    update_humble_bundles,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/scheduler/status")
def get_scheduler_status():
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run,
            "trigger": str(job.trigger),
        })
    return {
        "running": scheduler.running,
        "jobs": jobs,
    }


@router.post("/scheduler/run-now")
async def run_job_now(job: str):
    if job == "cheapshark":
        await update_cheapshark_prices()
        message = "Job cheapshark ejecutado manualmente"
    elif job == "steam":
        await update_steam_prices()
        message = "Job steam ejecutado manualmente"
    elif job == "fanatical":
        await update_fanatical_prices()
        message = "Job fanatical ejecutado manualmente"
    elif job == "humble":
        await update_humble_bundles()
        message = "Job humble ejecutado manualmente"
    else:
        raise HTTPException(status_code=400, detail="job debe ser 'cheapshark', 'steam', 'fanatical' o 'humble'")

    return {
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
