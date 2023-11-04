from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from schemas import ChatPrompt
from utils import generate_response
from logger import logging

logger = logging.getLogger('app')

app = FastAPI()


origins = [
        "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def prompt(prompt: ChatPrompt):
    return {"response": generate_response(prompt.messages)}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)