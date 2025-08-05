from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

transactions = []

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    balance = sum(t["value"] for t in transactions)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "current_balance": balance,
        "transactions": transactions
    })

@app.get("/new_vale")
def new_vale(value: float, description: str = ""):
    balance = sum(t["value"] for t in transactions)
    new_balance = balance - value
    transactions.append({
        "value": -abs(value),
        "description": description,
        "datetime_str": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "balance": new_balance
    })
    return RedirectResponse("/", status_code=303)

@app.get("/add_salary")
def add_salary(value: float, description: str = ""):
    balance = sum(t["value"] for t in transactions)
    new_balance = balance + value
    transactions.append({
        "value": abs(value),
        "description": description,
        "datetime_str": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "balance": new_balance
    })
    return RedirectResponse("/", status_code=303)
