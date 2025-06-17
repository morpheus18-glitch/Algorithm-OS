# Algorithm Dashboard

This project provides a lightweight dashboard for running and visualizing algorithms such as the Travelling Salesman Problem (TSP) and Dijkstra's shortest path. The frontend is written in vanilla JavaScript with D3.js for visualization, while the backend uses FastAPI.

## Features

- Upload datasets in JSON format and run algorithms through the dashboard
- Real‑time visualization of paths and graphs
- Easy to extend: drop new Python scripts into `backend/algorithms`
- Optional Docker Compose setup for running frontend and backend
- Export results as CSV

## Folder Structure

```
backend/              FastAPI application and algorithms
frontend/             Static files served to the browser
  css/               Stylesheets
  js/                JavaScript modules
  libs/              Local copies of D3 and Three.js
  sample_data/       Example datasets for testing
```

## Getting the Code

Clone the repository using git:

```bash
git clone https://github.com/yourusername/Algorithm-OS.git
cd Algorithm-OS
```

## Running Locally

1. Copy `.env.example` to `.env` and adjust the database settings if needed.
2. Install Python dependencies (requires PostgreSQL client libraries):
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Ensure PostgreSQL is running and accessible using the credentials in `.env`.
4. Start both backend and frontend together:
   ```bash
   ./start.sh
   ```
5. Open `http://localhost:8080` in your browser and load one of the JSON files in `frontend/sample_data`.

## Docker Compose

To run both services with Docker:

```bash
docker compose up --build
```

The frontend will be available on port `8080` and the API on port `8000`.
PostgreSQL will listen on port `5432` with credentials defined in `.env`.

## Adding New Algorithms

1. Create a new file in `backend/algorithms` with a `run(data: dict) -> dict` function.
2. The function receives the JSON payload from the frontend and should return a dictionary with any fields required for visualization.
3. The algorithm can then be selected from the dropdown on the dashboard by matching the filename (without extension).

## License

This project is licensed under the MIT License.
