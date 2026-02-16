from fastapi import FastAPI
from presentation.api.v1.routers import user_controller
from presentation.api.v1.routers import auth_controller
from presentation.api.v1.routers import student_controller
from presentation.api.v1.routers import report_card_controller
from presentation.api.v1.routers import counter_controller, content_controller, content_page_controller 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos: GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite todos los encabezados, incluido Authorization
)

script_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(script_dir, "contents")

# Montar la carpeta
app.mount("/contents", StaticFiles(directory=static_path), name="contents")

""" Sección de usuarios """
app.include_router(user_controller.router, tags=["Users"])
app.include_router(auth_controller.router, tags=["Auth"])

""" Sección de estudiantes """
app.include_router(student_controller.router, tags=["Students"])

""" Sección de reportes """
app.include_router(report_card_controller.router, prefix="/report_card", tags=["Report Cards"])

""" Sección de contadores y estadísticas """
app.include_router(counter_controller.router, prefix="/counters", tags=["Counters"])

""" Sección de comunicados y formatos """
app.include_router(content_controller.router, prefix="/contents", tags=["Contents"])

""" Sección de contenido de páginas """
app.include_router(content_page_controller.router, prefix="/content-pages", tags=["Content Pages"])