from fastapi import FastAPI
from . import main


def reg_v1(app: FastAPI):
    # Регистрируем все роутеры версии v1
    routers = [
        main.router,
    ]
    for router in routers:
        app.include_router(router, prefix="/api/v1")
