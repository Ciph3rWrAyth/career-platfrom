from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import AIUnavailable, AIBadResponse

from app.logging_config import logger


def _error(status_code: int, message):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": status_code, "message": message}},
    )


def register_error_handlers(app):
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        return _error(exc.status_code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        return _error(422, jsonable_encoder(exc.errors()))
    
    @app.exception_handler(AIUnavailable)
    async def handle_ai_unavailable(request: Request, exc:AIUnavailable):
        logger.warning("ИИ недоступен на %s: %s", request.url.path, exc)
        return _error(503, "ИИ-сервис временно недоступен, попробуйте позже")

    @app.exception_handler(AIBadResponse)
    async def handle_ai_bad_response(request: Request, exc:AIBadResponse):
        logger.error("Непригодный ответ ИИ на  %s: %s ", request.url.path, exc)
        return _error(502, "ИИ вернул некорректный ответ")

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        logger.exception("Необработанная ошибка при запросе %s", request.url.path)
        return _error(500, "Внутренняя ошибка сервера")
