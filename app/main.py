# from app.api.v1.routes import auth
from app.api.v1.dependencies import auth
from fastapi import FastAPI
from app.api.v1.routes import design
from app.database import engine, Base
import asyncio
from fastapi.routing import APIRoute

from fastapi.openapi.utils import get_openapi
from app.api.v1.dependencies import api_auth_router
from app.api.v1.routes import api_router

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(api_auth_router)
app.include_router(api_router)


# To list all registered endpoints
@app.get("/list-endpoints", tags=["Debug"])
def list_endpoints():
    endpoints = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"endpoints": endpoints}

# Add JWT bearer auth to Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SmartQP_API",
        version="1.0.0",
        description="API documentation with JWT Bearer authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.openapi = custom_openapi