# Universal RAG System

A production-ready RAG (Retrieval-Augmented Generation) system that works with various document types, optimized for deployment on Render.

## Features

- Supports multiple document types
- Fast and efficient processing
- Secure API access with API key authentication
- Optimized for deployment on Render (under 512MB)
- Uses Google's Generative AI for responses
- Pinecone for vector storage

## Prerequisites

- Python 3.10+
- Render account (free tier)
- Pinecone account (free tier)
- Google Generative AI API key

## Local Development

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements-optimized.txt
   ```
4. Copy `.env.sample` to `.env` and update with your API keys
5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Deployment to Render

### Method 1: Using Render Dashboard

1. Push your code to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: hackerx-rag (or your preferred name)
   - **Region**: Choose the one closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**:
     ```
     python -m pip install --upgrade pip
     pip install -r requirements-optimized.txt
     ```
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
6. Add the following environment variables:
   - `PYTHON_VERSION`: 3.10.13
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `GOOGLE_API_KEY`: Your Google Generative AI API key
   - `PINECONE_INDEX_NAME`: Your Pinecone index name (default: "hackerx")
7. Click "Create Web Service"

### Method 2: Using Render CLI (Alternative)

1. Install the Render CLI:
   ```bash
   npm install -g render-cli
   ```
2. Log in to your Render account:
   ```bash
   render login
   ```
3. Deploy the service:
   ```bash
   render deploy
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
PINECONE_API_KEY=your_pinecone_api_key
GOOGLE_API_KEY=your_google_api_key
PINECONE_INDEX_NAME=hackerx  # Optional, defaults to "hackerx"
```

## API Documentation

Once deployed, access the interactive API documentation at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc documentation

## API Endpoints

- `POST /submit` - Submit a document and get answers to questions
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with basic information

## Example Request

```bash
curl -X 'POST' \
  'https://your-render-app.onrender.com/submit' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer 612aeb3ebe9d63cfdb21e3f7d679fcebde54f7c1283c92b7937ea72c10c966af' \
  -H 'Content-Type: application/json' \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": ["What is the main topic of this document?"]
  }'
```

## Troubleshooting

- **Deployment Fails**: Check the build logs in the Render dashboard for specific error messages.
- **API Key Issues**: Ensure all required API keys are set in the environment variables.
- **Memory Issues**: The free tier has limited memory. If you encounter memory issues, try reducing the model size or optimizing your code further.

## License

This project is licensed under the MIT License.
   ```bash
   npm i -g @railway/cli
   ```
2. Login to your Railway account:
   ```bash
   railway login
   ```
3. Link your project:
   ```bash
   railway link
   ```
4. Deploy your application:
   ```bash
   railway up
   ```
5. Set the required environment variables:
   ```bash
   railway env set PYTHON_VERSION=3.10.12
   railway env set PINECONE_API_KEY=your_pinecone_key
   railway env set GOOGLE_API_KEY=your_google_key
   ```
   - `PINECONE_INDEX_NAME`: hackerx (or your preferred index name)
7. Click "Create Web Service"

### Method 2: Using Render Blueprint (render.yaml)

1. Push your code to a GitHub/GitLab/Bitbucket repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Blueprint"
4. Connect your repository
5. Select the branch containing the `render.yaml` file
6. Click "Apply"
7. Add your secrets (Pinecone and Google API keys) in the dashboard

## Environment Variables

See `.env.sample` for all required environment variables.

## API Documentation

Once deployed, access the API documentation at:
- Swagger UI: `https://your-render-url.onrender.com/docs`
- ReDoc: `https://your-render-url.onrender.com/redoc`

## Health Check

Check the service status:
```
GET /health
```

## License

MIT
