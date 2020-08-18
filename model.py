# coding: utf-8
from typing import List

from sqlalchemy import (
    CHAR,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
    inspect,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import database_exists

database_url = "sqlite:///transparentes.db"
initialize_database = not database_exists(database_url)

engine = create_engine(
    database_url, echo=False, connect_args={"check_same_thread": False}
)

Base = declarative_base()
metadata = Base.metadata


class Asistencias(Base):
    __tablename__ = "asistencias"

    id = Column("id", Integer, primary_key=True, unique=True)
    asistio = Column("asistió", CHAR(1))

    id_sesion = Column(Integer, ForeignKey("sesiones_consejos.id"))
    # fecha_sesion = Column(Date, ForeignKey("sesiones_consejos.fecha"))

    id_representante = Column(Integer, ForeignKey("representantes.id"))
    # nombre_representante = Column(CHAR(200), ForeignKey("representantes.nombre"))


class SesionConsejo(Base):
    __tablename__ = "sesiones_consejos"
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    nombre = Column(CHAR(50), unique=True, nullable=True)
    fecha = Column(Date, unique=True)
    representantes = relationship(
        "Representante", secondary="asistencias", viewonly=True
    )

    def __str__(self):
        if self.nombre:
            return self.nombre
        return "Consejo @", self.fecha.strftime("%d/%m/%Y")

    def add_representantes(self, asistencia):
        # tuplas tipo (<Representante>, True)
        for representante, asistio in asistencia:
            assert isinstance(asistio, str)
            assert isinstance(representante, Representante)
            assert isinstance(representante.id, int)
            assert isinstance(self.id, int)
            self.representantes.append(
                Asistencias(
                    id_sesion=self.id,
                    id_representante=representante.id,
                    asistio=asistio,
                )
            )

        return self

    def get_asistencias(self) -> List[Asistencias]:
        session = SessionLocal.object_session(self)
        return session.query(Asistencias).filter_by(id_sesion=self.id).all()


class Representante(Base):
    __tablename__ = "representantes"
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    nombre = Column(CHAR(200), unique=True, nullable=False)
    tipo = Column(CHAR(3), nullable=True)
    representa = Column(CHAR(200), nullable=True)
    sesiones = relationship(
        "SesionConsejo", secondary="asistencias", viewonly=True, lazy="immediate"
    )
    generacional = Column(Boolean())
    academico = Column(Boolean())

    def get_asistencias(self) -> List[Asistencias]:
        session = SessionLocal.object_session(self)
        return session.query(Asistencias).filter_by(id_representante=self.id).all()


Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
