## for server start up
node server/app.js

## API to save analysis result to databse hosted on render
uvicorn src.api.save_results:app --host 0.0.0.0 --port 8001

## API for Hugging Face
uvicorn src.api.app:app --host 127.0.0.1 --port 8000

