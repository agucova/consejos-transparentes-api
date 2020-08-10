from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from model import Session, SesionConsejo, Representante, Asistencias, cargar_db, as_dict
from sqlalchemy.orm import load_only
from pprint import pprint

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


@app.get("/")
def saludo():
    return {"saludo": "Hola, Mundo"}


def limpiar_asistencias(asistencias):
    asistencias = asistencias
    asistencias_l = []

    for asistencia in asistencias:
        asistencias_l.append(
            {"fecha": asistencia.fecha_sesion, "asistio": asistencia.asistio}
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


cargar_db()
