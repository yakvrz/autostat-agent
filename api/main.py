from fastapi import FastAPI

app = FastAPI(title = "AutoStat Agent")

@app.get("/health")
def health():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}