from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.api import venues, parsing, export

settings = get_settings()

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
@app.on_event("startup")
async def startup():
    init_db()


# Include routers
app.include_router(venues.router)
app.include_router(parsing.router)
app.include_router(export.router)


@app.get("/")
async def root():
    return {
        "message": "MyTravel AI Parser API",
        "version": settings.API_VERSION,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}