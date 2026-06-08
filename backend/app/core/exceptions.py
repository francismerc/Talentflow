import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.errors import ApplicationError

logger = logging.getLogger(__name__)


def register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request,
        exception: StarletteHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "success": False,
                "message": str(exception.detail),
            },
            headers=exception.headers,
        )

    @application.exception_handler(ApplicationError)
    async def application_exception_handler(
        _: Request,
        exception: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "success": False,
                "message": exception.message,
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exception: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "success": False,
                "message": "Request validation failed.",
                "errors": jsonable_encoder(exception.errors()),
            },
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exception: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled application error", exc_info=exception)
        origin = request.headers.get("origin")
        headers = {}
        if origin and origin in get_settings().cors_origins:
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Vary": "Origin",
            }
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected error occurred.",
            },
            headers=headers,
        )
