import logging

from fastapi import FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import Settings
from .pid_service import PidGenerator, PidRequest

settings = Settings()
pid_gen = PidGenerator(settings)
app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    logging.exception("Returned HTTP error:", exc_info=exc)
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.exception("Received invalid request:", exc_info=exc)
    return await request_validation_exception_handler(request, exc)


@app.post("/pid/")
def generate_pid(pid_request: PidRequest):
    pid = pid_gen.generate_pid(pid_request)
    return {"pid": pid}
