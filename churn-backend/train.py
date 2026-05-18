import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from catboost import CatBoostClassifier
import joblib
import os
import sys

from dotenv import load_dotenv
load_dotenv()

def get_database_engine():
    from sqlalchemy import create_engine
    user=os.getenv("DB_USER")
    password=os.getenv("DB_PASSWORD")
    host=os.getenv("DB_HOST")
    port=os.getenv("DB_PORT")
    db_name=os.getenv("DB_NAME")

    # URL Formatı: postgresql://user:password@host:port/dbname   !!
    connection_string=f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string)

def load_data_hybrid() -> pd.DataFrame:
    source_type=os.getenv("DATA_SOURCE_TYPE", "csv").lower() #. env kısmında eğer CSV gibi yazılırsa kod çökmesinin önüne geçmek için .lower() kullanıyoruz

    if source_type=="db":
        table_name=os.getenv("DB_TABLE", "telco_churn")  #os.getenv() ikinci parametresi ne olur ne olmaz bulamazsan default buna bak demek için
        print(f"--- Veritabanı bağlantısı kuruluyor... Tablo: {table_name} ---")
        from sqlalchemy import text
        try:
            engine=get_database_engine()
            with engine.connect() as conn:     #engine.connect() paranteze dikkat unutma
                df=pd.read_sql(text(f"SELECT * FROM {table_name}"), conn)
            print(f" PostgreSQL'den {len(df)} satır başarıyla yüklendi.")
            return df
        except Exception as e:
            print(f"Vt den veri çekilemedi: {e}")
            print(" Yedek plan olarak yerel CSV dosyasına geçiliyor...")
            # Eğer DB çökerse bağlanmazsa otomatik fallback (yedek) olarak CSV'ye geçer
            source_type = "csv"


    if source_type=="csv":
        csv_path=os.getenv("LOCAL_CSV_PATH")
        print(f"--- Yerel kaynak kullanılıyor... Dosya: {csv_path} ---")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Belirtilen dosya bulunamadı.")
        df=pd.read_csv(csv_path)
        printf(f"toplamda {len(df)} satır başarıyla yüklendi.")
        return df

    raise ValueError("DATA_SOURCE_TYPE sadece 'csv' ya da 'db' olabilir")


def train_model():
    df = load_data_hybrid()

    #kolon isimleri kucuk harfli ve boslukları olmayacak şekilde ayarladık
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

    y = df_encoded[target_col].astype(int)   # bu kısımın nedeni 0.0 ya da 1.0 gibi olmasın direkt 0 ya da 1 olsun diye
    X = df_encoded.drop(columns=[target_col])

    feature_columns = X.columns.tolist()
    print(f"Toplam özellik sayısı: {len(feature_columns)}")


    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    num_cols = ["tenure", "monthlycharges", "totalcharges"]
    num_cols = [c for c in num_cols if c in X.columns]

    #dikkat: sayısal sutunlar üzerinden
    scaler = StandardScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])

    # Notebook'taki CatBoost Modelimiz için GridSearchCV kullanarak verilen değerleri kullanıyoruz
    # best_estimator_ early stopping kullanmaz, biz de kullanmıyoruz
    print("CatBoost modeli eğitiliyor (notebook best_params)...")
    model = CatBoostClassifier(
        iterations=100,
        learning_rate=0.1,
        depth=4,
        auto_class_weights="Balanced",   #azınlıkta olan churn_yese daha fazla agırlık atanmasını sağladık
        random_seed=42,
        verbose=False,
    )
    model.fit(X_train, y_train)

    #SKOR KARSILASTIRMASI İLE MODEL KONTROLU
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    print(f"\nTest F1 Skoru: {f1:.4f}")
    print(classification_report(y_test, y_pred))

    #modeli backend apinin okuyabilmesi için model/ klasorune kaydettik
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/catboost_model.pkl")
    joblib.dump(scaler, "model/scaler.pkl")
    joblib.dump(feature_columns, "model/feature_columns.pkl")
    joblib.dump(num_cols, "model/num_cols.pkl")

    print("\nModel ve artefaktlar 'model/' klasörüne kaydedildi.")
    return model, scaler, feature_columns


if __name__ == "__main__":

    if len(sys.argv) >1:
        os.environ["DATA_SOURCE_TYPE"] ='csv'
        os.environ["LOCAL_CSV_PATH"] = sys.argv[1]

    train_model()
