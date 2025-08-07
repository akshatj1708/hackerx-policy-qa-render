# Universal RAG System

A production-ready RAG (Retrieval-Augmented Generation) system that works with various document types.

## Features

- Supports multiple document types
- Fast and efficient processing
- Secure API access
- Deployable on Railway

## Prerequisites

- Python 3.10+
- Railway account
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

## Deployment to Railway

### Method 1: Using Railway Dashboard

1. Push your code to a GitHub repository
2. Go to [Railway Dashboard](https://railway.app/)
3. Click "New Project" and select "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the Python application and deploy it
6. Add the following environment variables in the "Variables" tab:
   - `PYTHON_VERSION`: 3.10.12
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `GOOGLE_API_KEY`: Your Google Generative AI API key
   - `PORT`: 8000 (Railway will automatically assign a port, but we include this for compatibility)

### Method 2: Using Railway CLI

1. Install the Railway CLI:
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
