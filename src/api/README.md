# App.py - Your One-Stop Shop for Messing with the ML Model

## What's This?
This is a basic setup for working with the HF NLP model using FastAPI.

---

## Prerequisites
Before you start, make sure you have these:

1. **Python 3.7+** (I use 3.12.8 - 3.13+ does not support PyTorch for some reason)
2. The following Python packages:
    - FastAPI
    - Uvicorn
    - CORS Middleware
    - Transformers

Install everything you need in one go:
```bash
pip install fastapi[all] uvicorn transformers
```

---

## Running the API Service
How to start the API:

1. Open a terminal and navigate to the directory where `app.py` is located.
2. Run this command:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
3. The API will be running at `http://localhost:8000` (PLEASE change it once the API is hosted somewhere else).

### Endpoint Details
- **Endpoint to Analyze Text:**
  - **URL:** `http://localhost:8000/analyze_text`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "text": "Your text here"
    }
    ```
  - **Response:**
    ```json
    {
      "result": [
        {"label": "joy", "score": 0.85},
        {"label": "sadness", "score": 0.05},
        {"label": "anger", "score": 0.10}
      ]
    }
    ```

---

## Hooking It Up to the Frontend
Just two steps.

1. Install Axios:
   ```bash
   npm install axios
   ```

2. Configure your frontend to send a `POST` request to `http://localhost:8000/analyze_text`.

### Example Axios Call:
```javascript
import axios from 'axios';

async function analyzeText(text) {
  const response = await axios.post('http://localhost:8000/analyze_text', {
    text: text,
  });
  console.log(response.data);
}
```

---

## Tips & Workarounds
- **CORS Issues:** Add this to `app.py` (I already did) to handle Cross-Origin Resource Sharing:
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- **Testing the API:** Use Postman or `curl` (bash) or Invoke-WebRequest.
  ```bash
  curl -X POST "http://localhost:8000/analyze_text" \
       -H "Content-Type: application/json" \
       -d '{"text": "I love programming."}'
  ```

  ```
  Invoke-WebRequest -Uri "http://localhost:8000/analyze_text" `
                  -Method POST `
                  -Headers @{ "Content-Type" = "application/json" } `
                  -Body '{"text": "I love programming."}'
  ```

---

## Common Issues
- **404 Error:** Ensure the endpoint path is `/analyze_text`.
- **CORS Errors:** Verify the frontend and backend are communicating properly.
- **Model Problems:** Check if Hugging Face transformers are installed and functioning correctly.

---

That’s it.