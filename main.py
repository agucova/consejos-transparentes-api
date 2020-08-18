from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

import crud
import model
import schema
import tasks
from crud import get_representantes

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="(https://.*\.agucova\.me)|(http://127.0.0.1.*)|(https://.*\.github\.io)|(https://.*\.cai\.cl)",
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    session = model.SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Used for debugging
if __name__ == "__main__":
    print("Starting app in debugging mode.")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, use_colors=True)


@app.get("/")
def saludo():
    return "pong!"


@app.get("/rep/{consejo}/", response_model=List[schema.Representante])
def representantes(consejo: str, session: Session = Depends(get_db)):
    return get_representantes(session, consejo)


@app.get("/rep/generacional/", status_code=418)
def rep_academico():
    return "I'm a teapot."
