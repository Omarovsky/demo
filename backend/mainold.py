from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import os
import uvicorn
from room_manager import room_manager

app = FastAPI()

# Настройка пути к фронтенду (относительно расположения main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

# Раздача статических файлов (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# Роут для главной страницы
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Роут для комнаты
@app.get("/room/{room_id}")
async def serve_room(room_id: str):
    return FileResponse(os.path.join(FRONTEND_DIR, "room.html"))