from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db import models, database
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# List agents
@router.get("/agents", response_class=HTMLResponse)
def list_agents(request: Request, db: Session = Depends(database.get_db)):
    agents = db.query(models.Agent).all()
    return templates.TemplateResponse("agents.html", {"request": request, "agents": agents})

# Create new agent
@router.post("/agents/create")
def create_agent(
    name: str = Form(...),
    tone: str = Form("Friendly"),
    base_prompt: str = Form("You are a helpful AI assistant."),
    model_provider: str = Form("OpenAI"),
    model_id: str = Form("gpt-3.5-turbo"),
    db: Session = Depends(database.get_db)
):
    agent = models.Agent(
        name=name,
        tone=tone,
        base_prompt=base_prompt,
        model_provider=model_provider,
        model_id=model_id
    )
    db.add(agent)
    db.commit()
    return RedirectResponse("/agents", status_code=303)
