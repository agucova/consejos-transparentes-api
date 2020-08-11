from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from model import Asistencias, Representante, Session
from tasks import actualizar_db, as_dict


app = FastAPI()

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
