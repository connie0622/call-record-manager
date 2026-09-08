# Backend for call-record-manager

This is a minimal FastAPI-based backend (MVP) for uploading call recordings (MP3/MP4), transcribing them using OpenAI Whisper, and summarizing the transcript using an LLM. It stores results in a local SQLite database and files in the `uploads/` directory.

Environment variables
- OPENAI_API_KEY: your OpenAI API key
- DATABASE_URL: optional; default is sqlite:///./calls.db

Requirements
- ffmpeg must be installed on the host system and available in PATH. (The Docker image includes ffmpeg.)

Run locally (without Docker)
1. python -m venv .venv
2. source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
3. pip install -r requirements.txt
4. uvicorn main:app --reload --host 0.0.0.0 --port 8000

Run with Docker Compose (recommended for the simplest setup)
1. Copy the example env file and set your OpenAI key:
   cp ../.env.example .env
   # Edit .env and put your OPENAI_API_KEY

2. From the repository root, run:
   docker-compose up --build

3. The API will be available at http://localhost:8000

Upload usage
- POST /calls/upload multipart/form-data: file (mp3/mp4/wav/m4a), customer (optional)
- GET /calls/{call_id} to retrieve stored record (transcript, summary, status)

Notes
- The container includes ffmpeg, so no extra host install is required when using Docker Compose.
- Uploaded files are persisted to `backend/uploads` on the host via a bind mount.
