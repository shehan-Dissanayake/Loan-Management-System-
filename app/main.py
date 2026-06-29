from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import auth, customers, loans, payments, reports, chat
from app.rag.rag_engine import preload as preload_rag

app = FastAPI(title="Credit Loan Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://loan-management-system-frontend-two.vercel.app",
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(loans.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    preload_rag()

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return JSONResponse(content={"status": "ok"})