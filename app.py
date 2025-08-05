from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import pickle
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='secret-key')

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATA_FILE = "dados.pkl"
USERS = {
    "Davi Chaves": "123",
    "Thiago Chaves": "123",
    "Almir Chaves": "123",
    "Thallyta Sara": "123",
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) == password:
        request.session['user'] = username
        return RedirectResponse(url="/home", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Usuário ou senha incorretos."})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return user

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, user: str = Depends(get_current_user)):
    data = load_data()
    user_data = data.get(user, {"transactions": [], "balance": 0})
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user_name": user,
        "transactions": user_data["transactions"],
        "current_balance": user_data["balance"]
    })

@app.get("/new_vale")
async def new_vale(request: Request, value: float, description: str = ""):
    user = get_current_user(request)
    data = load_data()
    user_data = data.get(user, {"transactions": [], "balance": 0})
    new_balance = user_data["balance"] - value
    user_data["balance"] = new_balance
    user_data["transactions"].append({
        "value": -value,
        "description": description,
        "datetime_str": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "balance": new_balance
    })
    data[user] = user_data
    save_data(data)
    return RedirectResponse(url="/home", status_code=302)

@app.get("/add_salary")
async def add_salary(request: Request, value: float, description: str = "Pro labore semanal"):
    user = get_current_user(request)
    data = load_data()
    user_data = data.get(user, {"transactions": [], "balance": 0})
    new_balance = user_data["balance"] + value
    user_data["balance"] = new_balance
    user_data["transactions"].append({
        "value": value,
        "description": description,
        "datetime_str": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "balance": new_balance
    })
    data[user] = user_data
    save_data(data)
    return RedirectResponse(url="/home", status_code=302)

@app.get("/close_week")
async def close_week(request: Request):
    user = get_current_user(request)
    data = load_data()
    data[user] = {"transactions": [], "balance": 0}
    save_data(data)
    return RedirectResponse(url="/home", status_code=302)
