import yfinance as yf
import sqlite3
import pandas as pd

def fill_5_years():
    print("⏳ جاري تحميل البيانات... (المحاولة الثانية المحسنة)")

    # 1. جلب البيانات
    print("... تحميل بيانات الفضة (SLV)")
    silver = yf.Ticker("SLV").history(period="5y")['Close'] * 1.09
    
    print("... تحميل بيانات الدولار (TRY=X)")
    currency = yf.Ticker("TRY=X").history(period="5y")['Close']

    print(f"📊 وجدنا {len(silver)} يوم للفضة، و {len(currency)} يوم للدولار.")

    # --- الإصلاح السحري (توحيد التوقيت) ---
    # نقوم بإزالة معلومات المنطقة الزمنية (Timezone) ليصبحا متطابقين
    silver.index = silver.index.tz_localize(None)
    currency.index = currency.index.tz_localize(None)

    # 2. دمج الجدولين
    # نستخدم دمج ذكي يحافظ على كل التواريخ
    df = pd.DataFrame({'silver_usd': silver, 'usd_try': currency})

    # ملء الفراغات (Forward Fill)
    # إذا كان يوم السبت عطلة، نستخدم سعر الجمعة بدلاً من حذفه
    df = df.ffill().dropna()

    # 3. الحساب
    df['price_gram_try'] = (df['silver_usd'] * df['usd_try']) / 31.1035

    # 4. الحفظ في قاعدة البيانات
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()

    # مسح القديم
    cursor.execute("DELETE FROM silver_history")
    
    print("... جاري الحفظ")
    count = 0
    for date, row in df.iterrows():
        # تنسيق التاريخ ليكون نصاً بسيطاً
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")
        price = row['price_gram_try']
        
        cursor.execute('INSERT INTO silver_history (date, price) VALUES (?, ?)', (date_str, price))
        count += 1

    conn.commit()
    conn.close()
    
    print("-" * 40)
    print(f"✅ النتيجة النهائية: تم حفظ {count} يوم في الذاكرة.")
    print("-" * 40)

if __name__ == "__main__":
    fill_5_years()