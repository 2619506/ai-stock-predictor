from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI(title="Beginner Stock AI API")

# Allow React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockRequest(BaseModel):
    ticker: str

@app.get("/api/learn/analogies")
def get_analogies():
    return {
        "stock": "A stock is like owning a slice of a pizza shop 🍕. If the shop sells a lot of pizza, your slice becomes more valuable!",
        "volatility": "Volatility is how 'jumpy' a stock is — like a roller coaster 🎢 vs. a calm train 🚆.",
        "dividend": "A dividend is like the company giving you a small cash 'thank you' gift 🎁 just for holding onto their stock."
    }

@app.post("/api/insights/transparent")
def get_transparent_insight(request: StockRequest):
    # Simulated AI Chain-of-Thought outputting beginner-friendly trust language
    trend = random.choice(["growing", "resting", "pulling back"])
    
    return {
        "title": "Transparent AI Insight 🧠",
        "intro": f"Here is how I analyzed the recent data for {request.ticker}, step-by-step:",
        "steps": [
            "First, I looked at the price over the last 30 days to see the general mood of buyers.",
            f"Next, I noticed the stock is currently {trend}, which means it's acting like a runner catching their breath.",
            "Finally, I checked the trading volume (how many slices of the pizza are being traded) to make sure this move is normal."
        ],
        "conclusion": "Because the volume is steady, this looks like normal, healthy market behavior. No need to panic!"
    }
