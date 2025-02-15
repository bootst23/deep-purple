from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import requests
from dotenv import load_dotenv
import os
import re
import string

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deep-purple.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model
MODEL_PATH = "server/fine_tuned_distilbert_singlish"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.eval()

# Hugging Face API Key
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Define request models
class TextRequest(BaseModel):
    text: str

class BatchTextRequest(BaseModel):
    texts: List[str]

# Label mapping
label_to_emotion = {
    0: "Sadness",
    1: "Joy",
    2: "Love",
    3: "Anger",
    4: "Fear",
    5: "Surprise"
}

def get_influential_tokens(sentence):
    # Tokenize input
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True).to(device)
    
    # Forward pass with attention output
    model.to(device)
    outputs = model(**inputs)
    logits = outputs.logits.squeeze(0)
    attentions = outputs.attentions[-1]
    
    # Get tokens
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0].cpu())  # Convert to CPU for token mapping
    
    # Calculate influence for each token
    attention_scores = attentions.mean(dim=1)
    token_scores = attention_scores[0].sum(dim=0).cpu().tolist()
    
    # Map token scores to logits for each emotion
    emotion_influence = {label_to_emotion[i]: [] for i in range(len(label_to_emotion))}
    for i, token in enumerate(tokens):
        for j, emotion in label_to_emotion.items():
            influence_score = token_scores[i] * logits[j].item()
            emotion_influence[emotion].append((token, influence_score))
    
    # Sort tokens by influence for each emotion
    for emotion in emotion_influence:
        emotion_influence[emotion] = sorted(
            emotion_influence[emotion],
            key=lambda x: x[1],
            reverse=True
        )
    
    # Filter ignored tokens and punctuation
    IGNORE_TOKENS = ["[SEP]", "[CLS]", "[UNK]"] + list(string.punctuation)
    for emotion in emotion_influence:
        emotion_influence[emotion] = [
            {"token": tok, "score": score}
            for tok, score in emotion_influence[emotion]
            if tok not in IGNORE_TOKENS
        ]
    
    # Get predicted emotion
    predicted_emotion = label_to_emotion[torch.argmax(logits).item()]
    
    # Get raw predictions for all emotions
    scores = torch.nn.functional.softmax(logits, dim=-1).tolist()
    raw_predictions = [
        {"label": label_to_emotion[i], "score": score}
        for i, score in enumerate(scores)
    ]
    
    # Return formatted output
    return {
        "predicted_emotion": predicted_emotion,
        "emotion_influence": {
            emotion: tokens[:5] for emotion, tokens in emotion_influence.items()
        },
        "predictions": raw_predictions
    }

def generate_dynamic_insights(text, emotion_data, is_batch=False):
    predicted_emotion = emotion_data["predicted_emotion"]
    top_influences = emotion_data["emotion_influence"]

    if is_batch:
        prompt = f"""
        Analyze the following customer reviews with emotion analysis:
        
        Text: "{text}"
        Predicted Emotion: {predicted_emotion}
        Key Emotional Indicators: {top_influences}
        
        Provide:
        1. Overall sentiment summary
        2. Three actionable business suggestions
        3. A suggested response addressing the dominant emotions
        
        Format as:
        **Summary:** <summary>
        **Actionable Insights:**
        1. <insight 1>
        2. <insight 2>
        3. <insight 3>
        **Suggested Response:** <response>
        """
    else:
        prompt = f"""
        Analyze this customer review with emotion analysis:
        
        Review: "{text}"
        Predicted Emotion: {predicted_emotion}
        Key Emotional Indicators: {top_influences}
        
        Provide:
        1. Customer emotion summary
        2. Three actionable suggestions
        3. A suggested response
        
        Format as:
        **Summary:** <summary>
        **Actionable Insights:**
        1. <insight 1>
        2. <insight 2>
        3. <insight 3>
        **Suggested Response:** <response>
        """

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
        headers=headers,
        json={"inputs": prompt}
    )

    if response.status_code == 200:
        generated_text = response.json()[0]['generated_text']
        generated_text = generated_text.replace(prompt, "").strip()
        
        summary_match = re.search(r"\*\*Summary:\*\* (.*?)\n", generated_text, re.DOTALL)
        insights_match = re.search(r"\*\*Actionable Insights:\*\*([\s\S]*?)\*\*Suggested Response:\*\*", generated_text, re.DOTALL)
        response_match = re.search(r"\*\*Suggested Response:\*\*([\s\S]*)", generated_text, re.DOTALL)

        return {
            "summary": summary_match.group(1).strip() if summary_match else "No summary found.",
            "insights": insights_match.group(1).strip() if insights_match else "No insights found.",
            "suggested_response": response_match.group(1).strip() if response_match else "No suggested response found."
        }
    else:
        return {
            "summary": "Error generating insights.",
            "insights": f"Error: {response.text}",
            "suggested_response": "Error generating suggested response."
        }

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        emotion_data = get_influential_tokens(request.text)
        dynamic_insights = generate_dynamic_insights(request.text, emotion_data, is_batch=False)

        return {
            **emotion_data,
            "summary": dynamic_insights["summary"],
            "insights": dynamic_insights["insights"],
            "suggested_response": dynamic_insights["suggested_response"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-batch")
async def analyze_batch_texts(request: BatchTextRequest):
    try:
        combined_text = "\n\n".join(request.texts)
        emotion_data = get_influential_tokens(combined_text)
        dynamic_insights = generate_dynamic_insights(combined_text, emotion_data, is_batch=True)

        return {
            **emotion_data,
            "summary": dynamic_insights["summary"],
            "insights": dynamic_insights["insights"],
            "suggested_response": dynamic_insights["suggested_response"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health-check")
async def health_check():
    return {"message": "Server is running and healthy"}