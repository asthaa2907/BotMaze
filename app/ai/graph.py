from typing import Dict, Any
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel
from app.core.config import settings
from langchain_groq import ChatGroq


# ✅ Define ChatState properly
class ChatState(BaseModel):
    user: Dict[str, Any]
    message: Dict[str, Any]
    agent_prompt: Dict[str, Any]


# ✅ Build the LangGraph workflow
def build_graph():
    graph = StateGraph(ChatState)

    # This node handles LLM generation
    def generate_response(state: ChatState):
        llm = ChatGroq(
            temperature=0.7,
            model=settings.llm_model,
            api_key=settings.groq_api_key
        )

        user_message = state.message.get("body", "")
        agent_prompt = state.agent_prompt.get("prompt", "")

        mood_info = f"The user seems {state.user.get('mood', 'neutral')} today."
        prompt = (
            f"{agent_prompt}\n\n"
            f"{mood_info}\n"
            f"User: {user_message}\n"
            f"AI (respond with empathy):"
        )


        try:
            result = llm.invoke(prompt)
            reply_text = result.content if hasattr(result, "content") else str(result)
        except Exception as e:
            reply_text = f"Sorry, something went wrong: {e}"

        return {"message": {"body": reply_text}}

    # ✅ Add node and edges to graph
    graph.add_node("generate_response", generate_response)
    graph.add_edge(START, "generate_response")
    graph.add_edge("generate_response", END)

    # ✅ Compile and return the graph
    return graph.compile()
