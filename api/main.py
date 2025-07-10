# api/main.py
# FastAPI entry-point with robust error logging.

from fastapi import FastAPI, Request
from api.routers import datasets, analyze
import traceback
import logging

# Configure logging using uvicorn's logger
logger = logging.getLogger("uvicorn.error")

# FastAPI application setup
app = FastAPI(
    title="AutoStat-Agent API",
    version="0.1",
    description="Plan-only prototype for statistical analysis automation",
)

app.include_router(datasets.router)
app.include_router(analyze.router)

# Exception logging middleware
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(
            "Unhandled exception while processing %s %s\n%s",
            request.method,
            request.url.path,
            "".join(traceback.format_exception(exc)),
        )
        raise
