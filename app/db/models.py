from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    mood = Column(String(50), nullable=True)
    step = Column(Integer, default=1)
    password = Column(String, nullable=False)
    active_agent = Column(Integer, ForeignKey("agents.id"), nullable=True)
    is_admin = Column(Boolean, default=False)
    whatsapp_number = Column(String, nullable=True)


    whatsapp_token = Column(String, nullable=True)
    whatsapp_phone_id = Column(String, nullable=True)
    # ---- Relationships (disambiguated) ----
    # 1) current active agent object (note: no back_populates here)
    active_agent_obj = relationship("Agent", foreign_keys=[active_agent])

    # 2) agents created/owned by this user (if you support creators)
    agents = relationship(
        "Agent",
        back_populates="creator",
        foreign_keys="Agent.creator_id"
    )

    # 3) conversations this user is part of
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Conversation.user_id",
    )
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")


class UserMessage(Base):
    __tablename__ = "user_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sender = Column(String)   # "user" or "bot"
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    base_prompt = Column(Text, nullable=False)
    personality = Column(String, default="neutral")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))  
    is_active = Column(Boolean, default=False)
    # ---- Relationships ----
    creator = relationship(
        "User",
        back_populates="agents",
        foreign_keys=[creator_id],
    )

    # *** THIS IS THE MISSING PROPERTY ***
    conversations = relationship(
        "Conversation",
        back_populates="agent",
        cascade="all, delete-orphan",
        foreign_keys="Conversation.agent_id",
    )
    
    creator = relationship("User", back_populates="agents", foreign_keys=[creator_id])
    clients = relationship("Client", back_populates="agent")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # ---- Relationships (must match back_populates names exactly) ----
    user = relationship(
        "User",
        back_populates="conversations",
        foreign_keys=[user_id],
    )
    agent = relationship(
        "Agent",
        back_populates="conversations",
        foreign_keys=[agent_id],
    )

class Client(Base):

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), unique=True, nullable=False)
    last_message = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    greeted = Column(Boolean, default=False)
    # Relationships
    user = relationship("User", back_populates="clients")
    agent = relationship("Agent", back_populates="clients")