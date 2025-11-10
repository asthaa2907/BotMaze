## 🧩 System Flowchart — BotMaze (WhatsApp AI Agent Management System)

```mermaid
flowchart TD

A[Start] --> B[Client sends message to WhatsApp Business Number]
B --> C[Meta WhatsApp Cloud API]
C --> D[Webhook Endpoint: /webhook/whatsapp (FastAPI)]

D --> E{Is this a valid WhatsApp Verify Request?}
E -->|Yes| F[Return hub.challenge to verify]
E -->|No| G[Process incoming message]

G --> H[Extract phone_number_id and from_number]
H --> I[Find business user by whatsapp_phone_id in DB]

I -->|User not found| J[Log warning - Unknown business number]
I -->|User found| K[Check if client exists for this user]

K -->|Client not found| L[Create new Client record in DB]
L --> M[Send Greeting Message via send_whatsapp_message()]
M --> N[Store client.greeted = True]
N --> O[Wait for agent assignment]
O --> P[End]

K -->|Client exists| Q{Is agent assigned to client?}
Q -->|No| R[Send 'waiting for assignment' message]
R --> P[End]

Q -->|Yes| S[Fetch assigned agent details]
S --> T[Build AI Prompt (agent.base_prompt + message)]
T --> U[Call handle_conversation() → AI model generates reply]
U --> V[Save Conversation in DB]
V --> W[Send reply via send_whatsapp_message()]
W --> X[End]
