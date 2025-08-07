# Universal RAG System

A production-ready RAG (Retrieval-Augmented Generation) system that works with various document types.

## Features

- Supports multiple document types
- Fast and efficient processing
- Secure API access
- Deployable on Render

## Prerequisites

- Python 3.11+
- Render account
- Pinecone account
- Google Generative AI API key

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.sample` to `.env` and fill in your API keys
4. Run the application:
   ```bash
   bash start.sh
   ```

## Deployment to Render

### Method 1: Using Render Dashboard

1. Push your code to a GitHub/GitLab/Bitbucket repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your repository
5. Configure the following settings:
   - **Name**: universal-rag-system (or your preferred name)
   - **Region**: Choose the closest region
   - **Branch**: main (or your preferred branch)
   - **Root Directory**: / (if your files are in the root)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash start.sh`
6. Add the following environment variables in the "Advanced" section:
   - `PYTHON_VERSION`: 3.11.0
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `GOOGLE_API_KEY`: Your Google Generative AI API key
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
