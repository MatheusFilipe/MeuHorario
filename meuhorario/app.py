from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from meuhorario.routers import appointments, auth, services, users

app = FastAPI()

origins = [
    'http://localhost:5173',
    'http://localhost:3000',
    'https://matheusfilipe.github.io',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(appointments.router)
