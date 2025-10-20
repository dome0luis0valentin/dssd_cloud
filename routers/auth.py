from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from schemas.auth import Token
from utils.security import authenticate_user, create_access_token, get_db, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username
    user = authenticate_user(db, email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
