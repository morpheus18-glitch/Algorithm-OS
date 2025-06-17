# Algorithm Dashboard

This project provides a lightweight dashboard for running and visualizing algorithms such as the Travelling Salesman Problem (TSP) and Dijkstra's shortest path. The frontend is written in vanilla JavaScript with D3.js for visualization, while the backend uses FastAPI.

## Features

- Upload datasets in JSON format and run algorithms through the dashboard
- Real‑time visualization of paths and graphs
- Easy to extend: drop new Python scripts into `backend/algorithms` and they
  automatically appear in the UI
- Optional Docker Compose setup for running frontend and backend
- Export results as CSV

## Folder Structure

```
backend/              FastAPI application and algorithms
frontend/             Static files served to the browser
  libs/               Local copies of D3 and Three.js
  sample_data/        Example datasets for testing
```

## Running Locally

1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Start the API server:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Serve the frontend (for example using the built‑in server):
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```
4. Open `http://localhost:8080` in your browser. The dashboard queries the server
   for available algorithms and lets you upload a dataset (see `frontend/sample_data`).

## Docker Compose

To run both services with Docker:

```bash
docker compose up --build
```

The frontend will be available on port `8080` and the API on port `8000`.

## Adding New Algorithms

1. Create a new file in `backend/algorithms` with a `run(data: dict) -> dict` function.
2. The function receives the JSON payload from the frontend and should return a dictionary with any fields required for visualization.
3. When the server restarts, the algorithm is automatically listed by the `/api/algorithms` endpoint and becomes selectable in the dashboard.

## License

This project is licensed under the MIT License.
