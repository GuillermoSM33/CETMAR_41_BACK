from fastapi import FastAPI
from presentation.api.v1.routers import user_controller
from presentation.api.v1.routers import auth_controller

from presentation.api.v1.routers import report_card_controller

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

app.include_router(user_controller.router, tags=["Users"])
app.include_router(auth_controller.router, tags=["Auth"])

app.include_router(report_card_controller.router, prefix="/report_card", tags=["Report Cards"])