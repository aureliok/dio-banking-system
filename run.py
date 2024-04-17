from app.api.routes.routes import application
import uvicorn

if __name__ == "__main__":
    uvicorn.run(application, port=8000)