from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .routers import user, auth, policy
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse


app = FastAPI()

# Create tables on startup
Base.metadata.create_all(bind=engine)


# Mount static files
current_dir = os.path.dirname(__file__)
public_dir = os.path.abspath(os.path.join(current_dir, "..", "public", "images"))
app.mount("/static", StaticFiles(directory=public_dir), name="static")

# Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(os.path.join(public_dir, "favicon.ico"))

@app.middleware("http")
async def redirect_http_to_https(request: Request, call_next):
    if request.headers.get("x-forwarded-proto") == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(url))
    return await call_next(request)

app.include_router(user.v1_router, prefix="/api")
app.include_router(auth.v1_router, prefix="/api")
app.include_router(policy.v1_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello World"}