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
    name: str
    file_name: str
    content: str
    input_type: str
    emotion_result: list

@app.post("/save")
async def save_results(request: SaveRequest):
    try:
        # Map scores to labels
        scores = {emotion["label"]: emotion["score"] for emotion in request.emotion_result}

        # Extract emotion scores with default value 0 if not present
        anger_score = scores.get("anger", 0)
        disgust_score = scores.get("disgust", 0)
        fear_score = scores.get("fear", 0)
        joy_score = scores.get("joy", 0)
        neutral_score = scores.get("neutral", 0)
        sadness_score = scores.get("sadness", 0)
        surprise_score = scores.get("surprise", 0)

        cursor.execute(
            """
            INSERT INTO "Results" (name, content, input_type, anger_score, disgust_score, fear_score, joy_score, neutral_score, sadness_score, surprise_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request.name,
                request.content,
                request.input_type,
                anger_score,
                disgust_score,
                fear_score,
                joy_score,
                neutral_score,
                sadness_score,
                surprise_score,
            ),
        )
        conn.commit()
        return {"message": "Results saved successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
