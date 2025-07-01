from fastapi import FastAPI
from api.routers.datasets import router as datasets_router  # clearer import

app = FastAPI(title="AutoStat Agent")
app.include_router(datasets_router)


@app.get("/health")
def health():
    return {"status": "ok"}
