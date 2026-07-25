import pandas as pd
import sqlite3

print("🚀 BÜYÜK GÖÇ BAŞLATILIYOR: Tüm Oyunlar Sıfırdan SQL'e Taşınıyor...")

# 1. SQL KALESİNİ İNŞA ET
conn = sqlite3.connect('loto.db')
cursor = conn.cursor()

# 2. TABLOLARI SIFIRLAMA VE YENİDEN OLUŞTURMA
cursor.execute('DROP TABLE IF EXISTS super_loto')
cursor.execute('CREATE TABLE super_loto (id INTEGER PRIMARY KEY AUTOINCREMENT, t1 INTEGER, t2 INTEGER, t3 INTEGER, t4 INTEGER, t5 INTEGER, t6 INTEGER)')

cursor.execute('DROP TABLE IF EXISTS sans_topu')
cursor.execute('CREATE TABLE sans_topu (id INTEGER PRIMARY KEY AUTOINCREMENT, t1 INTEGER, t2 INTEGER, t3 INTEGER, t4 INTEGER, t5 INTEGER, arti INTEGER)')

cursor.execute('DROP TABLE IF EXISTS sayisal_loto')
cursor.execute('CREATE TABLE sayisal_loto (id INTEGER PRIMARY KEY AUTOINCREMENT, t1 INTEGER, t2 INTEGER, t3 INTEGER, t4 INTEGER, t5 INTEGER, t6 INTEGER)')

cursor.execute('DROP TABLE IF EXISTS on_numara')
cursor.execute('''CREATE TABLE on_numara (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    t1 INTEGER, t2 INTEGER, t3 INTEGER, t4 INTEGER, t5 INTEGER, t6 INTEGER,
    t7 INTEGER, t8 INTEGER, t9 INTEGER, t10 INTEGER, t11 INTEGER, t12 INTEGER,
    t13 INTEGER, t14 INTEGER, t15 INTEGER, t16 INTEGER, t17 INTEGER, t18 INTEGER,
    t19 INTEGER, t20 INTEGER, t21 INTEGER, t22 INTEGER
)''')

# ==========================================
# 🔵 SÜPER LOTO ('süper.xlsx')
# ==========================================
try:
    print("📂 Süper Loto işleniyor...")
    df_super = pd.read_excel('süper.xlsx', sheet_name=0, header=None)
    super_cekilisler = []
    for _, row in df_super.iterrows():
        try:
            raw_vals = row.iloc[2:8].values 
            nums = [int(float(str(x).replace(',', '.').strip())) for x in raw_vals if str(x).replace(',', '.').strip().isdigit()]
            main_balls = [x for x in nums if 1 <= x <= 60]
            if len(main_balls) == 6:
                t = tuple(sorted(main_balls))
                if t not in super_cekilisler: super_cekilisler.append(t)
        except: continue
    super_cekilisler.reverse()
    cursor.executemany('INSERT INTO super_loto (t1, t2, t3, t4, t5, t6) VALUES (?, ?, ?, ?, ?, ?)', super_cekilisler)
    print(f"✅ SÜPER LOTO: {len(super_cekilisler)} çekiliş SQL'e kazındı.")
except Exception as e: print(f"🚨 SÜPER LOTO HATASI: {e}")

# ==========================================
# 🟢 ŞANS TOPU ('şns_topu.xlsx')
# ==========================================
try:
    print("📂 Şans Topu işleniyor ('şns_topu.xlsx')...")
    df_sans = pd.read_excel('şns_topu.xlsx', sheet_name=0, header=None)
    sans_cekilisler = []
    for _, row in df_sans.iterrows():
        try:
            raw_vals = row.iloc[2:].values
            nums = [int(float(str(x).replace(',', '.').strip())) for x in raw_vals if str(x).replace(',', '.').strip().isdigit()]
            if len(nums) >= 5:
                main_balls = sorted([x for x in nums[:5] if 1 <= x <= 34])
                arti_top = nums[5] if len(nums) > 5 and 1 <= nums[5] <= 14 else 0
                if len(main_balls) == 5:
                    t = tuple(main_balls + [arti_top])
                    if t not in sans_cekilisler: sans_cekilisler.append(t)
        except: continue
    sans_cekilisler.reverse()
    cursor.executemany('INSERT INTO sans_topu (t1, t2, t3, t4, t5, arti) VALUES (?, ?, ?, ?, ?, ?)', sans_cekilisler)
    print(f"✅ ŞANS TOPU: {len(sans_cekilisler)} çekiliş SQL'e kazındı.")
except Exception as e: print(f"🚨 ŞANS TOPU HATASI: {e}")

# ==========================================
# 🔴 ÇILGIN SAYISAL LOTO ('çlgn_sysl.xlsx')
# ==========================================
try:
    print("📂 Çılgın Sayısal Loto işleniyor...")
    df_sayisal = pd.read_excel('çlgn_sysl.xlsx', sheet_name=0, header=None)
    sayisal_cekilisler = []
    for _, row in df_sayisal.iterrows():
        try:
            raw_vals = row.iloc[2:8].values
            nums = [int(float(str(x).replace(',', '.').strip())) for x in raw_vals if str(x).replace(',', '.').strip().isdigit()]
            main_balls = [x for x in nums if 1 <= x <= 90]
            if len(main_balls) == 6:
                t = tuple(sorted(main_balls))
                if t not in sayisal_cekilisler: sayisal_cekilisler.append(t)
        except: continue
    sayisal_cekilisler.reverse()
    cursor.executemany('INSERT INTO sayisal_loto (t1, t2, t3, t4, t5, t6) VALUES (?, ?, ?, ?, ?, ?)', sayisal_cekilisler)
    print(f"✅ ÇILGIN SAYISAL: {len(sayisal_cekilisler)} çekiliş SQL'e kazındı.")
except Exception as e: print(f"🚨 ÇILGIN SAYISAL HATASI: {e}")

# ==========================================
# 🟣 ON NUMARA ('onnumara.xlsx')
# ==========================================
try:
    print("📂 On Numara işleniyor...")
    df_on = pd.read_excel('onnumara.xlsx', sheet_name=0, header=None)
    on_cekilisler = []
    for _, row in df_on.iterrows():
        try:
            row_str = str(row.values).lower()
            if any(x in row_str for x in ['tarih', 'hafta', 'sayı', 'cekilis']): continue
            
            raw_vals = row.iloc[2:24].values 
            nums = [int(float(str(x).replace(',', '.').strip())) for x in raw_vals if str(x).replace(',', '.').strip().isdigit()]
            main_balls = [x for x in nums if 1 <= x <= 80]
            
            if len(main_balls) >= 22:
                t = tuple(sorted(main_balls[:22]))
                if t == tuple(range(1, 23)): continue
                if t not in on_cekilisler: on_cekilisler.append(t)
        except: continue
        
    on_cekilisler.reverse()
    q_marks = ', '.join(['?']*22)
    cursor.executemany(f'INSERT INTO on_numara (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16, t17, t18, t19, t20, t21, t22) VALUES ({q_marks})', on_cekilisler)
    print(f"✅ ON NUMARA: {len(on_cekilisler)} çekiliş SQL'e kazındı.")
except Exception as e: print(f"🚨 ON NUMARA HATASI: {e}")

# BAĞLANTIYI KAYDET VE KAPAT
conn.commit()
conn.close()
print("🔒 GÖÇ TAMAMLANDI! Tüm Motorlar için 'loto.db' kalesi hatasız güncellendi.")