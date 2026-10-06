from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active: dict[tuple[int, str], list[WebSocket]] = {}

    async def connect(self, user_id: int, canal: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active.setdefault((user_id, canal), []).append(websocket)

    def disconnect(self, user_id: int, canal: str, websocket: WebSocket) -> None:
        key = (user_id, canal)
        conexiones = self._active.get(key, [])
        if websocket in conexiones:
            conexiones.remove(websocket)
        if not conexiones:
            self._active.pop(key, None)

    def is_connected(self, user_id: int, canal: str) -> bool:
        return bool(self._active.get((user_id, canal)))

    async def send_to_channel(self, user_id: int, canal: str, payload: dict) -> None:
        muertas = []
        for websocket in self._active.get((user_id, canal), []):
            try:
                await websocket.send_json(payload)
            except Exception:
                muertas.append(websocket)
        for websocket in muertas:
            self.disconnect(user_id, canal, websocket)


connection_manager = ConnectionManager()