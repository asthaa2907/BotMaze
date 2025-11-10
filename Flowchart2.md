flowchart TD

A1[User Registers/Login to Dashboard] --> B1[Connect WhatsApp API]
B1 --> C1[Stores whatsapp_token, phone_id, and number in DB]

C1 --> D1[Creates Multiple AI Agents]
D1 --> E1[Each agent has name, tone, and base prompt]

E1 --> F1[Dashboard shows all agents and active status]
F1 --> G1[Admin views Clients auto-created from WhatsApp]

G1 --> H1[Assign specific Agent to a Client]
H1 --> I1[Agent now replies automatically to that client’s messages]

I1 --> J1[Admin can activate/deactivate agents anytime]
J1 --> K1[View analytics (total agents, active agents, etc.)]
K1 --> L1[End]
