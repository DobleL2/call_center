# Este archivo principal inicia la aplicación FastAPI y carga las rutas
from fastapi import FastAPI
from app.routers import user
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Call Center", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Ensure PUT is included
    allow_headers=["*"],
)

# Include the user router
app.include_router(user.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}
