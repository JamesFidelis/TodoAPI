import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt
from datetime import timedelta, datetime

SECRET_KEY = '$2b$12$LxPU.6sKqy/85DKxKbOku.XUSm6szcS5hYIb/oZ7oQt8vi3kwlSIu'
ALGORITHM = 'HS256'


class CreateUser(BaseModel):
    email: Optional[str]
    username: str
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        raise False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_user_token(username: str, user_id: int, expires_delta: Optional[int]):
    encode = {"sub": username, "id": user_id}

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


app = FastAPI()


def get_hashed_password(password):
    return bcrypt_context.hash(password)


@app.post("/create/user")
async def create_user(register: CreateUser, db: Session = Depends(get_db)):
    register_model = models.Users()
    register_model.email = register.email
    register_model.username = register.username
    register_model.first_name = register.first_name
    register_model.last_name = register.last_name
    hash_password = get_hashed_password(register.password)
    register_model.hashed_password = hash_password
    register_model.is_active = True

    db.add(register_model)
    db.commit()

    return statusResponse(201)


@app.post("/token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token_expires = timedelta(minutes=20)
    token = create_user_token(user.username, user.id, expires_delta=token_expires)

    return {"token": token}


def statusResponse(status_code: int):
    return {
        "Status": status_code,
        "response": " User Created Successfully"
    }


uvicorn.run(app)
