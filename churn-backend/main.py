from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import os

app = FastAPI(title="Churn Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = "model"
model = None
scaler = None
feature_columns = None
num_cols = None


def load_artifacts():
    global model, scaler, feature_columns, num_cols
    model = joblib.load(f"{MODEL_DIR}/catboost_model.pkl")
    scaler = joblib.load(f"{MODEL_DIR}/scaler.pkl")
    feature_columns = joblib.load(f"{MODEL_DIR}/feature_columns.pkl")
    num_cols = joblib.load(f"{MODEL_DIR}/num_cols.pkl")


try:
    load_artifacts()
    print("Model başarıyla yüklendi.")
except Exception as e:
    print(f"UYARI: Model yüklenemedi — {e}")
    print("Önce train.py'yi çalıştırın.")


class CustomerData(BaseModel):
    gender: str = Field(..., description="Male veya Female")
    seniorcitizen: int = Field(..., ge=0, le=1, description="0 veya 1")
    partner: str = Field(..., description="Yes veya No")
    dependents: str = Field(..., description="Yes veya No")
    tenure: int = Field(..., ge=0, le=72, description="Kaç aydır müşteri (0-72)")
    phoneservice: str = Field(..., description="Yes veya No")
    multiplelines: str = Field(..., description="No | No phone service | Yes")
    internetservice: str = Field(..., description="DSL | Fiber optic | No")
    onlinesecurity: str = Field(..., description="No | No internet service | Yes")
    onlinebackup: str = Field(..., description="No | No internet service | Yes")
    deviceprotection: str = Field(..., description="No | No internet service | Yes")
    techsupport: str = Field(..., description="No | No internet service | Yes")
    streamingtv: str = Field(..., description="No | No internet service | Yes")
    streamingmovies: str = Field(..., description="No | No internet service | Yes")
    contract: str = Field(..., description="Month-to-month | One year | Two year")
    paperlessbilling: str = Field(..., description="Yes veya No")
    paymentmethod: str = Field(
        ...,
        description="Bank transfer (automatic) | Credit card (automatic) | Electronic check | Mailed check",
    )
    monthlycharges: float = Field(..., ge=0, description="Aylık ücret ($)")
    totalcharges: float = Field(..., ge=0, description="Toplam ücret ($)")


def build_feature_row(data: CustomerData) -> dict:
    return {
        "seniorcitizen": data.seniorcitizen,
        "tenure": data.tenure,
        "monthlycharges": data.monthlycharges,
        "totalcharges": data.totalcharges,
        "gender_Male": 1 if data.gender == "Male" else 0,
        "partner_Yes": 1 if data.partner == "Yes" else 0,
        "dependents_Yes": 1 if data.dependents == "Yes" else 0,
        "phoneservice_Yes": 1 if data.phoneservice == "Yes" else 0,
        "multiplelines_No phone service": (
            1 if data.multiplelines == "No phone service" else 0
        ),
        "multiplelines_Yes": 1 if data.multiplelines == "Yes" else 0,
        "internetservice_Fiber optic": (
            1 if data.internetservice == "Fiber optic" else 0
        ),
        "internetservice_No": 1 if data.internetservice == "No" else 0,
        "onlinesecurity_No internet service": (
            1 if data.onlinesecurity == "No internet service" else 0
        ),
        "onlinesecurity_Yes": 1 if data.onlinesecurity == "Yes" else 0,
        "onlinebackup_No internet service": (
            1 if data.onlinebackup == "No internet service" else 0
        ),
        "onlinebackup_Yes": 1 if data.onlinebackup == "Yes" else 0,
        "deviceprotection_No internet service": (
            1 if data.deviceprotection == "No internet service" else 0
        ),
        "deviceprotection_Yes": 1 if data.deviceprotection == "Yes" else 0,
        "techsupport_No internet service": (
            1 if data.techsupport == "No internet service" else 0
        ),
        "techsupport_Yes": 1 if data.techsupport == "Yes" else 0,
        "streamingtv_No internet service": (
            1 if data.streamingtv == "No internet service" else 0
        ),
        "streamingtv_Yes": 1 if data.streamingtv == "Yes" else 0,
        "streamingmovies_No internet service": (
            1 if data.streamingmovies == "No internet service" else 0
        ),
        "streamingmovies_Yes": 1 if data.streamingmovies == "Yes" else 0,
        "contract_One year": 1 if data.contract == "One year" else 0,
        "contract_Two year": 1 if data.contract == "Two year" else 0,
        "paperlessbilling_Yes": 1 if data.paperlessbilling == "Yes" else 0,
        "paymentmethod_Credit card (automatic)": (
            1 if data.paymentmethod == "Credit card (automatic)" else 0
        ),
        "paymentmethod_Electronic check": (
            1 if data.paymentmethod == "Electronic check" else 0
        ),
        "paymentmethod_Mailed check": (
            1 if data.paymentmethod == "Mailed check" else 0
        ),
    }


def preprocess(data: CustomerData) -> pd.DataFrame:
    row = build_feature_row(data)
    df = pd.DataFrame([row])

    # Eğitim sırasındaki sütun sırasına göre hizala
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_columns]

    # Sayısal sütunları ölçekle
    df[num_cols] = scaler.transform(df[num_cols])

    return df


def risk_label(prob: float) -> str:
    if prob >= 0.70:
        return "Yüksek"
    if prob >= 0.40:
        return "Orta"
    return "Düşük"


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Churn Prediction API çalışıyor",
        "model_loaded": model is not None,
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")  #frontend buraya müşterinin tüm bilgilerini paket(JSON) olarak gönderir.
def predict(data: CustomerData):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model yüklenmedi. Lütfen önce train.py'yi çalıştırın.",
        )
    try:
        df = preprocess(data)
        prediction = int(model.predict(df)[0])
        probability = float(model.predict_proba(df)[0][1])

        return {
            "churn": bool(prediction),
            "probability": round(probability * 100, 2),
            "risk_level": risk_label(probability),
            "message": (
                "Bu müşteri büyük ihtimalle ayrılacak."
                if prediction == 1
                else "Bu müşteri büyük ihtimalle kalacak."
            ),
        }    #bu verileri tekrardan frontende fırlastır
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
