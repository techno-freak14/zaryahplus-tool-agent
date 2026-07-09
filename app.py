from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import agent  # Imports your updated agent.py

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    prompt: str

# Route to serve the HTML UI
@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
 return templates.TemplateResponse(request=request, name="index.html")
# Route to handle the chat logic
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Runs your agent loop and grabs the dictionary it returns
    result = agent.run_agent_loop(req.prompt)
    return {"answer": result["answer"], "trace": result["trace"]}

if __name__ == "__main__":
    print("Starting Web UI at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)