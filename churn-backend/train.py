import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from catboost import CatBoostClassifier
import joblib
import os
import sys


def load_data(source: str) -> pd.DataFrame:
    """CSV dosyasından veya PostgreSQL bağlantı string'inden veri yükle."""
    if source.startswith("postgresql") or source.startswith("postgres"):
        from sqlalchemy import create_engine, text
        engine = create_engine(source)
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM telco_churn"), conn)
        print(f"PostgreSQL'den {len(df)} satır yüklendi.")
    else:
        df = pd.read_csv(source)
        print(f"CSV'den {len(df)} satır yüklendi.")
    return df


def train_model(csv_path="WA_Fn-UseC_-Telco-Customer-Churn.csv"):
    print(f"Veri yükleniyor: {csv_path}")
    df = load_data(csv_path)

    df.columns = df.columns.str.lower().str.strip()

    df = df.drop(columns=["customerid"], errors="ignore")
    df["totalcharges"] = pd.to_numeric(df["totalcharges"], errors="coerce")
    df = df.dropna(subset=["totalcharges"]).reset_index(drop=True)

    print(f"Veri boyutu: {df.shape}")

    df_encoded = pd.get_dummies(df, drop_first=True)

    # Hedef değişken
    target_col = "churn_Yes"
    if target_col not in df_encoded.columns:
        # Farklı varyasyon dene
        churn_cols = [c for c in df_encoded.columns if "churn" in c.lower()]
        if not churn_cols:
            raise ValueError("Hedef sütun 'churn_Yes' bulunamadı.")
        target_col = churn_cols[0]
        print(f"Hedef sütun olarak '{target_col}' kullanılıyor.")

    y = df_encoded[target_col].astype(int)
    X = df_encoded.drop(columns=[target_col])

    feature_columns = X.columns.tolist()
    print(f"Toplam özellik sayısı: {len(feature_columns)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    num_cols = ["tenure", "monthlycharges", "totalcharges"]
    num_cols = [c for c in num_cols if c in X.columns]

    scaler = StandardScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])

    print("CatBoost modeli eğitiliyor...")
    model = CatBoostClassifier(
        iterations=100,
        learning_rate=0.1,
        depth=4,
        auto_class_weights="Balanced",
        random_seed=42,
        verbose=100,
    )
    model.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=50)

    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    print(f"\nTest F1 Skoru: {f1:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/catboost_model.pkl")
    joblib.dump(scaler, "model/scaler.pkl")
    joblib.dump(feature_columns, "model/feature_columns.pkl")
    joblib.dump(num_cols, "model/num_cols.pkl")

    print("\nModel ve artefaktlar 'model/' klasörüne kaydedildi.")
    return model, scaler, feature_columns


if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    train_model(csv)
