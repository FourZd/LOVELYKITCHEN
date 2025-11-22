from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from core.exceptions import BaseCustomException


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации запросов"""
    errors = {"non_field_error": []}
    for error in exc.errors():
        field_path = ".".join(
            str(x) for x in error["loc"] if not isinstance(x, int) and x != "body"
        )
        error_key = (
            "error.validation."
            + error["type"]
            + ("." + field_path if field_path else "")
        )
        if not field_path or any(isinstance(x, int) for x in error["loc"]):
            errors["non_field_error"].append(error_key)
        else:
            errors[field_path] = error_key
    return JSONResponse(status_code=400, content={"errors": errors, "status": "error"})


async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail, "status": "error"}
    )


async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    """Обработчик Starlette HTTP исключений"""
    if exc.status_code == 500:
        return JSONResponse(
            status_code=500,
            content={"error": "error.server.internal_error", "status": "error"},
        )

    return await http_exception_handler(request, exc)


async def custom_exception_handler(request: Request, exc: Exception):
    """Обработчик кастомных исключений - конвертирует их в HTTPException"""
    
    if isinstance(exc, BaseCustomException):
        return JSONResponse(
            status_code=exc.get_status_code(),
            content={"error": exc.message, "status": "error"}
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": "error.server.internal_error", "status": "error"}
    )
