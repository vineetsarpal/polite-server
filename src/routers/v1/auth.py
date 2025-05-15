from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from ... import schemas, models, security
from ... database import get_db
from datetime import timedelta
import os

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

v1_router = APIRouter(
    prefix='/v1/auth',
    tags=['Authentication']
)

@v1_router.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> schemas.Token:
    user = security.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return schemas.Token(access_token=access_token, token_type="bearer")

@v1_router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: Annotated[schemas.User, Depends(security.get_current_active_user)],):
    return current_user


# @router.post('/login', response_model=schemas.Token)
# def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

#     user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

#     if not utils.verify_password(user_credentials.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

#     # Create a token
#     access_token = security.create_access_token(data={"user_id": user.id})

#     # Return a Token
#     return {"access_token": access_token, "token_type": "bearer"}