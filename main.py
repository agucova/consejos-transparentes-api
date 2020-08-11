from typing import Optional
from fastapi import FastAPI, status
from pydantic import BaseModel
from model import Asistencias, Representante, Session
from tasks import actualizar_db, as_dict
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="(https://.*\.agucova\.me)|(http://127.0.0.1.*)|(https://.*\.github\.io)|(https://.*\.cai\.cl)",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Used for debugging
if __name__ == "__main__":
    print("Starting app in debugging mode.")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, use_colors=True)


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



@app.get("/rep/generacional/")
def rep_generacional():
    session = Session()
    representantes = [
        as_dict(representante) for representante in session.query(Representante).all()
    ]
    for indice, representante in enumerate(representantes):
        asistencias = limpiar_asistencias(
            session.query(Asistencias)
            .filter(Asistencias.id == representante["id"])
            .all()
        )
        representantes[indice]["asistencias"] = asistencias

    session.close()

    return representantes

@app.get("/rep/generacional/", status_code=418)
def rep_academico():
    return "I'm a teapot."
