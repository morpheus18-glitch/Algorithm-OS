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

## Hosting from a Git Repository

Clone the repository and run the startup script to host the dashboard locally:

```bash
git clone <repo-url> algorithm-dashboard
cd algorithm-dashboard
./startup.sh
```

This starts the backend on port `8000` and the frontend on `8080` so you can access the dashboard at `http://localhost:8080`.

## Running Locally

The quickest way to launch both services is with the provided `startup.sh` script. After cloning the repository, simply run:

```bash
./startup.sh
```

The script installs any missing Python dependencies, starts the API server on port `8000`, and serves the frontend on port `8080`. Open `http://localhost:8080` in your browser and load one of the JSON files in `frontend/sample_data`.

If you prefer to start the components manually:

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

## Docker Compose

To run both services with Docker:

```bash
docker compose up --build
```

The frontend will be available on port `8080` and the API on port `8000`.

## Adding New Algorithms

1. Create a new file in `backend/algorithms` with a `run(data: dict) -> dict` function.
2. The function receives the JSON payload from the frontend and should return a dictionary with any fields required for visualization.
3. The algorithm can then be selected from the dropdown on the dashboard by matching the filename (without extension).

## License

This project is licensed under the MIT License.
