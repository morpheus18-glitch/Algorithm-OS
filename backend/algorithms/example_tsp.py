def run(data: dict) -> dict:
    # Simple placeholder algorithm
    points = data.get('points', [])
    return {"path": list(range(len(points))), "elapsed": 0.0}
