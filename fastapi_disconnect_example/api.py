import asyncio
import logging

from fastapi import FastAPI

from fastapi_disconnect_example.middleware import HttpDisconnectMiddleware

logging.basicConfig()

app = FastAPI()

app.add_middleware(HttpDisconnectMiddleware)


@app.post("/")
async def some_long_operation():
    await asyncio.sleep(10)
    logging.warn("Finished some long operation, returning...")
    return {}
