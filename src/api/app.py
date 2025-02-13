from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline

#init fastAPI
app = FastAPI()

#allow CORS for all origins (only to make it easier for dev -- REMEMBER TO UPDATE WHEN CHANGED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deep-purple-site.onrender.com", "http://localhost:5173"],  # Replace "*" with a specific origin like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

#load HF model
classifier = pipeline("text-classification", model='michellejieli/emotion_text_classifier', return_all_scores=True)

#defining post params
class TextRequest(BaseModel):
    text: str

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        #classification
        predictions = classifier(request.text)

        #return results
        #return {"predictions": predictions}

        # Model updated so new response data and format
        emotion_scores = {pred["label"]: pred["score"] for pred in predictions[0]}
        predicted_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Token influence (dominant emotion for each individual token)
        emotion_influence = {emotion: [] for emotion in emotion_scores.keys()}

        # Construct response
        response = {
            "predicted_emotion": predicted_emotion,
            "emotion_influence": emotion_influence
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health-check endpoint
@app.get("/health-check")
async def health_check():
    return {"message": "Server is running and healthy"}
