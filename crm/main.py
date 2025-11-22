from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from core.container import container
from core.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    starlette_exception_handler,
    custom_exception_handler,
)
from core.exceptions import BaseCustomException

from auth.router import router as auth_router
from organizations.router import router as organizations_router
from contacts.router import router as contacts_router
from deals.router import router as deals_router
from tasks.router import router as tasks_router
from activities.router import router as activities_router
from analytics.router import router as analytics_router


app = FastAPI(
    title="Mini-CRM API",
    description="Multi-tenant test application CRM system with organizations, contacts, deals, tasks, and analytics",
    version="1.3.3.7",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_dishka(container, app)

app.include_router(auth_router)
app.include_router(organizations_router)
app.include_router(contacts_router)
app.include_router(deals_router)
app.include_router(tasks_router)
app.include_router(activities_router)
app.include_router(analytics_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
app.add_exception_handler(BaseCustomException, custom_exception_handler)


@app.get("/")
async def root():
    return {"message": "Mini-CRM API", "version": "1.3.3.7"}


