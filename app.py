import yfinance as yf
import sqlite3  # مكتبة قواعد البيانات
from datetime import datetime # مكتبة الوقت والتاريخ

# --- 1. وظيفة جلب السعر (نفس السابقة) ---
def get_silver_price():
    print("... جاري جلب السعر")
    try:
        silver_data = yf.Ticker("XAGUSD=X") 
        data = silver_data.history(period="1d")
        if data.empty:
            raise ValueError("No Data")
        price = data['Close'].iloc[-1]
    except:
        print("⚠️ تنبيه: نستخدم المصدر البديل (SLV)")
        silver_data = yf.Ticker("SLV")
        price = silver_data.history(period="1d")['Close'].iloc[-1] * 1.09

    # جلب سعر الدولار
    currency = yf.Ticker("TRY=X").history(period="1d")['Close'].iloc[-1]
    
    # حساب الجرام
    return (price * currency) / 31.1035

# --- 2. وظيفة إنشاء قاعدة البيانات (الذاكرة) ---
def init_db():
    # هذا الأمر ينشئ ملفاً اسمه prices.db إذا لم يكن موجوداً
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    
    # إنشاء جدول (Table) لتخزين البيانات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS silver_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ قاعدة البيانات جاهزة.")

# --- 3. وظيفة حفظ السعر ---
def save_price_to_db(price):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    
    # نجلب تاريخ ووقت هذه اللحظة
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # أمر الإضافة (INSERT)
    cursor.execute('INSERT INTO silver_history (date, price) VALUES (?, ?)', (current_time, price))
    
    conn.commit()
    conn.close()
    print(f"💾 تم حفظ السعر ({price:.2f}) في قاعدة البيانات بنجاح.")

# --- تشغيل البرنامج الرئيسي ---
if __name__ == "__main__":
    # 1. تجهيز الذاكرة
    init_db()
    
    # 2. جلب السعر
    current_price = get_silver_price()
    print(f"💰 السعر الحالي: {current_price:.2f} ليرة")
    
    # 3. حفظه
    save_price_to_db(current_price)