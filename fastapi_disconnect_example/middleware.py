import asyncio

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class HttpDisconnectException(BaseException):
    pass


class HttpDisconnectMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def _cancel() -> None:
            await disconnected_event.wait()
            raise HttpDisconnectException()

        message_queue = asyncio.Queue[Message]()
        completed_event = asyncio.Event()
        disconnected_event = asyncio.Event()

        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(
                self._queue_message(
                    receive,
                    message_queue,
                    completed_event,
                    disconnected_event,
                )
            )
            task_group.create_task(
                self._consume_message(
                    scope,
                    send,
                    message_queue,
                    completed_event,
                )
            )
            task_group.create_task(_cancel())

    async def _queue_message(
        self,
        receive: Receive,
        message_queue: asyncio.Queue[Message],
        completed_event: asyncio.Event,
        disconnected_event: asyncio.Event,
    ) -> None:
        while not completed_event.is_set():
            message = await receive()
            await message_queue.put(message)

            if message["type"] == "http.disconnect" and not completed_event.is_set():
                disconnected_event.set()
                break

    async def _consume_message(
        self,
        scope: Scope,
        send: Send,
        message_queue: asyncio.Queue[Message],
        completed_event: asyncio.Event,
    ) -> None:
        async def _send(message: Message) -> None:
            await send(message)
            completed_event.set()

        await self.app(scope, message_queue.get, _send)
