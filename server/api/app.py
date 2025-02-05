from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import requests
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the fine-tuned Singlish DistilBERT model
MODEL_PATH = "server/fine_tuned_distilbert_singlish"  # Ensure this is the correct path
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
model.eval()  # Set the model to evaluation mode

# Hugging Face API Key 
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  

# Define request models
class TextRequest(BaseModel):
    text: str

class BatchTextRequest(BaseModel):
    texts: List[str]  # List of customer reviews

# Emotion labels for the model
LABELS = ["sadness", "joy", "love", "anger", "fear", "surprise"] 

# Define prediction function
def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1).tolist()[0]
    
    # Convert scores to label-probability mapping
    predictions = [{"label": label, "score": score} for label, score in zip(LABELS, scores)]
    return predictions

# Define function to generate dynamic insights using Hugging Face API
def generate_dynamic_insights(text, dominant_emotion, is_batch=False):
    if is_batch:
        prompt = f"""
        Analyze the following customer reviews and provide structured insights based on the overall sentiment.

        Customer Reviews: "{text}"
        Detected Dominant Emotion: {dominant_emotion}

        Your response should include:
        1. A short summary of the overall customer sentiment.
        2. Three actionable business suggestions based on the overall sentiment.
        3. A suggested response the business can use to address the overall sentiment.

        Format the output as:
        **Summary:** <summary>
        **Actionable Insights:**
        1. <insight 1>
        2. <insight 2>
        3. <insight 3>
        **Suggested Response:** <suggested response>
        """
    else:
        prompt = f"""
        Analyze the following customer review and provide structured insights.

        Customer Review: "{text}"
        Detected Emotion: {dominant_emotion}

        Your response should include:
        1. A short summary of the customer's feelings.
        2. Three actionable business suggestions based on the sentiment.
        3. A suggested response the business can send to the customer.

        Format the output as:
        **Summary:** <summary>
        **Actionable Insights:**
        1. <insight 1>
        2. <insight 2>
        3. <insight 3>
        **Suggested Response:** <suggested response>
        """

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {"inputs": prompt}

    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",  # Use the correct model endpoint
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        generated_text = response.json()[0]['generated_text']
        # Remove the prompt from the generated text
        generated_text = generated_text.replace(prompt, "").strip()
        
        # Parse the generated text to extract summary, insights, and suggested response
        summary_match = re.search(r"\*\*Summary:\*\* (.*?)\n", generated_text, re.DOTALL)
        insights_match = re.search(r"\*\*Actionable Insights:\*\*([\s\S]*?)\*\*Suggested Response:\*\*", generated_text, re.DOTALL)
        response_match = re.search(r"\*\*Suggested Response:\*\*([\s\S]*)", generated_text, re.DOTALL)

        summary = summary_match.group(1).strip() if summary_match else "No summary found."
        insights = insights_match.group(1).strip() if insights_match else "No insights found."
        suggested_response = response_match.group(1).strip() if response_match else "No suggested response found."

        return {
            "summary": summary,
            "insights": insights,
            "suggested_response": suggested_response
        }
    else:
        return {
            "summary": "Error generating insights.",
            "insights": f"Error: {response.text}",
            "suggested_response": "Error generating suggested response."
        }

# Endpoint for direct input (individual review analysis)
@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        predictions = predict_emotion(request.text)
        sorted_predictions = sorted(predictions, key=lambda x: x["score"], reverse=True)
        dominant_emotion = sorted_predictions[0]["label"]

        # Generate dynamic insights using Hugging Face API
        dynamic_insights = generate_dynamic_insights(request.text, dominant_emotion, is_batch=False)

        return {
            "predictions": predictions,
            "dominant_emotion": dominant_emotion,
            "summary": dynamic_insights["summary"],
            "insights": dynamic_insights["insights"],
            "suggested_response": dynamic_insights["suggested_response"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for batch processing (multiple reviews)
@app.post("/analyze-batch")
async def analyze_batch_texts(request: BatchTextRequest):
    try:
        # Combine all reviews into a single string
        combined_text = "\n\n".join(request.texts)

        # Analyze the combined text
        predictions = predict_emotion(combined_text)
        sorted_predictions = sorted(predictions, key=lambda x: x["score"], reverse=True)
        dominant_emotion = sorted_predictions[0]["label"]

        # Generate dynamic insights using Hugging Face API
        dynamic_insights = generate_dynamic_insights(combined_text, dominant_emotion, is_batch=True)

        return {
            "predictions": predictions,
            "dominant_emotion": dominant_emotion,
            "summary": dynamic_insights["summary"],
            "insights": dynamic_insights["insights"],
            "suggested_response": dynamic_insights["suggested_response"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health-check endpoint
@app.get("/health-check")
async def health_check():
    return {"message": "Server is running and healthy"}