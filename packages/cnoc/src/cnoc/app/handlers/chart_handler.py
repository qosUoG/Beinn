from websockets import ServerConnection


async def chartHandler(ws: ServerConnection):
    # Subscribe websocket to chart stream

    # A client side readonly websocket
    await ws.wait_closed()
