from fastapi import FastAPI, HTTPException
from transformers import pipeline

# Initialize FastAPI app
app = FastAPI()

# Load the Hugging Face model
print("Loading the model...")
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilroberta-base-emotion")

@app.get("/")
def home():
    return {"message": "Welcome to the DeepPurple Emotion Detection API"}

@app.post("/analyze")
def analyze_emotions(text: str):
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    results = emotion_classifier(text)
    return {"text": text, "emotions": results}