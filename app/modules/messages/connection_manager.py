from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self._active.get(user_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self._active.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        conexiones_muertas = []
        for websocket in self._active.get(user_id, []):
            try:
                await websocket.send_json(payload)
            except Exception:
                conexiones_muertas.append(websocket)

        for websocket in conexiones_muertas:
            self.disconnect(user_id, websocket)


connection_manager = ConnectionManager()