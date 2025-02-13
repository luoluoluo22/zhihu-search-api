# Zhihu Search API

This is a simple Flask-based API that reads configuration from a `.env` file and returns it as a JSON response.

## Deployment

To deploy this API to Netlify, follow these steps:

1. Install the dependencies:
   ```bash
   pip install flask
   ```

2. Run the application locally:
   ```bash
   python zhihu_search.py
   ```

3. Deploy to Netlify using their CLI or web interface.

## Endpoints

- `GET /api`: Returns the configuration from `.env` as JSON.