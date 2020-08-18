import datetime as dt
from typing import List

import pandas as pd
from celery import Celery
from celery.schedules import solar
from sqlalchemy import (
    CHAR,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
    inspect,
)

from model import Representante, SesionConsejo, SessionLocal, initialize_database
from sheets import get_academic, get_generational, setup_service

queue = Celery("tasks", broker="redis://localhost:6379/0")
queue.conf.timezone = "America/Santiago"

queue.conf.beat_schedule = {
    # Actualizar la BBDD cuando se oscurece naúticamente en Santiago
    # Encontré notable que si quiera una opción así exista
    # Lo corre cuando el sol está 12 grados bajo el horizonte
    "actualizar-puesta-naútica": {
        "task": "tasks.actualizar_db",
        "schedule": solar("dusk_nautical", -33.459229, -70.645348),
    },
}

##########################
# Inicialización de BBDD #
##########################


def convertir_fecha(fecha_str):
    assert isinstance(fecha_str, str)

    fecha_l = fecha_str.strip().split("/")
    # El año está acortado, ojo con el siglo 22
    fecha_l[2] = "20" + fecha_l[2]
    fecha_l = [int(parte) for parte in fecha_l]
    assert len(fecha_l) == 3

    day, month, year = fecha_l

    return dt.date(year, month, day)


def transpose(lista: List[list]) -> List[list]:
    # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
    return list(map(list, zip(*lista)))


def transformar_representaciones(representaciones: list) -> list:
    representaciones_l = []
    for representacion in representaciones:
        if representacion.isdigit():
            representacion = ("DG", representacion)
        else:
            representacion = (representacion, "Ingeniería")

        representaciones_l.append(representacion)
    return representaciones_l


@queue.task
def actualizar_db():
    print("Updating database using the Google Sheets API.")
    session = SessionLocal()
    service = setup_service()
    # generacional = get_generational(
    #     service, "1USCGq_T6GfEC2662Z6iRrSzc1AAoMHM4W13ATAvFs54"
    # )
    generacional = [
        ["Representación", "Nombre", "7/5/20", "5/6/20", "1/7/20", "4/7/20", "06/8/20"],
        ["2020", "Agustín Covarrubias", "P", "P", "P", "P", "P"],
        ["2020", "Katherine Catoni", "P", "P", "P", "P", "P"],
        ["2020", "Rafael Rencoret", "P", "P", "P", "P", "P"],
        ["2019", "Tania Hinostroza", "P", "P", "P", "P", "P"],
        ["2019", "Florencia Sciaraffia", "P", "P", "P", "P", "P"],
        ["2019", "Martín Illanes", "P", "P", "P", "P", "P"],
        ["2018", "Joaquín Castaños", "P", "P", "J", "P", "P"],
        ["2018", "Elizabeth Hermosilla", "P", "P", "J", "P", "P"],
        ["2018", "Pedro Becker", "P", "P", "P", "P", "P"],
        ["2017", "Camila López", "P", "P", "P", "P", "P"],
        ["2017", "Francisco Úrzua", "P", "P", "P", "P", "O"],
        ["2017", "Bartolomé Peirano", "P", "P", "P", "P", "P"],
        ["2016", "Manuel Jara", "P", "P", "P", "P", "P"],
        ["2016", "Ivania Arias", "P", "P", "P", "P", "P"],
        ["2016", "María Belén Echenique", "P", "P", "P", "P", "P"],
        ["2015 y ant.", "Denise Cariaga", "P", "P", "P", "P", "P"],
        ["2015 y ant.", "Graciela Hernández", "P", "P", "P", "P", "P"],
        ["2015 y ant.", "Caterin Pinto", "P", "P", "P", "P", "O"],
        ["CAI", "Isa Oyarzo", "P", "P", "P", "P", "P"],
        ["CAI", "Thomas Struszer", "P", "P", "P", "P", "P"],
        ["CAI", "Agustín Cox", "P", "P", "P", "P", "P"],
        ["CAI", "Claudio Escobar", "P", "P", "P", "P", "P"],
        ["CAI", "Javiera Dawabe", "P", "P", "P", "P", "P"],
        ["CT", "José Pereira", "P", "P", "P", "A", "P"],
        ["CT", "Trinidad Larraín", "P", "P", "P", "P", "A"],
        ["CT", "María Ignacia Henriquez", "P", "P", "P", "J", "P"],
        ["CT", "Tomás Álvarez", "A", "A", "A", "A", "A"],
        ["CT", "Magdalena Merino", "P", "P", "P", "P", "P"],
    ]

    # academico = get_academic(service, "1ditHP6pQUyAx73t_76csuJUH4t4TPqlRa5CHHWRXz3o")

    fechas_existentes = [sesion.fecha for sesion in session.query(SesionConsejo).all()]
    fechas_en_tabla = [convertir_fecha(fecha) for fecha in generacional[0][2:]]
    fechas_por_agregar = [
        fecha for fecha in fechas_en_tabla if fecha not in fechas_existentes
    ]
    tgeneracional = transpose(generacional)
    nombres = tgeneracional[1][1:]
    representaciones = transformar_representaciones(tgeneracional[0][1:])

    sesiones = {}
    representantes = {}
    for indice, nombre in enumerate(nombres):
        representacion = representaciones[indice]
        tipo = representacion[0]
        representa = representacion[1]
        representantes[nombre] = Representante(
            nombre=nombre, representa=representa, tipo=tipo, generacional=True
        )

    for fecha in fechas_en_tabla:
        sesiones[fecha] = SesionConsejo(fecha=fecha)

    for representante in representantes.values():
        representantes[representante.nombre] = session.merge(representante, load=True)

    for sesion in sesiones.values():
        sesiones[sesion.fecha] = session.merge(sesion, load=True)

    session.flush()

    for indice_y, fecha in enumerate(fechas_por_agregar):
        y = indice_y + 2
        for indice_x, representante in enumerate(tgeneracional[indice_y][1:]):
            x = indice_x + 1
            nombre = nombres[x - 1]
            asistio = tgeneracional[y][x]

            representante = representantes[nombre]
            sesion = sesiones[fecha]

            print(representante.__dict__)
            print(sesion.__dict__)
            sesion.add_representantes([(representante, asistio)])

    session.commit()

    session.close()


# In case the database needs to initialize
if initialize_database:
    actualizar_db()
