import uvicorn
import sys

sys.path.append("..")

from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from TodosApp.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

SECRET_KEY = '$2b$12$LxPU.6sKqy/85DKxKbOku.XUSm6szcS5hYIb/oZ7oQt8vi3kwlSIu'
ALGORITHM = 'HS256'


class CreateUser(BaseModel):
    email: Optional[str]
    username: str
    first_name: str
    last_name: str
    password: str


class Login(BaseModel):
    username: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"user": "Not authorized"}}
)


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


def get_hashed_password(password):
    return bcrypt_context.hash(password)


@router.post("/create")
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

    return {
        "status": status_response(201),
        "username": register.username,
        "first_name": register.first_name,
        "last_name": register.last_name
    }


@router.post("/token")
async def get_token(
        login: Login,
        db: Session = Depends(get_db)):
    user = authenticate_user(login.username, login.password, db)
    if not user:
        raise token_exception()
    token_expires = timedelta(minutes=20)
    token = create_user_token(user.username, user.id, expires_delta=token_expires)
    user_data = db.query(models.Users).filter(models.Users.id == user.id).first()

    return {"token": token,
            "data": {
                "full_name": user_data.first_name + ' ' + user_data.last_name,
                "email": user_data.email
            }

            }


@router.get("/current")
async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise get_user_exception()


def status_response(status_code: int):
    return {
        "Status": status_code,
        "response": " User Created Successfully"
    }


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Verify credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return credentials_exception


def token_exception():
    token_fail = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_fail

# uvicorn.run(app, port=8000)
