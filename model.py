# coding: utf-8
from sqlalchemy import (
    CHAR,
    Column,
    Date,
    ForeignKey,
    Integer,
    Table,
    create_engine,
    String,
)
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy_utils import database_exists, create_database
from sheets import get_generational, get_academic, setup_service
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func, inspect


import pandas as pd

import datetime as dt

engine = create_engine("sqlite:///transparentes.db", echo=False)
Base = declarative_base()
metadata = Base.metadata


class Asistencias(Base):
    __tablename__ = "asistencias"

    id = Column("id", Integer, primary_key=True, unique=True)
    asistio = Column("asistió", CHAR(1))

    nombre_representante = Column(CHAR(200), ForeignKey("representantes.nombre"))
    fecha_sesion = Column(Date, ForeignKey("sesiones_consejos.fecha"))


class SesionConsejo(Base):
    __tablename__ = "sesiones_consejos"
    nombre = Column(CHAR(50), unique=True, nullable=True)
    fecha = Column(Date, nullable=False, unique=True, primary_key=True)
    representantes = relationship(
        "Representante", secondary="asistencias", viewonly=True
    )

    def __str__(self):
        if self.nombre:
            return self.nombre
        return self.fecha.strftime("%d/%m/%Y")

    def add_representantes(self, asistencia):
        for representante, asistio in asistencia:
            assert isinstance(asistio, str)
            assert isinstance(representante, Representante)
            self.asistencias.append(
                Asistencias(sesion=self, representante=representante, asistio=asistio)
            )

        return self


class Representante(Base):
    __tablename__ = "representantes"
    nombre = Column(CHAR(200), primary_key=True, unique=True, nullable=False)
    tipo = Column(CHAR(3), nullable=True)
    representa = Column(CHAR(200), nullable=True)
    sesiones = relationship(
        "SesionConsejo", secondary="asistencias", viewonly=True, lazy="immediate"
    )
    # entradas = association_proxy('sesiones', 'entrada')


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

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


def transpose(lista):
    # https://stackoverflow.com/questions/6473679/transpose-list-of-lists
    return list(map(list, zip(*lista)))


def as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def transformar_representaciones(representaciones):
    representaciones_l = []
    for representacion in representaciones:
        if representacion.isdigit():
            representacion = ("DG", representacion)
        else:
            representacion = (representacion, "Ingeniería")

        representaciones_l.append(representacion)
    return representaciones_l


def cargar_db():
    session = Session()
    # service = setup_service()
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
    print(pd.DataFrame(tgeneracional))
    nombres = tgeneracional[1][1:]
    representaciones = transformar_representaciones(tgeneracional[0][1:])

    sesiones = {}
    representantes = {}
    for indice, nombre in enumerate(nombres):
        representacion = representaciones[indice]
        tipo = representacion[0]
        representa = representacion[1]
        representantes[nombre] = Representante(
            nombre=nombre, representa=representa, tipo=tipo
        )

    for fecha in fechas_en_tabla:
        sesiones[fecha] = SesionConsejo(fecha=fecha)

    for indice_y, fecha in enumerate(fechas_por_agregar):
        y = indice_y + 2
        for indice_x, representante in enumerate(tgeneracional[indice_y][1:]):
            x = indice_x + 1
            nombre = nombres[x - 1]
            asistio = tgeneracional[y][x]

            representante = representantes[nombre]
            sesion = sesiones[fecha]

            sesion.add_representantes([(representante, asistio)])

    for representante in representantes.values():
        session.merge(representante)

    for sesion in sesiones.values():
        session.merge(sesion)

    session.commit()

    session.close()
