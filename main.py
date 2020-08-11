from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from model import Asistencias, Representante, Session
from tasks import actualizar_db, as_dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()

# Used for debugging
if __name__ == "__main__":
    print("Starting app in debugging mode.")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, use_colors=True)

origins = [
    "https://ct.agucova.me"
    "https://agucova.github.io",
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def saludo():
    return "pong!"


def limpiar_asistencias(asistencias):
    asistencias = asistencias
    asistencias_l = []

    for asistencia in asistencias:
        asistencias_l.append(
            {
                "fecha": asistencia.fecha_sesion.strftime("%d/%m/%Y"),
                "asistio": asistencia.asistio,
            }
        )

    return asistencias_l


@app.get("/consejo/generacional/")
def read_item():
    session = Session()
    representantes = [
        as_dict(representante) for representante in session.query(Representante).all()
    ]
    for indice, representante in enumerate(representantes):
        asistencias = limpiar_asistencias(
            session.query(Asistencias)
            .filter(Asistencias.nombre_representante == representante["nombre"])
            .all()
        )
        representantes[indice]["asistencias"] = asistencias

    session.close()

    return representantes
