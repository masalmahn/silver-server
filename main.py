from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import pandas as pd

# ==========================================
# ⚙️ إعدادات التحكم (Configuration)
# ==========================================

# 1. مفتاح الأمان (لحماية المحفظة من التعديل)
MY_SECRET_KEY = "Silver_2025_Secret_Key"

# 2. إعدادات معايرة السعر (لمطابقة البنك)
CALIBRATION = 1.12  # معامل تصحيح السعر العالمي
BANK_SPREAD = 7.35  # الفرق بين البيع والشراء

# 3. سعر الليرة السورية الاحتياطي (في حال تعطل الموقع)
FALLBACK_SYP_RATE = 15200.0 

# ==========================================

app = FastAPI()

# السماح بالاتصال من أي مكان (للموبايل والمتصفح)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🛠️ تجهيز قاعدة البيانات (المحفظة) ---
def init_db():
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    # جدول المحفظة
    cursor.execute('CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, grams REAL)')
    # قيمة افتراضية صفر
    cursor.execute('INSERT OR IGNORE INTO wallet (id, grams) VALUES (1, 0.0)')
    conn.commit()
    conn.close()

init_db() # تشغيل عند البداية

# --- 🔐 دالة الحارس (التحقق من كلمة السر) ---
async def verify_key(x_api_key: str = Header(None)):
    # هذه الدالة تتأكد أن الطلب القادم يحمل المفتاح الصحيح
    if x_api_key != MY_SECRET_KEY:
        raise HTTPException(status_code=401, detail="❌ مفتاح الأمان غير صحيح أو مفقود")

# --- 🇸🇾 دالة جلب سعر الليرة السورية (Scraper) ---
def get_syp_rate():
    print("... جاري جلب سعر الليرة السورية (sp-today)")
    url = "https://sp-today.com/en/currency/us_dollar"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # البحث عن الأسعار في الموقع
        spans = soup.find_all("span", class_="value")
        for span in spans:
            try:
                text = span.text.replace(",", "").replace("SYP", "").strip()
                price = float(text)
                if price > 10000: # فلتر للتأكد أنه سعر منطقي
                    return price
            except:
                continue
        raise Exception("لم يتم العثور على السعر")
        
    except Exception as e:
        print(f"⚠️ فشل جلب السوري ({e})، نستخدم الاحتياطي.")
        return FALLBACK_SYP_RATE

# --- 💰 نموذج البيانات (للمحفظة) ---
class WalletUpdate(BaseModel):
    grams: float

# ==========================================
# 🚀 الروابط (Endpoints)
# ==========================================

@app.get("/")
def home():
    return {"message": "✅ السيرفر المالي (Full Stack) يعمل بنجاح!"}

# --- الرابط الشامل (يغذي التطبيق بكل شيء) ---
@app.get("/all_data")
def get_all_data():
    try:
        # 1. جلب البيانات العالمية (نطلب 5 أيام لضمان العمل في العطلات)
        # نستخدم SLV لأنه مستقر جداً للتاريخ، و XAGUSD للسعر اللحظي إن وجد
        print("1. جلب البيانات العالمية...")
        
        # نستخدم SLV للتاريخ (5 سنوات)
        history_data = yf.Ticker("SLV").history(period="5y", interval="1wk")
        
        # نستخدم بيانات 5 أيام للسعر الحالي (لتجنب الأصفار في العطلة)
        current_silver = yf.Ticker("SLV").history(period="5d")
        current_usd_try = yf.Ticker("TRY=X").history(period="5d")

        # أخذ آخر سعر إغلاق متوفر
        last_slv = current_silver['Close'].iloc[-1]
        last_usd_try = current_usd_try['Close'].iloc[-1]

        # 2. جلب سعر الليرة السورية
        last_usd_syp = get_syp_rate()

        # 3. الحسابات الرئيسية
        # سعر الغرام بالدولار (مع التصحيح)
        gram_usd = (last_slv * CALIBRATION) / 31.1035
        
        # سعر الغرام بالتركي
        gram_try = gram_usd * last_usd_try
        
        # سعر الغرام بالسوري
        gram_syp = gram_usd * last_usd_syp

        # 4. جلب رصيد المحفظة من قاعدة البيانات
        conn = sqlite3.connect('prices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT grams FROM wallet WHERE id=1")
        wallet_grams = cursor.fetchone()[0]
        conn.close()

        # 5. تجهيز بيانات الرسم البياني (JSON)
        chart_list = []
        for date, row in history_data.iterrows():
            # نحول سعر تاريخي لغرامات
            hist_gram_price = (row['Close'] * CALIBRATION) / 31.1035
            chart_list.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(hist_gram_price, 2)
            })

        # 6. الرد النهائي للتطبيق
        return {
            "prices": {
                "gram_usd": round(gram_usd, 3),
                "gram_try": round(gram_try, 2), # سعر البيع (الأساسي)
                "bank_buy_try": round(gram_try - BANK_SPREAD, 2), # سعر الشراء (للبنك)
                "gram_syp": round(gram_syp, 0),
            },
            "rates": {
                "usd_try": round(last_usd_try, 2),
                "usd_syp": round(last_usd_syp, 0)
            },
            "wallet": wallet_grams,
            "history": chart_list
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

# --- رابط تحديث المحفظة (محمي بالقفل) ---
@app.post("/update_wallet", dependencies=[Depends(verify_key)])
def update_wallet(data: WalletUpdate):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE wallet SET grams = ? WHERE id=1", (data.grams,))
    conn.commit()
    conn.close()
    return {"status": "saved", "grams": data.grams}