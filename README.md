# 🤖 BotMaze – AI WhatsApp Assistant Platform

BotMaze is an AI-powered WhatsApp automation platform where multiple chat agents can be created, customized, and assigned to clients dynamically.  
It allows admins to manage agents, clients, and conversations seamlessly from an intuitive dashboard built using **FastAPI**, **Jinja2**, and **TailwindCSS**.

---

## 🚀 Features

### 🌐 WhatsApp Integration
- Real-time WhatsApp messaging through **Meta WhatsApp Cloud API**  
- Supports **permanent access tokens**  
- Auto-greeting for new clients  
- Dynamic client-agent conversation routing  

### 🧩 Agent Management
- Create, edit, delete, activate, and deactivate agents  
- Define unique personality, tone, and behavior for each agent  
- Agents respond intelligently using integrated AI models  

### 🗣️ Client Management
- Automatic client creation on first WhatsApp message  
- Assign or reassign any agent to any client  
- Real-time client list with last message, phone number, and current agent  

### 📊 Admin Dashboard
- Clean dashboard interface built with TailwindCSS  
- Manage agents and clients easily  
- Displays total active agents, connected WhatsApp details, and account summary  

---

## 🖼 BotMaze Dashboard & Pages Showcase

<p align="center">
  <img src="screenshots/Dashboard.png" alt="Dashboard View" width="70%">
  <br>
  <em>📊 Dashboard – View your connected WhatsApp and manage your account.</em>
</p>

<p align="center">
  <img src="screenshots/agents.png" alt="Agents Page" width="70%">
  <br>
  <em>🤖 Agents Page – Create and manage multiple AI-powered agents.</em>
</p>

<p align="center">
  <img src="screenshots/Clients.png" alt="Clients Page" width="70%">
  <br>
  <em>👥 Clients Page – Assign agents to clients and view latest messages.</em>
</p>

<p align="center">
  <img src="screenshots/Create_new_agent.png" alt="Create Agent" width="70%">
  <br>
  <em>⚙ Create New Agent – Customize agent name, tone, and base prompt.</em>
</p>

---

## 💬 WhatsApp Chat Demos

<p align="center">
  <img src="screenshots/Chat_with_StudyBot.jpg" alt="Chat with StudyBot" width="29%">
  <img src="screenshots/Chat_ with_HealthCoach.png" alt="Chat with Health Coach" width="30%">
  <br>
  <em>💬 AI Agent Conversations – StudyBot (left) and Health Coach (right).</em>
</p>
---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | FastAPI |
| Database | SQLite (SQLAlchemy ORM) |
| Frontend | Jinja2 + TailwindCSS |
| Messaging | Meta WhatsApp Cloud API |
| AI Layer | Custom NLP + Prompt-based response logic |
| Authentication | Basic user management (Admin login) |

---


## 🔐 Environment Variables (.env)
Create a `.env` file in the root directory with the following:

```bash
WHATSAPP_VERIFY_TOKEN=your_meta_verify_token
WHATSAPP_PHONE_NUMBER_ID=your_meta_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token
DATABASE_URL=sqlite:///./botmaze.db










