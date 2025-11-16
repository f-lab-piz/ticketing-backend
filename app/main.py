from fastapi import FastAPI
from app.db import Base, engine
from app.models import User

app = FastAPI()

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
