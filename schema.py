from typing import List, Optional

from pydantic import BaseModel


class Asistencias(BaseModel):
    asistio: str
    fecha: str

    class Config:
        orm_mode = True


class SesionConsejo(BaseModel):
    id: int
    nombre: str
    fecha: str
    representantes: List["Representante"]
    asistencias: List["Asistencias"]

    class Config:
        orm_mode = True


class Representante(BaseModel):
    id: int
    nombre: str
    tipo: str
    representa: str
    asistencias: List["Asistencias"]
    generacional: Optional[bool]
    academico: Optional[bool]

    class Config:
        orm_mode = True
