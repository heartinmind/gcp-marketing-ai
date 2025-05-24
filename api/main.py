from fastapi import FastAPI

app = FastAPI(title="MarketingAI API")

@app.get("/")
async def root():
    return {"message": "Hello"}
