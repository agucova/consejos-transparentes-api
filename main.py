from typing import Optional, List
from fastapi import Depends, FastAPI, status
from pydantic import BaseModel
from crud import get_representantes
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import uvicorn
import tasks, model, schema, crud


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


@app.get("/rep/generacional/", response_model=List[schema.Representante])
def rep_generacional(session: Session = Depends(get_db)):
    return get_representantes(session, "generacional")


@app.get("/rep/generacional/", status_code=418)
def rep_academico():
    return "I'm a teapot."
