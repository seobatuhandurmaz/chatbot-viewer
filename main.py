from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

# 🔒 CORS sadece bu domainden gelen istekleri kabul eder
origins = [
    "https://www.batuhandurmaz.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],     # Sadece POST istekleri kabul edilsin
    allow_headers=["*"],
)

class RequestData(BaseModel):
    url: str
    mode: str

@app.post("/analyze")
def analyze(data: RequestData):
    headers = {'User-Agent': 'GPTBot (https://openai.com/gptbot)'}
    try:
        response = requests.get(data.url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"result": f"Hata oluştu: {e}"}

    if data.mode == "clean":
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "noscript", "footer", "header", "nav", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join(line for line in lines if line and not re.match(r'^[\W_]*$', line))
        return {"result": cleaned}
    else:
        return {"result": response.text}
