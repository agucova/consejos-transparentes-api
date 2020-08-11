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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property




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
        return "Consejo @", self.fecha.strftime("%d/%m/%Y")

    def add_representantes(self, asistencia):
        for representante, asistio in asistencia:
            assert isinstance(asistio, str)
            assert isinstance(representante, Representante)
            self.representantes.append(
                Asistencias(fecha_sesion=self.fecha, nombre_representante=representante.nombre, asistio=asistio)
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
