from fastapi import FastAPI

app = FastAPI()


@app.get("/api")
async def root():
    return {"message": "Hello World!"}


@app.get("/api/wall/")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
