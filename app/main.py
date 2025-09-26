from fastapi import FastAPI
from presentation.api.v1.routers import user_controller

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

app.include_router(user_controller.router, tags=["Users"])
