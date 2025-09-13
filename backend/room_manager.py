import secrets
from typing import Dict, Set
from fastapi import FastAPI, WebSocket

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}  # room_id -> участники

    def generate_room_id(self) -> str:
        """Генерация уникального ID комнаты (6 символов)"""
        room_id = secrets.token_hex(3).upper()
        while room_id in self.rooms:
            room_id = secrets.token_hex(3).upper()
        return room_id

    async def join_room(self, room_id: str, websocket: WebSocket):
        """Подключение участника к комнате"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(websocket)

    async def leave_room(self, room_id: str, websocket: WebSocket):
        """Отключение участника"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

room_manager = RoomManager()