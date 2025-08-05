from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="chave_super_secreta")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=".")

# Lista de usuários válidos
usuarios_validos = {
    "Davi": "senha123",
    "Thiago": "senha123",
    "Almir": "senha123",
}

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in usuarios_validos and usuarios_validos[username] == password:
        request.session["user"] = username
        return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Usuário ou senha inválidos"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("home.html", {"request": request, "user_name": user})

# Adicione aqui suas outras rotas e funcionalidades (como lançamentos, saldos etc.)

