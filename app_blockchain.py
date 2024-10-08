from fastapi import FastAPI
from blockchain import Blockchain
from block import Block

app = FastAPI()


@app.get("/hello/{name}")
async def root(name:str):
    return {"HELLO "+name.upper()}