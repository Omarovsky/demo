from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import uvicorn
from room_manager import room_manager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Настройка путей
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR)

# Инициализация шаблонов
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Раздача статических файлов
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API для создания комнаты
@app.get("/create_room")
async def create_room():
    room_id = room_manager.generate_room_id()
    return {"room_id": room_id}

# WebSocket для комнаты
@app.websocket("/ws/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str):
    await websocket.accept()
    await room_manager.join_room(room_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Рассылка сообщений всем в комнате
            for member in room_manager.rooms[room_id]:
                if member != websocket:
                    await member.send_text(data)
    except:
        await room_manager.leave_room(room_id, websocket)

# Страница комнаты
@app.get("/room/{room_id}", response_class=HTMLResponse)
async def get_room(request: Request, room_id: str):
    return templates.TemplateResponse("room.html", {"request": request, "room_id": room_id})

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ws="wsproto",  # Используем ws вместо wss для разработки
        reload=True
    )