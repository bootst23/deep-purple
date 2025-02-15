from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

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
        current_time = datetime.utcnow()
        
        # Initialize emotion scores with default value 0
        emotion_scores = {
            "sadness": 0,
            "joy": 0,
            "love": 0,
            "anger": 0,
            "fear": 0,
            "surprise": 0
        }
        
        # Update emotion scores based on the emotion_result
        for emotion in request.emotion_result:
            label = emotion["label"].lower()  # Ensure the label is lowercase to match the keys
            if label in emotion_scores:
                emotion_scores[label] = emotion["score"]
        
        # Extract emotion scores
        sadness_score = emotion_scores["sadness"]
        joy_score = emotion_scores["joy"]
        love_score = emotion_scores["love"]
        anger_score = emotion_scores["anger"]
        fear_score = emotion_scores["fear"]
        surprise_score = emotion_scores["surprise"]

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
    group_by: str = Query("day", description="Group by day, week, or month"),
    emotions: str = Query(None, description="Comma-separated list of emotions to filter by")
):
    try:
        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Determine the SQL GROUP BY clause based on the group_by parameter
        if group_by == "week":
            group_by_clause = "DATE_TRUNC('week', \"createdAt\")"
        elif group_by == "month":
            group_by_clause = "DATE_TRUNC('month', \"createdAt\")"
        else:  # Default to day
            group_by_clause = 'DATE("createdAt")'

        # Convert emotions string to list
        selected_emotions = emotions.split(',') if emotions else []

        # Query to count the frequency of each dominant emotion per time period
        query = f"""
            WITH emotion_counts AS (
                SELECT 
                    {group_by_clause} AS date,
                    dominant_emotion,
                    COUNT(*) AS emotion_count,
                    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY {group_by_clause}) AS percentage
                FROM "Results"
                WHERE "createdAt" BETWEEN %s AND %s
                {'AND dominant_emotion IN %s' if selected_emotions else ''}
                GROUP BY {group_by_clause}, dominant_emotion
            ),
            all_dates AS (
                SELECT DISTINCT {group_by_clause} AS date
                FROM "Results"
                WHERE "createdAt" BETWEEN %s AND %s
            ),
            all_emotions AS (
                SELECT DISTINCT dominant_emotion
                FROM "Results"
                WHERE "createdAt" BETWEEN %s AND %s
                {'AND dominant_emotion IN %s' if selected_emotions else ''}
            ),
            date_emotion_matrix AS (
                SELECT 
                    d.date,
                    e.dominant_emotion,
                    COALESCE(ec.percentage, 0) as percentage
                FROM all_dates d
                CROSS JOIN all_emotions e
                LEFT JOIN emotion_counts ec 
                    ON d.date = ec.date 
                    AND e.dominant_emotion = ec.dominant_emotion
            )
            SELECT 
                date,
                dominant_emotion,
                percentage
            FROM date_emotion_matrix
            ORDER BY date, dominant_emotion;
        """
        
        # Execute the query with parameters
        if selected_emotions:
            cursor.execute(query, (start_date, end_date, tuple(selected_emotions), start_date, end_date, start_date, end_date, tuple(selected_emotions)))
        else:
            cursor.execute(query, (start_date, end_date, start_date, end_date, start_date, end_date))

        results = cursor.fetchall()

        # Process results into the required format
        emotion_data = {}
        dates = []
        current_date = None

        for row in results:
            date = row[0].strftime("%Y-%m-%d")
            emotion = row[1].lower()  # Convert emotion to lowercase
            percentage = float(row[2])

            if date not in dates:
                dates.append(date)

            if emotion not in emotion_data:
                emotion_data[emotion] = []
            
            emotion_data[emotion].append(percentage)

        # Format the results
        emotion_trends = [
            {
                "date": date,
                "sadness": emotion_data.get("sadness", [0] * len(dates))[i],
                "joy": emotion_data.get("joy", [0] * len(dates))[i],
                "anger": emotion_data.get("anger", [0] * len(dates))[i],
                "fear": emotion_data.get("fear", [0] * len(dates))[i],
                "surprise": emotion_data.get("surprise", [0] * len(dates))[i],
                "love": emotion_data.get("love", [0] * len(dates))[i]
            }
            for i, date in enumerate(dates)
        ]

        return {"emotion_trends": emotion_trends}
    except Exception as e:
        print(f"Error in get_emotion_trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
# Health-check endpoint
@app.get("/health-check")
async def health_check():
    return {"message": "Server is running and healthy"}