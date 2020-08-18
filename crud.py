from typing import List

from sqlalchemy.orm import Session, load_only

import model
import schema


def enriquecer_asistencias(
    session: Session, asistencias: List[model.Asistencias]
) -> List[dict]:
    asistencias = asistencias
    asistencias_limpias = []

    for asistencia in asistencias:
        fecha = (
            session.query(model.SesionConsejo)
            .get(asistencia.id_sesion)
            .fecha.strftime("%d/%m/%Y")
        )
        asistencias_limpias.append(
            {"fecha": fecha, "asistio": asistencia.asistio,}
        )

    return asistencias_limpias


def get_representantes(session: Session, consejo: str) -> List[model.Representante]:
    if consejo == "generacional":
        representantes = (
            session.query(model.Representante)
            .filter(model.Representante.generacional == True)
            .options(load_only("id", "nombre", "tipo", "representa"))
            .all()
        )
    elif consejo in ["académico", "academico"]:
        representantes = (
            session.query(model.Representante)
            .filter(model.Representante.academico == True)
            .options(load_only("id", "nombre", "tipo", "representa"))
            .all()
        )
    else:
        representantes = (
            session.query(model.Representante)
            .options(
                load_only(
                    "id", "nombre", "tipo", "representa", "generacional", "academico"
                )
            )
            .all()
        )

    for indice, representante in enumerate(representantes):
        asistencias = enriquecer_asistencias(session, representante.get_asistencias())
        representante.asistencias = asistencias
        representantes[indice] = representante

    return representantes
