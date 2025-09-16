
# rdrive-file-upload-api

A zero-cost FastAPI service for uploading files. Deploy from GitHub to Render's free tier. Includes optional API key protection.

## Endpoints
- `GET /health` – health check
- `POST /upload` – single file upload (multipart/form-data, field name `file`)
- `POST /upload-multiple` – multiple files (field name `files`)
- `GET /files` – list uploaded files

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export API_KEY=change-me  # Windows PowerShell: $env:API_KEY='change-me'
uvicorn app:app --reload
# Open http://127.0.0.1:8000/docs
```

## cURL test
```bash
curl -X POST "http://127.0.0.1:8000/upload"   -H "X-API-Key: change-me"   -F "file=@/path/to/your/file.pdf"
```

## Deploy to Render (free)
1. Create a GitHub repo and push this folder.
2. Create a free account at https://render.com
3. New → **Web Service** → Connect your GitHub → select this repo.
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add Environment Variables:
   - `API_KEY` (any strong value)
   - `ALLOWED_ORIGINS` (optional, e.g. `*`)
6. Deploy → Note the public URL → open `/docs` for Swagger UI.

## MacroDroid upload
Use **HTTP Request** action:
- Method: `POST`
- URL: `https://<your-render-service>.onrender.com/upload`
- Headers: `X-API-Key: <your API_KEY>`
- Enable **multipart/form-data**
- Add file parameter named **file** and choose the file path.

## Security
- Never commit secrets (client_id / client_secret) to GitHub.
- Use API key header or OAuth in front of this service if exposed publicly.
