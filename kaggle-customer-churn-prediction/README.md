# Telco Customer Churn Prediction (Müşteri Kayıp Tahmini)
Bu proje, telekomünikasyon sektöründeki müşterilerin şirketi terk etme (Churn) potansiyellerini önceden tespit etmeyi amaçlayan bir veri bilimi projesidir. Proje, verinin veri tabanından çekilmesinden hiperparametre optimizasyonuna kadar kapsamlı bir adımlama süreci içermektedir.

## Projenin Amacı
Şirketi terk etme riski yüksek olan müşterileri makine öğrenmesi algoritmalarıyla önceden tespit ederek, iş birimlerinin bu müşterilere yönelik kampanya vb. düzenlemesine olanak sağlamaktır.

## Kullanılan Teknolojiler
* **Veritabanı Yönetimi:** PostgreSQL (Verilerin SQL sorguları ile veri tabanından doğrudan çekilmesi)
* **Veri İşleme ve Analiz:** Python, Pandas, NumPy
* **Veri Görselleştirme:** Matplotlib, Seaborn, Plotly
* **Makine Öğrenmesi:** Scikit-Learn, LightGBM, XGBoost, CatBoost

## Proje İş Akışı (Workflow)

1. **Veri Toplama:** `SQLAlchemy` kullanılarak veriler PostgreSQL veritabanından çekilmiş ve Pandas DataFrame'e aktarılmıştır.
2. **Keşifçi Veri Analizi (EDA) & Görselleştirme:** Hedef değişken (Churn) ile öznitelikler arasındaki ilişkiler görselleştirilmiştir. KDE (Kernel Density Estimation) ve Korelasyon Matrisleri ile öznitelik etkileşimleri analiz edilmiştir.
3. **Veri Ön İşleme:**
   * Eksik veri (Missing Value) analizi ve temizliği.
   * Kategorik verilerin `One-Hot Encoding` (Get Dummies) ile sayısallaştırılması.
   * Veri sızıntısını (Data Leakage) önlemek amacıyla ölçeklendirme (StandardScaler) işleminin Train-Test ayrımından sonra sadece sayısal kolonlara uygulanması.
4. **Modelleme Evrimi (Mühendislik Yaklaşımı):**
   * **Base Modeller:** Dengesiz veri setinde algoritmaların (Logistic Reg, KNN, SVM, Tree Models vb.) baz performansları ölçüldü. (Recall: ~%51)
   * **Balanced Modeller:** Veri setindeki %73 - %27 dengesizliğini çözmek için sınıf ağırlıkları (`class_weight='balanced'`) ayarlandı ve en güçlü 3 model (Lojistik Regresyon, LightGBM, CatBoost) seçildi. (Recall: ~%79)
   * **Tuned Model (Final):** Şampiyon model olarak seçilen **CatBoost**, `GridSearchCV` ile hiperparametre optimizasyonuna sokularak maksimum potansiyeline ulaştırıldı. (Recall: %82)

## Final Model Performansı: CatBoost (Tuned)
Final modelinin odak noktası, kaçacak olan müşterileri gözden kaçırmamak adına **Recall (Duyarlılık)** metriğini maksimize etmek olarak belirlenmiştir.

* **Accuracy:** %73
* **Precision (Sınıf 1):** %50
* **Recall (Sınıf 1):** %82
* **F1-Score (Sınıf 1):** %62
* **ROC-AUC Score:** %84

*Not: Şirket stratejisi gereği, yanlış alarm (False Positive) verip bir müşteriye fazladan indirim sunmak, o müşteriyi tamamen kaybetmekten çok daha ucuz olduğu için "Yüksek Recall, Düşük Precision" senaryosu bilinçli olarak tercih edilmiştir.*

## İş Birimlerine Aksiyon Önerisi (Business Impact)
Modelin `Feature Importance` (Öznitelik Önemi) çıktıları incelendiğinde; **Sözleşme Tipi (Contract), Şirkette Kalma Süresi (Tenure) ve Aylık Fatura (MonthlyCharges)** değişkenlerinin müşteri kaybında en büyük rolü oynadığı görülmüştür.

1. Churn riski yüksek olarak işaretlenen (True) müşterilere otomatik olarak "İndirim" veya "Ücretsiz Paket Yükseltme" SMS'leri atan bir sistem kurulması tavsiye edilir.
2. Müşteri kaybını önlemenin temel yolu müşteriyi gerçekten tanımaktır. Tespit edilen riskli gruba sadece standart indirimler değil, marka sadakatini artıracak kişiselleştirilmiş müşteri hizmetleri sunulmalıdır.
3. Gelecekteki kayıpları önlemek adına, geçmişte şirketi terk etmiş müşterilerle iletişime geçilerek ayrılığın kök nedenleri daha derinlemesine analiz edilmelidir.

## Kurulum ve Kullanım
Bu projeyi kendi lokalinizde çalıştırmak için:
1. Repoyu klonlayın: `git clone https://github.com/kullaniciadiniz/telecom-churn-prediction.git`
2. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
3. PostgreSQL veritabanı bağlantı ayarlarını kod içerisindeki `create_engine` satırından kendi lokal bilgilerinize göre güncelleyin.
4. Jupyter Notebook'u çalıştırın: `jupyter lab` veya `jupyter notebook`
