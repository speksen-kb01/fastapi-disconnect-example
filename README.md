#### Run the project

```bash
poetry install
poetry shell
# with granian
granian --interface asgi fastapi_disconnect_example.api:app
# with hypercorn
hypercorn fastapi_disconnect_example.api:app
# with uvicorn
uvicorn fastapi_disconnect_example.api:app
```

After running the project, make a simple post request:

```bash
curl --location --request POST 'http://localhost:8000/'
```

After making the request, it should return in 10 seconds. If you cancel the request in the meantime, it should raise `HttpDisconnectException`.
You can cancel the requests this way with hypercorn and uvicorn, but not with granian. Granian doesn't seem to raise this exception (maybe not sending the disconnect message to the middleware?).
Granian after cancelling the request, keeps running the process and returns a result. You can see the log "Finished some long operation, returning..." after cancelling.

versions:

- granian = 1.3.1
- uvicorn = 0.29.0
- hypercorn = 0.16.0
