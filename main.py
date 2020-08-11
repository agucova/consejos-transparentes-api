from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from model import Asistencias, Representante, Session
from tasks import actualizar_db, as_dict
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "https://agucova.github.io",
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

actualizar_db()

@app.get("/ping")
def saludo():
    return "pong!"


def limpiar_asistencias(asistencias):
    asistencias = asistencias
    asistencias_l = []

    for asistencia in asistencias:
        asistencias_l.append(
            {"fecha": asistencia.fecha_sesion.strftime("%d/%m/%Y"), "asistio": asistencia.asistio}
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
