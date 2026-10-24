from fastapi import FastAPI

from app.routers import vehicles

app = FastAPI()
app.include_router(vehicles.router)


@app.get("/health")
def health():
    return {"status": "ok"}
