from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)
cursor = conn.cursor()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SaveRequest(BaseModel):
    file_name: str
    emotion_result: list

@app.post("/save")
async def save_results(request: SaveRequest):
    try:
        # Extract emotion scores
        emotions = request.emotion_result[0]  # Get the first element as it's an array
        anger_score = emotions[0]["score"]
        disgust_score = emotions[1]["score"]
        fear_score = emotions[2]["score"]
        joy_score = emotions[3]["score"]
        neutral_score = emotions[4]["score"]
        sadness_score = emotions[5]["score"]
        surprise_score = emotions[6]["score"]

        # Insert into emotions table
        cursor.execute(
            """
            INSERT INTO emotions (file_name, anger_score, disgust_score, fear_score, joy_score, neutral_score, sadness_score, surprise_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
            """,
            (request.file_name, anger_score, disgust_score, fear_score, joy_score, neutral_score, sadness_score, surprise_score),
        )
        conn.commit()
        return {"message": "Results saved successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
