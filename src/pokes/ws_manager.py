from fastapi import WebSocket, WebSocketDisconnect


class PokeConnectionManager:
    """
    Tracks live `/pokes/ws` connections per user, so a poke can be pushed to
    whoever's on the receiving end without them refreshing the page.

    A user may have the app open in several tabs/devices at once, hence the set.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self._connections.get(user_id)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            del self._connections[user_id]

    async def send_to_user(self, user_id: int, message: dict) -> None:
        """Best-effort: a send failure just drops that connection, never raises."""
        for websocket in list(self._connections.get(user_id, ())):
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(user_id, websocket)


poke_connections = PokeConnectionManager()
