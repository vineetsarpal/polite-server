from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request, Security
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .routers.v1 import user, auth, policy
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from . import config
from fastapi.responses import FileResponse
from fastapi_auth0 import Auth0, Auth0User

auth0 = Auth0(
    domain=config.AUTH0_DOMAIN,
    api_audience=config.AUTH0_AUDIENCE,
    scopes={'read:messages': ''}
)

app = FastAPI()

API_BASE_PREFIX = "/api"

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

app.include_router(auth.v1_router, prefix=API_BASE_PREFIX)
app.include_router(user.v1_router, prefix=API_BASE_PREFIX)
app.include_router(policy.v1_router, prefix=API_BASE_PREFIX)

# Auth0 private endpoint test
@app.get("/api/private", dependencies=[Depends(auth0.implicit_scheme)])
def private(user: Auth0User = Security(auth0.get_user)):
    return {"user": user}


@app.get("/")
async def root():
    return {"message": "Hello World 2!"}