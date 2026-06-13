from fastapi import FastAPI

from meuhorario.routers import appointments, auth, services, users

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(appointments.router)
