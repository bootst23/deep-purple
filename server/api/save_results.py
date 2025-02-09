from fastapi import FastAPI, HTTPException, Query
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
    dominant_emotion: str
    summary: str
    actionable_insights: str
    suggested_response: str

@app.post("/save")
async def save_results(request: SaveRequest):
    try:
        # Map scores to labels
        scores = {emotion["label"]: emotion["score"] for emotion in request.emotion_result}

        # Extract emotion scores with default value 0 if not present
        sadness_score = scores.get("sadness", 0)
        joy_score = scores.get("joy", 0)
        love_score = scores.get("love", 0)
        anger_score = scores.get("anger", 0)
        fear_score = scores.get("fear", 0)
        surprise_score = scores.get("surprise", 0)

        cursor.execute(
            """
            INSERT INTO "Results" (name, content, input_type, sadness_score, joy_score, love_score, anger_score, fear_score, surprise_score, dominant_emotion, summary, actionable_insights, suggested_response)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request.name,
                request.content,
                request.input_type,
                sadness_score,
                joy_score,
                love_score,
                anger_score,
                fear_score,
                surprise_score,
                request.dominant_emotion,
                request.summary,
                request.actionable_insights,
                request.suggested_response,
            ),
        )
        conn.commit()
        return {"message": "Results saved successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emotion-trends")
async def get_emotion_trends(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    group_by: str = Query("day", description="Group by day, week, or month")
):
    try:
        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Determine the SQL GROUP BY clause based on the group_by parameter
        if group_by == "week":
            group_by_clause = "DATE_TRUNC('week', createdAt)"
        elif group_by == "month":
            group_by_clause = "DATE_TRUNC('month', createdAt)"
        else:  # Default to day
            group_by_clause = "DATE(createdAt)"

        # Query the database for emotion trends
        cursor.execute(
            f"""
            SELECT
                {group_by_clause} AS date,
                AVG(sadness_score) AS avg_sadness,
                AVG(joy_score) AS avg_joy,
                AVG(love_score) AS avg_love,
                AVG(anger_score) AS avg_anger,
                AVG(fear_score) AS avg_fear,
                AVG(surprise_score) AS avg_surprise
            FROM "Results"
            WHERE createdAt BETWEEN %s AND %s
            GROUP BY {group_by_clause}
            ORDER BY {group_by_clause}
            """,
            (start_date, end_date)
        )
        results = cursor.fetchall()

        # Format the results
        emotion_trends = [
            {
                "date": row[0].strftime("%Y-%m-%d"),
                "sadness": row[1],
                "joy": row[2],
                "love": row[3],
                "anger": row[4],
                "fear": row[5],
                "surprise": row[6],
            }
            for row in results
        ]

        return {"emotion_trends": emotion_trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health-check endpoint
@app.get("/health-check")
async def health_check():
    return {"message": "Server is running and healthy"}

