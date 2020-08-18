import model, schema
from sqlalchemy.orm import load_only


def enriquecer_asistencias(session, asistencias):
    asistencias = asistencias
    asistencias_limpias = []

    for asistencia in asistencias:
        fecha = session.query(model.SesionConsejo).get(asistencia.id_sesion).fecha.strftime("%d/%m/%Y")
        asistencias_limpias.append(
            {
                "fecha": fecha,
                "asistio": asistencia.asistio,
            }
        )

    return asistencias_limpias

def get_representantes(session, consejo):
    if consejo == "generacional":
        representantes = session.query(model.Representante).filter(model.Representante.generacional == True).options(load_only("id", "nombre", "tipo", "representa")).all()
    elif consejo in ["académico", "academico"]:
        representantes = session.query(model.Representante).filter(model.Representante.academico == True).options(load_only("id", "nombre", "tipo", "representa")).all()
    else:
        representantes = session.query(model.Representante).options(load_only("id", "nombre", "tipo", "representa", "generacional", "academico")).all()

    for indice, representante in enumerate(representantes):
        asistencias = enriquecer_asistencias(session, representante.get_asistencias())
        representante.asistencias = asistencias
        representantes[indice] = representante

    return representantes