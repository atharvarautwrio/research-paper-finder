import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting ResearchFinder API server on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
