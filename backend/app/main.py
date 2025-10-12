"""Main FastAPI application."""
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import (
    BlueTraceException,
    bluetrace_exception_handler,
    general_exception_handler,
    http_exception_handler,
)
from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import rate_limiter
from app.telemetry.otel import setup_telemetry, instrument_app
from app.api.v1 import health, admin, tides, sst, currents, turbidity, bathy
from app.api.v1.stripe_webhook import router as stripe_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting BlueTrace API")
    
    # Initialize rate limiter
    await rate_limiter.initialize()
    logger.info("Rate limiter initialized")
    
    # Setup telemetry
    setup_telemetry()
    logger.info("Telemetry configured")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BlueTrace API")
    await rate_limiter.close()


# Create FastAPI app
app = FastAPI(
    title="BlueTrace API",
    description="Production-grade REST API for marine and coastal datasets",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> JSONResponse:
    """Log all requests with structured data."""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Extract API key prefix if available
    api_key_prefix = "anonymous"
    if hasattr(request.state, "api_key"):
        api_key_prefix = request.state.api_key.prefix
    
    # Log request
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "api_key_prefix": api_key_prefix,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-RateLimit-Limit"] = "30"  # Will be dynamic later
    response.headers["X-RateLimit-Remaining"] = "29"
    
    return response


# Exception handlers
app.add_exception_handler(BlueTraceException, bluetrace_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(health.router, prefix="/v1", tags=["Health"])
app.include_router(admin.router, prefix="/v1/admin", tags=["Admin"])
app.include_router(tides.router, prefix="/v1", tags=["Tides"])
app.include_router(sst.router, prefix="/v1", tags=["SST"])
app.include_router(currents.router, prefix="/v1", tags=["Currents"])
app.include_router(turbidity.router, prefix="/v1", tags=["Turbidity"])
app.include_router(bathy.router, prefix="/v1", tags=["Bathymetry"])
app.include_router(stripe_router, prefix="/stripe", tags=["Stripe"])

# Instrument with OpenTelemetry
instrument_app(app)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "BlueTrace API",
        "docs": "/docs",
        "version": "0.1.0"
    }

