from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

import subprocess

from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title="MoySklad Sync API",
    description="API for synchronizing data between two MoySklad accounts",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Configure OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
    scheme_name="OAuth2PasswordBearer",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items."
    }
)

@app.get("/", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "ok", "message": "MoySklad Sync API is running"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="MoySklad Sync API - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "tryItOutEnabled": True,
            "syntaxHighlight.theme": "monokai"
        }
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return get_openapi(
        title="MoySklad Sync API",
        version="1.0.0",
        description="API for synchronizing data between two MoySklad accounts",
        routes=app.routes,
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler to catch and report all unhandled exceptions.
    """
    import traceback
    error_detail = traceback.format_exc()

    # Here you could add logging to a file or external service
    print(f"Unhandled exception: {exc}")
    print(error_detail)

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "type": str(type(exc).__name__)},
    )