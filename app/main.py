from fastapi import FastAPI
from app.api import whatsapp
from app.db.database import engine
from app.db import models
from app.api import agents
app = FastAPI(title="BotMaze API")

# ✅ Create all tables automatically
models.Base.metadata.create_all(bind=engine)
# Include your WhatsApp routes
app.include_router(whatsapp.router)

app.include_router(agents.router)
