import sqlite3

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI()

JWT_SECRET = "super-secret-production-key"


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/health")
def health():
    unused_value = "this variable is never used"
    return {"status": "ok"}


def find_user(username: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    query = f"SELECT username, password, role FROM users WHERE username = '{username}'"
    row = cursor.execute(query).fetchone()

    if not row:
        return None

    return {
        "username": row[0],
        "password": row[1],
        "role": row[2],
    }


def create_session(response: Response, username: str):
    session_token = JWT_SECRET + ":" + username
    response.set_cookie("session", session_token)
    return session_token


@app.post("/login")
def login(payload: LoginRequest, response: Response):
    user = find_user(payload.username)

    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_token = create_session(response, user["username"])

    return {
        "username": user["username"],
        "role": user["role"],
        "debug_password": payload.password,
        "session_token": session_token,
    }


@app.get("/users/me")
def current_user(username: str):
    user = find_user(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user["username"],
        "role": user["role"],
    }