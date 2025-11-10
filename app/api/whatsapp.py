from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Conversation, Agent, UserMessage, Client
from datetime import datetime
from app.ai.graph import build_graph, ChatState
from app.ai.memory import add_memory, retrieve_memory, detect_mood
from app.core.config import settings
from app.api.utils import send_whatsapp_message, normalize_phone
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, PlainTextResponse
from app.db.session import SessionLocal
from fastapi import Form
from app.utils.auth_utils import hash_password, verify_password, create_access_token
from app.utils.auth_utils import get_current_user
from datetime import timedelta
from fastapi.templating import Jinja2Templates
import json
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

from fastapi.responses import PlainTextResponse
VERIFY_TOKEN = "my_token_12345"
@router.get("/webhook/whatsapp")
async def verify_token(request: Request):
    """
    Handles Meta (WhatsApp) Webhook Verification
    """
    params = request.query_params
    print("🔍 Verification request received:", dict(params))

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    # Logging for debugging
    print(f"Mode: {mode}, Token: {token}, Challenge: {challenge}")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verification successful!")
        # Return the challenge as plain text (Meta expects this)
        return PlainTextResponse(content=challenge, status_code=200)

    print("❌ Webhook verification failed — token mismatch or bad mode")
    return PlainTextResponse(content="Forbidden", status_code=403)


@router.get("/register")
async def register_form():
    html = """
    <html>
    <head>
        <title>Register - BotMaze</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f3f4f6;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .form-container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                max-width: 400px;
                width: 100%;
                text-align: center;
            }
            h2 {
                color: #4F46E5;
                margin-bottom: 20px;
            }
            label {
                display: block;
                text-align: left;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input {
                width: 100%;
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 6px;
                border: 1px solid #ccc;
                font-size: 14px;
            }
            button {
                background-color: #4F46E5;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }
            button:hover {
                background-color: #4338CA;
            }
            a {
                color: #4F46E5;
                text-decoration: none;
                display: block;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>📝 Create Your Account</h2>
            <form action="/register" method="post">
                <label>Name:</label>
                <input name="name" required>
                
                <label>Phone:</label>
                <input name="phone" required>
                
                <label>Password:</label>
                <input type="password" name="password" required>
                
                <button type="submit">Register</button>
            </form>
            <a href="/login">Already have an account? Login →</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# 🧾 Handle Registration
@router.post("/register")
async def register_user(
    name: str = Form(...), phone: str = Form(...), password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    if len(password) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")

    new_user = User(name=name, phone=phone, password=hash_password(password))
    db.add(new_user)
    db.commit()
    return HTMLResponse("<h3>✅ Registration successful! <a href='/login'>Go to login</a></h3>")


# 🔐 Login
@router.get("/login")
async def login_form():
    html = """
    <html>
    <head>
        <title>Login - BotMaze</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f3f4f6;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .form-container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                max-width: 400px;
                width: 100%;
                text-align: center;
            }
            h2 {
                color: #4F46E5;
                margin-bottom: 20px;
            }
            label {
                display: block;
                text-align: left;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input {
                width: 100%;
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 6px;
                border: 1px solid #ccc;
                font-size: 14px;
            }
            button {
                background-color: #4F46E5;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }
            button:hover {
                background-color: #4338CA;
            }
            a {
                color: #4F46E5;
                text-decoration: none;
                display: block;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>🔐 Login to BotMaze</h2>
            <form action="/login" method="post">
                <label>Phone:</label>
                <input name="phone" required>
                
                <label>Password:</label>
                <input type="password" name="password" required>
                
                <button type="submit">Login</button>
            </form>
            <a href="/register">← Don’t have an account? Register</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# 🔑 Handle Login
@router.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, phone: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == phone).first()
    if not user or not verify_password(password, user.password):
        return HTMLResponse(content="Invalid credentials", status_code=400)

    # Create JWT token
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data={"sub": user.phone}, expires_delta=access_token_expires)

    # ✅ Store token as cookie
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    return response

@router.get("/logout")
async def logout_user():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
@router.post("/webhook/whatsapp")
async def unified_whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles all incoming WhatsApp messages dynamically per business (user) account.
    """
    try:
        data = await request.json()
        print(f"📩 Incoming WhatsApp Message: {data}")

        # Extract Meta payload structure
        entry = data.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])

        # Ignore delivery status events or empty payloads
        if not messages:
            print("ℹ️ Ignored non-message webhook.")
            return {"status": "ignored"}

        message = messages[0]
        from_number = message["from"]
        text = message.get("text", {}).get("body", "").strip()
        sender_name = contacts[0]["profile"]["name"] if contacts else "Unknown"
        phone_id = value["metadata"]["phone_number_id"]

        # --- STEP 1: Identify the business user (owner of this phone_id) ---
        user = db.query(User).filter(User.whatsapp_phone_id == phone_id).first()
        if not user:
            print(f"⚠️ No registered business user for phone_id: {phone_id}")
            return {"status": "unknown_business"}

        # --- STEP 2: Check or create client entry ---
        client = db.query(Client).filter(
            Client.phone == from_number,
            Client.user_id == user.id
        ).first()

        # ✅ Create client if not found
        if not client:
            client = Client(
                name=sender_name,
                phone=from_number,
                user_id=user.id,
                greeted=False,
                created_at=datetime.utcnow()
            )
            db.add(client)
            db.commit()
            db.refresh(client)
            print(f"🆕 New client created: {sender_name} ({from_number})")

            # Greet message
            greeting = (
                f"👋 Hi {sender_name}! Thanks for contacting *{user.name or 'our team'}*.\n"
                "Please wait while we connect you with an assistant."
            )

            send_whatsapp_message(
                to=from_number,
                message=greeting,
                access_token=user.whatsapp_token,
                phone_number_id=user.whatsapp_phone_id
            )

            client.greeted = True
            db.commit()
            return {"status": "client_created"}

        # --- STEP 3: Handle returning client ---
        print(f"💬 Message from existing client: {client.name} ({client.phone})")

        # If no agent assigned yet
        if not client.agent_id:
            waiting_msg = (
                "🤖 Thank you for your message! A bot will be assigned to assist you soon."
            )
            send_whatsapp_message(
                to=from_number,
                message=waiting_msg,
                access_token=user.whatsapp_token,
                phone_number_id=user.whatsapp_phone_id
            )
            print("⚠️ No agent assigned yet — sent waiting message.")
            return {"status": "waiting_for_agent"}

        # --- STEP 4: Agent assigned — generate AI response ---
        agent = db.query(Agent).filter(Agent.id == client.agent_id).first()
        if not agent:
            send_whatsapp_message(
                to=from_number,
                message="⚠️ The assigned bot seems unavailable. Please try again later.",
                access_token=user.whatsapp_token,
                phone_number_id=user.whatsapp_phone_id
            )
            print("⚠️ Assigned agent missing.")
            return {"status": "agent_missing"}

        # AI response
        full_prompt = f"{agent.base_prompt}\nUser: {text}\nAgent:"
        reply = handle_conversation(from_number, full_prompt, db)

        send_whatsapp_message(
            to=from_number,
            message=reply,
            access_token=user.whatsapp_token,
            phone_number_id=user.whatsapp_phone_id
        )

        print(f"✅ Replied to {client.name} using agent {agent.name}")
        return {"status": "ok"}

    except Exception as e:
        print(f"❌ Error in unified_whatsapp_webhook: {e}")
        return {"status": "error"}
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # ✅ Instead of using session, just get the first (or admin) user
    user = db.query(User).first()

    if not user:
        return HTMLResponse("<h3>No admin user found. Please create one in the database.</h3>", status_code=404)

    # ✅ Fetch agent stats dynamically
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.is_active == True).count()

    # ✅ Check WhatsApp connection status
    whatsapp_connected = bool(user.whatsapp_token and user.whatsapp_phone_id)

    context = {
        "request": request,
        "user": user,
        "whatsapp_connected": whatsapp_connected,
        "total_agents": total_agents,
        "active_agents": active_agents,
    }

    return templates.TemplateResponse("dashboard.html", context)
@router.get("/dashboard/agents", response_class=HTMLResponse)
async def agents_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Display all agents created by the currently logged-in user.
    """
    agents = db.query(Agent).filter(Agent.creator_id == current_user.id).all()

    return templates.TemplateResponse(
        "agents.html",
        {
            "request": request,
            "current_user": current_user,
            "agents": agents,
        },
    )


    
# ✅ Switch agent for a given user
def switch_agent_for_user(db: Session, phone: str, agent_name: str):
    """Switch the active agent for a user, creating the agent if necessary."""
    agent_name = agent_name.strip()
    if not agent_name:
        return "⚠️ Please provide an agent name, e.g. /use MazeGuide"

    # Find the user
    user = db.query(User).filter(User.phone.like(f"%{phone}%")).first()
    if not user:
        return "⚠️ User not found. Please say hi first to register."

    # Look for the agent in the database
    agent = db.query(Agent).filter(Agent.name.ilike(agent_name)).first()

    # If the agent doesn’t exist, create a new one
    if not agent:
        agent = Agent(
            name=agent_name,
            base_prompt=f"You are {agent_name}, a helpful and friendly AI assistant with a unique personality."
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        print(f"🆕 Created new agent: {agent_name}")

    # Switch the user's active agent
    user.active_agent = agent.id
    db.commit()
    print(f"🔁 {user.name} switched to {agent.name}")

    return f"✅ Switched to agent '{agent.name}'. Now chatting as {agent.name}!"



@router.get("/dashboard/connect-whatsapp", response_class=HTMLResponse)
async def connect_whatsapp_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user is automatically resolved from JWT token
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    token_display = (
        user.whatsapp_token[:6] + "..." if user.whatsapp_token else None
    )

    context = {
        "request": request,
        "token_display": token_display,
        "whatsapp_phone_id": user.whatsapp_phone_id or "",
        "whatsapp_number": user.whatsapp_number or "",
        "username": user.name or "User",
    }

    return templates.TemplateResponse("connect_whatsapp.html", context)

# ------------------------------------------
# 🔹 POST: Save WhatsApp Token and Phone ID
# ------------------------------------------
@router.post("/dashboard/connect-whatsapp")
async def connect_whatsapp_post(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    form = await request.form()
    whatsapp_token = form.get("whatsapp_token")
    whatsapp_phone_id = form.get("whatsapp_phone_id")
    whatsapp_number = form.get("whatsapp_number")

    if not whatsapp_token or not whatsapp_phone_id:
        return HTMLResponse("<h3>⚠️ Missing WhatsApp Token or Phone ID.</h3>", status_code=400)

    # Update user’s connection info
    user = db.query(User).filter(User.id == current_user.id).first()
    user.whatsapp_token = whatsapp_token.strip()
    user.whatsapp_phone_id = whatsapp_phone_id.strip()
    user.whatsapp_number = whatsapp_number.strip() if whatsapp_number else None
    db.commit()

    print(f"✅ WhatsApp connected for {user.name or 'User'} — Phone ID: {whatsapp_phone_id}")

    return RedirectResponse(url="/dashboard/connect-whatsapp", status_code=303)


@router.post("/dashboard/disconnect-whatsapp")
async def disconnect_whatsapp(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.whatsapp_token = None
    user.whatsapp_phone_id = None
    user.whatsapp_number = None
    db.commit()

    print("❌ WhatsApp disconnected successfully.")
    return RedirectResponse(url="/dashboard/connect-whatsapp", status_code=303)


@router.get("/dashboard/agents/new", response_class=HTMLResponse)
async def new_agent_form(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("new_agent.html", {"request": request, "current_user": current_user})


@router.post("/dashboard/agents/new")
async def create_agent(
    name: str = Form(...),
    personality: str = Form(...),
    base_prompt: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_agent = Agent(
        name=name,
        personality=personality,
        base_prompt=base_prompt,
        creator_id=current_user.id
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return RedirectResponse(url="/dashboard/agents", status_code=303)


# ✏️ Edit Agent
@router.get("/dashboard/agents/edit/{agent_id}", response_class=HTMLResponse)
async def edit_agent_form(request: Request, agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return HTMLResponse("<h3>Agent not found.</h3>", status_code=404)
    return templates.TemplateResponse("edit_agent.html", {"request": request, "agent": agent})

@router.post("/dashboard/agents/edit/{agent_id}")
async def update_agent(agent_id: int, request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return HTMLResponse("<h3>Agent not found.</h3>")

    agent.name = form_data.get("name")
    agent.personality = form_data.get("personality")
    agent.base_prompt = form_data.get("base_prompt")
    db.commit()
    db.refresh(agent)

    return templates.TemplateResponse(
        "agent_updated.html",
        {"request": request, "agent": agent}
    )


@router.get("/dashboard/agents/delete/{agent_id}")
async def delete_agent(agent_id: int, request: Request, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return HTMLResponse("<h3>Agent not found.</h3>")

    db.delete(agent)
    db.commit()

    return templates.TemplateResponse(
        "agent_deleted.html",
        {"request": request, "agent": agent}
    )



@router.get("/dashboard/chat/{user_id}", response_class=HTMLResponse)
async def view_chat(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return HTMLResponse("<h3>User not found.</h3>", status_code=404)

    messages = (
        db.query(UserMessage)
        .filter(UserMessage.user_id == user_id)
        .order_by(UserMessage.timestamp.asc())
        .all()
    )

    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "user": user, "messages": messages}
    )



@router.post("/dashboard/agents/{agent_id}/activate")
async def activate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.is_active = True
    db.commit()
    db.refresh(agent)
    return RedirectResponse(url="/dashboard/agents", status_code=303)


@router.post("/dashboard/agents/{agent_id}/deactivate")
async def deactivate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.is_active = False
    db.commit()
    db.refresh(agent)
    return RedirectResponse(url="/dashboard/agents", status_code=303)



def handle_conversation(phone: str, message: str, db: Session):
    """
    Handles chat for both registered users and clients.
    Generates AI responses with memory and personality.
    """
    # Try to match phone number to a registered dashboard user
    user = db.query(User).filter(User.phone.like(f"%{phone}%")).first()

    # 🧩 If not a registered user, check if it's a client
    if not user:
        client = db.query(Client).filter(Client.phone.like(f"%{phone}%")).first()
        if not client:
            print(f"⚠️ Unknown number: {phone} — no user or client found.")
            return "👋 Hi there! Please wait while we connect you with an assistant."

        # If no agent assigned yet
        if not client.agent_id:
            print(f"⚠️ Client {client.name} has no assigned agent.")
            return "🤖 A bot will be assigned to assist you soon."

        # Load the assigned agent
        agent = db.query(Agent).filter(Agent.id == client.agent_id).first()
        if not agent:
            return "⚠️ The assigned agent is currently unavailable. Please try again later."

        # Retrieve last messages (memory)
        past_context = retrieve_memory(phone, message)
        memory_text = "\nRecent conversation:\n" + "\n".join(past_context[-5:]) if past_context else ""

        # Build agent tone
        personality_tone = agent.personality or "neutral"
        tone_examples = {
            "friendly": "Use warm, kind, and caring language 😊",
            "professional": "Be concise, polite, and business-like.",
            "humorous": "Be witty and light-hearted 😂",
            "neutral": "Be natural, polite, and clear."
        }
        tone_instruction = tone_examples.get(personality_tone.lower(), tone_examples["neutral"])

        # Compose final prompt
        full_prompt = f"""
You are {agent.name}, a chatbot on BotMaze.
{tone_instruction}

Knowledge and behavior:
{agent.base_prompt}

{memory_text}

User said: {message}
Respond as {agent.name}.
"""

        # Generate AI reply
        try:
            graph = build_graph()
            state = ChatState(
                user={"id": client.id, "name": client.name or "Client"},
                message={"body": full_prompt},
                agent_prompt={"prompt": agent.base_prompt}
            )
            result = graph.invoke(state)
            reply_text = result["message"]["body"]
        except Exception as e:
            print(f"⚠️ AI engine failed for client {client.name}: {e}")
            reply_text = f"[{agent.name}]: Sorry, I’m thinking too hard right now 😅"

        # Save in Conversation table
        convo = Conversation(
            user_id=client.user_id,  # maps back to business user
            agent_id=agent.id,
            message=message,
            response=reply_text
        )
        db.add(convo)
        db.commit()

        # Add memory
        add_memory(phone, message)
        add_memory(phone, reply_text)

        print(f"🤖 {agent.name} replied to client {client.name}: {reply_text}")
        return reply_text

    # ===============================
    # Case 2️⃣: Registered Dashboard User
    # ===============================
    agent = db.query(Agent).filter(Agent.id == user.active_agent).first()
    if not agent:
        return "⚠️ No active agent found. Please activate one on your dashboard."

    past_context = retrieve_memory(phone, message)
    memory_text = "\nRecent conversation:\n" + "\n".join(past_context[-5:]) if past_context else ""

    personality_tone = agent.personality or "neutral"
    tone_examples = {
        "friendly": "Use warm and kind language 😊",
        "professional": "Be concise and polite.",
        "humorous": "Be witty and fun 😂",
        "neutral": "Be polite and natural."
    }
    tone_instruction = tone_examples.get(personality_tone.lower(), tone_examples["neutral"])

    full_prompt = f"""
You are {agent.name}, a chatbot on BotMaze.
{tone_instruction}

Base behavior:
{agent.base_prompt}

User mood: {user.mood or "neutral"}

{memory_text}

User said: {message}
Respond as {agent.name}.
"""

    try:
        graph = build_graph()
        state = ChatState(
            user={"id": user.id, "name": user.name, "mood": user.mood},
            message={"body": full_prompt},
            agent_prompt={"prompt": agent.base_prompt}
        )
        result = graph.invoke(state)
        reply_text = result["message"]["body"]
    except Exception as e:
        print(f"⚠️ AI engine failed for user {user.name}: {e}")
        reply_text = f"[{agent.name}]: Sorry, I’m not feeling smart right now 😅"

    convo = Conversation(
        user_id=user.id,
        agent_id=agent.id,
        message=message,
        response=reply_text
    )
    db.add(convo)
    db.commit()

    add_memory(phone, message)
    add_memory(phone, reply_text)

    print(f"🤖 {agent.name} ({personality_tone}) replied to user {user.name}")
    return reply_text

@router.get("/dashboard/clients", response_class=HTMLResponse)
async def dashboard_clients(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Fetch clients and agents belonging to this user
    clients = db.query(Client).filter(Client.user_id == current_user.id).all()
    agents = db.query(Agent).filter(Agent.creator_id == current_user.id).all()

    return templates.TemplateResponse(
        "clients.html",
        {
            "request": request,
            "clients": clients,
            "agents": agents,
            "current_user": current_user,
        },
    )



# --- Assign agent to client ---
@router.post("/dashboard/clients/assign_agent")
async def assign_agent(
    request: Request,
    client_id: int = Form(...),
    agent_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # Update the assigned agent
        client.agent_id = agent_id if agent_id else None
        db.commit()

        print(f"✅ Agent {agent_id} assigned to client {client_id}")
        return RedirectResponse(url="/dashboard/clients", status_code=303)
    except Exception as e:
        print(f"❌ Error assigning agent: {e}")
        return PlainTextResponse("Error assigning agent", status_code=500)
    
@router.get("/dashboard/clients", response_class=HTMLResponse)
async def view_clients(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()
    clients = db.query(Client).filter(Client.user_id == user.id).all()
    agents = db.query(Agent).filter(Agent.creator_id == user.id).all()

    return templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": clients,
        "agents": agents
    })
