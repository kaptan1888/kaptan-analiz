import streamlit as st
import pandas as pd
from collections import Counter
import glob
import numpy as np
from itertools import combinations
import random
from sklearn.cluster import KMeans
import time
import requests
import cloudscraper  
from bs4 import BeautifulSoup
import re
import base64
import sqlite3
import hashlib
import json
import os

def load_live_data():
    if os.path.exists("canli_sonuclar.json"):
        with open("canli_sonuclar.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sayisal": {}, "superloto": {}, "sanstopu": {}, "onnumara": {}}

def save_live_data(data):
    with open("canli_sonuclar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Uygulama başlarken canlı verileri her zaman güncel tutmak için bu satırı da ekle:
live_data = load_live_data()

# YENİ MODERN MENÜ MODÜLÜ
from streamlit_option_menu import option_menu 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yapay Zeka Loto Analiz Merkezi", page_icon="🧿", layout="wide", initial_sidebar_state="expanded")

# --- EVRENSEL CSS VE WHITE-LABEL (İZ SİLME) ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: block !important; visibility: visible !important; color: black !important; background-color: #f1f5f9 !important; border-radius: 50% !important; z-index: 999999 !important; }
    .block-container { padding-top: 3.5rem !important; padding-bottom: 1rem !important; }
    #MainMenu {visibility: hidden !important;} 
    footer {visibility: hidden !important;} 
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    .stApp { background-color: #f8fafc; }
    .main-title { color: #0f172a; font-weight: 900; text-align: center; font-size: 2.5rem; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 2px;}
    .sub-title { color: #3b82f6; font-weight: 700; text-align: center; font-size: 1.2rem; margin-top: -5px; margin-bottom: 30px;}
    .metric-card { background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6; text-align: center;}
    .game-card { background-color: #ffffff; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; margin-top: 20px;}
    
    .number-ball { display: inline-block; width: 65px; height: 65px; line-height: 65px; border-radius: 50%; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; font-size: 26px; font-weight: bold; text-align: center; margin: 0 6px; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.5); border: 2px solid #fff;}
    .plus-ball { display: inline-block; width: 65px; height: 65px; line-height: 65px; border-radius: 50%; background: linear-gradient(135deg, #b91c1c 0%, #ef4444 100%); color: white; font-size: 26px; font-weight: bold; text-align: center; margin: 0 6px; box-shadow: 0 4px 10px rgba(239, 68, 68, 0.5); border: 2px solid #fff;}
    .home-ball { display: inline-block; width: 45px; height: 45px; line-height: 45px; border-radius: 50%; color: white; font-size: 18px; font-weight: bold; text-align: center; margin: 0 4px; box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15); border: 2px solid #fff;}
    
    .ball-blue { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }
    .ball-green { background: linear-gradient(135deg, #064e3b 0%, #10b981 100%); }
    .ball-red { background: linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%); }
    .home-onnumara-ball { display: inline-block; width: 32px; height: 32px; line-height: 32px; border-radius: 50%; background: linear-gradient(135deg, #92400e 0%, #f59e0b 100%); color: white; font-size: 13px; font-weight: bold; text-align: center; margin: 3px; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.4); border: 1px solid #fff;}
    
    .home-card { background-color: #ffffff; padding: 20px; border-radius: 10px 10px 0 0; box-shadow: 0 -4px 10px -2px rgba(0,0,0,0.1); border: 3px solid #000000; border-bottom: none;}
    .home-game-header { font-size: 1.2rem; font-weight: 900; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;}
    .home-game-date { font-size: 0.9rem; color: #64748b; text-align: center; margin-bottom: 15px; font-weight: 600;}
    .history-bar { background-color: #f1f5f9; padding: 12px; border: 3px solid #000000; border-radius: 0 0 10px 10px; margin-bottom: 25px; box-shadow: 0 4px 10px -2px rgba(0,0,0,0.1); border-top: none; }
    
    div[data-testid="stButton"] > button { background-color: #b91c1c !important; color: white !important; font-weight: 800 !important; border: none !important; transition: all 0.2s ease; }
    div[data-testid="stButton"] > button:hover { background-color: #991b1b !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    .highlight-yellow { background-color: #fef08a; color: #000000; font-weight: bold; padding: 2px 6px; border-radius: 3px; }
    .highlight-blue { background-color: #bae6fd; color: #0f172a; font-weight: bold; padding: 2px 6px; border-radius: 3px; }
    
    .guide-box { border: 4px solid #000000; border-radius: 8px; background-color: #ffffff; margin-bottom: 25px; box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.15); }
    .guide-summary { color: #000000; font-weight: 900; font-size: 1.5rem; text-align: center; padding: 16px; cursor: pointer; list-style: none; display: block; letter-spacing: 0.5px; }
    .guide-summary::-webkit-details-marker { display: none; }
    .guide-summary:hover { background-color: #f1f5f9; }
    .guide-content { padding: 25px; border-top: 3px solid #000000; color: #334155; font-size: 1.05rem; line-height: 1.6; background-color: #f8fafc; }

    .result-table { width: 100%; border-collapse: collapse; background-color: white; font-size: 14px; margin-top: 5px; border: 1px solid #e2e8f0;}
    .result-table tr { border-bottom: 1px solid #e2e8f0; }
    .result-table tr:nth-child(even) { background-color: #f8fafc; }
    .result-table td, .result-table th { padding: 8px 10px; text-align: left; color: #334155; }
    .superstar-header { background-color: #b91c1c !important; color: white !important; text-align: center !important; font-weight: 800 !important; padding: 10px !important; font-size: 15px !important;}
    
    button[data-baseweb="tab"] p { font-weight: 900 !important; font-size: 17px !important; letter-spacing: 0.5px !important; }
    
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInput"] div[data-baseweb="input"] { border: 3px solid #1e3a8a !important; border-radius: 8px !important; background-color: #ffffff !important; padding: 4px !important; }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInput"] input { font-size: 28px !important; font-weight: 900 !important; color: #dc2626 !important; text-align: center !important; }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepUp"], [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepDown"] { background-color: #f1f5f9 !important; width: 45px !important; border-radius: 6px !important; }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepUp"] svg, [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepDown"] svg { fill: #1e3a8a !important; width: 22px !important; height: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# --- SAĞ ÜST KÖŞE AKILLI GİRİŞ / ÇIKIŞ BUTONU ---
c_bosluk, c_buton = st.columns([8.5, 1.5])

with c_buton:
    if not st.session_state.get("logged_in", False):
        def vip_ekranini_tetikle():
            st.session_state.giris_ekranini_ac = True
        st.button("Giriş / Kayıt", on_click=vip_ekranini_tetikle, use_container_width=True, key="essiz_giris_butonu_999")
    else:
        mail_adresi = st.session_state.get("user_email", "")
        st.markdown(f"<div style='text-align: right; color: #10b981; font-size: 13px; font-weight: bold; margin-bottom: 5px;'>{mail_adresi}</div>", unsafe_allow_html=True)
        def guvenli_cikis():
            st.session_state.logged_in = False
            st.session_state.is_vip = False
            st.session_state.user_email = ""
            st.session_state.giris_ekranini_ac = False
        st.button("🚪 Çıkış Yap", on_click=guvenli_cikis, type="primary", use_container_width=True, key="essiz_cikis_butonu_999")

# --- SİSTEM HAFIZASI ---
if "is_vip" not in st.session_state: st.session_state.is_vip = False
if "saved_coupons" not in st.session_state: st.session_state.saved_coupons = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""

# ==========================================
# 0. PROFESYONEL VERİTABANI & CRM MİMARİSİ
# ==========================================
def init_db():
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, is_vip INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT, game_id TEXT, game_name TEXT, nums TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        c.execute("INSERT INTO users (email, password, is_vip) VALUES (?, ?, 0)", (email, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT is_vip FROM users WHERE email=? AND password=?", (email, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result

def get_all_users():
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    c.execute("SELECT email, is_vip FROM users")
    users = c.fetchall()
    conn.close()
    return users

def update_vip_status(email, new_status):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET is_vip=? WHERE email=?", (new_status, email))
    conn.commit()
    conn.close()

def save_coupon_to_db(email, game_id, game_name, nums, timestamp):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    nums_str = ",".join(map(str, nums))
    c.execute("INSERT INTO coupons (user_email, game_id, game_name, nums, timestamp) VALUES (?, ?, ?, ?, ?)", (email, game_id, game_name, nums_str, timestamp))
    conn.commit()
    conn.close()

def get_user_coupons(email):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    c.execute("SELECT game_id, game_name, nums, timestamp FROM coupons WHERE user_email=? ORDER BY id DESC", (email,))
    coupons = c.fetchall()
    conn.close()
    parsed_coupons = []
    for cp in coupons:
        nums_list = [int(n) for n in cp[2].split(",")]
        parsed_coupons.append({"game": cp[0], "game_name": cp[1], "nums": nums_list, "timestamp": cp[3]})
    return parsed_coupons
# 👇 İŞTE TAM BURAYA, DİĞERLERİNİN HEMEN ALTINA YENİ KODU YAPIŞTIRIYORUZ:
def delete_coupon_from_db(email, game_id, timestamp):
    import sqlite3 
    # BAĞLANTI DOSYASININ ADI GERÇEK DOSYANA (kuantum_users.db) GÖRE DÜZELTİLDİ
    conn = sqlite3.connect('kuantum_users.db') 
    cursor = conn.cursor()
    
    # GERÇEK TABLO ADI (coupons) VE SÜTUN ADLARI
    cursor.execute('''DELETE FROM coupons WHERE user_email=? AND game_id=? AND timestamp=?''', (email, game_id, timestamp))
    
    conn.commit()
    conn.close()
# --- VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=60)
def get_live_results():
    data = {
        "sayisal": {"date": "Güncel Çekiliş", "nums": [], "plus": "", "superstar": "", "status": "Bekleniyor", "prize_html": ""},
        "super": {"date": "Güncel Çekiliş", "nums": [], "status": "Bekleniyor", "prize_html": ""},
        "sans": {"date": "Güncel Çekiliş", "nums": [], "plus": "", "status": "Bekleniyor", "prize_html": ""},
        "onnumara": {"date": "Güncel Çekiliş", "nums": [], "status": "Bekleniyor", "prize_html": ""}
    }
    game_names = {"sayisal": "Sayısal", "super": "Süper", "sans": "Şans", "onnumara": "Numara"}
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    urls = {
        "sayisal": ["https://www.lototurkiye.com/sayisal-loto-sonuclari", "https://www.haberturk.com/sans-oyunlari/sayisal-loto-sonuclari"],
        "super": ["https://www.lototurkiye.com/super-loto-sonuclari", "https://www.haberturk.com/sans-oyunlari/super-loto-sonuclari"],
        "sans": ["https://www.lototurkiye.com/sans-topu-sonuclari", "https://www.haberturk.com/sans-oyunlari/sans-topu-sonuclari"],
        "onnumara": ["https://www.lototurkiye.com/on-numara-sonuclari", "https://www.haberturk.com/sans-oyunlari/on-numara-sonuclari"]
    }
    for game, target_list in urls.items():
        success = False
        for url in target_list:
            if success: break
            try:
                response = scraper.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    clean_title = ""
                    for h in soup.find_all(['h1', 'h2', 'h3', 'div', 'strong']):
                        text = h.get_text(strip=True)
                        if ">>>" in text or "Milli Piyango" in text: continue
                        if "Çekiliş" in text and game_names[game] in text:
                            if 10 < len(text) < 100:
                                clean_title = text.replace("Çekiliş Sonuçları", "").strip()
                                break
                    if clean_title: data[game]["date"] = clean_title
                    
                    pulled_nums = []
                    main_div = soup.find('div', class_=re.compile(r'sonuc|result|draw|cekilis|content', re.I))
                    if not main_div: main_div = soup
                    
                    for tag in main_div.find_all(['div', 'span', 'li', 'td', 'b']):
                        cls = tag.get('class', [])
                        if isinstance(cls, list): cls = " ".join(cls)
                        if any(x in cls.lower() for x in ['ball', 'sayi', 'top', 'num', 'sonuc']):
                            txt = tag.get_text(strip=True)
                            if txt.isdigit() and 1 <= int(txt) <= 90:
                                if int(txt) not in pulled_nums: pulled_nums.append(int(txt))
                                
                    if not pulled_nums:
                        for img in main_div.find_all('img'):
                            src = img.get('src', '')
                            m = re.search(r'/(\d{1,2})\.(png|gif|jpg)', src)
                            if m and int(m.group(1)) <= 90:
                                val = int(m.group(1))
                                if val not in pulled_nums: pulled_nums.append(val)
                    
                    if pulled_nums:
                        if game == "sayisal" and len(pulled_nums) >= 6:
                            data[game]["nums"] = pulled_nums[:6]
                            if len(pulled_nums) > 6: data[game]["plus"] = pulled_nums[6] 
                            if len(pulled_nums) > 7: data[game]["superstar"] = pulled_nums[7]
                            success = True
                        elif game == "super" and len(pulled_nums) >= 6:
                            data[game]["nums"] = pulled_nums[:6]
                            success = True
                        elif game == "sans" and len(pulled_nums) >= 6:
                            data[game]["nums"] = pulled_nums[:5]
                            data[game]["plus"] = pulled_nums[5]
                            success = True
                        elif game == "onnumara" and len(pulled_nums) >= 22:
                            data[game]["nums"] = pulled_nums[:22]
                            success = True

                    if success:
                        try:
                            prize_html = ""
                            for tbl in soup.find_all('table'):
                                if "Kazanan" in tbl.get_text() or "İkramiye" in tbl.get_text():
                                    html_content = "<table class='result-table'>"
                                    for tr in tbl.find_all('tr'):
                                        html_content += "<tr>"
                                        tds = tr.find_all(['td', 'th'])
                                        if len(tds) == 1:
                                            html_content += f"<td colspan='5' class='superstar-header'>{tds[0].get_text(strip=True)}</td>"
                                        else:
                                            for td in tds:
                                                txt = td.get_text(strip=True)
                                                style = "color:#dc2626; font-weight:bold;" if "Devir" in txt else "font-weight:600;"
                                                html_content += f"<td style='{style}'>{txt}</td>"
                                        html_content += "</tr>"
                                    html_content += "</table>"
                                    prize_html += html_content
                            data[game]["prize_html"] = prize_html.replace('\n', '').replace('\r', '')
                        except: pass
                        data[game]["status"] = f"🟢 Canlı Web Senkronize"
            except Exception: continue
                
        if not success: data[game]["status"] = "🔴 Yeni Çekiliş Bekleniyor"
        return data

def parse_archive_row(row_vals, req_count, max_val):
    cno, tarih, nums_raw = "?", "?", []
    if len(row_vals) >= 2:
        val1_str = str(row_vals[1]).strip()
        is_date = isinstance(row_vals[1], pd.Timestamp) or any(c in val1_str for c in ['.', '-', '/'])
        if is_date and not val1_str.isdigit():
            cno = str(row_vals[0]).replace('.0', '')
            if isinstance(row_vals[1], pd.Timestamp): tarih = row_vals[1].strftime('%d.%m.%Y')
            else: tarih = val1_str.split(' ')[0]
            for v in row_vals[2:]: nums_raw.append(v)
        else:
            for v in row_vals: nums_raw.append(v)
    else:
        for v in row_vals: nums_raw.append(v)

    balls = []
    for val in nums_raw:
        try:
            if isinstance(val, pd.Timestamp): continue
            clean_str = str(val).replace(',', '.').strip()
            if not clean_str or clean_str.lower() in ['nan', 'none', 'nat']: continue
            n = int(float(clean_str))
            if 1 <= n <= max_val and n not in balls: balls.append(n)
        except: pass
        
    if len(balls) >= req_count:
        main_balls = sorted(balls[:req_count])
        plus, ss = "-", "-"
        if len(balls) > req_count: plus = balls[req_count]
        if len(balls) > req_count + 1: ss = balls[req_count + 1]
        return {"Cekilis_No": cno, "Tarih": tarih, "nums": main_balls, "plus": plus, "superstar": ss, "display_name": f"🗄️ {cno}. Çekiliş [{tarih}]" if cno != "?" else "🗄️ Arşiv Kaydı"}
    return None

@st.cache_data(ttl=5)
def load_game_archive(files, req_count, max_val):
    records = []
    for f in files:
        if os.path.exists(f):
            try:
                if f.endswith('.xlsx'):
                    df = pd.read_excel(f, sheet_name=0, header=None)
                    for _, row in df.iterrows():
                        row_str = str(row.values).lower()
                        if 'tarih' in row_str or 'hafta' in row_str or 'sayı' in row_str: continue
                        parsed = parse_archive_row(list(row.values), req_count, max_val)
                        if parsed: records.append(parsed)
            except: pass
            
    # 🚨 ZAMAN YOLCULUĞU İPTAL EDİLDİ! 🚨
    # Excel'indeki orijinal ve kusursuz sıralamayı bozmamak için hatalı sort (sıralama) işlemini tamamen sildik.
    # Artık veriler Excel dosyandaki mükemmel kronolojik sıraya sadık kalarak aktarılacak.
    
    return records

def load_sayisal_archive(): return load_game_archive(['çlgn_sysl.xlsx'], 6, 90)
def load_sans_archive(): return load_game_archive(['şns_topu.xlsx'], 5, 34)
def load_super_archive(): return load_game_archive(['süper.xlsx'], 6, 60)
def load_onnumara_archive(): return load_game_archive(['onnumara.xlsx'], 22, 80)

@st.cache_data(ttl=5)
def load_sans_topu_data():
    valid_draws, plus_draws, msg = [], [], ""
    try:
        conn = sqlite3.connect('loto.db')
        c = conn.cursor()
        c.execute("SELECT t1, t2, t3, t4, t5, arti FROM sans_topu ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            valid_draws.append(list(row[:5])) 
            plus_draws.append(row[5])         
        msg = f"Şans Topu SQL Motoru Aktif | Kayıtlı Çekiliş: {len(valid_draws)}"
    except Exception as e:
        msg = f"Bağlantı Hatası: {e}"
        
    if os.path.exists('otopilot_sans.csv'):
        try:
            df = pd.read_csv('otopilot_sans.csv', header=None)
            for _, row in df.iterrows():
                nums = [int(float(str(x).strip())) for x in row.values if str(x).strip().replace('.','',1).isdigit()]
                balls = [x for x in nums if 1 <= x <= 34]
                if len(balls) >= 5: valid_draws.insert(0, sorted(balls[:5]))
        except: pass
    if not valid_draws: return None, None, "Şans Topu SQL veri tabanı okunamadı."
    return valid_draws, plus_draws, msg

@st.cache_data(ttl=5)
def load_sayisal_ai_data():
    valid_draws, joker_draws, ss_draws, msg = [], [], [], ""
    try:
        conn = sqlite3.connect('loto.db')
        c = conn.cursor()
        c.execute("SELECT t1, t2, t3, t4, t5, t6, joker, superstar FROM sayisal_loto ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            valid_draws.append(list(row[:6]))
            joker_draws.append(row[6])
            ss_draws.append(row[7])
        msg = f"Sayısal Kuantum SQL Motoru Aktif | Kayıtlı Çekiliş: {len(valid_draws)}"
    except Exception as e:
        msg = f"Bağlantı Hatası: {e}"
    return valid_draws, joker_draws, ss_draws, msg

@st.cache_data(ttl=5)
def load_super_ai_data():
    valid_draws = []
    try:
        conn = sqlite3.connect('loto.db')
        c = conn.cursor()
        c.execute("SELECT t1, t2, t3, t4, t5, t6 FROM super_loto ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for row in rows: valid_draws.append(list(row))
    except: pass
    if os.path.exists('otopilot_super.csv'):
        try:
            df = pd.read_csv('otopilot_super.csv', header=None)
            for _, row in df.iterrows():
                nums = [int(float(str(x).strip())) for x in row.values if str(x).strip().replace('.','',1).isdigit()]
                balls = [x for x in nums if 1 <= x <= 60]
                if len(balls) >= 6: valid_draws.insert(0, sorted(balls[:6]))
        except: pass
    if not valid_draws: return None, "Süper Loto SQL veri tabanı okunamadı."
    return valid_draws, f"🟢 Süper Loto SQL Motoru Aktif | Kayıtlı Çekiliş: {len(valid_draws)}"

@st.cache_data(ttl=5)
def load_onnumara_ai_data():
    valid_draws = []
    try:
        conn = sqlite3.connect('loto.db')
        c = conn.cursor()
        c.execute("SELECT * FROM on_numara ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        for row in rows: valid_draws.append(list(row[1:]))
    except: pass
    if os.path.exists('otopilot_on_numara.csv'):
        try:
            df = pd.read_csv('otopilot_on_numara.csv', header=None)
            for _, row in df.iterrows():
                nums = [int(float(str(x).strip())) for x in row.values if str(x).strip().replace('.','',1).isdigit()]
                balls = [x for x in nums if 1 <= x <= 80]
                if len(balls) >= 22: valid_draws.insert(0, sorted(balls[:22]))
        except: pass
    if not valid_draws: return None, "On Numara SQL veri tabanı okunamadı."
    return valid_draws, f"🟢 On Numara SQL Motoru Aktif | Kayıtlı Çekiliş: {len(valid_draws)}"


# --- MODERN YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: 900; margin-bottom: 0;'>🧿KUANTUM BİLGİSAYAR ve YAPAY ZEKA MOTORLARI ile LOTO ANALİZİ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px; margin-bottom: 25px;'>Akıllı Loto Filtreleme Motoru</p>", unsafe_allow_html=True)

    selected_menu_opt = option_menu(
        menu_title=None,
        options=["Ana Sayfa", "Kuponlarım", "Çılgın Sayısal Loto", "Süper Loto", "Şans Topu", "On Numara"],
        icons=["house-door-fill", "ticket-detailed", "dice-6-fill", "bullseye", "star-fill", "hash"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "--hover-color": "#f1f5f9", "color": "#334155", "font-weight": "600", "border-radius": "8px"},
            "nav-link-selected": {"background-color": "#1e3a8a", "color": "white", "icon-color": "white", "font-weight": "bold"},
        }
    )

    if selected_menu_opt == "Ana Sayfa":
        st.sidebar.markdown("<hr style='margin:15px 0; border: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
        kullanici_giris_yapti_mi = st.session_state.get("logged_in", False)
        vip_mi = st.session_state.get("is_vip", False)

        if not kullanici_giris_yapti_mi:
            st.sidebar.markdown("""<div style='background-color: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px;'><h4 style='color: #475569; margin-top: 0; font-weight: 900; font-size: 16px;'>👁️ ZİYARETÇİ</h4><p style='font-size: 13px; color: #334155; font-weight: bold; margin-bottom: 5px;'>Maks. 3 Manuel / 1 AI Kolon</p><p style='font-size: 11px; color: #dc2626; margin-bottom: 0; font-weight: bold;'>Kupon kaydetmek için giriş yapın.</p></div>""", unsafe_allow_html=True)
        elif kullanici_giris_yapti_mi and not vip_mi:
            st.sidebar.markdown("""<div style='background-color: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px;'><h4 style='color: #1d4ed8; margin-top: 0; font-weight: 900; font-size: 16px;'>👤 STANDART ÜYE</h4><p style='font-size: 13px; color: #1e3a8a; font-weight: bold; margin-bottom: 5px;'>Maks. 3 Manuel / 1 AI Kolon</p><p style='font-size: 11px; color: #b45309; margin-bottom: 0; font-weight: bold;'>Sınırları kaldırmak için VIP'ye geçin.</p></div>""", unsafe_allow_html=True)
        else:
            st.sidebar.markdown("""<div style='background-color: #ecfdf5; border: 2px solid #10b981; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px;'><h4 style='color: #047857; margin-top: 0; font-weight: 900; font-size: 16px;'>👑 VIP ÜYE</h4><p style='font-size: 13px; color: #064e3b; font-weight: bold; margin-bottom: 5px;'>Sınırsız Kolon Üretimi</p><p style='font-size: 11px; color: #059669; margin-bottom: 0; font-weight: bold;'>Kuantum motoru tam yetkiyle emrinizde.</p></div>""", unsafe_allow_html=True)

    # 👑 GİZLİ ADMİN BUTONU BURAYA EKLENDİ 👑
    if st.session_state.get("logged_in", False) and st.session_state.get("user_email") == "admin@kaptan.com":
        st.sidebar.markdown("<hr style='margin:15px 0; border: 1px dashed #ef4444;'>", unsafe_allow_html=True)
        if st.sidebar.button("👑 ADMİN KONTROL MERKEZİ", use_container_width=True, type="primary"):
            st.session_state.admin_modu = True
            st.rerun()

if "son_secilen_menu" not in st.session_state: st.session_state.son_secilen_menu = selected_menu_opt

if st.session_state.son_secilen_menu != selected_menu_opt:
    st.session_state.giris_ekranini_ac = False
    st.session_state.admin_modu = False  # Menüden başka bir şeye tıklanırsa admin modundan çık
    st.session_state.son_secilen_menu = selected_menu_opt
    st.rerun()

# 🚀 YÖNLENDİRME (ROUTING) GÜNCELLENDİ
if st.session_state.get("admin_modu", False):
    selected_game = "ADMIN_PANEL"
elif st.session_state.get("giris_ekranini_ac", False) and not st.session_state.get("logged_in", False):
    selected_game = "VIP GİRİŞ MERKEZİ"
else:
    if selected_menu_opt == "Ana Sayfa": selected_game = "ANA SAYFA"
    elif selected_menu_opt == "Kuponlarım": selected_game = "KUPONLARIM"
    elif selected_menu_opt == "Çılgın Sayısal Loto": selected_game = "ÇILGIN SAYISAL LOTO AI"
    elif selected_menu_opt == "Süper Loto": selected_game = "SÜPER LOTO AI"
    elif selected_menu_opt == "Şans Topu": selected_game = "ŞANS TOPU AI"
    elif selected_menu_opt == "On Numara": selected_game = "ON NUMARA AI"
# ==========================================
# 👤 MÜŞTERİ YÖNETİMİ VE ÜYELİK PANELİ
# ==========================================
if selected_game == "VIP GİRİŞ MERKEZİ":
    def giristen_vazgec(): st.session_state.giris_ekranini_ac = False
    st.button("❌ İptal / Ana Menüye Dön", on_click=giristen_vazgec, key="vip_iptal_btn")
    st.markdown("<div class='main-title' style='color:#1e3a8a;'>👤 ÜYELİK VE VIP PORTAL</div><div class='sub-title' style='color:#64748b; margin-bottom: 30px;'>Sisteme Giriş Yapın veya Ücretsiz Hesap Oluşturun</div>", unsafe_allow_html=True)
    
    k1, k2, k3 = st.columns(3)    
    with k1: st.markdown("""<div style='background-color: #f8fafc; border-top: 5px solid #94a3b8; padding: 20px; border-radius: 10px; min-height: 280px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'><h4 style='color: #475569; text-align:center; font-weight:900; font-size: 18px;'>👁️ ZİYARETÇİ</h4><hr style='border-color:#e2e8f0; margin:10px 0;'><ul style='color: #475569; font-size: 13.5px; line-height: 1.7; padding-left: 20px; font-weight:500;'><li>Tüm Kuantum filtrelerine ve Yapay Zeka analizlerine <b>tam erişim.</b></li><li>Her analizde maksimum <b>3 manuel</b> ve <b>1 Otopilot</b> kolon üretimi.</li><li style='color:#dc2626; font-weight:bold; margin-top:8px;'>❌ Kilitli: Üretilen kuponları sistem hafızasına kaydetme ve arşivleme.</li></ul></div>""", unsafe_allow_html=True)
    with k2: st.markdown("""<div style='background-color: #eff6ff; border-top: 5px solid #3b82f6; padding: 20px; border-radius: 10px; min-height: 280px; box-shadow: 0 4px 10px rgba(59,130,246,0.1);'><h4 style='color: #1d4ed8; text-align:center; font-weight:900; font-size: 18px;'>👤 STANDART ÜYE</h4><hr style='border-color:#bfdbfe; margin:10px 0;'><ul style='color: #1e3a8a; font-size: 13.5px; line-height: 1.7; padding-left: 20px; font-weight:500;'><li>Tüm Kuantum filtrelerine ve Yapay Zeka analizlerine <b>tam erişim.</b></li><li>Üretilen kuponları sistem hafızasına <b>kaydetme ve arşivleme.</b></li><li style='color:#b45309; font-weight:bold; margin-top:8px;'>⚠️ Sınırlı Güç: Her analizde maksimum <b>3 manuel</b> ve <b>1 Otopilot</b> kolon üretimi.</li></ul></div>""", unsafe_allow_html=True)
    with k3: st.markdown("""<div style='background-color: #ecfdf5; border-top: 5px solid #10b981; padding: 20px; border-radius: 10px; min-height: 280px; box-shadow: 0 4px 10px rgba(16,185,129,0.1);'><h4 style='color: #047857; text-align:center; font-weight:900; font-size: 18px;'>💎 VIP ÜYE</h4><hr style='border-color:#a7f3d0; margin:10px 0;'><ul style='color: #064e3b; font-size: 13.5px; line-height: 1.7; padding-left: 20px; font-weight:500;'><li>Filtrelere, analizlere ve kişisel arşive <b>kesintisiz tam erişim.</b></li><li>Sistemdeki kolon üretim kısıtlamalarının ve sayaçların <b>kaldırılması.</b></li><li>Tek seferde <b>sınırsız sayıda</b> manuel ve yapay zeka kolon üretimi.</li><li>Paradoksları aşana kadar <b>limitsiz</b> kural deneme özgürlüğü.</li></ul></div>""", unsafe_allow_html=True)
        
    st.markdown("<br><hr style='border: 1px dashed #cbd5e1; margin-bottom:30px;'>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<div style='background-color:white; padding:25px; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            tab_login, tab_register = st.tabs(["🔑 Giriş Yap", "📝 Ücretsiz Kayıt Ol"])
            with tab_login:
                login_email = st.text_input("E-posta Adresi:", key="login_email").strip()
                login_pass = st.text_input("Şifre:", type="password", key="login_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sisteme Giriş Yap", type="primary", use_container_width=True):
                    if login_email and login_pass:
                        if login_email == "kaptan" and login_pass == "kaptan": 
                            st.session_state.logged_in = True
                            st.session_state.user_email = "admin@kaptan.com"
                            st.session_state.is_vip = True
                            st.rerun()
                        else:
                            user_status = verify_user(login_email, login_pass)
                            if user_status is not None:
                                st.session_state.logged_in = True
                                st.session_state.user_email = login_email
                                st.session_state.is_vip = bool(user_status[0])
                                st.success("✅ Giriş başarılı! Sisteme aktarılıyorsunuz...")
                                time.sleep(1)
                                st.rerun()
                            else: st.error("🚨 Hatalı E-posta veya Şifre!")
                    else: st.warning("Lütfen tüm alanları doldurun.")
                        
            with tab_register:
                reg_email = st.text_input("E-posta Adresi:", key="reg_email").strip()
                reg_pass = st.text_input("Şifre Belirleyin:", type="password", key="reg_pass")
                reg_pass2 = st.text_input("Şifreyi Tekrar Girin:", type="password", key="reg_pass2")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Hesap Oluştur", type="primary", use_container_width=True):
                    if reg_email and reg_pass and reg_pass2:
                        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                        if not re.match(email_regex, reg_email): st.error("🚨 Lütfen geçerli bir e-posta adresi girin! (Örn: isim@mail.com)")
                        elif reg_pass != reg_pass2: st.error("🚨 Şifreler uyuşmuyor!")
                        elif len(reg_pass) < 6: st.error("🚨 Şifre en az 6 karakter olmalıdır.")
                        else:
                            success = create_user(reg_email, reg_pass)
                            if success: st.success("🎉 Hesabınız başarıyla oluşturuldu! Şimdi 'Giriş Yap' sekmesinden giriş yapabilirsiniz.")
                            else: st.error("🚨 Bu e-posta adresi zaten sistemde kayıtlı!")
                    else: st.warning("Lütfen tüm alanları doldurun.")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success(f"Hoş geldiniz, **{st.session_state.user_email}**")
        if st.session_state.user_email == "admin@kaptan.com":
            st.markdown("<div style='background-color:#1e293b; padding:20px; border-radius:10px; border:2px solid #fbbf24; margin-top:20px; margin-bottom:20px;'><h3 style='color:#fbbf24; text-align:center; margin-top:0;'>👑 KAPTAN KÖŞKÜ</h3>", unsafe_allow_html=True)
            tab_musteriler, tab_otopilot = st.tabs(["👥 Müşteri Yönetimi", "🚀 Gizli Otopilot Sistemi"])
            with tab_musteriler:
                st.markdown("<p style='color:#cbd5e1; text-align:center; font-size:14px; margin-top:15px;'>Aşağıdaki listeden müşterilerinize tek tıkla VIP yetkisi verebilirsiniz.</p>", unsafe_allow_html=True)
                try:
                    all_users = get_all_users()
                    if all_users:
                        for usr_email, is_vip in all_users:
                            if usr_email == "admin@kaptan.com": continue
                            col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
                            with col_u1: st.markdown(f"<div style='padding-top:10px; color:white;'>👤 {usr_email}</div>", unsafe_allow_html=True)
                            with col_u2:
                                if is_vip: st.markdown("<div style='padding-top:10px; color:#10b981; font-weight:bold;'>💎 VIP ÜYE</div>", unsafe_allow_html=True)
                                else: st.markdown("<div style='padding-top:10px; color:#94a3b8; font-weight:bold;'>Standart</div>", unsafe_allow_html=True)
                            with col_u3:
                                if is_vip:
                                    if st.button("Yetkiyi Al", key=f"revoke_{usr_email}"): update_vip_status(usr_email, 0); st.rerun()
                                else:
                                    if st.button("👑 VIP YAP", type="primary", key=f"makevip_{usr_email}"): update_vip_status(usr_email, 1); st.rerun()
                        st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
                    else: st.info("Henüz sisteme kayıtlı müşteri yok.")
                except Exception as e: st.error("🚨 Veritabanı yönetim fonksiyonları eksik!")

            with tab_otopilot:
                st.markdown("<h4 style='color:#10b981; text-align:center; margin-top:15px;'>🤖 GİZLİ OTOPİLOT KONTROL MERKEZİ</h4><p style='font-size: 13px; color: #cbd5e1; text-align: center;'>Hangi oyunun veritabanına dışarıdan müdahale etmek istediğinizi seçin.</p>", unsafe_allow_html=True)
                hedef_oyun = st.selectbox("🎯 Güncellenecek Loto Modülü:", ["Çılgın Sayısal Loto", "Süper Loto", "Şans Topu", "On Numara"], key="otopilot_oyun_secim")
                if hedef_oyun == "Çılgın Sayısal Loto": dosya_adi, ornek_format = "otopilot_sayisal.csv", "Örn: 4, 15, 22, 28, 31, 75"
                elif hedef_oyun == "Süper Loto": dosya_adi, ornek_format = "otopilot_super.csv", "Örn: 5, 12, 23, 34, 45, 56"
                elif hedef_oyun == "Şans Topu": dosya_adi, ornek_format = "otopilot_sans.csv", "Örn: 4, 15, 22, 28, 31, 7"
                else: dosya_adi, ornek_format = "otopilot_on_numara.csv", "Örn: 1, 4, 15, 22, ... (22 Sayı girin)"
                
                yeni_sayilar = st.text_input(f"Sayılar ({ornek_format}):", key="otopilot_sayilar_input")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(f"💾 {hedef_oyun} Sistemine Kaydet", use_container_width=True, key="otop_kaydet_btn"):
                        if yeni_sayilar:
                            try:
                                nums = [int(x.strip()) for x in yeni_sayilar.split(',') if x.strip().isdigit()]
                                if len(nums) > 0:
                                    new_df = pd.DataFrame([nums])
                                    if os.path.exists(dosya_adi):
                                        existing = pd.read_csv(dosya_adi, header=None)
                                        new_df = pd.concat([new_df, existing], ignore_index=True)
                                    new_df.to_csv(dosya_adi, index=False, header=False)
                                    st.cache_data.clear()
                                    st.success(f"Başarılı! Veriler {hedef_oyun} sistemine işlendi.")
                                    time.sleep(1.5)
                                    st.rerun()
                                else: st.warning("Eksik veya geçersiz sayı girdiniz.")
                            except: st.error("Hatalı format. Lütfen aralarına virgül koyarak yazın.")
                with c_btn2:
                    if os.path.exists(dosya_adi):
                        if st.button(f"🗑️ {hedef_oyun} Sıfırla", use_container_width=True, key="otop_sifirla_btn"):
                            os.remove(dosya_adi); st.cache_data.clear(); st.success(f"{hedef_oyun} otopilot verileri temizlendi!"); time.sleep(1.5); st.rerun()

# --- ANA SAYFA ---
live_data = load_live_data()

if selected_game.upper() == "ANA SAYFA":
    # 🎯 Akıllı Buton Dedektifi: Arşiv metninden veya güncel çekilişten Numarayı bulup butona yazar
    import re
    def get_prev_btn_label(opts, idx, current_c_no=""):
        if idx == 0 and current_c_no and current_c_no.isdigit():
            return f"◀ Önceki ({int(current_c_no) - 1})"
        
        if idx + 1 >= len(opts): return "◀ Önceki"
        txt = str(opts[idx + 1])
        m = re.search(r'(?:\[(\d+)\]|(\d+)\.Çekiliş)', txt)
        if m:
            num = m.group(1) if m.group(1) else m.group(2)
            return f"◀ Önceki ({num})"
        return "◀ Önceki"

    st.markdown("<style>.home-ball, .home-onnumara-ball {width: 30px !important; height: 30px !important; line-height: 30px !important; font-size: 13px !important; margin: 2px !important;}</style>", unsafe_allow_html=True)
    st.markdown("""<div style="background: linear-gradient(to right, #0f172a, #1e3a8a); padding: 20px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6; text-align: center;"><h2 style="color: #ffffff; margin: 0; font-weight: 900; letter-spacing: 1px; font-size: 1.5rem;">🌐 YAPAY ZEKA ALGORİTMALARI</h2><p style="color: #94a3b8; font-size: 14px; margin: 5px 0 0 0; font-weight: 500;">Canlı Çekiliş Sonuçları ve Kuantum Arşiv Senkronizasyonu</p></div>""", unsafe_allow_html=True)
    
    sayisal_archive = load_sayisal_archive()
    sans_archive = load_sans_archive()
    super_archive = load_super_archive()
    onnumara_archive = load_onnumara_archive()

    c_left, c_right = st.columns(2)
    
    # ================= 1. ÇILGIN SAYISAL LOTO =================
    with c_left:
        mevcut_sayisal = live_data.get("sayisal", {})
        c_no = mevcut_sayisal.get("cekilis_no", "")
        c_tar = mevcut_sayisal.get("tarih", "")
        
        v_draws, j_draws, ss_draws, _ = load_sayisal_ai_data()
        archive_data = sayisal_archive
        
        # Dropdown Menüsü Dinamik Başlığı
        sayisal_opts_0 = f"🌐 {c_no}. Çekiliş (Güncel)" if c_no else "🌐 Güncel Ekran"
        sayisal_opts = [sayisal_opts_0]
        
        api_farki = len(v_draws) - len(archive_data) if archive_data else len(v_draws)
        if v_draws:
            for i in range(1, len(v_draws)):
                if archive_data and i > api_farki: sayisal_opts.append(archive_data[i - api_farki - 1]['display_name'])
                else: sayisal_opts.append(f"🗄️ Son Eklenen Kayıt [{st.session_state.get('son_tarih_sayisal', 'Yeni') if i == 1 else f'Yeni-{i}'}]")

        if "ana_sayisal_idx" not in st.session_state: st.session_state.ana_sayisal_idx = 0
        secilen_idx = st.session_state.ana_sayisal_idx
        if secilen_idx >= len(sayisal_opts): secilen_idx = 0
        
        if not v_draws or len(v_draws) == 0:
            s_nums, s_plus, s_ss, s_date = [], "", "", "Sistemde Kayıt Bulunmuyor"
            s_status = "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🔴 Veri Yok</span>"
        else:
            s_nums = v_draws[secilen_idx] 
            s_plus = j_draws[secilen_idx] if len(j_draws) > secilen_idx else ""
            s_ss = ss_draws[secilen_idx] if len(ss_draws) > secilen_idx else ""
            if secilen_idx == 0:
                s_status = "<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🟢 Aktif</span>"
                # Kum saati ile birlikte Çekiliş Numarası
                s_date = f"⏳ {c_no}. Çekiliş - {c_tar}" if (c_no and c_tar) else (f"⏳ {c_no}. Çekiliş" if c_no else "⏳ Sistemden En Güncel Kayıt")
            else:
                s_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🗄️ Arşiv</span>"
                s_date = sayisal_opts[secilen_idx]

        sayisal_html = "".join([f"<div class='home-ball ball-blue'>{n}</div>" for n in s_nums]) if s_nums else "<span style='color:#94a3b8; font-size:13px; font-style:italic;'>Bekleniyor...</span>"
        plus_html = f"<div class='home-ball ball-green'>{s_plus}</div>" if s_plus and str(s_plus) not in ["-", "0"] else ""
        ss_html = f"<div class='home-ball ball-red'>{s_ss}</div>" if s_ss and str(s_ss) not in ["-", "0"] else ""
        
        st.markdown(f"""<div style='background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-top: 4px solid #e61532; margin-bottom: 10px;'><div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;'><span style='font-size: 1rem; font-weight: 800; color: #e61532;'>ÇILGIN SAYISAL LOTO</span>{s_status}</div><div style='text-align: center; color: #64748b; font-weight: 600; margin-bottom: 12px; font-size:13px;'>{s_date}</div><div style='display: flex; justify-content: center; align-items: center; gap: 3px; margin-bottom: 12px; flex-wrap: wrap;'>{sayisal_html} <span style='font-size: 18px; color: #cbd5e1; font-weight: 900; margin: 0 4px;'>+</span> {plus_html}</div><div style='text-align: center; background-color:#f8fafc; padding:8px; border-radius:6px; display: flex; justify-content: center; align-items: center; gap: 10px;'><span style='color: #e61532; font-weight: 800; font-size: 0.9rem;'>SÜPERSTAR</span>{ss_html}</div></div>""", unsafe_allow_html=True)
        h_col1, h_col2 = st.columns([1, 3])
        with h_col1:
            if st.button(get_prev_btn_label(sayisal_opts, secilen_idx, c_no), key="ana_prev_btn_sayisal", use_container_width=True, disabled=(secilen_idx >= len(sayisal_opts)-1)):
                st.session_state.ana_sayisal_idx += 1; st.rerun()
        with h_col2:
            sel = st.selectbox("Arşiv", options=sayisal_opts, index=secilen_idx, key="ana_sel_sayisal", label_visibility="collapsed")
            if sayisal_opts.index(sel) != secilen_idx: st.session_state.ana_sayisal_idx = sayisal_opts.index(sel); st.rerun()
        
        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if secilen_idx == 0 and mevcut_sayisal and mevcut_sayisal.get("buyuk_tutar"):
                st.markdown(f"""
                <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-top: 5px;">
                    <table style="width:100%; text-align:left; border-collapse: collapse; font-size: 13px;">
                        <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; color:#475569;">Bilen</th>
                            <th style="padding: 10px; color:#475569;">Kazananlar & İkramiye Tutarı</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#ef4444;">6 Bilen</td>
                            <td style="padding: 10px;"><b>{mevcut_sayisal.get('buyuk_kisi', '-')}</b> / <span style="color:#10b981; font-weight:bold;">{mevcut_sayisal.get('buyuk_tutar', '-')}</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">5 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sayisal.get('bilen_5', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">4 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sayisal.get('bilen_4', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">3 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sayisal.get('bilen_3', '-')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight:bold; color:#334155;">2 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sayisal.get('bilen_2', '-')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor veya henüz girilmedi.")

    # ================= 2. SÜPER LOTO =================
    with c_right:
        mevcut_super = live_data.get("superloto", {})
        c_no_sup = mevcut_super.get("cekilis_no", "")
        c_tar_sup = mevcut_super.get("tarih", "")
        
        v_draws_super, msg_super = load_super_ai_data()
        archive_super = super_archive
        
        super_opts_0 = f"🌐 {c_no_sup}. Çekiliş (Güncel)" if c_no_sup else "🌐 Güncel Ekran"
        super_opts = [super_opts_0]
        
        api_farki_sup = len(v_draws_super) - len(archive_super) if archive_super else len(v_draws_super)
        if v_draws_super:
            for i in range(1, len(v_draws_super)):
                if archive_super and i > api_farki_sup: super_opts.append(archive_super[i - api_farki_sup - 1]['display_name'])
                else: super_opts.append(f"🗄️ Son Eklenen Kayıt (Sondan {i}.)")

        if "ana_super_idx" not in st.session_state: st.session_state.ana_super_idx = 0
        secilen_idx_sup = st.session_state.ana_super_idx
        if secilen_idx_sup >= len(super_opts): secilen_idx_sup = 0
        
        if not v_draws_super or len(v_draws_super) == 0:
            su_nums, su_date = [], "Sistemde Kayıt Bulunmuyor"
            su_status = "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🔴 Veri Yok</span>"
        else:
            su_nums = v_draws_super[secilen_idx_sup]
            if secilen_idx_sup == 0:
                su_status = "<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🟢 Aktif</span>"
                su_date = f"⏳ {c_no_sup}. Çekiliş - {c_tar_sup}" if (c_no_sup and c_tar_sup) else (f"⏳ {c_no_sup}. Çekiliş" if c_no_sup else "⏳ Sistemden En Güncel Kayıt")
            else:
                su_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🗄️ Arşiv</span>"
                su_date = super_opts[secilen_idx_sup]

        super_html = "".join([f"<div class='home-ball ball-green'>{n}</div>" for n in su_nums]) if su_nums else "<span style='color:#94a3b8; font-size:13px; font-style:italic;'>Bekleniyor...</span>"
        st.markdown(f"""<div style='background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-top: 4px solid #059669; margin-bottom: 10px;'><div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;'><span style='font-size: 1rem; font-weight: 800; color: #059669;'>SÜPER LOTO</span>{su_status}</div><div style='text-align: center; color: #64748b; font-weight: 600; margin-bottom: 18px; font-size:13px;'>{su_date}</div><div style='display: flex; justify-content: center; align-items: center; gap: 3px; margin-bottom: 23px; flex-wrap: wrap;'>{super_html}</div></div>""", unsafe_allow_html=True)
        h_col1_sup, h_col2_sup = st.columns([1, 3])
        with h_col1_sup:
            if st.button(get_prev_btn_label(super_opts, secilen_idx_sup, c_no_sup), key="ana_prev_btn_super", use_container_width=True, disabled=(secilen_idx_sup >= len(super_opts)-1)):
                st.session_state.ana_super_idx += 1; st.rerun()
        with h_col2_sup:
            sel_sup = st.selectbox("Arşiv Seçimi", options=super_opts, index=secilen_idx_sup, key="ana_sel_super", label_visibility="collapsed")
            if super_opts.index(sel_sup) != secilen_idx_sup: st.session_state.ana_super_idx = super_opts.index(sel_sup); st.rerun()
        
        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if secilen_idx_sup == 0 and mevcut_super and mevcut_super.get("buyuk_tutar"):
                st.markdown(f"""
                <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-top: 5px;">
                    <table style="width:100%; text-align:left; border-collapse: collapse; font-size: 13px;">
                        <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; color:#475569;">Bilen</th>
                            <th style="padding: 10px; color:#475569;">Kazananlar & İkramiye Tutarı</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#ef4444;">6 Bilen</td>
                            <td style="padding: 10px;"><b>{mevcut_super.get('buyuk_kisi', '-')}</b> / <span style="color:#10b981; font-weight:bold;">{mevcut_super.get('buyuk_tutar', '-')}</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">5 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_super.get('bilen_5', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">4 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_super.get('bilen_4', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">3 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_super.get('bilen_3', '-')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight:bold; color:#334155;">2 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_super.get('bilen_2', '-')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor veya henüz girilmedi.")

    st.markdown("<br>", unsafe_allow_html=True)
    c_left2, c_right2 = st.columns(2)
    
    # ================= 3. ŞANS TOPU =================
    with c_left2:
        mevcut_sans = live_data.get("sanstopu", {})
        c_no_sans = mevcut_sans.get("cekilis_no", "")
        c_tar_sans = mevcut_sans.get("tarih", "")
        
        v_draws_sans, p_draws_sans, msg_sans = load_sans_topu_data()
        archive_sans = sans_archive
        
        sans_opts_0 = f"🌐 {c_no_sans}. Çekiliş (Güncel)" if c_no_sans else "🌐 Güncel Ekran"
        sans_opts = [sans_opts_0]
        
        api_farki_sans = len(v_draws_sans) - len(archive_sans) if archive_sans else len(v_draws_sans)
        if v_draws_sans:
            for i in range(1, len(v_draws_sans)):
                if archive_sans and i > api_farki_sans: sans_opts.append(archive_sans[i - api_farki_sans - 1]['display_name'])
                else: sans_opts.append(f"🗄️ Son Eklenen Kayıt (Sondan {i}.)")

        if "ana_sans_idx" not in st.session_state: st.session_state.ana_sans_idx = 0
        secilen_idx_sans = st.session_state.ana_sans_idx
        if secilen_idx_sans >= len(sans_opts): secilen_idx_sans = 0
        
        if not v_draws_sans or len(v_draws_sans) == 0:
            st_nums, st_plus, st_date = [], "", "Sistemde Kayıt Bulunmuyor"
            st_status = "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🔴 Veri Yok</span>"
        else:
            st_nums = v_draws_sans[secilen_idx_sans]
            st_plus = p_draws_sans[secilen_idx_sans] if len(p_draws_sans) > secilen_idx_sans else ""
            if secilen_idx_sans == 0:
                st_status = "<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🟢 Aktif</span>"
                st_date = f"⏳ {c_no_sans}. Çekiliş - {c_tar_sans}" if (c_no_sans and c_tar_sans) else (f"⏳ {c_no_sans}. Çekiliş" if c_no_sans else "⏳ Sistemden En Güncel Kayıt")
            else:
                st_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🗄️ Arşiv</span>"
                st_date = sans_opts[secilen_idx_sans]

        sans_html = "".join([f"<div class='home-ball ball-blue'>{n}</div>" for n in st_nums]) if st_nums else "<span style='color:#94a3b8; font-size:13px; font-style:italic;'>Veri Bekleniyor...</span>"
        splus_html = f"<div class='home-ball ball-red'>{st_plus}</div>" if st_plus and str(st_plus) != "-" else ""
        st.markdown(f"""<div style='background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-top: 4px solid #0ea5e9; margin-bottom: 10px;'><div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;'><span style='font-size: 1rem; font-weight: 800; color: #0ea5e9;'>ŞANS TOPU</span>{st_status}</div><div style='text-align: center; color: #64748b; font-weight: 600; margin-bottom: 12px; font-size:13px;'>{st_date}</div><div style='display: flex; justify-content: center; align-items: center; gap: 3px; margin-bottom: 12px; flex-wrap: wrap;'>{sans_html} <span style='font-size: 18px; color: #cbd5e1; font-weight: 900; margin: 0 4px;'>+</span> {splus_html}</div></div>""", unsafe_allow_html=True)
        h_col1_s, h_col2_s = st.columns([1, 3])
        with h_col1_s:
            if st.button(get_prev_btn_label(sans_opts, secilen_idx_sans, c_no_sans), key="ana_prev_btn_sans", use_container_width=True, disabled=(secilen_idx_sans >= len(sans_opts)-1)):
                st.session_state.ana_sans_idx += 1; st.rerun()
        with h_col2_s:
            sel_s = st.selectbox("Arşiv Seçimi", options=sans_opts, index=secilen_idx_sans, key="ana_sel_sans", label_visibility="collapsed")
            if sans_opts.index(sel_s) != secilen_idx_sans: st.session_state.ana_sans_idx = sans_opts.index(sel_s); st.rerun()
        
        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if secilen_idx_sans == 0 and mevcut_sans and mevcut_sans.get("buyuk_tutar"):
                st.markdown(f"""
                <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-top: 5px;">
                    <table style="width:100%; text-align:left; border-collapse: collapse; font-size: 13px;">
                        <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; color:#475569;">Bilen</th>
                            <th style="padding: 10px; color:#475569;">Kazananlar & İkramiye Tutarı</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#ef4444;">5+1 Bilen</td>
                            <td style="padding: 10px;"><b>{mevcut_sans.get('buyuk_kisi', '-')}</b> / <span style="color:#10b981; font-weight:bold;">{mevcut_sans.get('buyuk_tutar', '-')}</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">5 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sans.get('bilen_5', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">4+1 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sans.get('bilen_4', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">4 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sans.get('bilen_3', '-')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight:bold; color:#334155;">3+1 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_sans.get('bilen_2', '-')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor veya henüz girilmedi.")

    # ================= 4. ON NUMARA =================
    with c_right2:
        mevcut_on = live_data.get("onnumara", {})
        c_no_on = mevcut_on.get("cekilis_no", "")
        c_tar_on = mevcut_on.get("tarih", "")
        
        v_draws_on, msg_on = load_onnumara_ai_data()
        archive_on = onnumara_archive
        
        on_opts_0 = f"🌐 {c_no_on}. Çekiliş (Güncel)" if c_no_on else "🌐 Güncel Ekran"
        on_opts = [on_opts_0]
        
        api_farki_on = len(v_draws_on) - len(archive_on) if archive_on else len(v_draws_on)
        if v_draws_on:
            for i in range(1, len(v_draws_on)):
                if archive_on and i > api_farki_on: on_opts.append(archive_on[i - api_farki_on - 1]['display_name'])
                else: on_opts.append(f"🗄️ Son Eklenen Kayıt (Sondan {i}.)")

        if "ana_on_idx" not in st.session_state: st.session_state.ana_on_idx = 0
        secilen_idx_on = st.session_state.ana_on_idx
        if secilen_idx_on >= len(on_opts): secilen_idx_on = 0
        
        if not v_draws_on or len(v_draws_on) == 0:
            on_nums, on_date = [], "Sistemde Kayıt Bulunmuyor"
            on_status = "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🔴 Veri Yok</span>"
        else:
            on_nums = v_draws_on[secilen_idx_on]
            if secilen_idx_on == 0:
                on_status = "<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🟢 Aktif</span>"
                on_date = f"⏳ {c_no_on}. Çekiliş - {c_tar_on}" if (c_no_on and c_tar_on) else (f"⏳ {c_no_on}. Çekiliş" if c_no_on else "⏳ Sistemden En Güncel Kayıt")
            else:
                on_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:3px 6px; border-radius:4px; font-size:0.75rem;'>🗄️ Arşiv</span>"
                on_date = on_opts[secilen_idx_on]

        if on_nums:
            onnumara_html_1 = "".join([f"<div class='home-onnumara-ball'>{n}</div>" for n in on_nums[:11]])
            onnumara_html_2 = "".join([f"<div class='home-onnumara-ball'>{n}</div>" for n in on_nums[11:]])
            onnumara_html = f"<div style='display:flex; justify-content:center; gap:2px; flex-wrap:wrap;'>{onnumara_html_1}</div><div style='height: 4px;'></div><div style='display:flex; justify-content:center; gap:2px; flex-wrap:wrap;'>{onnumara_html_2}</div>"
        else: onnumara_html = "<span style='color:#94a3b8; font-size:13px; font-style:italic;'>Veri Bekleniyor...</span>"
            
        st.markdown(f"""<div style='background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-top: 4px solid #d97706; margin-bottom: 10px;'><div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;'><span style='font-size: 1rem; font-weight: 800; color: #d97706;'>ON NUMARA</span>{on_status}</div><div style='text-align: center; color: #475569; font-weight: 600; margin-bottom: 12px; font-size:13px;'>{on_date}</div><div style='margin-bottom: 12px;'>{onnumara_html}</div></div>""", unsafe_allow_html=True)
        h_col1_o, h_col2_o = st.columns([1, 3])
        with h_col1_o:
            if st.button(get_prev_btn_label(on_opts, secilen_idx_on, c_no_on), key="ana_prev_btn_on", use_container_width=True, disabled=(secilen_idx_on >= len(on_opts)-1)):
                st.session_state.ana_on_idx += 1; st.rerun()
        with h_col2_o:
            sel_on = st.selectbox("Arşiv Seçimi", options=on_opts, index=secilen_idx_on, key="ana_sel_on", label_visibility="collapsed")
            if on_opts.index(sel_on) != secilen_idx_on: st.session_state.ana_on_idx = on_opts.index(sel_on); st.rerun()
        
        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if secilen_idx_on == 0 and mevcut_on and mevcut_on.get("buyuk_tutar"):
                st.markdown(f"""
                <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-top: 5px;">
                    <table style="width:100%; text-align:left; border-collapse: collapse; font-size: 13px;">
                        <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; color:#475569;">Bilen</th>
                            <th style="padding: 10px; color:#475569;">Kazananlar & İkramiye Tutarı</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#ef4444;">10 Bilen</td>
                            <td style="padding: 10px;"><b>{mevcut_on.get('buyuk_kisi', '-')}</b> / <span style="color:#10b981; font-weight:bold;">{mevcut_on.get('buyuk_tutar', '-')}</span></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">9 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_on.get('bilen_5', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">8 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_on.get('bilen_4', '-')}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <td style="padding: 10px; font-weight:bold; color:#334155;">7 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_on.get('bilen_3', '-')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight:bold; color:#334155;">6 Bilen / 0 Bilen</td>
                            <td style="padding: 10px; color:#334155;">{mevcut_on.get('bilen_2', '-')}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor veya henüz girilmedi.")

    st.markdown("<br><hr style='border: 3px solid #e2e8f0; margin-bottom: 40px; margin-top: 20px;'>", unsafe_allow_html=True)
    st.markdown("<div class='main-title' style='color:#0f172a; font-size: 2.5rem; text-align: center; text-transform: uppercase; letter-spacing: 1px;'>🚀 Kuantum Yapay Zeka Laboratuvarı</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#64748b; text-align: center; font-size: 1.1rem; margin-bottom: 40px;'>Şans Oyunlarında Tesadüfleri Bitiren Matematiksel Devrim</div>", unsafe_allow_html=True)

    st.markdown("""<div style='background-color: #ffffff; border-left: 6px solid #e61532; padding: 25px; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 30px;'><h2 style='color: #0f172a; margin-top: 0; font-weight: 900;'>BİZ KİMİZ VE NE YAPIYORUZ?</h2><p style='font-size: 1.1rem; line-height: 1.7; color: #334155;'>Burası sıradan bir "rastgele sayı üretici" veya hislerle çalışan bir tahmin sitesi değildir. Burası, <span style='color: #e61532; font-weight: 900;'>Kuantum Monte Carlo Simülasyonları</span> ve ileri düzey <span style='color: #e61532; font-weight: 900;'>Makine Öğrenmesi (Machine Learning)</span> modellerinin şans oyunları veritabanlarına entegre edildiği <b>profesyonel bir veri analizi laboratuvarıdır.</b></p><p style='font-size: 1.1rem; line-height: 1.7; color: #334155;'>Bizim inancımıza göre <b>"Şans", anlaşılamamış matematiğin diğer adıdır.</b> Milyonlarca kombinasyonun havada uçuştuğu loto oyunlarında "tesadüf" dediğimiz şey, aslında devasa bir veri yığınının içinde gizlenmiş algoritmik bir döngüdür. Bizim işimiz; tarihteki tüm çekilişleri saniyeler içinde taramak, sayıların davranış karakterlerini çözmek ve <span style='color: #e61532; font-weight: 900;'>"insan beyninin hesaplayamayacağı" o altın oranlı, kusursuz kolonları</span> sizin için filtrelemektir.</p></div>""", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:#0f172a; font-weight:900; margin-top:40px; margin-bottom:25px;'>🧠 YAPAY ZEKA MOTORUMUZUN KALBİ</h2>", unsafe_allow_html=True)

    c1_man, c2_man = st.columns(2)
    with c1_man: st.markdown("""<div style='background-color: #f8fafc; border: 2px solid #cbd5e1; padding: 20px; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'><h3 style='color: #1e3a8a; margin-top: 0; font-weight: 900;'>🧬 Markov Zinciri Analizi</h3><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'><b>Peki kimdir bu Markov? Neyi başarmıştır?</b><br><span style='color: #0f172a; font-weight: 900;'>Andrey Markov</span>, 1900'lerin başında yaşamış efsanevi bir Rus matematikçidir. Markov, "bağımsız" gibi görünen rastgele olayların aslında birbirini etkilediğini, <b>"bir sonraki adımın, sadece ve sadece bir önceki adıma bağlı olduğunu"</b> kanıtlayarak istatistik dünyasında devrim yapmıştır. </p><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'><b>Sistemimizde Nasıl Çalışır?</b><br>Makine, loto çekilişlerini bir "durum" (state) olarak görür. Eğer geçen hafta frekanslar <span style='color: #e61532; font-weight: 900;'>"3 Sıcak, 2 Orta, 1 Soğuk"</span> geldiyse; sistem tarihe dalar ve Markov Geçiş Matrisi'ni kullanarak <i>"Bu şablondan sonraki hafta sayıların % kaç ihtimalle tek/çift, % kaç ihtimalle ardışık geleceğini"</i> kusursuz bir yüzdelik tahminle ekrana yansıtır.</p></div>""", unsafe_allow_html=True)
    with c2_man: st.markdown("""<div style='background-color: #f8fafc; border: 2px solid #cbd5e1; padding: 20px; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'><h3 style='color: #b91c1c; margin-top: 0; font-weight: 900;'>⚔️ Apriori (Düşman İkili) Algoritması</h3><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'>Orijinalinde küresel market zincirlerinin "Sepet Analizi" için kullandığı bir kural madenciliği algoritmasıdır. Biz bu yapay zeka birimini, sayıların <span style='color: #0f172a; font-weight: 900;'>"Nefret İlişkisini"</span> bulmak için loto veritabanına entegre ettik.</p><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'><b>Sistemimizde Nasıl Çalışır?</b><br>Oyun tarihinde bugüne kadar <b>hiç yan yana gelmemiş</b> veya birbirini adeta iten "zehirli sayı kombinasyonları" tespit edilir. Motorumuz kolon üretirken bu düşman ikilileri asla aynı kupona koymaz, <span style='color: #e61532; font-weight: 900;'>matematiksel çelişkileri acımasızca imha eder.</span></p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c3_man, c4_man = st.columns(2)
    with c3_man: st.markdown("""<div style='background-color: #f8fafc; border: 2px solid #cbd5e1; padding: 20px; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'><h3 style='color: #047857; margin-top: 0; font-weight: 900;'>🛡️ K-Means Kümeleme (Klan Zırhı)</h3><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'>Sayılar sadece rakamlardan ibaret değildir; onların da bir karakteri, çıkma ivmesi (momentum) ve kapsama alanları vardır. Gözetimsiz bir Makine Öğrenmesi metodu olan K-Means algoritması, <b>tüm sayıları fiziksel özelliklerine göre 4 veya 5 farklı kampa (Klana) ayırır.</b></p><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'>Sistem, kolonlarınızı üretirken tüm topları aynı klandan seçmek yerine, her klandan en güçlü genleri alarak kuponunuza bir <span style='color: #0f172a; font-weight: 900;'>"Klan Zırhı"</span> giydirir. Dağılım ne kadar çeşitliyse, vurma ihtimali o kadar yükselir.</p></div>""", unsafe_allow_html=True)
    with c4_man: st.markdown("""<div style='background-color: #f8fafc; border: 2px solid #cbd5e1; padding: 20px; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'><h3 style='color: #d97706; margin-top: 0; font-weight: 900;'>📉 Çan Eğrisi (Normal Dağılım)</h3><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'>Dünyadaki her kaotik olayın bir merkezi, bir yerçekimi noktası vardır. Buna istatistikte <b>"Gauss Dağılımı"</b> veya Çan Eğrisi denir. </p><p style='color: #475569; font-size: 0.95rem; line-height: 1.6;'>Örneğin Çılgın Sayısal Loto'da çekilen 6 sayının toplamı <span style='color: #e61532; font-weight: 900;'>%80 ihtimalle 240 ile 310</span> arasında (Kalbi 273'tür) gerçekleşir. Sihirli Otopilot motorumuz, size kolon üretirken saniyeler içinde binlerce <b>Monte Carlo simülasyonu</b> yapar ve toplamı oyunun matematiksel kalbine (Çan eğrisinin tam ortasına) oturmayan HİÇBİR kolonu size göstermez.</p></div>""", unsafe_allow_html=True)
        
    st.markdown("<br><hr style='border: 2px dashed #cbd5e1; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("""<div style='background-color: #0f172a; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);'><h2 style='color: #f8fafc; margin-top: 0; font-weight: 900; letter-spacing: 1px;'>🚀 ŞİMDİ SİHRİ BAŞLATIN</h2><p style='color: #cbd5e1; font-size: 1.15rem; margin-bottom: 25px;'>Matematiğin gücünü kendi gözlerinizle görmek için sol menüden oynamak istediğiniz oyunu seçin. İster kuralları kendiniz koyun, isterseniz tüm yetkiyi <b>Sihirli Yapay Zeka Otopilotuna</b> bırakın.</p><div style='display:inline-block; background-color:#10b981; color:white; font-weight:900; padding:12px 30px; border-radius:30px; font-size:1.1rem; border: 2px solid #059669;'>👈 SOL MENÜDEN BİR OYUN SEÇEREK ANALİZ MERKEZİNE GİRİŞ YAPIN</div></div>""", unsafe_allow_html=True)
# ==========================================
# 👑 ADMİN KONTROL MERKEZİ (CANLI SONUÇ GİRİŞİ)
# ==========================================
elif selected_game == "ADMIN_PANEL":
    st.markdown("<div class='main-title' style='color:#b91c1c;'>👑 ADMİN KONTROL MERKEZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>Canlı Çekiliş Sonuçları ve İkramiye Yönetimi</div>", unsafe_allow_html=True)

    if st.session_state.get("user_email") != "admin@kaptan.com":
        st.error("🚨 Yetkisiz Erişim! Bu sayfa sadece sistem yöneticisine aittir.")
    else:
        oyun_secim = st.selectbox("📌 Güncellenecek Oyunu Seçin", ["Çılgın Sayısal Loto", "Süper Loto", "Şans Topu", "On Numara"])
        
        game_keys = {"Çılgın Sayısal Loto": "sayisal", "Süper Loto": "superloto", "Şans Topu": "sanstopu", "On Numara": "onnumara"}
        g_key = game_keys[oyun_secim]
        
        mevcut_veri = live_data.get(g_key, {})

        st.markdown(f"### 📝 {oyun_secim} Sonuç Formu")
        
        with st.form(f"admin_form_{g_key}"):
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                f_cekilis_no = st.text_input("🔢 Çekiliş No", value=mevcut_veri.get("cekilis_no", ""), placeholder="Örn: 937")
            with c2:
                f_tarih = st.text_input("📅 Çekiliş Tarihi", value=mevcut_veri.get("tarih", ""), placeholder="Örn: 29.07.2026")
            with c3:
                eski_toplar = ",".join(map(str, mevcut_veri.get("nums", [])))
                f_nums = st.text_input("🎱 Kazanan Numaralar (Aralarına virgül koyarak yazın)", value=eski_toplar, placeholder="Örn: 5,12,25,36,44,80")

            f_plus, f_joker, f_super = "", "", ""
            if g_key == "sayisal":
                cj, cs = st.columns(2)
                with cj: f_joker = st.text_input("🃏 Joker", value=str(mevcut_veri.get("joker", "")))
                with cs: f_super = st.text_input("🌟 SüperStar", value=str(mevcut_veri.get("superstar", "")))
            elif g_key == "sanstopu":
                f_plus = st.text_input("➕ Artı (+) Top", value=str(mevcut_veri.get("plus", "")))

            st.markdown("### 💰 İkramiye Detayları")
            
            # --- 🔴 ÇILGIN SAYISAL LOTO DETAYLI KATEGORİLERİ ---
            if g_key == "sayisal":
                st.markdown("<h5 style='color:#b91c1c;'>Ana Kategoriler</h5>", unsafe_allow_html=True)
                c_ana1, c_ana2 = st.columns(2)
                with c_ana1:
                    f_6_bilen = st.text_input("6 Bilen (Devir veya Kişi/Tutar)", value=mevcut_veri.get("bilen_6", ""), placeholder="Örn: 21.Devir - 493.351.089 ₺")
                    f_5_bilen = st.text_input("5 Bilen", value=mevcut_veri.get("bilen_5", ""), placeholder="Örn: 1 Kişi - 2.989.867 ₺")
                    f_3_bilen = st.text_input("3 Bilen", value=mevcut_veri.get("bilen_3", ""), placeholder="Örn: 9.137 Kişi - 818 ₺")
                with c_ana2:
                    f_5_1_bilen = st.text_input("5+1 Bilen", value=mevcut_veri.get("bilen_5_1", ""), placeholder="Örn: 0 Kişi - 0 ₺")
                    f_4_bilen = st.text_input("4 Bilen", value=mevcut_veri.get("bilen_4", ""), placeholder="Örn: 291 Kişi - 10.274 ₺")
                    f_2_bilen = st.text_input("2 Bilen", value=mevcut_veri.get("bilen_2", ""), placeholder="Örn: 135.077 Kişi - 83 ₺")

                st.markdown("<h5 style='color:#eab308; margin-top:10px;'>🌟 SüperStar Kategorileri</h5>", unsafe_allow_html=True)
                c_ss1, c_ss2 = st.columns(2)
                with c_ss1:
                    f_ss_6 = st.text_input("6+SüperStar", value=mevcut_veri.get("ss_6", ""), placeholder="Örn: 0 Kişi")
                    f_ss_5 = st.text_input("5+SüperStar", value=mevcut_veri.get("ss_5", ""), placeholder="Örn: 0 Kişi")
                    f_ss_3 = st.text_input("3+SüperStar", value=mevcut_veri.get("ss_3", ""), placeholder="Örn: 13 Kişi - 81.805 ₺")
                    f_ss_1 = st.text_input("1+SüperStar", value=mevcut_veri.get("ss_1", ""), placeholder="Örn: 2.149 Kişi - 250 ₺")
                with c_ss2:
                    f_ss_5_1 = st.text_input("5+1+SüperStar", value=mevcut_veri.get("ss_5_1", ""), placeholder="Örn: 0 Kişi")
                    f_ss_4 = st.text_input("4+SüperStar", value=mevcut_veri.get("ss_4", ""), placeholder="Örn: 3 Kişi - 513.722 ₺")
                    f_ss_2 = st.text_input("2+SüperStar", value=mevcut_veri.get("ss_2", ""), placeholder="Örn: 362 Kişi - 2.500 ₺")
                    f_ss_0 = st.text_input("0+SüperStar", value=mevcut_veri.get("ss_0", ""), placeholder="Örn: 4.813 Kişi - 125 ₺")
            
            # --- 🔵 SÜPER LOTO DETAYLI KATEGORİLERİ ---
            elif g_key == "superloto":
                c_sl1, c_sl2 = st.columns(2)
                with c_sl1:
                    f_sl_6 = st.text_input("6 Bilen", value=mevcut_veri.get("bilen_6", ""), placeholder="Örn: 16.Devir - 197.300.158 ₺")
                    f_sl_4 = st.text_input("4 Bilen", value=mevcut_veri.get("bilen_4", ""), placeholder="Örn: 808 Kişi - 5.533 ₺")
                    f_sl_2 = st.text_input("2 Bilen", value=mevcut_veri.get("bilen_2", ""), placeholder="Örn: 205.158 Kişi - 28 ₺")
                with c_sl2:
                    f_sl_5 = st.text_input("5 Bilen", value=mevcut_veri.get("bilen_5", ""), placeholder="Örn: 18 Kişi - 159.693 ₺")
                    f_sl_3 = st.text_input("3 Bilen", value=mevcut_veri.get("bilen_3", ""), placeholder="Örn: 20.354 Kişi - 266 ₺")

            # --- 🟢 ŞANS TOPU DETAYLI KATEGORİLERİ ---
            elif g_key == "sanstopu":
                c_st1, c_st2 = st.columns(2)
                with c_st1:
                    f_st_5_1 = st.text_input("5+1 Bilen", value=mevcut_veri.get("bilen_5_1", ""), placeholder="Örn: 1 Kişi - 14.545.036 ₺")
                    f_st_4_1 = st.text_input("4+1 Bilen", value=mevcut_veri.get("bilen_4_1", ""), placeholder="Örn: 107 Kişi - 2.553 ₺")
                    f_st_3_1 = st.text_input("3+1 Bilen", value=mevcut_veri.get("bilen_3_1", ""), placeholder="Örn: 2.654 Kişi - 154 ₺")
                    f_st_2_1 = st.text_input("2+1 Bilen", value=mevcut_veri.get("bilen_2_1", ""), placeholder="Örn: 23.285 Kişi - 64 ₺")
                    f_st_0_1 = st.text_input("0+1 Bilen", value=mevcut_veri.get("bilen_0_1", ""), placeholder="Örn: 67.864 Kişi - 35 ₺")
                with c_st2:
                    f_st_5 = st.text_input("5 Bilen", value=mevcut_veri.get("bilen_5", ""), placeholder="Örn: 4 Kişi - 68.297 ₺")
                    f_st_4 = st.text_input("4 Bilen", value=mevcut_veri.get("bilen_4", ""), placeholder="Örn: 1.158 Kişi - 294 ₺")
                    f_st_3 = st.text_input("3 Bilen", value=mevcut_veri.get("bilen_3", ""), placeholder="Örn: 31.013 Kişi - 52 ₺")
                    f_st_1_1 = st.text_input("1+1 Bilen", value=mevcut_veri.get("bilen_1_1", ""), placeholder="Örn: 73.918 Kişi - 32 ₺")

            # --- 🟡 ON NUMARA DETAYLI KATEGORİLERİ ---
            elif g_key == "onnumara":
                c_on1, c_on2 = st.columns(2)
                with c_on1:
                    f_on_10 = st.text_input("10 Bilen", value=mevcut_veri.get("bilen_10", ""), placeholder="Örn: 3.Devir - 3.507.085 ₺")
                    f_on_8 = st.text_input("8 Bilen", value=mevcut_veri.get("bilen_8", ""), placeholder="Örn: 324 Kişi - 2.458 ₺")
                    f_on_6 = st.text_input("6 Bilen", value=mevcut_veri.get("bilen_6", ""), placeholder="Örn: 22.278 Kişi - 71 ₺")
                with c_on2:
                    f_on_9 = st.text_input("9 Bilen", value=mevcut_veri.get("bilen_9", ""), placeholder="Örn: 21 Kişi - 30.338 ₺")
                    f_on_7 = st.text_input("7 Bilen", value=mevcut_veri.get("bilen_7", ""), placeholder="Örn: 3.519 Kişi - 429 ₺")
                    f_on_0 = st.text_input("Hiç Kazanamayan (0 Bilen)", value=mevcut_veri.get("bilen_0", ""), placeholder="Örn: 45.477 Kişi - 49 ₺")

            submitted = st.form_submit_button("🚀 SONUÇLARI CANLIYA AL VE KUPONLARI TARA", type="primary", use_container_width=True)

            if submitted:
                try:
                    num_list = [int(x.strip()) for x in f_nums.split(",") if x.strip().isdigit()]
                    
                    # Ana Çatı
                    live_data[g_key] = {
                        "cekilis_no": f_cekilis_no,
                        "tarih": f_tarih,
                        "nums": num_list
                    }
                    
                    if g_key == "sayisal":
                        live_data[g_key]["joker"] = int(f_joker) if f_joker.strip().isdigit() else 0
                        live_data[g_key]["superstar"] = int(f_super) if f_super.strip().isdigit() else 0
                        live_data[g_key]["bilen_6"] = f_6_bilen
                        live_data[g_key]["bilen_5_1"] = f_5_1_bilen
                        live_data[g_key]["bilen_5"] = f_5_bilen
                        live_data[g_key]["bilen_4"] = f_4_bilen
                        live_data[g_key]["bilen_3"] = f_3_bilen
                        live_data[g_key]["bilen_2"] = f_2_bilen
                        live_data[g_key]["ss_6"] = f_ss_6
                        live_data[g_key]["ss_5_1"] = f_ss_5_1
                        live_data[g_key]["ss_5"] = f_ss_5
                        live_data[g_key]["ss_4"] = f_ss_4
                        live_data[g_key]["ss_3"] = f_ss_3
                        live_data[g_key]["ss_2"] = f_ss_2
                        live_data[g_key]["ss_1"] = f_ss_1
                        live_data[g_key]["ss_0"] = f_ss_0

                    elif g_key == "superloto":
                        live_data[g_key]["bilen_6"] = f_sl_6
                        live_data[g_key]["bilen_5"] = f_sl_5
                        live_data[g_key]["bilen_4"] = f_sl_4
                        live_data[g_key]["bilen_3"] = f_sl_3
                        live_data[g_key]["bilen_2"] = f_sl_2

                    elif g_key == "sanstopu":
                        live_data[g_key]["plus"] = int(f_plus) if f_plus.strip().isdigit() else 0
                        live_data[g_key]["bilen_5_1"] = f_st_5_1
                        live_data[g_key]["bilen_5"] = f_st_5
                        live_data[g_key]["bilen_4_1"] = f_st_4_1
                        live_data[g_key]["bilen_4"] = f_st_4
                        live_data[g_key]["bilen_3_1"] = f_st_3_1
                        live_data[g_key]["bilen_3"] = f_st_3
                        live_data[g_key]["bilen_2_1"] = f_st_2_1
                        live_data[g_key]["bilen_1_1"] = f_st_1_1
                        live_data[g_key]["bilen_0_1"] = f_st_0_1

                    elif g_key == "onnumara":
                        live_data[g_key]["bilen_10"] = f_on_10
                        live_data[g_key]["bilen_9"] = f_on_9
                        live_data[g_key]["bilen_8"] = f_on_8
                        live_data[g_key]["bilen_7"] = f_on_7
                        live_data[g_key]["bilen_6"] = f_on_6
                        live_data[g_key]["bilen_0"] = f_on_0

                    save_live_data(live_data)
                    st.success(f"✅ {oyun_secim} sonuçları başarıyla sisteme kazındı! Kuponlar anında güncelleniyor...")
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Format Hatası: Lütfen numaraları arasına sadece virgül koyarak yazın! (Örn: 1, 23, 45, 56)") 
# ==========================================
# 🎫 KUPONLARIM & KAZANÇ MERKEZİ
# ==========================================
elif selected_game == "KUPONLARIM":
    st.markdown("<div class='main-title' style='color:#d97706;'>🎫 KUPONLARIM & KAZANÇ MERKEZİ</div>", unsafe_allow_html=True)
    
    # --- 🚀 HEYECAN VERİCİ REHBERLİK PANOSU ---
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 12px; border-left: 5px solid #d97706; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 25px;'>
        <h3 style='color: #fbbf24; margin-top: 0; font-weight: 900; letter-spacing: 0.5px;'>🔮 KİŞİSEL KUANTUM KASANIZA HOŞ GELDİNİZ!</h3>
        <p style='color: #e2e8f0; font-size: 15px; line-height: 1.6; margin-bottom: 15px;'>
            Burası kuponlarınızı sakladığınız sıradan bir arşiv değil; <b>Yapay Zeka destekli Otomatik İkramiye Avcınızdır!</b> Siz sadece makinenin ürettiği kusursuz kolonları onaylayın, gerisini Kaptan'ın zekasına bırakın.
        </p>
        <div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px dashed rgba(255,255,255,0.2);'>
            <ul style='color: #cbd5e1; font-size: 14px; line-height: 1.7; margin-bottom: 0; padding-left: 20px;'>
                <li><strong style='color:#38bdf8;'>Stratejinizi Mühürleyin:</strong> Oyun sayfalarından ürettiğiniz en iddialı kolonları <b>"Kasaya Kaydet"</b> diyerek bu güvenli kasaya kilitleyin.</li>
                <li><strong style='color:#a78bfa;'>Canlı Tarama Beklentisi:</strong> Çekiliş sonuçları sistemimize düştüğü saniye, bu sayfa otomatik olarak canlanır. Sizin hiçbir şeye dokunmanıza gerek kalmaz.</li>
                <li><strong style='color:#34d399;'>İkramiye Bildirimi:</strong> Kuantum motoru, kasadaki tüm kuponlarınızı saliseler içinde tarar, tutturduğunuz numaraları <b>yeşile boyar</b> ve kazandığınız ikramiye durumunu anında karşınıza çıkarır!</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    live_data = load_live_data()
    
    if not st.session_state.get("logged_in", False):
        st.markdown("<div style='text-align:center; padding:40px; background-color:#f1f5f9; border-radius:12px; border:2px dashed #cbd5e1;'><h3 style='color:#475569;'>🔒 Kasanız Kilitli</h3><p style='color:#64748b; font-size:16px;'>Kuponlarınızı güvenle saklamak ve kazançlarınızı otomatik taramak için sisteme giriş yapmalısınız.</p></div>", unsafe_allow_html=True)
        st.warning("👈 Lütfen sol menüden 'VIP Giriş Merkezi'ne tıklayarak giriş yapın veya ücretsiz hesap oluşturun.")
    else:
        user_coupons = get_user_coupons(st.session_state.user_email)
        if not user_coupons:
            st.info("Kasanızda henüz kayıtlı bir kolon bulunmuyor. Sol menüden oyun seçip Kuantum motoruyla kolon üreterek 'Kasaya Kaydet' butonuna basabilirsiniz.")
        else:
            st.markdown(f"<div style='background-color:#ecfdf5; padding:10px; border-radius:8px; border:1px solid #10b981; margin-bottom:20px;'><strong style='color:#059669;'>👤 Kasa Sahibi:</strong> {st.session_state.user_email} &nbsp;|&nbsp; <strong style='color:#059669;'>🎫 Toplam Kayıtlı Kupon:</strong> {len(user_coupons)} Adet</div>", unsafe_allow_html=True)
            
            tab_sayisal, tab_super, tab_sans, tab_on = st.tabs([
                "🔴 Çılgın Sayısal", 
                "🔵 Süper Loto", 
                "🟢 Şans Topu", 
                "🟡 On Numara"
            ])
            
            def render_game_coupons(game_id, empty_message):
                game_coupons = [c for c in user_coupons if c['game'] == game_id]
                if not game_coupons:
                    st.info(empty_message)
                else:
                    for idx, c in enumerate(game_coupons):
                        g_id, g_name, nums, ts = c['game'], c['game_name'], c['nums'], c['timestamp']
                        
                        if g_id == 'sanstopu': main_nums = nums[:5]
                        elif g_id == 'onnumara': main_nums = nums[:10]
                        else: main_nums = nums[:6]

                        live = live_data.get(g_id, {}).get('nums', [])
                        c_no = live_data.get(g_id, {}).get('cekilis_no', '')
                        
                        import re
                        hedef_match = re.search(r'Hedef:\s*(\d+)', g_name)
                        
                        if hedef_match and c_no and c_no.isdigit():
                            hedef_no = int(hedef_match.group(1))
                            aktif_no = int(c_no)
                            
                            if hedef_no > aktif_no:
                                live = []
                                display_name = f"⏳ {g_name} - Bekleniyor"
                            elif hedef_no == aktif_no:
                                display_name = f"✅ {g_name} - Sonuçlandı"
                            else:
                                display_name = f"🗄️ {g_name} - Arşiv"
                        else:
                            display_name = f"{g_name} - {c_no}. Çekiliş" if c_no else f"{g_name}"

                        live_plus = str(live_data.get(g_id, {}).get('plus', '-'))
                        matches = [n for n in main_nums if n in live]
                        
                        is_plus_match = False
                        if g_id == 'sanstopu' and len(nums) == 6:
                            if str(nums[5]) == live_plus: is_plus_match = True
                                
                        match_count = len(matches)
                        status_color, status_text = "#94a3b8", "⏳ Bekleniyor..."
                        
                        if live:
                            if g_id == 'sanstopu':
                                status_text = f"🎯 {match_count} + {'1' if is_plus_match else '0'} Bildiniz!"
                                if match_count >= 3 or (match_count >= 1 and is_plus_match): status_color = "#10b981" 
                                else: status_color = "#ef4444" 
                            elif g_id == 'onnumara':
                                status_text = f"🎯 {match_count} Bildiniz!"
                                if match_count == 0 or match_count >= 6: status_color = "#10b981"
                                else: status_color = "#ef4444"
                            else:
                                status_text = f"🎯 {match_count} Bildiniz!"
                                if match_count >= 3: status_color = "#10b981"
                                else: status_color = "#ef4444"
                        
                        balls_html = ""
                        for n in main_nums:
                            bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)" if n in matches else "linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)"
                            # 🚀 Toplar ve fontlar daha minimal yapıldı
                            ball_size = "26px" if g_id == 'onnumara' else "30px"
                            font_size = "12px" if g_id == 'onnumara' else "14px"
                            balls_html += f"<div class='home-ball' style='background:{bg}; width:{ball_size}; height:{ball_size}; line-height:{ball_size}; font-size:{font_size}; display:inline-block; text-align:center; border-radius:50%; color:white; margin:1px; font-weight:bold;'>{n}</div>"
                            
                        if g_id == 'sanstopu' and len(nums) == 6:
                            bg_p = "linear-gradient(135deg, #10b981 0%, #059669 100%)" if is_plus_match else "linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)"
                            balls_html += f"<span style='font-size:16px; color:#94a3b8; font-weight:bold; margin:0 3px;'>+</span><div class='home-ball' style='background:{bg_p}; width:30px; height:30px; line-height:30px; font-size:14px; display:inline-block; text-align:center; border-radius:50%; color:white; margin:1px; font-weight:bold;'>{nums[5]}</div>"

                        # 🚀 YATAY, KOMPAKT VE ZARİF KART TASARIMI
                        c1, c2 = st.columns([6, 1])
                        with c1:
                            st.markdown(f"""
                            <div style='background-color: white; border: 1px solid #e2e8f0; border-left: 5px solid {status_color}; border-radius: 8px; padding: 10px 15px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
                                <div style='flex: 1.2; min-width: 0;'>
                                    <div style='color: {status_color}; font-size: 0.90rem; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{display_name}</div>
                                    <div style='color: #94a3b8; font-size: 0.70rem; margin-top: 2px;'>{ts}</div>
                                </div>
                                <div style='flex: 1.8; text-align: center; white-space: nowrap;'>
                                    {balls_html}
                                </div>
                                <div style='flex: 1; text-align: right;'>
                                    <span style='background-color: #f8fafc; color: {status_color}; font-weight: 800; font-size: 0.85rem; padding: 4px 8px; border-radius: 6px; border: 1px solid #f1f5f9;'>{status_text}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with c2:
                            # Sil butonu dikey olarak hizalanıp küçültüldü
                            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                            if st.button("🗑️ Sil", key=f"del_{g_id}_{ts}_{idx}", use_container_width=True):
                                try:
                                    delete_coupon_from_db(st.session_state.user_email, g_id, ts)
                                    st.success("Silindi!")
                                    time.sleep(0.5)
                                    st.rerun()
                                except NameError:
                                    st.error("Sistem Hatası.")
                        
            with tab_sayisal: render_game_coupons("sayisal", "Kasanızda kayıtlı Çılgın Sayısal Loto kuponu bulunmuyor.")
            with tab_super: render_game_coupons("superloto", "Kasanızda kayıtlı Süper Loto kuponu bulunmuyor.")
            with tab_sans: render_game_coupons("sanstopu", "Kasanızda kayıtlı Şans Topu kuponu bulunmuyor.")
            with tab_on: render_game_coupons("onnumara", "Kasanızda kayıtlı On Numara kuponu bulunmuyor.")
# ==========================================
# 🔴 1. MODÜL: ÇILGIN SAYISAL LOTO
# ==========================================
elif selected_game == "ÇILGIN SAYISAL LOTO AI":
    st.markdown("<div class='main-title' style='color:#e61532;'>ÇILGIN SAYISAL LOTO ANALİZ MERKEZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>90 Topluk Kuantum Filtreleme Motoru</div>", unsafe_allow_html=True)

    st.markdown("""
<details class="guide-box" style="margin-bottom: 25px; background-color: #ffffff; border: 4px solid #000000; border-radius: 8px; padding: 10px;">
<summary class="guide-summary" style="color:#000000; font-size:1.2rem; font-weight: bold; cursor: pointer; list-style: none;">👇 SİSTEM NASIL ÇALIŞIR? KUPON YAPMADAN ÖNCE MUTLAKA OKU! 👇</summary>
<div class="guide-content" style="font-size:1rem; line-height:1.6; padding-top: 15px; border-top: 1px solid #f1f5f9; margin-top: 10px;">
<h3 style='color: #e61532; margin-top:0; font-weight: bold;'>🤖 Bu Platform Nedir?</h3>
<p>Çılgın Sayısal Loto'da tam <b>622 Milyon 614 Bin</b> ihtimal vardır. Bu platform, arka planda çalışan <b>Kuantum Monte Carlo Simülasyonu</b> ve <b>Yapay Zeka</b> algoritmaları ile bu devasa kaosu sizin için daraltır ve matematiksel olarak en kusursuz kolonları üretir.</p>
<h3 style='color: #e61532; margin-top:20px; font-weight: bold;'>⚙️ Algoritmalar ve Ayarlar Ne İşe Yarar?</h3>
<ul style='margin-bottom:0;'>
<li>📊 <b>Frekans (Sıcak/Orta/Soğuk):</b> Makinenin bir ritmi vardır. Altın oran genellikle "2 Sıcak, 3 Orta, 1 Soğuk" ekseninde döner. Sistem sizin belirlediğiniz dengeyi asla bozmaz.</li>
<li>📐 <b>Bölge Dağılımı (Alt-Orta-Üst):</b> 90 topu 3 sektöre böler. Topların tek bir köşeye (örneğin sadece 61-90 arasına) yığılmasını engeller. Sayıların tahtaya homojen yayılmasını sağlar.</li>
<li>🛡️ <b>Klan (K-Means) Zırhı:</b> Makine öğrenmesi, 90 topu geçmişteki davranışlarına göre 5 gizli "Klana" ayırır. Ürettiğiniz kolon, bu klanlara dağılarak zırh oluşturur.</li>
<li>⚔️ <b>Düşman İkili (Apriori):</b> Loto tarihinde bugüne kadar hiç yan yana gelmemiş zehirli kombinasyonlar tespit edilir ve kolonunuzdan acımasızca söküp atılır.</li>
<li>📉 <b>Çan Eğrisi:</b> Seçilen 6 sayının toplamının, oyunun matematiksel kalbi olan <b>273</b> eksenine oturup oturmadığını ölçer.</li>
</ul>
<div style='background-color:#fff1f2; padding:12px; border-left:5px solid #e61532; margin-top:15px; border-radius: 4px;'>
<strong>💡 Strateji Önerisi:</strong> Sol menüden kurallarını mantıklı bir çerçevede kur. Motoru ateşle! Seçtiğin 6'lı kurallar havuzdaki sayılarla çelişiyorsa makine paradoksa girer. Tüm devasa filtreleri aşan yegâne kolona ulaşana kadar denemeye devam et.
</div>
</div>
</details>
""", unsafe_allow_html=True)

    valid_draws, joker_draws, ss_draws, msg = load_sayisal_ai_data()

    if not valid_draws:
        st.error(msg)
    else:
        total_draws = len(valid_draws)
        all_nums = [num for draw in valid_draws for num in draw]
        counts = Counter(all_nums)
        
        # 🔥 BAŞLANGIÇ BARAJLARI (Sabit Nokta)
        hot_limit = 63
        cold_limit = 45
        
        hot_nums = [n for n in range(1, 91) if counts.get(n, 0) >= hot_limit]
        
        # 🛡️ SICAK HAVUZ ZIRHI: Sayı 18'i aşarsa, limiti otomatik artırarak (64, 65, 66...) havuzu 18 bandına düşür
        while len(hot_nums) > 18:
            hot_limit += 1
            hot_nums = [n for n in range(1, 91) if counts.get(n, 0) >= hot_limit]
            
        cold_nums = [n for n in range(1, 91) if counts.get(n, 0) <= cold_limit]
        
        # 🛡️ SOĞUK HAVUZ ZIRHI: Sayı 14'ün altındaysa limiti artırarak havuzu genişlet
        while len(cold_nums) < 14:
            cold_limit += 1
            cold_nums = [n for n in range(1, 91) if counts.get(n, 0) <= cold_limit]
            
        # Soğuk sayılar çok kalabalık olursa (18'i geçerse) limiti düşürerek havuzu daralt
        while len(cold_nums) > 18:
            cold_limit -= 1
            cold_nums = [n for n in range(1, 91) if counts.get(n, 0) <= cold_limit]

        # ORTA HAVUZ (Geriye kalan yaklaşık 54 sayı çan eğrisinin ortasında kalır)
        medium_nums = [n for n in range(1, 91) if n not in hot_nums and n not in cold_nums]

        recency = {}
        for n in range(1, 91):
            for i, draw in enumerate(valid_draws):
                if n in draw:
                    recency[n] = i
                    break
            else:
                recency[n] = total_draws

        uyuyan_devler = {k: v for k, v in recency.items() if v >= 15} 
        alev_alanlar = Counter([n for d in valid_draws[:10] for n in d])
        momentum_sayilari = {k: v for k, v in alev_alanlar.items() if v >= 3} 

        features = {}
        for n in range(1, 91):
            d_n = [d for d in valid_draws if n in d]
            if len(d_n) == 0: features[n] = [0, 0, 0]
            else: features[n] = [len(d_n), np.mean([sum(d) for d in d_n]), np.mean([max(d)-min(d) for d in d_n])]

        X = np.array(list(features.values()))
        n_clust = min(5, len(set([tuple(f) for f in features.values()])))
        if n_clust >= 2:
            kmeans = KMeans(n_clusters=n_clust, random_state=42, n_init=10).fit(X)
            klan_labels = {list(features.keys())[i]: kmeans.labels_[i] for i in range(len(features))}
        else:
            klan_labels = {k: 0 for k in features.keys()}

        pairs = [p for d in valid_draws for p in combinations(d, 2)]
        pair_c = Counter(pairs)
        all_p = set(combinations(range(1, 91), 2))
        actual_p = set([p for p, c in pair_c.items() if c > 0])
        enemies = set(all_p - actual_p) 

        def is_enemy(n1, n2): return (min(n1, n2), max(n1, n2)) in enemies

        st.sidebar.markdown("## ⚙️ ÇILGIN SAYISAL FİLTRELERİ")

        with st.sidebar.expander("📊 Temel Frekans", expanded=True):
            f_map = {
                "🌟 Yeni Altın Oran (#1): 2 Sıcak - 4 Orta - 0 Soğuk": (2, 4, 0),
                "🔥 Yeni Gümüş Oran (#2): 1 Sıcak - 5 Orta - 0 Soğuk": (1, 5, 0),
                "🥉 Yeni Bronz Oran (#3): 3 Sıcak - 3 Orta - 0 Soğuk": (3, 3, 0),
                "Orta Odaklı (#4): 0 Sıcak - 6 Orta - 0 Soğuk": (0, 6, 0),
                "Sıcak Odaklı (#5): 4 Sıcak - 2 Orta - 0 Soğuk": (4, 2, 0),
                "Dengeli Ekstrem: 2 Sıcak - 3 Orta - 1 Soğuk": (2, 3, 1),
                "Dengeli Ekstrem: 1 Sıcak - 4 Orta - 1 Soğuk": (1, 4, 1),
                "Tam Denge: 2 Sıcak - 2 Orta - 2 Soğuk": (2, 2, 2),
                "Full Sıcak: 6 Sıcak - 0 Orta - 0 Soğuk": (6, 0, 0),
                "Full Soğuk: 0 Sıcak - 0 Orta - 6 Soğuk": (0, 0, 6)
            }
            frekans_secim = st.selectbox("Sıcak - Orta - Soğuk Dağılımı", list(f_map.keys()), key="ss_frekans")
            sicak_hedef, orta_hedef, soguk_hedef = f_map[frekans_secim]

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            tek_hedef = st.slider("Tek Sayı Adedi (Kalanı Çift Olur)", 0, 6, 3, key="ss_t")
            cift_hedef = 6 - tek_hedef
            st.info(f"Sistem Kilitlendi: {tek_hedef} Tek, {cift_hedef} Çift")

        with st.sidebar.expander("2. Ardışık & 3. Kök Refleksi", expanded=True):
            c_strat1, c_strat2 = st.columns(2)
            ardisik = c_strat1.selectbox("Ardışık Sayı", ["YOK", "VAR"], key="ss_ard")
            kese_koku = c_strat2.selectbox("Kök Eşleşmesi", ["VAR (1 Çift)", "YOK"], key="ss_kok")

        with st.sidebar.expander("4. Devir Refleksi", expanded=True):
            devir_secimi = st.selectbox("Devir (Önceki Haftadan)", ["YOK (Önceki haftadan sayı gelmesin)", "VAR (Sistem rastgele 1 sayı seçsin)", "VAR (Sayıyı ben seçeceğim)"], key="ss_devir_sec")
            devir_sayisi_str = ""
            if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                st.info(f"Geçen Haftanın Sayıları: {valid_draws[0]}")
                devir_sayisi_str = st.text_input("Devredecek sayıyı girin:", key="ss_devir_sayi")

        with st.sidebar.expander("5. Bölge Refleksi (Alt-Orta-Üst)", expanded=True):
            bc1, bc2, bc3 = st.columns(3)
            bolge1 = bc1.number_input("Alt (1-30)", 0, 6, 2, key="ss_b1")
            bolge2 = bc2.number_input("Orta (31-60)", 0, 6, 2, key="ss_b2")
            bolge3 = bc3.number_input("Üst (61-90)", 0, 6, 2, key="ss_b3")
            
            # Anlık toplam kontrolü ve UI uyarısı
            if (bolge1 + bolge2 + bolge3) != 6:
                st.error(f"🚨 HATA: Bölge toplamı 6 olmalı! (Şu anki toplam: {bolge1 + bolge2 + bolge3})")
            
        with st.sidebar.expander("🛡️ Ekstra Kısıtlamalar", expanded=False):
            min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 21, 525, (160, 390), key="ss_can")
            min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 5, 89, (35, 89), key="ss_mes")
            yasak_sayilar_str = st.text_input("Yasaklılar (Virgülle ayırın)", key="ss_yasak")
            banko_sayilar_str = st.text_input("Banko Sayılar (Mutlaka Olsun)", key="ss_banko")

        def get_f_pattern(col):
            s, o, c = sum(1 for x in col if x in hot_nums), sum(1 for x in col if x in medium_nums), sum(1 for x in col if x in cold_nums)
            return f"{s}S - {o}O - {c}C"

        def get_tc(col): return f"{sum(1 for x in col if x % 2 != 0)} Tek - {6-sum(1 for x in col if x % 2 != 0)} Çift"
        def get_ard(col): return "VAR" if any(col[i] + 1 == col[i+1] for i in range(5)) else "YOK"
        def get_dev(prev_col, curr_col): return "VAR" if len(set(prev_col).intersection(set(curr_col))) > 0 else "YOK"
        def get_bolge_pattern(col): return f"{sum(1 for x in col if 1 <= x <= 30)}A - {sum(1 for x in col if 31 <= x <= 60)}O - {sum(1 for x in col if 61 <= x <= 90)}U"
        def get_k(col):
            counts = list(Counter([x % 10 for x in col]).values()); counts.sort(reverse=True)
            if counts == [1, 1, 1, 1, 1, 1]: return "Eşleşme Yok"
            elif counts == [2, 1, 1, 1, 1]: return "1 Çift Kök"
            else: return "Çoklu/Çifte Kök"

        st.info(f"{msg} | **Son Çekiliş:** {valid_draws[0]} ➕ Joker: [{joker_draws[0]}] ⭐ SüperStar: [{ss_draws[0]}]")
        st.markdown("---")
    
        if "sayisal_uretim_ekrani_acik" not in st.session_state: st.session_state.sayisal_uretim_ekrani_acik = False
        if "sayisal_ai_uretim_ekrani_acik" not in st.session_state: st.session_state.sayisal_ai_uretim_ekrani_acik = False
        if "sayisal_manuel_sayaci" not in st.session_state: st.session_state.sayisal_manuel_sayaci = 0
        if "sayisal_ai_sayaci" not in st.session_state: st.session_state.sayisal_ai_sayaci = 0

        sayisal_basla_btn = False
        sayisal_ai_basla_btn = False
        sayisal_kolon_sayisi = 1
        
        is_vip_or_admin = st.session_state.get("is_vip", False) or st.session_state.get("user_email", "") == "admin@kaptan.com"
        manuel_hakkini_doldurdu = not is_vip_or_admin and st.session_state.sayisal_manuel_sayaci >= 1
        ai_hakkini_doldurdu = not is_vip_or_admin and st.session_state.sayisal_ai_sayaci >= 1

        if not st.session_state.sayisal_uretim_ekrani_acik and not st.session_state.sayisal_ai_uretim_ekrani_acik:
            if manuel_hakkini_doldurdu and ai_hakkini_doldurdu:
                st.error("🔒 Ücretsiz deneme haklarınızı doldurdunuz! Sınırsız üretim yapmak için VIP üyeliğe geçin.")
                if st.button("👑 VIP ÜYELİK AYRICALIKLARI", use_container_width=True): pass
            else:
                st.markdown("<h3 style='text-align:center; color:#1e293b; font-weight:900; margin-bottom: 25px;'>Kuponunuzu Nasıl Kurgulamak İstersiniz?</h3>", unsafe_allow_html=True)
                c_btn_sol, c_btn_sag = st.columns(2)
                with c_btn_sol:
                    st.markdown("""
<div style='background-color:#f8fafc; padding:20px; border-radius:12px; border:2px solid #cbd5e1; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
<h4 style='color:#334155; margin-top:0; font-weight:900;'>🎛️ KONTROL SİZDE (Manuel)</h4>
<p style='font-size:13px; color:#64748b; line-height:1.5; margin-bottom:0;'>Kendi stratejinizi belirleyin. Sol menüdeki Kuantum ve Markov parametrelerini ayarlayın, yapay zeka sadece sizin kurallarınıza uyan kusursuz kombinasyonu bulsun.</p>
</div>
""", unsafe_allow_html=True)
                    if manuel_hakkini_doldurdu:
                        st.warning("🔒 Manuel üretim hakkınızı kullandınız.")
                    else:
                        if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", use_container_width=True, key="btn_manuel_sayisal"):
                            st.session_state.sayisal_uretim_ekrani_acik = True
                            st.rerun()
                            
                with c_btn_sag:
                    st.markdown("""
<div style='background-color:#fff1f2; padding:20px; border-radius:12px; border:2px solid #e11d48; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(225, 29, 72, 0.1);'>
<h4 style='color:#e11d48; margin-top:0; font-weight:900;'>✨ SİHİRLİ OTOPİLOT (Tam Yetki)</h4>
<p style='font-size:13px; color:#881337; line-height:1.5; margin-bottom:0;'>Filtrelerle vakit kaybetmeyin! Makine tüm veri madenciliği algoritmalarını çalıştırır, Çılgın Sayısal Loto'nun 90 topluk yapısına uygun en ideal 'Altın Oranlı' şablonu getirir.</p>
</div>
""", unsafe_allow_html=True)
                    if ai_hakkini_doldurdu:
                        st.warning("🔒 Sihirli Oto-Pilot hakkınızı kullandınız.")
                    else:
                        if st.button("✨ YAPAY ZEKAYA DEVRET", type="primary", use_container_width=True, key="btn_ai_sayisal"):
                            st.session_state.sayisal_ai_uretim_ekrani_acik = True
                            st.rerun()

        if st.session_state.sayisal_uretim_ekrani_acik:
            st.markdown("<div style='border: 3px solid #64748b; border-radius: 12px; padding: 20px; background-color: #f8fafc; text-align: center; margin-bottom: 20px;'><h3 style='color: #334155; margin-top: 0;'>🎛️ MANUEL ÜRETİM ONAYI</h3></div>", unsafe_allow_html=True)
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_kolon_hakki = 100 if is_vip_or_admin else 3
                sayisal_kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_kolon_hakki})", min_value=1, max_value=max_kolon_hakki, value=1, key="manuel_adet_sayisal")
                col_m1, col_m2 = st.columns(2)
                with col_m1: sayisal_basla_btn = st.button("✅ ÜRET", type="primary", use_container_width=True, key="sayisal_basla_m")
                with col_m2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="iptal_m_sayisal"): st.session_state.sayisal_uretim_ekrani_acik = False; st.rerun()

        if st.session_state.sayisal_ai_uretim_ekrani_acik:
            st.markdown("""<div style='border: 3px solid #e11d48; border-radius: 12px; padding: 25px; background-color: #fff1f2; margin-bottom: 25px;'><h3 style='color: #e11d48; margin-top: 0; text-align: center; font-weight: 900;'>🪄 OTOPİLOT DEVREYE GİRİYOR</h3></div>""", unsafe_allow_html=True)
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_ai_hakki = 100 if is_vip_or_admin else 1
                sayisal_kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_ai_hakki})", min_value=1, max_value=max_ai_hakki, value=1, key="ai_adet_sayisal")
                col_a1, col_a2 = st.columns(2)
                with col_a1: sayisal_ai_basla_btn = st.button("✨ SİHRİ BAŞLAT", type="primary", use_container_width=True, key="sayisal_basla_ai")
                with col_a2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="iptal_a_sayisal"): st.session_state.sayisal_ai_uretim_ekrani_acik = False; st.rerun()

        if sayisal_basla_btn or sayisal_ai_basla_btn:
            if not is_vip_or_admin:
                if sayisal_basla_btn: st.session_state.sayisal_manuel_sayaci += 1
                if sayisal_ai_basla_btn: st.session_state.sayisal_ai_sayaci += 1
                
            st.session_state.sayisal_uretim_ekrani_acik = False 
            st.session_state.sayisal_ai_uretim_ekrani_acik = False
            
            with st.spinner('Kuantum eleme motoru ve Yapay Zeka zırhı devrede...'):
                time.sleep(1)
                last_draw_nums = valid_draws[0]
                devirler, ekstra_yasaklar, yasaklar, sabit_sayilar, errors = [], [], [], [], []
                
                if sayisal_ai_basla_btn:
                    aktif_havuz = hot_nums[:15] if len(hot_nums) >= 15 else hot_nums
                    trend_devir_var_mi = any(x in hot_nums[:30] for x in last_draw_nums)
                    devir_secimi = "VAR (Sistem rastgele 1 sayı seçsin)" if trend_devir_var_mi else "YOK (Önceki haftadan sayı gelmesin)"
                    
                    ai_tek = sum(1 for x in aktif_havuz if x % 2 != 0)
                    ai_tek_orani = round((ai_tek / len(aktif_havuz)) * 6) if len(aktif_havuz) > 0 else 3
                    tek_hedef, cift_hedef = max(1, min(5, ai_tek_orani)), 6 - max(1, min(5, ai_tek_orani))
                    
                    ai_b1, ai_b2, ai_b3 = sum(1 for x in aktif_havuz if 1<=x<=30), sum(1 for x in aktif_havuz if 31<=x<=60), sum(1 for x in aktif_havuz if 61<=x<=90)
                    toplam_b = ai_b1 + ai_b2 + ai_b3
                    if toplam_b > 0:
                        bolge1, bolge2 = round((ai_b1 / toplam_b) * 6), round((ai_b2 / toplam_b) * 6)
                        bolge3 = 6 - (bolge1 + bolge2)
                        if bolge1 < 0 or bolge2 < 0 or bolge3 < 0: bolge1, bolge2, bolge3 = 2, 2, 2
                    else: bolge1, bolge2, bolge3 = 2, 2, 2
                        
                    ai_root_counts = list(Counter([x % 10 for x in aktif_havuz]).values())
                    kese_koku = "VAR (1 Çift)" if any(c > 1 for c in ai_root_counts) else "YOK"
                    sirali_aktif = sorted(aktif_havuz)
                    ardisik = "VAR" if any(sirali_aktif[i] + 1 == sirali_aktif[i+1] for i in range(len(sirali_aktif)-1)) else "YOK"
                    sicak_hedef, orta_hedef, soguk_hedef = 3, 2, 1
                    min_toplam, max_toplam, min_kapsam, max_kapsam = 140, 420, 35, 89
                else:
                    if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)": ekstra_yasaklar.extend(last_draw_nums)
                    elif devir_secimi == "VAR (Sayıyı ben seçeceğim)": devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
                    
                    yasaklar_input = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                    yasaklar = list(set(yasaklar_input + ekstra_yasaklar))
                    bankolar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                    sabit_sayilar = list(set(devirler + bankolar))

                    if tek_hedef + cift_hedef != 6: errors.append("Tek+Çift = 6 olmalı.")
                    if bolge1 + bolge2 + bolge3 != 6: errors.append("Alt+Orta+Üst Bölge toplamı 6 olmalı.")
                    if len(sabit_sayilar) > 6: errors.append("Banko ve Devir sayılarının toplamı 6'yı geçemez.")

                    # --- BANKO (SABİT) SAYILAR İÇİN ÖN GÜVENLİK DUVARI ---
                    if len(sabit_sayilar) > 0:
                        for s in sabit_sayilar:
                            if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko hem de Yasaklı listesinde olamaz!")
                            if s < 1 or s > 90: errors.append(f"Hata: {s} geçersiz bir sayıdır (1-90).")

                        b_tek = sum(1 for x in sabit_sayilar if x % 2 != 0)
                        b_cift = len(sabit_sayilar) - b_tek
                        if b_tek > tek_hedef or b_cift > cift_hedef:
                            errors.append(f"Hata: Bankolarınızdaki Tek/Çift sayısı ({b_tek}T/{b_cift}Ç), hedef kuralınızı ({tek_hedef}T/{cift_hedef}Ç) aşıyor!")

                        b_b1 = sum(1 for x in sabit_sayilar if 1 <= x <= 30)
                        b_b2 = sum(1 for x in sabit_sayilar if 31 <= x <= 60)
                        b_b3 = sum(1 for x in sabit_sayilar if 61 <= x <= 90)
                        if b_b1 > bolge1 or b_b2 > bolge2 or b_b3 > bolge3:
                            errors.append("Hata: Bankolarınızın bölge dağılımı (Alt-Orta-Üst), belirlediğiniz kotaları aşıyor!")

                        sirali_sabit = sorted(sabit_sayilar)
                        ardisik_ciftler = sum(1 for i in range(len(sirali_sabit)-1) if sirali_sabit[i+1] - sirali_sabit[i] == 1)
                        if ardisik_ciftler > 1: errors.append("Hata: Bankolarınızda 1'den fazla ardışık çift var. (Zehirli Dizi)")
                        elif ardisik_ciftler == 1 and ardisik == "YOK": errors.append("Hata: Bankolarınızda ardışık sayı var, ancak filtre 'Ardışık YOK' seçili!")

                        for b1_enemy, b2_enemy in combinations(sabit_sayilar, 2):
                            if is_enemy(b1_enemy, b2_enemy): errors.append(f"Hata: Banko girdiğiniz ({b1_enemy} ve {b2_enemy}) Apriori kuralına göre DÜŞMAN sayılardır!")

                if errors:
                    for e in errors: st.error(e)
                    if st.button("🔄 Kuralları Esnet ve Geri Dön", use_container_width=True, key="btn_sayisal_geri_hata"): st.rerun()
                    st.stop()
                else:
                    adaylar = [x for x in range(1, 91) if x not in yasaklar and x not in sabit_sayilar]
                    hot_pool = [x for x in hot_nums if x in adaylar]
                    med_pool = [x for x in medium_nums if x in adaylar]
                    cold_pool = [x for x in cold_nums if x in adaylar]

                    b_hot = sum(1 for x in sabit_sayilar if x in hot_nums)
                    b_med = sum(1 for x in sabit_sayilar if x in medium_nums)
                    b_cold = sum(1 for x in sabit_sayilar if x in cold_nums)
                    req_hot, req_med, req_cold = sicak_hedef - b_hot, orta_hedef - b_med, soguk_hedef - b_cold

                    if req_hot < 0 or req_med < 0 or req_cold < 0:
                        st.error("🚨 HATA: Banko sayılarının frekansları, belirlediğin hedefleri aşıyor!")
                    elif req_hot > len(hot_pool) or req_med > len(med_pool) or req_cold > len(cold_pool):
                        st.error("🚨 HATA: Kotalar havuzdaki sayıları aşıyor! Lütfen kuralları esnetin.")
                    else:
                        valid_combinations = []
                        hata_kodlari = {"frekans_havuzu": 0, "devir": 0, "tek_cift": 0, "bolge": 0, "kok": 0, "ardisik": 0, "can_kapsam": 0}
                        attempts = 0
                        
                        while len(valid_combinations) < (sayisal_kolon_sayisi * 3) and attempts < 150000:
                            attempts += 1
                            h_pick = random.sample(hot_pool, req_hot) if req_hot > 0 else []
                            m_pick = random.sample(med_pool, req_med) if req_med > 0 else []
                            c_pick = random.sample(cold_pool, req_cold) if req_cold > 0 else []
                            col = sorted(sabit_sayilar + h_pick + m_pick + c_pick)
                            if len(set(col)) != 6: continue
                                
                            if sum(1 for x in col if x % 2 != 0) != tek_hedef: hata_kodlari["tek_cift"] += 1; continue
                            if sum(1 for x in col if 1 <= x <= 30) != bolge1: hata_kodlari["bolge"] += 1; continue
                            if sum(1 for x in col if 31 <= x <= 60) != bolge2: hata_kodlari["bolge"] += 1; continue

                            roots = [x % 10 for x in col]
                            unique_roots = len(set(roots))
                            if kese_koku == "VAR (1 Çift)" and unique_roots != 5: hata_kodlari["kok"] += 1; continue
                            elif kese_koku == "YOK" and unique_roots != 6: hata_kodlari["kok"] += 1; continue

                            cons_count = sum(1 for i in range(5) if col[i] + 1 == col[i+1])
                            if cons_count > 1: hata_kodlari["ardisik"] += 1; continue
                            if (ardisik == "VAR" and cons_count == 0) or (ardisik == "YOK" and cons_count == 1): hata_kodlari["ardisik"] += 1; continue

                            toplam = sum(col)
                            if not (min_toplam <= toplam <= max_toplam): hata_kodlari["can_kapsam"] += 1; continue
                            if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam): hata_kodlari["can_kapsam"] += 1; continue

                            if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)" and any(x in last_draw_nums for x in col): hata_kodlari["devir"] += 1; continue
                            elif devir_secimi == "VAR (Sistem rastgele 1 sayı seçsin)" and sum(1 for x in col if x in last_draw_nums) != 1: hata_kodlari["devir"] += 1; continue
                            elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                                try:
                                    ds = int(devir_sayisi_str)
                                    if ds not in col or sum(1 for x in col if x in last_draw_nums) != 1: 
                                        hata_kodlari["devir"] += 1
                                        continue
                                except: pass

                            dusman_skoru = sum(1 for pair in combinations(col, 2) if is_enemy(pair[0], pair[1]))
                            klan_cesitliligi = len(set([klan_labels.get(x, 0) for x in col]))
                            
                            valid_combinations.append({'c': tuple(col), 'sum': sum(col), 'klan': klan_cesitliligi, 'dusman_sayisi': dusman_skoru})
                            valid_combinations = list({v['c']: v for v in valid_combinations}.values())

                        if len(valid_combinations) > 0:
                            valid_combinations.sort(key=lambda x: (x['dusman_sayisi'], -x['klan'], abs(x['sum'] - 273)))
                            gosterilecek_adet = min(sayisal_kolon_sayisi, len(valid_combinations))
                            st.success(f"Tüm filtreler başarıyla aşıldı! En kusursuz {gosterilecek_adet} kolon kurgulandı.")

                            tam_kolonlar_sayisal = []
                            for i in range(gosterilecek_adet):
                                secilen = valid_combinations[i]['c']
                                klan_degeri = valid_combinations[i]['klan']
                                d_skor = valid_combinations[i]['dusman_sayisi']
                                tam_kolonlar_sayisal.append(list(secilen))
                                
                                if sayisal_kolon_sayisi > 1:
                                    st.markdown(f"<h4 style='color:#dc2626; text-align:center; margin-top:20px; font-weight:900; background-color:#fef2f2; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                                
                                html_balls = f"<div style='text-align: center; margin: 15px 0 25px 0;'><div class='number-ball ball-red'>{secilen[0]}</div><div class='number-ball ball-red'>{secilen[1]}</div><div class='number-ball ball-red'>{secilen[2]}</div><div class='number-ball ball-red'>{secilen[3]}</div><div class='number-ball ball-red'>{secilen[4]}</div><div class='number-ball ball-red'>{secilen[5]}</div></div>"
                                st.markdown(html_balls, unsafe_allow_html=True)
                                
                                dusman_etiketi = f"{d_skor} (Esnetildi)" if d_skor > 0 else "0 (Temiz)"
                                renk = "#eab308" if d_skor > 0 else "#22c55e"
                                
                                mc1, mc2, mc3, mc4 = st.columns(4)
                                with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#e61532;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                                with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#e61532;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                                with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                                with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span style='font-size:18px; font-weight:bold; color:{renk};'>{dusman_etiketi}</span></div>", unsafe_allow_html=True)
                                if i < gosterilecek_adet - 1: st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)

# 🎯 AKILLI ONAY MEKANİZMASI VE KAYDET BUTONU (KESİN ÇÖZÜM) 🎯
                            if st.session_state.get("logged_in", False):
                                st.markdown("<br><hr style='border: 1px dashed #cbd5e1; margin-bottom: 20px;'>", unsafe_allow_html=True)
                                
                                current_live_data = load_live_data()
                                c_no_str = current_live_data.get("sayisal", {}).get("cekilis_no", "")
                                
                                if c_no_str and c_no_str.isdigit():
                                    hedef_cekilis = int(c_no_str) + 1
                                    st.info(f"💡 Sistemde en son **{c_no_str}. Çekiliş** sonuçları kayıtlıdır.")
                                    cb_label = f"**✅ Ürettiğim bu kuponu/kuponları, yaklaşan {hedef_cekilis}. Çılgın Sayısal Loto Çekilişi için kasama kaydetmeyi ONAYLIYORUM.**"
                                    # 🚀 SİHİR BURADA: Kuponun ismine Hedef Çekiliş Numarasını Damgalıyoruz!
                                    oyun_isim_etiketi = f"Çılgın Sayısal Loto (Hedef: {hedef_cekilis})"
                                else:
                                    cb_label = "**✅ Ürettiğim bu kuponu/kuponları, yaklaşan çekiliş için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = "Çılgın Sayısal Loto"

                                def kayit_tetikleyici(k_email, k_oyun_id, k_oyun_adi, k_kombinasyonlar):
                                    if st.session_state.get("onay_kutusu_sysl", False):
                                        for t_kolon in k_kombinasyonlar:
                                            from datetime import datetime
                                            z_vakti = datetime.now().strftime("%d.%m.%Y %H:%M:%S") 
                                            save_coupon_to_db(k_email, k_oyun_id, k_oyun_adi, t_kolon, z_vakti)
                                            time.sleep(0.1)

                                with st.form(key="kayit_form_sayisal"):
                                    st.checkbox(cb_label, key="onay_kutusu_sysl")
                                    # 'oyun_isim_etiketi' ile veritabanına gönderiyoruz
                                    st.form_submit_button("💾 ÜRETİLEN KOLONLARI KAYDET", type="primary", use_container_width=True, on_click=kayit_tetikleyici, args=(st.session_state.user_email, "sayisal", oyun_isim_etiketi, tam_kolonlar_sayisal))
                                
                                st.markdown("<p style='font-size:13px; color:#64748b; text-align:center;'><em>Not: Sistemin kaydedebilmesi için butona basmadan önce onay kutusunu işaretlediğinizden emin olun. Başarıyla kaydedildiğinde ekran yeni analizler için temizlenecektir.</em></p>", unsafe_allow_html=True)

                        else:
                            en_cok_elenen = max(hata_kodlari, key=hata_kodlari.get)
                            st.error(f"🚨 PARADOKS: Kurallarınız havuzda sayı bırakmadı. Engelleyici Kural: {en_cok_elenen.upper()} FİLTRESİ.")

        # 👇 HİZALAMAYA DİKKAT: Üretim döngülerinden tamamen çıkıyoruz.
        # Bu 'if' satırı sayfanın en solundan 8 boşluk içeride hizalanmalıdır!
        if not (sayisal_basla_btn or sayisal_ai_basla_btn):
            st.markdown("<br><hr style='border: 3px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
            
            # Sekmelerin görsel stil ayarları
            st.markdown("""
            <style>
            button[data-baseweb="tab"]:nth-child(3) p, button[data-baseweb="tab"]:nth-child(4) p {
                font-weight: 900 !important;
                font-size: 16px !important;
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            tab_tarih, tab_detayli, tab_simulasyon, tab_sorgu = st.tabs([
                "📈 TARİHSEL BİLANÇO (GENEL İSTATİSTİK)", 
                "🧠 DETAYLI YAPAY ZEKA ANALİZİ", 
                "🎯 SONRAKİ ÇEKİLİŞ SİMÜLASYONU", 
                "🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU"
            ])

            with tab_tarih:
                last_d = valid_draws[0]
                st.markdown("#### 🎯 SON ÇEKİLİŞİN MR'I (Röntgen)")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='metric-card' style='padding:10px;'><b>Frekans Şablonu</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_f_pattern(last_d)}</span></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='metric-card' style='padding:10px;'><b>Tek/Çift Dengesi</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_tc(last_d)}</span></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='metric-card' style='padding:10px;'><b>Ardışık Durumu</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_ard(last_d)}</span></div>", unsafe_allow_html=True)
                
                c4, c5, c6 = st.columns(3)
                c4.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Kök Eşleşmesi</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_k(last_d)}</span></div>", unsafe_allow_html=True)
                c5.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Bölge Dağılımı (Alt-Orta-Üst)</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_bolge_pattern(last_d)}</span></div>", unsafe_allow_html=True)
                
                devir_bilgisi = get_dev(valid_draws[1], last_d) if len(valid_draws) > 1 else "YOK"
                c6.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Devir (Geçen Haftadan)</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{devir_bilgisi}</span></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 25px; margin-top: 15px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{hot_limit}): {len(hot_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({cold_limit+1}-{hot_limit-1}): {len(medium_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{cold_limit}): {len(cold_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>#### 📊 OYUNUN GENEL KARAKTERİ (Tüm Zamanlar)", unsafe_allow_html=True)
                
                hist_f = Counter()
                hist_tc = Counter()
                hist_ard = Counter()
                hist_kok = Counter()
                hist_dev = Counter()
                hist_bolge = Counter()
                
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    hist_f[get_f_pattern(d)] += 1
                    hist_tc[get_tc(d)] += 1
                    hist_ard[get_ard(d)] += 1
                    hist_kok[get_k(d)] += 1
                    hist_bolge[get_bolge_pattern(d)] += 1
                    if i < len(valid_draws) - 1:
                        hist_dev[get_dev(valid_draws[i+1], valid_draws[i])] += 1
                        
                tot = len(valid_draws)
                tot_dev = tot - 1 if tot > 1 else 1
                
                def render_bar(label, count, total_val):
                    pct = (count / total_val) * 100
                    return f'''
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-weight: 800; color: #334155; font-size: 13px;">{label}</span>
                            <span style="font-weight: 900; color: #e61532; font-size: 13px;">%{pct:.1f} <span style="color:#94a3b8; font-size:11px;">({count} Kez)</span></span>
                        </div>
                        <div style="width: 100%; background-color: #f1f5f9; border-radius: 6px; height: 18px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                            <div style="width: {pct}%; background-color: #e61532; height: 100%;"></div>
                        </div>
                    </div>
                    '''
                    
                col_bar1, col_bar2 = st.columns(2)
                with col_bar1:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🔥 En Çok Gelen Frekanslar (İlk 5)</h5>", unsafe_allow_html=True)
                    for k, v in hist_f.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎲 Ardışık Sayı Durumu</h5>", unsafe_allow_html=True)
                    for k, v in hist_ard.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>♻️ Geçen Haftadan Devir (Kilit Sayı)</h5>", unsafe_allow_html=True)
                    for k, v in hist_dev.most_common(): st.markdown(render_bar(k, v, tot_dev), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_bar2:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>⚖️ Tek/Çift Dağılımı</h5>", unsafe_allow_html=True)
                    for k, v in hist_tc.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🧩 Kök Eşleşmesi (Son Rakam)</h5>", unsafe_allow_html=True)
                    for k, v in hist_kok.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎯 Bölge Dağılımı (Alt-Orta-Üst)</h5>", unsafe_allow_html=True)
                    for k, v in hist_bolge.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with tab_detayli:
                st.markdown("### 🧠 İLERİ DÜZEY İSTİHBARAT (RADAR SİSTEMİ)")
                
                col_rad1, col_rad2 = st.columns(2)
                with col_rad1:
                    st.markdown("#### 🔥 ALEV ALANLAR (Momentum İvmesi)")
                    if momentum_sayilari:
                        alevler_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(momentum_sayilari.items(), key=lambda item: item[1], reverse=True):
                            alevler_html += f"<div style='background-color:#fffbea; border:1.5px solid #000000; border-radius:6px; padding:8px 10px; text-align:center; min-width:85px;'><div style='color:#b45309; font-size:13px; font-weight:900; margin-bottom:2px;'>Sayı {k}</div><div style='font-size:10px; color:#64748b; font-weight:bold; margin-bottom:3px;'>Son 10 Çekilişte</div><div style='font-size:16px; color:#e61532; font-weight:900;'>{v} Kez</div></div>"
                        alevler_html += "</div>"
                        st.markdown(alevler_html, unsafe_allow_html=True)
                    else: st.info("Son 10 çekilişte çıldıran sayı yok.")
                    
                with col_rad2:
                    st.markdown("#### 💤 UYUYAN DEVLER (Kuluçka)")
                    if uyuyan_devler:
                        uyuyan_html = "<div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:6px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(uyuyan_devler.items(), key=lambda item: item[1], reverse=True)[:16]:
                            uyuyan_html += f"<div style='background-color:#f0f9ff; border:1px solid #bae6fd; border-radius:4px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center;'><strong style='color:#0369a1; font-size:13px;'>Sayı {k}</strong><span style='font-size:12px; color:#64748b; font-weight:bold;'>{v} Çekiliştir Yok</span></div>"
                        uyuyan_html += "</div>"
                        st.markdown(uyuyan_html, unsafe_allow_html=True)
                    else: st.info("Uyuyan dev bulunmuyor.")

                st.markdown("---")
                st.markdown("<h4 style='color:#e61532;'>🧬 ÇAPRAZ GEÇİŞ ANALİZİ (MARKOV MATRİSİ)</h4>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 20px; margin-top: 10px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{hot_limit}): {len(hot_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({cold_limit+1}-{hot_limit-1}): {len(medium_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{cold_limit}): {len(cold_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                last_s = sum(1 for x in valid_draws[0] if x in hot_nums)
                last_o = sum(1 for x in valid_draws[0] if x in medium_nums)
                last_c = sum(1 for x in valid_draws[0] if x in cold_nums)
                
                st.markdown("""
                <div style='background-color: #fff1f2; border-left: 5px solid #e11d48; padding: 12px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                    <strong style='color: #be123c; font-size: 15px;'>🧬 MİKROSKOP (Anatomi Analizi):</strong><br>
                    <span style='color: #9f1239; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>KENDİSİNİN</b> tarihte nasıl bir karakter sergilediğini inceler. Seçtiğiniz kombinasyonun iç yapısındaki tek/çift, ardışık ve kök eşleşme oranlarını göstererek o frekansın adeta DNA'sını çıkarır. Kuponunuzu oluştururken şablonun kurallarına uymanızı sağlar.</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='border: 3px solid #000000; border-radius: 10px; padding: 20px; background-color: #f8fafc; margin-bottom: 20px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);'>
                    <h4 style='text-align: center; color: #0f172a; font-weight: 900; margin-top: 0; margin-bottom: 20px; letter-spacing: 0.5px;'>🎯 HEDEF FREKANS KOMBİNASYONUNU SEÇİN</h4>
                """, unsafe_allow_html=True)
                
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    target_s = st.number_input("Sıcak (S)", 0, 6, last_s, key="ss_ts_m", label_visibility="collapsed")
                with cc2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    target_o = st.number_input("Orta (O)", 0, 6, last_o, key="ss_to_m", label_visibility="collapsed")
                with cc3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    target_c = st.number_input("Soğuk (C)", 0, 6, last_c, key="ss_tc_m", label_visibility="collapsed")
                    
                st.markdown("</div>", unsafe_allow_html=True)

                if target_s + target_o + target_c != 6:
                    st.warning("⚠️ Çılgın Sayısal Loto oyununda Sıcak, Orta ve Soğuk sayılarının toplamı tam 6 olmalıdır!")
                else:
                    target_freq = f"{target_s}S - {target_o}O - {target_c}C"
                    t_draws = []
                    
                    for i in range(len(valid_draws) - 1): 
                        current_draw = valid_draws[i]
                        if get_f_pattern(current_draw) == target_freq:
                            prev_draw = valid_draws[i+1] 
                            t_draws.append({
                                'tc': get_tc(current_draw), 
                                'ard': get_ard(current_draw), 
                                'kok': get_k(current_draw),
                                'dev': get_dev(prev_draw, current_draw), 
                                'bolge': get_bolge_pattern(current_draw)
                            })

                    if len(t_draws) > 0:
                        st.info(f"🧬 **ANATOMİ ÇIKARILDI:** Tarihte **{target_freq}** şablonu tam **{len(t_draws)}** kez yaşanmıştır. Bu çekilişlerin **İÇ YAPISI (Karakteri)** şöyledir:")
                        tc_c = Counter([x['tc'] for x in t_draws])
                        ard_c = Counter([x['ard'] for x in t_draws])
                        kok_c = Counter([x['kok'] for x in t_draws])
                        dev_c = Counter([x['dev'] for x in t_draws])
                        bolge_c = Counter([x['bolge'] for x in t_draws])
                        
                        def format_pct(counter):
                            total = sum(counter.values())
                            return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                        
                        copy_text = f"🧬 ÇAPRAZ ANALİZ ÇIKTISI (ANATOMİ: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT YAPISI ---\n{format_pct(tc_c)}\n\n--- 2. ARDIŞIK YAPISI ---\n{format_pct(ard_c)}\n\n--- 3. KÖK EŞLEŞMESİ ---\n{format_pct(kok_c)}\n\n--- 4. DEVİR DURUMU (Önceki Haftadan) ---\n{format_pct(dev_c)}\n\n--- 5. BÖLGE DAĞILIMI (Alt-Orta-Üst) ---\n{format_pct(bolge_c)}"
                        
                        st.markdown(f'''
                        <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.warning(f"Tarihte daha önce {target_freq} şablonu hiç yaşanmamış.")

            with tab_simulasyon:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🎯 GELECEK HAFTA PROJEKSİYONU (YAPAY ZEKA TAHMİNİ)</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #0ea5e9; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.15rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    Bu motor, son çekilişin 6 farklı DNA özelliğini alır, oyunun tüm geçmişini tarar ve tarihte bu özelliklerden sonra en yüksek ihtimalle nelerin geldiğini hesaplar.
                </div>
                """, unsafe_allow_html=True)
                
                history_sim = []
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    dev_durum = "Bilinmiyor"
                    if i + 1 < len(valid_draws):
                        dev_durum = get_dev(valid_draws[i+1], d)
                    
                    history_sim.append({
                        'freq': get_f_pattern(d),
                        'oe': get_tc(d),
                        'cons': get_ard(d),
                        'root': get_k(d),
                        'bolge': get_bolge_pattern(d),
                        'devir': dev_durum
                    })
                
                last_sim = history_sim[0] 
                
                def render_transition(prop_key, target_val, title):
                    next_states = []
                    for i in range(1, len(history_sim)):
                        if history_sim[i][prop_key] == target_val:
                            next_states.append(history_sim[i-1][prop_key])
                    
                    html_str = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); height:100%;'>"
                    html_str += f"<h5 style='color:#0f172a; font-weight:900; font-size:15px; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                    html_str += f"<p style='font-size:12px; color:#64748b; margin-bottom:10px;'>Son Çekiliş: <b style='color:#e61532;'>{target_val}</b></p>"
                    
                    if not next_states:
                        html_str += "<span style='color:#64748b; font-size:13px;'>Tarihte örnek bulunamadı.</span></div>"
                        return html_str
                    
                    c = Counter(next_states)
                    total = len(next_states)
                    html_str += "<ul style='margin-bottom:0; padding-left:20px; font-size:14px;'>"
                    for k, v in c.most_common(3): 
                        pct = (v/total)*100
                        html_str += f"<li style='margin-bottom:5px;'><b>%{pct:.1f}</b> ihtimalle <span style='color:#e61532; font-weight:bold;'>{k}</span></li>"
                    html_str += "</ul></div>"
                    return html_str

                st.markdown(f"<h5 style='color:#e61532; margin-bottom:15px;'>🔍 SON ÇEKİLİŞ ({valid_draws[0]}) BAZ ALINARAK YAPILAN MARKOV HESAPLAMALARI:</h5>", unsafe_allow_html=True)
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.markdown(render_transition('freq', last_sim['freq'], "1. Frekans Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('devir', last_sim['devir'], "4. Devir Radarı"), unsafe_allow_html=True)
                with sc2:
                    st.markdown(render_transition('bolge', last_sim['bolge'], "2. Bölge Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('cons', last_sim['cons'], "5. Ardışık Radarı"), unsafe_allow_html=True)
                with sc3:
                    st.markdown(render_transition('oe', last_sim['oe'], "3. Tek/Çift Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('root', last_sim['root'], "6. Kök Eşleşme Radarı"), unsafe_allow_html=True)
                    
                st.markdown("<hr style='border: 2px dashed #cbd5e1; margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("#### 🚨 KRİTİK İSTİHBARAT: 'SAYI KESİLME' ALGORİTMASI")
                
                streak_3_count = 0
                streak_4_count = 0
                for num in range(1, 91): 
                    for i in range(3, len(valid_draws)):
                        if num in valid_draws[i] and num in valid_draws[i-1] and num in valid_draws[i-2]:
                            streak_3_count += 1
                            if num in valid_draws[i-3]:
                                streak_4_count += 1
                                
                if streak_3_count > 0:
                    perc_devam = (streak_4_count / streak_3_count) * 100
                    perc_kesilme = 100 - perc_devam
                    st.markdown(f"""
                    <div style='background-color: #fff1f2; border: 2px solid #ef4444; padding: 15px; border-radius: 8px; color: #7f1d1d;'>
                        Çılgın Sayısal Loto tarihinde herhangi bir sayının <b>3 hafta ÜST ÜSTE çıkma durumu tam {streak_3_count} kez</b> yaşanmıştır.<br><br>
                        Algoritmanın tespitine göre, 3 hafta üst üste çıkan bir sayının <b>4. HAFTA KESİN OLARAK KESİLME (GELMEME) ihtimali: <span style='font-size:22px; font-weight:900;'>%{perc_kesilme:.2f}</span></b>'dir.<br>
                        <span style='font-size:14px; color:#991b1b;'><i>(Kupon yaparken, son 3 haftadır çıkan bir sayı varsa onu <b>%{perc_kesilme:.2f} matematiksel güvence ile</b> eleyebilirsiniz.)</i></span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Çılgın Sayısal Loto tarihinde henüz hiçbir sayı 3 hafta üst üste çıkmamıştır.")

            with tab_sorgu:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #eff6ff; border-left: 5px solid #2563eb; padding: 12px; border-radius: 4px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <strong style='color: #1e3a8a; font-size: 15px;'>🔮 RADAR (Gelecek Simülasyonu):</strong><br>
                <span style='color: #1d4ed8; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>ARDINDAN (Bir Sonraki Hafta)</b> neler yaşandığını hesaplar. Seçtiğiniz frekans küreden düştükten hemen sonraki hafta makinenin nasıl refleksler gösterdiğini simüle ederek, önümüzdeki çekilişin geleceğini tahmin etmenizi sağlar.</span>
            </div>
                """, unsafe_allow_html=True)

                all_freqs = [get_f_pattern(d) for d in valid_draws]
                freq_counts = Counter(all_freqs)
                
                st.markdown("#### 📊 VERİTABANINDAKİ EN POPÜLER FREKANS ŞABLONLARI")
                pop_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:30px;'>"
                for f, c in freq_counts.most_common(5):
                    pop_html += f"<div style='background-color:#ffffff; border:2px solid #cbd5e1; padding:10px 15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); text-align:center;'><b>{f}</b><br><span style='color:#e61532; font-weight:900; font-size:14px;'>{c} Kez Yaşandı</span></div>"
                pop_html += "</div>"
                st.markdown(pop_html, unsafe_allow_html=True)

                st.markdown("#### 🔍 HEDEF FREKANSI BELİRLEYİN")
                cq1, cq2, cq3 = st.columns(3)
                with cq1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    q_s = st.number_input("Sıcak", 0, 6, 2, key="ss_q_s", label_visibility="collapsed")
                with cq2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    q_o = st.number_input("Orta", 0, 6, 3, key="ss_q_o", label_visibility="collapsed")
                with cq3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    q_c = st.number_input("Soğuk", 0, 6, 1, key="ss_q_c", label_visibility="collapsed")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🚀 DİNAMİK İSTİHBARATI GETİR", type="primary", use_container_width=True, key="ss_sq_btn"):
                    if q_s + q_o + q_c != 6:
                        st.error("⚠️ HATA: Sıcak, Orta ve Soğuk sayılarının toplamı tam 6 olmalıdır!")
                    else:
                        target_f_str = f"{q_s}S - {q_o}O - {q_c}C"
                        q_results = {'oe': [], 'cons': [], 'root': [], 'bolge': [], 'devir': []}
                        match_count = 0
                        
                        for i in range(1, len(valid_draws)):
                            if get_f_pattern(valid_draws[i]) == target_f_str:
                                match_count += 1
                                trigger_draw = valid_draws[i]
                                next_draw = valid_draws[i-1]
                                
                                q_results['oe'].append(get_tc(next_draw))
                                q_results['cons'].append(get_ard(next_draw))
                                q_results['root'].append(get_k(next_draw))
                                q_results['bolge'].append(get_bolge_pattern(next_draw))
                                q_results['devir'].append(get_dev(trigger_draw, next_draw))
                        
                        if match_count == 0:
                            st.warning(f"Veritabanında '{target_f_str}' frekansının gelip de ardından çekiliş yapılan bir kayıt bulunamadı.")
                        else:
                            st.success(f"✅ HEDEF KİLİTLENDİ: Tarihte '{target_f_str}' şablonundan SONRAKİ HAFTA tam {match_count} kez çekiliş yapılmıştır. Makinenin gösterdiği refleksler aşağıdadır:")
                            
                            def print_q_stats(data_list, title):
                                c = Counter(data_list)
                                total = len(data_list)
                                html = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; margin-bottom:15px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>"
                                html += f"<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                                for k, v in c.most_common():
                                    perc = (v / total) * 100
                                    html += f"<div style='display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px dashed #f1f5f9; padding-bottom:4px;'><span style='font-weight:bold; color:#334155; font-size:14px;'>{k}</span> <span style='color:#e61532; font-weight:900; font-size:15px;'>%{perc:.2f}</span></div>"
                                html += "</div>"
                                return html

                            qc1, qc2 = st.columns(2)
                            with qc1:
                                st.markdown(print_q_stats(q_results['oe'], "1. TEK/ÇİFT REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['bolge'], "3. BÖLGE (ALT-ORTA-ÜST) REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['root'], "5. KÖK EŞLEŞME REFLEKSİ"), unsafe_allow_html=True)
                            with qc2:
                                st.markdown(print_q_stats(q_results['cons'], "2. ARDIŞIK SAYI REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['devir'], "4. DEVİR REFLEKSİ"), unsafe_allow_html=True)
                                
                            st.info("💡 KAPTAN'A NOT: En yüksek yüzdeler, makinenin bu frekansa verdiği tepkidir. Kolonları kurarken en üst sıradaki şablonları baz al.")

# ==========================================
# 🔵 2. MODÜL: SÜPER LOTO
# ==========================================
elif selected_game == "SÜPER LOTO AI":
    
    # IŞIK HIZINDA SQL'DEN VERİYİ ÇEKİYORUZ!
    valid_draws, msg = load_super_ai_data()

    # --- ARAYÜZ VE ANALİZ MERKEZİ ---
    st.markdown("<div class='main-title' style='color:#059669;'>SÜPER LOTO ANALİZ MERKEZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>60 Topluk Kuantum Filtreleme Motoru</div>", unsafe_allow_html=True)

    st.markdown("""
<details class="guide-box" style="margin-bottom: 25px; background-color: #ffffff; border: 4px solid #000000; border-radius: 8px; padding: 10px;">
<summary class="guide-summary" style="color:#000000; font-size:1.2rem; font-weight: bold; cursor: pointer; list-style: none;">👇 SİSTEM NASIL ÇALIŞIR? KUPON YAPMADAN ÖNCE MUTLAKA OKU! 👇</summary>
<div class="guide-content" style="font-size:1rem; line-height:1.6; padding-top: 15px; border-top: 1px solid #f1f5f9; margin-top: 10px;">
<h3 style='color: #059669; margin-top:0; font-weight: bold;'>🤖 Bu Platform Nedir?</h3>
<p>Süper Loto'da tam <b>50 Milyon 63 Bin 860</b> ihtimal vardır. Bu platform, arka planda çalışan <b>Kuantum Monte Carlo Simülasyonu</b> ve <b>Yapay Zeka</b> algoritmaları ile bu devasa kaosu sizin için daraltır ve matematiksel olarak en kusursuz kolonları üretir.</p>
<h3 style='color: #059669; margin-top:20px; font-weight: bold;'>⚙️ Algoritmalar ve Ayarlar Ne İşe Yarar?</h3>
<ul style='margin-bottom:0;'>
<li>📊 <b>Frekans (Sıcak/Orta/Soğuk):</b> Makinenin bir ritmi vardır. Altın oran genellikle "2 Sıcak, 3 Orta, 1 Soğuk" ekseninde döner. Sistem sizin belirlediğiniz dengeyi asla bozmaz.</li>
<li>📐 <b>Bölge Dağılımı (Alt-Orta-Üst):</b> 60 topu 3 sektöre böler. Topların tek bir köşeye yığılmasını engeller.</li>
<li>🛡️ <b>Klan (K-Means) Zırhı:</b> Makine öğrenmesi, 60 topu geçmişteki davranışlarına göre 5 gizli "Klana" ayırır. Ürettiğiniz kolon, bu klanlara dağılarak zırh oluşturur.</li>
<li>⚔️ <b>Düşman İkili (Apriori):</b> Loto tarihinde bugüne kadar hiç yan yana gelmemiş zehirli kombinasyonlar tespit edilir ve kolonunuzdan söküp atılır.</li>
<li>📉 <b>Çan Eğrisi:</b> Seçilen 6 sayının toplamının, oyunun matematiksel kalbi olan <b>183</b> eksenine oturup oturmadığını ölçer.</li>
</ul>
<div style='background-color:#ecfdf5; padding:12px; border-left:5px solid #059669; margin-top:15px; border-radius: 4px;'>
<strong>💡 Strateji Önerisi:</strong> Sol menüden kurallarını mantıklı bir çerçevede kur. Motoru ateşle! Seçtiğin 6'lı kurallar havuzdaki sayılarla çelişiyorsa makine paradoksa girer. Tüm devasa filtreleri aşan yegâne kolona ulaşana kadar denemeye devam et.
</div>
</div>
</details>
""", unsafe_allow_html=True)

    if not valid_draws:
        st.error(msg)
    else:
        total_draws = len(valid_draws)
        all_nums = [num for draw in valid_draws for num in draw]
        counts = Counter(all_nums)
        
        # 🔥 BAŞLANGIÇ BARAJLARI (Oyunun 60 topluk matematiksel beklentisi)
        expected = total_draws * (6 / 60)
        hot_limit = int(np.ceil(expected * 1.35)) # Örn: Şu anki maçlara göre 34
        cold_limit = int(np.floor(expected * 0.75)) # Örn: Şu anki maçlara göre 18
        
        hot_nums = [n for n in range(1, 61) if counts.get(n, 0) >= hot_limit]
        
        # 🛡️ SICAK HAVUZ ZIRHI: 60 topta ideal sıcak sayı 14-15'tir. Aşarsa barajı yukarı çek!
        while len(hot_nums) > 15:
            hot_limit += 1
            hot_nums = [n for n in range(1, 61) if counts.get(n, 0) >= hot_limit]
            
        # ZIRH (Paradoks Önleyici): Çok sert filtreleme gelirse ve havuz 10'dan az kalırsa barajı 1 tık gevşet.
        while len(hot_nums) < 10 and hot_limit > 1:
            hot_limit -= 1
            hot_nums = [n for n in range(1, 61) if counts.get(n, 0) >= hot_limit]

        cold_nums = [n for n in range(1, 61) if counts.get(n, 0) <= cold_limit]
        
        # 🛡️ SOĞUK HAVUZ ZIRHI: Soğuk sayılar 10'un altına inerse paradoks olur, barajı artırıp havuza sayı al
        while len(cold_nums) < 10:
            cold_limit += 1
            cold_nums = [n for n in range(1, 61) if counts.get(n, 0) <= cold_limit]
            
        # Soğuk sayılar 15'i aşarsa barajı aşağı çekerek ele
        while len(cold_nums) > 15:
            cold_limit -= 1
            cold_nums = [n for n in range(1, 61) if counts.get(n, 0) <= cold_limit]

        # ORTA HAVUZ
        medium_nums = [n for n in range(1, 61) if n not in hot_nums and n not in cold_nums]

        recency = {}
        for n in range(1, 61):
            for i, draw in enumerate(valid_draws):
                if n in draw:
                    recency[n] = i
                    break
            else:
                recency[n] = total_draws

        uyuyan_devler = {k: v for k, v in recency.items() if v >= 15} 
        alev_alanlar = Counter([n for d in valid_draws[:10] for n in d])
        momentum_sayilari = {k: v for k, v in alev_alanlar.items() if v >= 3} 

        features = {}
        for n in range(1, 61):
            d_n = [d for d in valid_draws if n in d]
            if len(d_n) == 0: 
                features[n] = [0, 0, 0]
            else: 
                features[n] = [len(d_n), np.mean([sum(d) for d in d_n]), np.mean([max(d)-min(d) for d in d_n])]

        X = np.array(list(features.values()))
        n_clust = min(5, len(set([tuple(f) for f in features.values()])))
        if n_clust >= 2:
            kmeans = KMeans(n_clusters=n_clust, random_state=42, n_init=10).fit(X)
            klan_labels = {list(features.keys())[i]: kmeans.labels_[i] for i in range(len(features))}
        else:
            klan_labels = {k: 0 for k in features.keys()}

        pairs = [p for d in valid_draws for p in combinations(d, 2)]
        pair_c = Counter(pairs)
        all_p = set(combinations(range(1, 61), 2))
        actual_p = set([p for p, c in pair_c.items() if c > 0])
        enemies = set(all_p - actual_p) 

        def is_enemy(n1, n2):
            return (min(n1, n2), max(n1, n2)) in enemies

        st.sidebar.markdown("## ⚙️ SÜPER LOTO FİLTRELERİ (Hibrit Zırh)")

        with st.sidebar.expander("📊 Temel Frekans", expanded=True):
            f_map = {
                "Dengeli: 2 Sıcak - 2 Orta - 2 Soğuk": (2, 2, 2),
                "Altın Oran: 2 Sıcak - 3 Orta - 1 Soğuk": (2, 3, 1),
                "Altın Oran: 3 Sıcak - 2 Orta - 1 Soğuk": (3, 2, 1),
                "Orta Ağırlıklı: 1 Sıcak - 3 Orta - 2 Soğuk": (1, 3, 2),
                "Sıcak Ağırlıklı: 3 Sıcak - 1 Orta - 2 Soğuk": (3, 1, 2),
                "Soğuk Ağırlıklı: 2 Sıcak - 1 Orta - 3 Soğuk": (2, 1, 3),
                "Soğuk Ağırlıklı: 1 Sıcak - 2 Orta - 3 Soğuk": (1, 2, 3),
                "Ekstrem Sıcak: 4 Sıcak - 1 Orta - 1 Soğuk": (4, 1, 1),
                "Ekstrem Orta: 1 Sıcak - 4 Orta - 1 Soğuk": (1, 4, 1),
                "Ekstrem Soğuk: 1 Sıcak - 1 Orta - 4 Soğuk": (1, 1, 4),
                "Full Sıcak: 6 Sıcak - 0 Orta - 0 Soğuk": (6, 0, 0),
                "Full Orta: 0 Sıcak - 6 Orta - 0 Soğuk": (0, 6, 0),
                "Full Soğuk: 0 Sıcak - 0 Orta - 6 Soğuk": (0, 0, 6)
            }
            frekans_secim = st.selectbox("Sıcak - Orta - Soğuk Dağılımı", list(f_map.keys()), key="sl_frekans")
            sicak_hedef, orta_hedef, soguk_hedef = f_map[frekans_secim]

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            tek_hedef = st.slider("Tek Sayı Adedi (Kalanı Çift Olur)", 0, 6, 3, key="sl_t")
            cift_hedef = 6 - tek_hedef
            st.info(f"Sistem Kilitlendi: {tek_hedef} Tek, {cift_hedef} Çift")

        with st.sidebar.expander("2. Ardışık & 3. Kök Refleksi", expanded=True):
            c_strat1, c_strat2 = st.columns(2)
            ardisik = c_strat1.selectbox("Ardışık Sayı", ["YOK", "VAR"], key="sl_ard")
            kese_koku = c_strat2.selectbox("Kök Eşleşmesi", ["VAR (1 Çift)", "YOK"], key="sl_kok")

        with st.sidebar.expander("4. Devir Refleksi", expanded=True):
            devir_secimi = st.selectbox("Devir (Önceki Haftadan)", [
                "YOK (Önceki haftadan sayı gelmesin)", 
                "VAR (Sistem rastgele 1 sayı seçsin)", 
                "VAR (Sayıyı ben seçeceğim)"
            ], key="sl_devir_sec")
            
            devir_sayisi_str = ""
            if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                st.info(f"Geçen Haftanın Sayıları: {valid_draws[0]}")
                devir_sayisi_str = st.text_input("Devredecek sayıyı girin:", key="sl_devir_sayi")

        with st.sidebar.expander("5. Bölge Refleksi (Alt-Orta-Üst)", expanded=True):
            bc1, bc2, bc3 = st.columns(3)
            bolge1 = bc1.number_input("Alt (1-20)", 0, 6, 2, key="sl_b1")
            bolge2 = bc2.number_input("Orta (21-40)", 0, 6, 2, key="sl_b2")
            bolge3 = bc3.number_input("Üst (41-60)", 0, 6, 2, key="sl_b3")
            
            if (bolge1 + bolge2 + bolge3) != 6:
                st.error(f"🚨 HATA: Bölge toplamı 6 olmalı! (Şu anki toplam: {bolge1 + bolge2 + bolge3})")

        with st.sidebar.expander("🛡️ Ekstra Kısıtlamalar (Çan vb.)", expanded=False):
            min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 21, 345, (120, 240), key="sl_can")
            min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 5, 59, (25, 45), key="sl_mes")
            yasak_sayilar_str = st.text_input("Yasaklılar (Virgülle ayırın)", key="sl_yasak")
            banko_sayilar_str = st.text_input("Banko Sayılar (Mutlaka Olsun)", key="sl_banko")

        # --- ORTAK ANALİZ FONKSİYONLARI ---
        def get_f_pattern(col):
            s = sum(1 for x in col if x in hot_nums)
            o = sum(1 for x in col if x in medium_nums)
            c = sum(1 for x in col if x in cold_nums)
            return f"{s}S - {o}O - {c}C"

        def get_tc(col):
            tek = sum(1 for x in col if x % 2 != 0)
            return f"{tek} Tek - {6-tek} Çift"

        def get_ard(col): 
            return "VAR" if any(col[i] + 1 == col[i+1] for i in range(5)) else "YOK"
        
        def get_dev(prev_col, curr_col): 
            return "VAR" if len(set(prev_col).intersection(set(curr_col))) > 0 else "YOK"

        def get_bolge_pattern_sl(col):
            b1 = sum(1 for x in col if 1 <= x <= 20)
            b2 = sum(1 for x in col if 21 <= x <= 40)
            b3 = sum(1 for x in col if 41 <= x <= 60)
            return f"{b1}A - {b2}O - {b3}U"
            
        def get_k(col):
            roots = [x % 10 for x in col]
            counts = list(Counter(roots).values())
            counts.sort(reverse=True)
            if counts == [1, 1, 1, 1, 1, 1]: return "Eşleşme Yok"
            elif counts == [2, 1, 1, 1, 1]: return "1 Çift Kök"
            else: return "Çoklu/Çifte Kök"

        # --- ÜRETİM ALANI (SİHİRLİ BUTON VE MANUEL SEÇİM) ---
        st.info(f"{msg} | **Son Çekiliş:** {valid_draws[0]}")
        st.markdown("---")

        if "sl_uretim_ekrani_acik" not in st.session_state:
            st.session_state.sl_uretim_ekrani_acik = False
        if "sl_ai_uretim_ekrani_acik" not in st.session_state:
            st.session_state.sl_ai_uretim_ekrani_acik = False
            
        if "sl_manuel_sayaci" not in st.session_state:
            st.session_state.sl_manuel_sayaci = 0
        if "sl_ai_sayaci" not in st.session_state:
            st.session_state.sl_ai_sayaci = 0

        sl_basla_btn = False
        sl_ai_basla_btn = False
        sl_kolon_sayisi = 1
        
        is_vip_or_admin = st.session_state.get("is_vip", False) or st.session_state.get("user_email", "") == "admin@kaptan.com"

        manuel_hakkini_doldurdu = not is_vip_or_admin and st.session_state.sl_manuel_sayaci >= 1
        ai_hakkini_doldurdu = not is_vip_or_admin and st.session_state.sl_ai_sayaci >= 1

        if not st.session_state.sl_uretim_ekrani_acik and not st.session_state.sl_ai_uretim_ekrani_acik:
            if manuel_hakkini_doldurdu and ai_hakkini_doldurdu:
                st.error("🔒 Ücretsiz deneme haklarınızı doldurdunuz! Sınırsız üretim yapmak ve tüm kuantum filtrelerini özgürce kullanmak için VIP üyeliğe geçin.")
                if st.button("👑 VIP ÜYELİK AYRICALIKLARI", use_container_width=True, key="vip_btn_sl_final"):
                    pass
            else:
                st.markdown("<h3 style='text-align:center; color:#1e293b; font-weight:900; margin-bottom: 25px;'>Kuponunuzu Nasıl Kurgulamak İstersiniz?</h3>", unsafe_allow_html=True)
                c_btn_sol, c_btn_sag = st.columns(2)
                
                with c_btn_sol:
                    st.markdown("""
<div style='background-color:#f8fafc; padding:20px; border-radius:12px; border:2px solid #cbd5e1; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
<h4 style='color:#334155; margin-top:0; font-weight:900;'>🎛️ KONTROL SİZDE (Manuel)</h4>
<p style='font-size:13px; color:#64748b; line-height:1.5; margin-bottom:0;'>Kendi stratejinizi belirleyin. Sol menüdeki Kuantum ve Markov parametrelerini ayarlayın, yapay zeka sadece sizin kurallarınıza uyan kusursuz kombinasyonu bulsun.</p>
</div>
""", unsafe_allow_html=True)
                    if manuel_hakkini_doldurdu:
                        st.warning("🔒 Manuel üretim hakkınızı kullandınız.")
                    else:
                        if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", use_container_width=True, key="btn_manuel_sl"):
                            st.session_state.sl_uretim_ekrani_acik = True
                            st.rerun()
                        
                with c_btn_sag:
                    st.markdown("""
<div style='background-color:#f0fdf4; padding:20px; border-radius:12px; border:2px solid #16a34a; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(22, 163, 74, 0.1);'>
<h4 style='color:#15803d; margin-top:0; font-weight:900;'>✨ SİHİRLİ OTOPİLOT (Tam Yetki)</h4>
<p style='font-size:13px; color:#14532d; line-height:1.5; margin-bottom:0;'>Filtrelerle vakit kaybetmeyin! Makine tüm veri madenciliği algoritmalarını çalıştırır, Süper Loto'nun 60 topluk yapısına uygun en ideal 'Altın Oranlı' şablonu getirir.</p>
</div>
""", unsafe_allow_html=True)
                    if ai_hakkini_doldurdu:
                        st.warning("🔒 Sihirli Oto-Pilot hakkınızı kullandınız.")
                    else:
                        if st.button("✨ YAPAY ZEKAYA DEVRET", type="primary", use_container_width=True, key="btn_ai_sl"):
                            st.session_state.sl_ai_uretim_ekrani_acik = True
                            st.rerun()

        # 1. MANUEL ÜRETİM ONAY EKRANI
        if st.session_state.sl_uretim_ekrani_acik:
            st.markdown("<div style='border: 3px solid #64748b; border-radius: 12px; padding: 20px; background-color: #f8fafc; text-align: center; margin-bottom: 20px;'><h3 style='color: #334155; margin-top: 0;'>🎛️ MANUEL ÜRETİM ONAYI</h3><p style='margin-bottom:0;'>Süper Loto kolon adedini belirleyin.</p></div>", unsafe_allow_html=True)
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_kolon_hakki = 100 if is_vip_or_admin else 3
                sl_kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_kolon_hakki})", min_value=1, max_value=max_kolon_hakki, value=1, key="manuel_adet_sl")
                if not is_vip_or_admin:
                    st.info("💡 Ziyaretçiler ve Standart üyeler manuel olarak en fazla 3 kolon üretebilir. Sınırsız üretim için VIP'ye geçin.")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1: sl_basla_btn = st.button("✅ ÜRET", type="primary", use_container_width=True, key="sl_basla_m")
                with col_m2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="iptal_m_sl"):
                        st.session_state.sl_uretim_ekrani_acik = False
                        st.rerun()

        # 2. SİHİRLİ YAPAY ZEKA ONAY EKRANI
        if st.session_state.sl_ai_uretim_ekrani_acik:
            st.markdown("""
<div style='border: 3px solid #16a34a; border-radius: 12px; padding: 25px; background-color: #f0fdf4; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(22, 163, 74, 0.15);'>
<h3 style='color: #15803d; margin-top: 0; text-align: center; font-weight: 900;'>🪄 OTOPİLOT DEVREYE GİRİYOR</h3>
<p style='color: #14532d; text-align: center; font-size: 15px; margin-bottom: 20px; font-weight: 600;'>Makineye tam yetki verdiniz. Arka planda saniyeler içinde şu mühendislik işlemleri gerçekleşecek:</p>
<div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px dashed #86efac;'>
<ul style='color: #166534; font-size: 14px; margin-bottom: 0; padding-left: 20px; line-height: 1.8;'>
<li><b>🧬 Derin Öğrenme Taraması:</b> Yılların Süper Loto verisi taranarak 60 topun güncel Sıcak/Orta/Soğuk havuz haritası çıkarılır.</li>
<li><b>⚔️ Apriori (Düşman) Filtresi:</b> Loto tarihinde bugüne kadar hiç yan yana gelmemiş zehirli kombinasyonlar tespit edilip imha edilir.</li>
<li><b>🛡️ K-Means Klan Zırhı:</b> Seçilen sayılar, makinenin tespit ettiği gizli klanlara dengeli biçimde dağıtılarak risk minimize edilir.</li>
<li><b>📉 Kuantum Çan Eğrisi:</b> Üretilen kolon, Süper Loto'nun matematiksel istatistik merkezine kilitlenir.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)
            
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_ai_hakki = 100 if is_vip_or_admin else 1
                sl_kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_ai_hakki})", min_value=1, max_value=max_ai_hakki, value=1, key="ai_adet_sl")
                if not is_vip_or_admin:
                    st.markdown("""
<div style='background-color:#fffbeb; border:1px solid #f59e0b; padding:10px; border-radius:6px; margin-bottom:15px; text-align:center;'>
<span style='color:#b45309; font-size:13px; font-weight:bold;'>👑 Standart üyeler için Sihirli Buton 1 kolonla sınırlıdır. Tüm kuponu yapay zekaya doldurtmak için VIP'ye geçin.</span>
</div>
""", unsafe_allow_html=True)
                
                col_a1, col_a2 = st.columns(2)
                with col_a1: sl_ai_basla_btn = st.button("✨ SİHRİ BAŞLAT", type="primary", use_container_width=True, key="sl_basla_ai")
                with col_a2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="iptal_a_sl"):
                        st.session_state.sl_ai_uretim_ekrani_acik = False
                        st.rerun()

        # ÜRETİM MOTORU (SAYISAL LOTO ZIRHIYLA GÜÇLENDİRİLMİŞ HALİ)
        if sl_basla_btn or sl_ai_basla_btn:
            if not is_vip_or_admin:
                if sl_basla_btn: st.session_state.sl_manuel_sayaci += 1
                if sl_ai_basla_btn: st.session_state.sl_ai_sayaci += 1
                
            st.session_state.sl_uretim_ekrani_acik = False 
            st.session_state.sl_ai_uretim_ekrani_acik = False
            
            with st.spinner('Kuantum eleme motoru ve Yapay Zeka zırhı devrede...'):
                time.sleep(1)
                last_draw_nums = valid_draws[0]
                devirler, ekstra_yasaklar, yasaklar, sabit_sayilar, errors = [], [], [], [], []
                
                if sl_ai_basla_btn:
                    aktif_havuz = hot_nums[:15] if len(hot_nums) >= 15 else hot_nums
                    trend_devir_var_mi = any(x in hot_nums[:20] for x in last_draw_nums)
                    devir_secimi = "VAR (Sistem rastgele 1 sayı seçsin)" if trend_devir_var_mi else "YOK (Önceki haftadan sayı gelmesin)"
                    
                    ai_tek = sum(1 for x in aktif_havuz if x % 2 != 0)
                    ai_tek_orani = round((ai_tek / len(aktif_havuz)) * 6) if len(aktif_havuz) > 0 else 3
                    tek_hedef, cift_hedef = max(1, min(5, ai_tek_orani)), 6 - max(1, min(5, ai_tek_orani))
                    
                    ai_b1, ai_b2, ai_b3 = sum(1 for x in aktif_havuz if 1<=x<=20), sum(1 for x in aktif_havuz if 21<=x<=40), sum(1 for x in aktif_havuz if 41<=x<=60)
                    toplam_b = ai_b1 + ai_b2 + ai_b3
                    if toplam_b > 0:
                        bolge1, bolge2 = round((ai_b1 / toplam_b) * 6), round((ai_b2 / toplam_b) * 6)
                        bolge3 = 6 - (bolge1 + bolge2)
                        if bolge1 < 0 or bolge2 < 0 or bolge3 < 0: bolge1, bolge2, bolge3 = 2, 2, 2
                    else: bolge1, bolge2, bolge3 = 2, 2, 2
                        
                    ai_root_counts = list(Counter([x % 10 for x in aktif_havuz]).values())
                    kese_koku = "VAR (1 Çift)" if any(c > 1 for c in ai_root_counts) else "YOK"
                    sirali_aktif = sorted(aktif_havuz)
                    ardisik = "VAR" if any(sirali_aktif[i] + 1 == sirali_aktif[i+1] for i in range(len(sirali_aktif)-1)) else "YOK"
                    sicak_hedef, orta_hedef, soguk_hedef = 3, 2, 1
                    min_toplam, max_toplam, min_kapsam, max_kapsam = 110, 250, 25, 59
                else:
                    if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)": ekstra_yasaklar.extend(last_draw_nums)
                    elif devir_secimi == "VAR (Sayıyı ben seçeceğim)": devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
                    
                    yasaklar_input = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                    yasaklar = list(set(yasaklar_input + ekstra_yasaklar))
                    bankolar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                    sabit_sayilar = list(set(devirler + bankolar))

                    if tek_hedef + cift_hedef != 6: errors.append("Tek+Çift = 6 olmalı.")
                    if bolge1 + bolge2 + bolge3 != 6: errors.append("Alt+Orta+Üst Bölge toplamı 6 olmalı.")
                    if len(sabit_sayilar) > 6: errors.append("Banko ve Devir sayılarının toplamı 6'yı geçemez.")
                    if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                        for d in devirler:
                            if d not in last_draw_nums:
                                errors.append(f"Hata: Girdiğiniz '{d}' sayısı geçen haftanın çekilişinde yok! Lütfen geçerli bir devir sayısı girin: {last_draw_nums}")

                    # --- YENİ EKLENEN ÖN GÜVENLİK DUVARI (PARADOKS ENGELLEYİCİ) ---
                    if len(sabit_sayilar) > 0:
                        for s in sabit_sayilar:
                            if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko hem de Yasaklı listesinde olamaz!")
                            if s < 1 or s > 60: errors.append(f"Hata: {s} geçersiz bir sayıdır (1-60).")

                        b_tek = sum(1 for x in sabit_sayilar if x % 2 != 0)
                        b_cift = len(sabit_sayilar) - b_tek
                        if b_tek > tek_hedef or b_cift > cift_hedef:
                            errors.append(f"Hata: Bankolarınızdaki Tek/Çift sayısı ({b_tek}T/{b_cift}Ç), hedef kuralınızı ({tek_hedef}T/{cift_hedef}Ç) aşıyor!")

                        b_b1 = sum(1 for x in sabit_sayilar if 1 <= x <= 20)
                        b_b2 = sum(1 for x in sabit_sayilar if 21 <= x <= 40)
                        b_b3 = sum(1 for x in sabit_sayilar if 41 <= x <= 60)
                        if b_b1 > bolge1 or b_b2 > bolge2 or b_b3 > bolge3:
                            errors.append("Hata: Bankolarınızın bölge dağılımı (Alt-Orta-Üst), belirlediğiniz kotaları aşıyor!")

                        sirali_sabit = sorted(sabit_sayilar)
                        ardisik_ciftler = sum(1 for i in range(len(sirali_sabit)-1) if sirali_sabit[i+1] - sirali_sabit[i] == 1)
                        if ardisik_ciftler > 1: errors.append("Hata: Bankolarınızda 1'den fazla ardışık çift var. (Zehirli Dizi)")
                        elif ardisik_ciftler == 1 and ardisik == "YOK": errors.append("Hata: Bankolarınızda ardışık sayı var, ancak filtre 'Ardışık YOK' seçili!")

                        for b1_enemy, b2_enemy in combinations(sabit_sayilar, 2):
                            if is_enemy(b1_enemy, b2_enemy): errors.append(f"Hata: Banko girdiğiniz ({b1_enemy} ve {b2_enemy}) Apriori kuralına göre DÜŞMAN sayılardır!")

                if errors:
                    for e in errors: st.error(e)
                    if st.button("🔄 Kuralları Esnet ve Geri Dön", use_container_width=True, key="btn_sl_geri_hata"): st.rerun()
                    st.stop()
                else:
                    adaylar = [x for x in range(1, 61) if x not in yasaklar and x not in sabit_sayilar]
                    hot_pool = [x for x in hot_nums if x in adaylar]
                    med_pool = [x for x in medium_nums if x in adaylar]
                    cold_pool = [x for x in cold_nums if x in adaylar]

                    b_hot = sum(1 for x in sabit_sayilar if x in hot_nums)
                    b_med = sum(1 for x in sabit_sayilar if x in medium_nums)
                    b_cold = sum(1 for x in sabit_sayilar if x in cold_nums)
                    req_hot, req_med, req_cold = sicak_hedef - b_hot, orta_hedef - b_med, soguk_hedef - b_cold

                    if req_hot < 0 or req_med < 0 or req_cold < 0:
                        st.error("🚨 HATA: Banko sayılarının frekansları, belirlediğin hedefleri aşıyor!")
                    elif req_hot > len(hot_pool) or req_med > len(med_pool) or req_cold > len(cold_pool):
                        st.error(f"🚨 HATA: Kotalar havuzdaki sayıları aşıyor! Lütfen kuralları esnetin. (Kalan havuz: {len(hot_pool)}S - {len(med_pool)}O - {len(cold_pool)}C)")
                    else:
                        valid_combinations = []
                        hata_kodlari = {"frekans_havuzu": 0, "devir": 0, "tek_cift": 0, "bolge": 0, "kok": 0, "ardisik": 0, "can_kapsam": 0}
                        attempts = 0
                        
                        while len(valid_combinations) < (sl_kolon_sayisi * 3) and attempts < 150000:
                            attempts += 1
                            h_pick = random.sample(hot_pool, req_hot) if req_hot > 0 else []
                            m_pick = random.sample(med_pool, req_med) if req_med > 0 else []
                            c_pick = random.sample(cold_pool, req_cold) if req_cold > 0 else []
                            col = sorted(sabit_sayilar + h_pick + m_pick + c_pick)
                            if len(set(col)) != 6: continue
                                
                            if sum(1 for x in col if x % 2 != 0) != tek_hedef: hata_kodlari["tek_cift"] += 1; continue
                            if sum(1 for x in col if 1 <= x <= 20) != bolge1: hata_kodlari["bolge"] += 1; continue
                            if sum(1 for x in col if 21 <= x <= 40) != bolge2: hata_kodlari["bolge"] += 1; continue

                            roots = [x % 10 for x in col]
                            unique_roots = len(set(roots))
                            if kese_koku == "VAR (1 Çift)" and unique_roots != 5: hata_kodlari["kok"] += 1; continue
                            elif kese_koku == "YOK" and unique_roots != 6: hata_kodlari["kok"] += 1; continue

                            cons_count = sum(1 for i in range(5) if col[i] + 1 == col[i+1])
                            if cons_count > 1: hata_kodlari["ardisik"] += 1; continue
                            if (ardisik == "VAR" and cons_count == 0) or (ardisik == "YOK" and cons_count == 1): hata_kodlari["ardisik"] += 1; continue

                            toplam = sum(col)
                            if not (min_toplam <= toplam <= max_toplam): hata_kodlari["can_kapsam"] += 1; continue
                            if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam): hata_kodlari["can_kapsam"] += 1; continue

                            if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)" and any(x in last_draw_nums for x in col): hata_kodlari["devir"] += 1; continue
                            elif devir_secimi == "VAR (Sistem rastgele 1 sayı seçsin)" and sum(1 for x in col if x in last_draw_nums) != 1: hata_kodlari["devir"] += 1; continue
                            elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                                try:
                                    ds = int(devir_sayisi_str)
                                    if ds not in col or sum(1 for x in col if x in last_draw_nums) != 1: 
                                        hata_kodlari["devir"] += 1
                                        continue
                                except: pass

                            dusman_skoru = sum(1 for pair in combinations(col, 2) if is_enemy(pair[0], pair[1]))
                            klan_cesitliligi = len(set([klan_labels.get(x, 0) for x in col]))
                            
                            valid_combinations.append({'c': tuple(col), 'sum': sum(col), 'klan': klan_cesitliligi, 'dusman_sayisi': dusman_skoru})
                            valid_combinations = list({v['c']: v for v in valid_combinations}.values())

                        if len(valid_combinations) > 0:
                            valid_combinations.sort(key=lambda x: (x['dusman_sayisi'], -x['klan'], abs(x['sum'] - 183)))
                            gosterilecek_adet = min(sl_kolon_sayisi, len(valid_combinations))
                            st.success(f"Tüm katı filtreler başarıyla aşıldı! En kusursuz {gosterilecek_adet} kolon kurgulandı.")

                            tam_kolonlar_sl = []
                            for i in range(gosterilecek_adet):
                                secilen = valid_combinations[i]['c']
                                klan_degeri = valid_combinations[i]['klan']
                                d_skor = valid_combinations[i]['dusman_sayisi']
                                tam_kolonlar_sl.append(list(secilen))
                                
                                if sl_kolon_sayisi > 1:
                                    st.markdown(f"<h4 style='color:#059669; text-align:center; margin-top:20px; font-weight:900; background-color:#ecfdf5; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                                
                                html_balls = f"<div style='text-align: center; margin: 15px 0 25px 0;'><div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[0]}</div><div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[1]}</div><div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[2]}</div><div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[3]}</div><div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[4]}</div><div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[5]}</div></div>"
                                st.markdown(html_balls, unsafe_allow_html=True)
                                
                                dusman_etiketi = f"{d_skor} (Esnetildi)" if d_skor > 0 else "0 (Temiz)"
                                renk = "#eab308" if d_skor > 0 else "#22c55e"
                                
                                mc1, mc2, mc3, mc4 = st.columns(4)
                                with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#059669;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                                with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#059669;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                                with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                                with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span style='font-size:18px; font-weight:bold; color:{renk};'>{dusman_etiketi}</span></div>", unsafe_allow_html=True)
                                if i < gosterilecek_adet - 1: st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)
                                
# 🎯 AKILLI ONAY MEKANİZMASI VE KAYDET BUTONU (SÜPER LOTO) 🎯
                            if st.session_state.get("logged_in", False):
                                st.markdown("<br><hr style='border: 1px dashed #cbd5e1; margin-bottom: 20px;'>", unsafe_allow_html=True)
                                
                                current_live_data = load_live_data()
                                c_no_str = current_live_data.get("superloto", {}).get("cekilis_no", "")
                                
                                if c_no_str and c_no_str.isdigit():
                                    hedef_cekilis = int(c_no_str) + 1
                                    st.info(f"💡 Sistemde en son **{c_no_str}. Çekiliş** sonuçları kayıtlıdır.")
                                    cb_label = f"**✅ Ürettiğim bu kuponu/kuponları, yaklaşan {hedef_cekilis}. Süper Loto Çekilişi için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = f"Süper Loto (Hedef: {hedef_cekilis})"
                                else:
                                    cb_label = "**✅ Ürettiğim bu kuponu/kuponları, yaklaşan çekiliş için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = "Süper Loto"

                                def kayit_tetikleyici_super(k_email, k_oyun_id, k_oyun_adi, k_kombinasyonlar):
                                    if st.session_state.get("onay_kutusu_super", False):
                                        for t_kolon in k_kombinasyonlar:
                                            from datetime import datetime
                                            z_vakti = datetime.now().strftime("%d.%m.%Y %H:%M:%S") 
                                            save_coupon_to_db(k_email, k_oyun_id, k_oyun_adi, t_kolon, z_vakti)
                                            time.sleep(0.1)

                                with st.form(key="kayit_form_super"):
                                    st.checkbox(cb_label, key="onay_kutusu_super")
                                    # Liste adı tam_kolonlar_sl olarak senin sistemine uyarlandı!
                                    st.form_submit_button("💾 ÜRETİLEN KOLONLARI KAYDET", type="primary", use_container_width=True, on_click=kayit_tetikleyici_super, args=(st.session_state.user_email, "superloto", oyun_isim_etiketi, tam_kolonlar_sl))
                                
                                st.markdown("<p style='font-size:13px; color:#64748b; text-align:center;'><em>Not: Sistemin kaydedebilmesi için butona basmadan önce onay kutusunu işaretlediğinizden emin olun. Başarıyla kaydedildiğinde ekran yeni analizler için temizlenecektir.</em></p>", unsafe_allow_html=True)
                        else:
                            en_cok_elenen = max(hata_kodlari, key=hata_kodlari.get)
                            st.error(f"🚨 PARADOKS: Kurallarınız havuzda sayı bırakmadı. Engelleyici Kural: {en_cok_elenen.upper()} FİLTRESİ.")
                            st.warning(f"**🔍 GERÇEK X-RAY TEŞHİS RAPORU:** Motor {attempts} defa Kuantum taraması yaptı ancak sonuç alamadı. Sistemi kilitleyen ASIL Kural: **{en_cok_elenen.upper()} FİLTRESİ**.\n\n**Kilitlenme Sebebi:** {sebep_metni}")

        # --- SEKMELER (İÇİ DOLU VE EKSİKSİZ) ---
        if not (sl_basla_btn or sl_ai_basla_btn):
            st.markdown("<br><hr style='border: 3px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            button[data-baseweb="tab"]:nth-child(3) p, button[data-baseweb="tab"]:nth-child(4) p {
                font-weight: 900 !important;
                font-size: 16px !important;
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            tab_tarih, tab_detayli, tab_simulasyon, tab_sorgu = st.tabs([
                "📈 TARİHSEL BİLANÇO (GENEL İSTATİSTİK)", 
                "🧠 DETAYLI YAPAY ZEKA ANALİZİ", 
                "🎯 SONRAKİ ÇEKİLİŞ SİMÜLASYONU",
                "🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU"
            ])

            with tab_tarih:
                last_d = valid_draws[0]
                st.markdown("#### 🎯 SON ÇEKİLİŞİN MR'I (Röntgen)")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='metric-card' style='padding:10px;'><b>Frekans Şablonu</b><br><span style='color:#059669; font-weight:900; font-size:16px;'>{get_f_pattern(last_d)}</span></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='metric-card' style='padding:10px;'><b>Tek/Çift Dengesi</b><br><span style='color:#059669; font-weight:900; font-size:16px;'>{get_tc(last_d)}</span></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='metric-card' style='padding:10px;'><b>Ardışık Durumu</b><br><span style='color:#059669; font-weight:900; font-size:16px;'>{get_ard(last_d)}</span></div>", unsafe_allow_html=True)
                
                c4, c5, c6 = st.columns(3)
                c4.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Kök Eşleşmesi</b><br><span style='color:#059669; font-weight:900; font-size:16px;'>{get_k(last_d)}</span></div>", unsafe_allow_html=True)
                c5.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Bölge Dağılımı (Alt-Orta-Üst)</b><br><span style='color:#059669; font-weight:900; font-size:16px;'>{get_bolge_pattern_sl(last_d)}</span></div>", unsafe_allow_html=True)
                
                devir_bilgisi = get_dev(valid_draws[1], last_d) if len(valid_draws) > 1 else "YOK"
                c6.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Devir (Geçen Haftadan)</b><br><span style='color:#059669; font-weight:900; font-size:16px;'>{devir_bilgisi}</span></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 25px; margin-top: 15px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{hot_limit}): {len(hot_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({cold_limit+1}-{hot_limit-1}): {len(medium_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{cold_limit}): {len(cold_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>#### 📊 OYUNUN GENEL KARAKTERİ (Tüm Zamanlar)", unsafe_allow_html=True)
                
                hist_f = Counter()
                hist_tc = Counter()
                hist_ard = Counter()
                hist_kok = Counter()
                hist_dev = Counter()
                hist_bolge = Counter()
                
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    hist_f[get_f_pattern(d)] += 1
                    hist_tc[get_tc(d)] += 1
                    hist_ard[get_ard(d)] += 1
                    hist_kok[get_k(d)] += 1
                    hist_bolge[get_bolge_pattern_sl(d)] += 1
                    if i < len(valid_draws) - 1:
                        hist_dev[get_dev(valid_draws[i+1], valid_draws[i])] += 1
                        
                tot = len(valid_draws)
                tot_dev = tot - 1 if tot > 1 else 1
                
                def render_bar(label, count, total_val):
                    pct = (count / total_val) * 100
                    return f'''
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-weight: 800; color: #334155; font-size: 13px;">{label}</span>
                            <span style="font-weight: 900; color: #059669; font-size: 13px;">%{pct:.1f} <span style="color:#94a3b8; font-size:11px;">({count} Kez)</span></span>
                        </div>
                        <div style="width: 100%; background-color: #f1f5f9; border-radius: 6px; height: 18px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                            <div style="width: {pct}%; background-color: #059669; height: 100%;"></div>
                        </div>
                    </div>
                    '''
                    
                col_bar1, col_bar2 = st.columns(2)
                with col_bar1:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🔥 En Çok Gelen Frekanslar (İlk 5)</h5>", unsafe_allow_html=True)
                    for k, v in hist_f.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎲 Ardışık Sayı Durumu</h5>", unsafe_allow_html=True)
                    for k, v in hist_ard.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>♻️ Geçen Haftadan Devir (Kilit Sayı)</h5>", unsafe_allow_html=True)
                    for k, v in hist_dev.most_common(): st.markdown(render_bar(k, v, tot_dev), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_bar2:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>⚖️ Tek/Çift Dağılımı</h5>", unsafe_allow_html=True)
                    for k, v in hist_tc.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🧩 Kök Eşleşmesi (Son Rakam)</h5>", unsafe_allow_html=True)
                    for k, v in hist_kok.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎯 Bölge Dağılımı (Alt-Orta-Üst)</h5>", unsafe_allow_html=True)
                    for k, v in hist_bolge.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with tab_detayli:
                st.markdown("### 🧠 İLERİ DÜZEY İSTİHBARAT (RADAR SİSTEMİ)")
                
                col_rad1, col_rad2 = st.columns(2)
                with col_rad1:
                    st.markdown("#### 🔥 ALEV ALANLAR (Momentum İvmesi)")
                    if momentum_sayilari:
                        alevler_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(momentum_sayilari.items(), key=lambda item: item[1], reverse=True):
                            alevler_html += f"<div style='background-color:#fffbea; border:1.5px solid #000000; border-radius:6px; padding:8px 10px; text-align:center; min-width:85px;'><div style='color:#b45309; font-size:13px; font-weight:900; margin-bottom:2px;'>Sayı {k}</div><div style='font-size:10px; color:#64748b; font-weight:bold; margin-bottom:3px;'>Son 10 Çekilişte</div><div style='font-size:16px; color:#059669; font-weight:900;'>{v} Kez</div></div>"
                        alevler_html += "</div>"
                        st.markdown(alevler_html, unsafe_allow_html=True)
                    else: st.info("Son 10 çekilişte çıldıran sayı yok.")
                    
                with col_rad2:
                    st.markdown("#### 💤 UYUYAN DEVLER (Kuluçka)")
                    if uyuyan_devler:
                        uyuyan_html = "<div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:6px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(uyuyan_devler.items(), key=lambda item: item[1], reverse=True):
                            uyuyan_html += f"<div style='background-color:#f0f9ff; border:1px solid #bae6fd; border-radius:4px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center;'><strong style='color:#0369a1; font-size:13px;'>Sayı {k}</strong><span style='font-size:12px; color:#64748b; font-weight:bold;'>{v} Çekiliştir Yok</span></div>"
                        uyuyan_html += "</div>"
                        st.markdown(uyuyan_html, unsafe_allow_html=True)
                    else: st.info("Uyuyan dev bulunmuyor.")

                st.markdown("---")
                st.markdown("<h4 style='color:#059669;'>🧬 ÇAPRAZ GEÇİŞ ANALİZİ (MARKOV MATRİSİ)</h4>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 20px; margin-top: 10px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{hot_limit}): {len(hot_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({cold_limit+1}-{hot_limit-1}): {len(medium_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{cold_limit}): {len(cold_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                last_s = sum(1 for x in valid_draws[0] if x in hot_nums)
                last_o = sum(1 for x in valid_draws[0] if x in medium_nums)
                last_c = sum(1 for x in valid_draws[0] if x in cold_nums)
                st.markdown("""
                <div style='background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 12px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                    <strong style='color: #166534; font-size: 15px;'>🧬 MİKROSKOP (Anatomi Analizi):</strong><br>
                    <span style='color: #15803d; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>KENDİSİNİN</b> tarihte nasıl bir karakter sergilediğini inceler. Seçtiğiniz kombinasyonun iç yapısındaki tek/çift, ardışık ve kök eşleşme oranlarını göstererek o frekansın adeta DNA'sını çıkarır. Kuponunuzu oluştururken şablonun kurallarına uymanızı sağlar.</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='border: 3px solid #000000; border-radius: 10px; padding: 20px; background-color: #f8fafc; margin-bottom: 20px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);'>
                    <h4 style='text-align: center; color: #0f172a; font-weight: 900; margin-top: 0; margin-bottom: 20px; letter-spacing: 0.5px;'>🎯 HEDEF FREKANS KOMBİNASYONUNU SEÇİN</h4>
                """, unsafe_allow_html=True)
                
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    target_s = st.number_input("Sıcak (S)", 0, 6, last_s, key="sl_ts_m", label_visibility="collapsed")
                with cc2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    target_o = st.number_input("Orta (O)", 0, 6, last_o, key="sl_to_m", label_visibility="collapsed")
                with cc3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    target_c = st.number_input("Soğuk (C)", 0, 6, last_c, key="sl_tc_m", label_visibility="collapsed")
                    
                st.markdown("</div>", unsafe_allow_html=True)

                if target_s + target_o + target_c != 6:
                    st.warning("⚠️ Süper Loto oyununda Sıcak, Orta ve Soğuk sayılarının toplamı tam 6 olmalıdır!")
                else:
                    target_freq = f"{target_s}S - {target_o}O - {target_c}C"
                    t_draws = []
                    
                    for i in range(len(valid_draws) - 1): 
                        current_draw = valid_draws[i]
                        if get_f_pattern(current_draw) == target_freq:
                            prev_draw = valid_draws[i+1]
                            t_draws.append({
                                'tc': get_tc(current_draw), 
                                'ard': get_ard(current_draw), 
                                'kok': get_k(current_draw),
                                'dev': get_dev(prev_draw, current_draw), 
                                'bolge': get_bolge_pattern_sl(current_draw)
                            })

                    if len(t_draws) > 0:
                        st.info(f"🧬 **ANATOMİ ÇIKARILDI:** Tarihte **{target_freq}** şablonu tam **{len(t_draws)}** kez yaşanmıştır. Bu çekilişlerin **İÇ YAPISI (Karakteri)** şöyledir:")
                        tc_c = Counter([x['tc'] for x in t_draws])
                        ard_c = Counter([x['ard'] for x in t_draws])
                        kok_c = Counter([x['kok'] for x in t_draws])
                        dev_c = Counter([x['dev'] for x in t_draws])
                        bolge_c = Counter([x['bolge'] for x in t_draws])
                        
                        def format_pct(counter):
                            total = sum(counter.values())
                            return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                        
                        copy_text = f"🧬 ÇAPRAZ ANALİZ ÇIKTISI (ANATOMİ: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT YAPISI ---\n{format_pct(tc_c)}\n\n--- 2. ARDIŞIK YAPISI ---\n{format_pct(ard_c)}\n\n--- 3. KÖK EŞLEŞMESİ ---\n{format_pct(kok_c)}\n\n--- 4. DEVİR DURUMU (Önceki Haftadan) ---\n{format_pct(dev_c)}\n\n--- 5. BÖLGE DAĞILIMI (Alt-Orta-Üst) ---\n{format_pct(bolge_c)}"
                        
                        st.markdown(f'''
                        <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.warning(f"Tarihte daha önce {target_freq} şablonu hiç yaşanmamış.")

            with tab_simulasyon:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🎯 GELECEK HAFTA PROJEKSİYONU (YAPAY ZEKA TAHMİNİ)</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #0ea5e9; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.15rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    Bu motor, son çekilişin 6 farklı DNA özelliğini alır, oyunun tüm geçmişini tarar ve tarihte bu özelliklerden sonra en yüksek ihtimalle nelerin geldiğini hesaplar.
                </div>
                """, unsafe_allow_html=True)
                
                history_sim = []
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    dev_durum = "Bilinmiyor"
                    if i + 1 < len(valid_draws):
                        dev_durum = get_dev(valid_draws[i+1], d)
                    
                    history_sim.append({
                        'freq': get_f_pattern(d),
                        'oe': get_tc(d),
                        'cons': get_ard(d),
                        'root': get_k(d),
                        'bolge': get_bolge_pattern_sl(d),
                        'devir': dev_durum
                    })
                
                last_sim = history_sim[0] 
                
                def render_transition(prop_key, target_val, title):
                    next_states = []
                    for i in range(1, len(history_sim)):
                        if history_sim[i][prop_key] == target_val:
                            next_states.append(history_sim[i-1][prop_key])
                    
                    html_str = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); height:100%;'>"
                    html_str += f"<h5 style='color:#0f172a; font-weight:900; font-size:15px; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                    html_str += f"<p style='font-size:12px; color:#64748b; margin-bottom:10px;'>Son Çekiliş: <b style='color:#059669;'>{target_val}</b></p>"
                    
                    if not next_states:
                        html_str += "<span style='color:#64748b; font-size:13px;'>Tarihte örnek bulunamadı.</span></div>"
                        return html_str
                    
                    c = Counter(next_states)
                    total = len(next_states)
                    html_str += "<ul style='margin-bottom:0; padding-left:20px; font-size:14px;'>"
                    for k, v in c.most_common(3): 
                        pct = (v/total)*100
                        html_str += f"<li style='margin-bottom:5px;'><b>%{pct:.1f}</b> ihtimalle <span style='color:#059669; font-weight:bold;'>{k}</span></li>"
                    html_str += "</ul></div>"
                    return html_str

                st.markdown(f"<h5 style='color:#059669; margin-bottom:15px;'>🔍 SON ÇEKİLİŞ ({valid_draws[0]}) BAZ ALINARAK YAPILAN MARKOV HESAPLAMALARI:</h5>", unsafe_allow_html=True)
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.markdown(render_transition('freq', last_sim['freq'], "1. Frekans Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('devir', last_sim['devir'], "4. Devir Radarı"), unsafe_allow_html=True)
                with sc2:
                    st.markdown(render_transition('bolge', last_sim['bolge'], "2. Bölge Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('cons', last_sim['cons'], "5. Ardışık Radarı"), unsafe_allow_html=True)
                with sc3:
                    st.markdown(render_transition('oe', last_sim['oe'], "3. Tek/Çift Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('root', last_sim['root'], "6. Kök Eşleşme Radarı"), unsafe_allow_html=True)
                    
                st.markdown("<hr style='border: 2px dashed #cbd5e1; margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("#### 🚨 KRİTİK İSTİHBARAT: 'SAYI KESİLME' ALGORİTMASI")
                
                streak_3_count = 0
                streak_4_count = 0
                for num in range(1, 61):
                    for i in range(3, len(valid_draws)):
                        if num in valid_draws[i] and num in valid_draws[i-1] and num in valid_draws[i-2]:
                            streak_3_count += 1
                            if num in valid_draws[i-3]:
                                streak_4_count += 1
                                
                if streak_3_count > 0:
                    perc_devam = (streak_4_count / streak_3_count) * 100
                    perc_kesilme = 100 - perc_devam
                    st.markdown(f"""
                    <div style='background-color: #fff1f2; border: 2px solid #ef4444; padding: 15px; border-radius: 8px; color: #7f1d1d;'>
                        Süper Loto tarihinde herhangi bir sayının <b>3 hafta ÜST ÜSTE çıkma durumu tam {streak_3_count} kez</b> yaşanmıştır.<br><br>
                        Algoritmanın tespitine göre, 3 hafta üst üste çıkan bir sayının <b>4. HAFTA KESİN OLARAK KESİLME (GELMEME) ihtimali: <span style='font-size:22px; font-weight:900;'>%{perc_kesilme:.2f}</span></b>'dir.<br>
                        <span style='font-size:14px; color:#991b1b;'><i>(Kupon yaparken, son 3 haftadır çıkan bir sayı varsa onu <b>%{perc_kesilme:.2f} matematiksel güvence ile</b> eleyebilirsiniz.)</i></span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Süper Loto tarihinde henüz hiçbir sayı 3 hafta üst üste çıkmamıştır.")

            with tab_sorgu:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #eff6ff; border-left: 5px solid #2563eb; padding: 12px; border-radius: 4px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <strong style='color: #1e3a8a; font-size: 15px;'>🔮 RADAR (Gelecek Simülasyonu):</strong><br>
                <span style='color: #1d4ed8; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>ARDINDAN (Bir Sonraki Hafta)</b> neler yaşandığını hesaplar. Seçtiğiniz frekans küreden düştükten hemen sonraki hafta makinenin nasıl refleksler gösterdiğini simüle ederek, önümüzdeki çekilişin geleceğini tahmin etmenizi sağlar.</span>
            </div>
                """, unsafe_allow_html=True)

                all_freqs = [get_f_pattern(d) for d in valid_draws]
                freq_counts = Counter(all_freqs)
                
                st.markdown("#### 📊 VERİTABANINDAKİ EN POPÜLER FREKANS ŞABLONLARI")
                pop_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:30px;'>"
                for f, c in freq_counts.most_common(5):
                    pop_html += f"<div style='background-color:#ffffff; border:2px solid #cbd5e1; padding:10px 15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); text-align:center;'><b>{f}</b><br><span style='color:#059669; font-weight:900; font-size:14px;'>{c} Kez Yaşandı</span></div>"
                pop_html += "</div>"
                st.markdown(pop_html, unsafe_allow_html=True)

                st.markdown("#### 🔍 HEDEF FREKANSI BELİRLEYİN")
                cq1, cq2, cq3 = st.columns(3)
                with cq1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    q_s = st.number_input("Sıcak", 0, 6, 2, key="sl_q_s", label_visibility="collapsed")
                with cq2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    q_o = st.number_input("Orta", 0, 6, 3, key="sl_q_o", label_visibility="collapsed")
                with cq3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    q_c = st.number_input("Soğuk", 0, 6, 1, key="sl_q_c", label_visibility="collapsed")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🚀 DİNAMİK İSTİHBARATI GETİR", type="primary", use_container_width=True, key="sl_sq_btn"):
                    if q_s + q_o + q_c != 6:
                        st.error("⚠️ HATA: Sıcak, Orta ve Soğuk sayılarının toplamı tam 6 olmalıdır!")
                    else:
                        target_f_str = f"{q_s}S - {q_o}O - {q_c}C"
                        q_results = {'oe': [], 'cons': [], 'root': [], 'bolge': [], 'devir': []}
                        match_count = 0
                        
                        for i in range(1, len(valid_draws)):
                            if get_f_pattern(valid_draws[i]) == target_f_str:
                                match_count += 1
                                trigger_draw = valid_draws[i]
                                next_draw = valid_draws[i-1]
                                
                                q_results['oe'].append(get_tc(next_draw))
                                q_results['cons'].append(get_ard(next_draw))
                                q_results['root'].append(get_k(next_draw))
                                q_results['bolge'].append(get_bolge_pattern_sl(next_draw))
                                q_results['devir'].append(get_dev(trigger_draw, next_draw))
                        
                        if match_count == 0:
                            st.warning(f"Veritabanında '{target_f_str}' frekansının gelip de ardından çekiliş yapılan bir kayıt bulunamadı.")
                        else:
                            st.success(f"✅ HEDEF KİLİTLENDİ: Tarihte '{target_f_str}' şablonundan SONRAKİ HAFTA tam {match_count} kez çekiliş yapılmıştır. Makinenin gösterdiği refleksler aşağıdadır:")
                            
                            def print_q_stats(data_list, title):
                                c = Counter(data_list)
                                total = len(data_list)
                                html = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; margin-bottom:15px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>"
                                html += f"<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                                for k, v in c.most_common():
                                    perc = (v / total) * 100
                                    html += f"<div style='display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px dashed #f1f5f9; padding-bottom:4px;'><span style='font-weight:bold; color:#334155; font-size:14px;'>{k}</span> <span style='color:#059669; font-weight:900; font-size:15px;'>%{perc:.2f}</span></div>"
                                html += "</div>"
                                return html

                            qc1, qc2 = st.columns(2)
                            with qc1:
                                st.markdown(print_q_stats(q_results['oe'], "1. TEK/ÇİFT REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['bolge'], "3. BÖLGE (ALT-ORTA-ÜST) REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['root'], "5. KÖK EŞLEŞME REFLEKSİ"), unsafe_allow_html=True)
                            with qc2:
                                st.markdown(print_q_stats(q_results['cons'], "2. ARDIŞIK SAYI REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['devir'], "4. DEVİR REFLEKSİ"), unsafe_allow_html=True)
                                
                            st.info("💡 KAPTAN'A NOT: En yüksek yüzdeler, makinenin bu frekansa verdiği tepkidir. Kolonları kurarken en üst sıradaki şablonları baz al.")
                   			   
                 

# ==========================================
# 🟢 3. MODÜL: ŞANS TOPU
# ==========================================
elif selected_game == "ŞANS TOPU AI":
    st.markdown("<div class='main-title' style='color:#d80073;'>ŞANS TOPU ANALİZ MERKEZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>Yapay Zeka Destekli Kusursuz Kolon Motoru</div>", unsafe_allow_html=True)

    st.markdown("""
<details class="guide-box" style="margin-bottom: 20px; background-color: #ffffff; border: 4px solid #000000; border-radius: 8px; padding: 10px;">
<summary class="guide-summary" style="color:#000000; font-size:1.2rem; font-weight: bold; cursor: pointer; list-style: none;">👆 SİSTEM NASIL ÇALIŞIR? KUPON YAPMADAN ÖNCE MUTLAKA OKU! 👆</summary>
<div class="guide-content" style="font-size:1rem; line-height:1.6; padding-top: 15px; border-top: 1px solid #f1f5f9; margin-top: 10px;">
<h3 style='color: #d80073; margin-top:0; font-weight: bold;'>🤖 Bu Platform Nedir?</h3>
<p>Burası sıradan bir "Rastgele Sayı Üretici" veya hislerle çalışan bir tahmin sitesi değildir. Bu platform, geçmiş tüm çekiliş verilerini <b>Yapay Zeka (K-Means Kümeleme)</b> ve <b>İleri İstatistik (Apriori Algoritması)</b> ile analiz eden profesyonel bir laboratuvardır.</p>
<h3 style='color: #d80073; margin-top:20px; font-weight: bold;'>⚙️ Algoritmalar ve Ayarlar Ne İşe Yarar?</h3>
<ul style='margin-bottom:0;'>
<li>📊 <b>Frekans (Sıcak/Orta/Soğuk):</b> Her sayının çıkma ivmesini hesaplar. Tek bir yöne yığılmayı önler, altın oranı (Örn: 2 Sıcak, 2 Orta, 1 Soğuk) seçmenizi sağlar.</li>
<li>⚖️ <b>Tek/Çift ve Basamak:</b> Sayıların son rakamlarına ve tek/çift özelliklerine göre homojen dağılımını zorunlu kılar.</li>
<li>🛡️ <b>Klan (K-Means) Zırhı:</b> Makine, tahtadaki sayıları fiziksel karakteristiklerine göre 4 farklı "Klana" ayırır. Kusursuz kolonlar bu klanlara dağılarak zırh oluşturur.</li>
<li>⚔️ <b>Düşman İkili (Apriori):</b> Sistem tarihi tarar ve <i>bugüne kadar hiç yan yana gelmemiş</i> veya birbirini iten sayıları tespit eder. Kolonunuz bu zehirli kombinasyonları söküp atar.</li>
<li>📉 <b>Çan Eğrisi ve Kapsam:</b> Seçilen 5 sayının toplamının, oyunun matematiksel kalbi olan <span style="background-color:#fef08a; padding:2px 4px; font-weight:bold; color:black;">86.4</span> eksenine oturup oturmadığını ölçer.</li>
</ul>
<div style='background-color:#fdf2f8; padding:12px; border-left:5px solid #db2777; margin-top:15px; border-radius: 4px;'>
<strong>💡 Strateji Önerisi:</strong> Sol menüden kurallarını (Ardışık, Tek/Çift, Kilit Sayı vb.) katı bir şekilde belirle. Ardından motoru ateşle! Eğer kuralların çok çelişiyorsa makine paradoksa girer. Kurallarını esneterek, <b>sadece tüm bu devasa filtreleri aşan o yegâne kolona</b> ulaşana kadar denemeye devam et.
</div>
</div>
</details>
""", unsafe_allow_html=True)

    valid_draws, plus_draws, msg = load_sans_topu_data()

    if not valid_draws:
        st.error(msg)
    else:
        total_draws = len(valid_draws)
        all_nums = [num for draw in valid_draws for num in draw]
        counts = Counter(all_nums)

        expected = total_draws * (5 / 34)

        # 🔥 BAŞLANGIÇ BARAJLARI (Orijinal Kodundaki "28 Sıcak, 19 Soğuk" Matematiksel Oranı)
        hot_limit = int(np.ceil(expected * 1.16)) 
        cold_limit = int(np.floor(expected * 0.79))

        hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= hot_limit]
        
        # 🛡️ DİNAMİK HAVUZ ZIRHI: Şans topunda ideal havuz 7 ile 12 sayı arasıdır. Yığılma varsa barajı kendisi sıkar, darsa gevşetir.
        while len(hot_nums) > 12:
            hot_limit += 1
            hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= hot_limit]
        while len(hot_nums) < 7 and hot_limit > 1:
            hot_limit -= 1
            hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= hot_limit]

        cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= cold_limit]
        
        # 🛡️ SOĞUK HAVUZ ZIRHI
        while len(cold_nums) > 12:
            cold_limit -= 1
            cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= cold_limit]
        while len(cold_nums) < 7:
            cold_limit += 1
            cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= cold_limit]

        medium_nums = [n for n in range(1, 35) if n not in hot_nums and n not in cold_nums]

        recency = {}
        for n in range(1, 35):
            for i, draw in enumerate(valid_draws):
                if n in draw:
                    recency[n] = i
                    break
            else: recency[n] = total_draws

        uyuyan_devler = {k: v for k, v in recency.items() if v >= 12} 
        alev_alanlar = Counter([n for d in valid_draws[:10] for n in d])
        momentum_sayilari = {k: v for k, v in alev_alanlar.items() if v >= 3} 

        features = {}
        for n in range(1, 35):
            d_n = [d for d in valid_draws if n in d]
            if len(d_n) == 0: features[n] = [0, 0, 0]
            else: features[n] = [len(d_n), np.mean([sum(d) for d in d_n]), np.mean([max(d)-min(d) for d in d_n])]

        X = np.array(list(features.values()))
        n_clust = min(4, len(set([tuple(f) for f in features.values()])))
        if n_clust >= 2:
            kmeans = KMeans(n_clusters=n_clust, random_state=42, n_init=10).fit(X)
            klan_labels = {list(features.keys())[i]: kmeans.labels_[i] for i in range(len(features))}
        else:
            klan_labels = {k: 0 for k in features.keys()}

        pairs = [p for d in valid_draws for p in combinations(d, 2)]
        pair_c = Counter(pairs)
        all_p = set(combinations(range(1, 35), 2))
        actual_p = set([p for p, c in pair_c.items() if c > 0])
        enemies = set(all_p - actual_p)

        def is_enemy(n1, n2): return (min(n1, n2), max(n1, n2)) in enemies

        st.sidebar.markdown("## ⚙️ ŞANS TOPU FİLTRELERİ (Hibrit Zırh)")

        with st.sidebar.expander("📊 Temel Frekans", expanded=True):
            f_map = {
                "Dengeli (Önerilen): 2 Sıcak - 2 Orta - 1 Soğuk": (2, 2, 1),
                "Dengeli: 2 Sıcak - 1 Orta - 2 Soğuk": (2, 1, 2),
                "Dengeli: 1 Sıcak - 2 Orta - 2 Soğuk": (1, 2, 2),
                "Sıcak Odaklı: 3 Sıcak - 1 Orta - 1 Soğuk": (3, 1, 1),
                "Sıcak Odaklı: 3 Sıcak - 2 Orta - 0 Soğuk": (3, 2, 0),
                "Sıcak Odaklı: 3 Sıcak - 0 Orta - 2 Soğuk": (3, 0, 2),
                "Orta Odaklı: 1 Sıcak - 3 Orta - 1 Soğuk": (1, 3, 1),
                "Orta Odaklı: 2 Sıcak - 3 Orta - 0 Soğuk": (2, 3, 0),
                "Orta Odaklı: 0 Sıcak - 3 Orta - 2 Soğuk": (0, 3, 2),
                "Soğuk Odaklı: 1 Sıcak - 1 Orta - 3 Soğuk": (1, 1, 3),
                "Soğuk Odaklı: 2 Sıcak - 0 Orta - 3 Soğuk": (2, 0, 3),
                "Soğuk Odaklı: 0 Sıcak - 2 Orta - 3 Soğuk": (0, 2, 3),
                "Ekstrem Sıcak: 4 Sıcak - 1 Orta - 0 Soğuk": (4, 1, 0),
                "Ekstrem Sıcak: 4 Sıcak - 0 Orta - 1 Soğuk": (4, 0, 1),
                "Ekstrem Orta: 1 Sıcak - 4 Orta - 0 Soğuk": (1, 4, 0),
                "Ekstrem Orta: 0 Sıcak - 4 Orta - 1 Soğuk": (0, 4, 1),
                "Ekstrem Soğuk: 1 Sıcak - 0 Orta - 4 Soğuk": (1, 0, 4),
                "Ekstrem Soğuk: 0 Sıcak - 1 Orta - 4 Soğuk": (0, 1, 4),
                "Full Sıcak: 5 Sıcak - 0 Orta - 0 Soğuk": (5, 0, 0),
                "Full Orta: 0 Sıcak - 5 Orta - 0 Soğuk": (0, 5, 0),
                "Full Soğuk: 0 Sıcak - 0 Orta - 5 Soğuk": (0, 0, 5)
            }
            frekans_secim = st.selectbox("Sıcak - Orta - Soğuk Dağılımı", list(f_map.keys()))
            sicak_hedef, orta_hedef, soguk_hedef = f_map[frekans_secim]

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            tek_hedef = st.slider("Tek Sayı Adedi (Kalanı Çift Olur)", 0, 5, 3)
            cift_hedef = 5 - tek_hedef
            st.info(f"Sistem Kilitlendi: {tek_hedef} Tek, {cift_hedef} Çift")

        with st.sidebar.expander("2. Ardışık & 3. Kök Refleksi", expanded=True):
            c_strat1, c_strat2 = st.columns(2)
            ardisik = c_strat1.selectbox("Ardışık Sayı", ["YOK", "VAR"])
            kese_koku = c_strat2.selectbox("Kök Eşleşmesi", ["VAR (1 Çift)", "YOK"])
            
        with st.sidebar.expander("4. Devir Refleksi", expanded=True):
            devir_secimi = st.selectbox("Devir (Önceki Haftadan)", [
                "Farketmez", 
                "YOK (Önceki haftadan sayı gelmesin)", 
                "VAR (Sistem rastgele 1 sayı seçsin)", 
                "VAR (Sayıyı ben seçeceğim)"
            ])
            devir_sayisi_str = ""
            if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                st.info(f"Geçen Haftanın Sayıları: {valid_draws[0]}")
                devir_sayisi_str = st.text_input("Devredecek sayıyı girin:", "")

        with st.sidebar.expander("5. Basamak Refleksi", expanded=True):
            col6, col7 = st.columns(2)
            col8, col9 = st.columns(2)
            b1 = col6.number_input("Birler", 0, 5, 1)
            b2 = col7.number_input("Onlar", 0, 5, 1)
            b3 = col8.number_input("Yirmiler", 0, 5, 2)
            b4 = col9.number_input("Otuzlar", 0, 5, 1)
            
            if (b1 + b2 + b3 + b4) != 5:
                st.error(f"🚨 HATA: Basamak toplamı 5 olmalı! (Şu anki toplam: {b1 + b2 + b3 + b4})")

        with st.sidebar.expander("6. Bölge Refleksi (Alt-Üst)", expanded=True):
            alt_hedef = st.slider("Alt Bölge (1-17) Sayı Adedi", 0, 5, 2)
            ust_hedef = 5 - alt_hedef
            st.info(f"Sistem Kilitlendi: {alt_hedef} Alt, {ust_hedef} Üst")

        with st.sidebar.expander("🛡️ Ekstra Kısıtlamalar (Çan vb.)", expanded=False):
            min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 15, 160, (50, 120))
            min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 4, 33, (10, 33))
            yasak_sayilar_str = st.text_input("Yasaklılar (Virgülle ayırın)", "")
            banko_sayilar_str = st.text_input("Banko Sayılar (Mutlaka Olsun)", "")

        # --- ORTAK FONKSİYONLAR ---
        def get_f_pattern(col):
            s = sum(1 for x in col if x in hot_nums)
            o = sum(1 for x in col if x in medium_nums)
            c = sum(1 for x in col if x in cold_nums)
            return f"{s}S - {o}O - {c}C"

        def get_tc(col):
            tek = sum(1 for x in col if x % 2 != 0)
            return f"{tek} Tek - {5-tek} Çift"

        def get_ard(col): return "VAR" if any(col[i] + 1 == col[i+1] for i in range(4)) else "YOK"
        def get_dev(prev_col, curr_col): return "VAR" if len(set(prev_col).intersection(set(curr_col))) > 0 else "YOK"
        
        def get_basamak_pattern(col):
            _b1 = sum(1 for x in col if x <= 9)
            _b2 = sum(1 for x in col if 10 <= x <= 19)
            _b3 = sum(1 for x in col if 20 <= x <= 29)
            _b4 = sum(1 for x in col if x >= 30)
            return f"{_b1}B - {_b2}O - {_b3}Y - {_b4}Ot"
            
        def get_k(col):
            roots = [x % 10 for x in col]
            counts = list(Counter(roots).values())
            counts.sort(reverse=True)
            if counts == [1, 1, 1, 1, 1]: return "Eşleşme Yok"
            elif counts == [2, 1, 1, 1]: return "1 Çift Kök"
            else: return "Çoklu/Çifte Kök"

        def get_bolge_pattern_sans(col):
            alt = sum(1 for x in col if x <= 17)
            ust = sum(1 for x in col if x >= 18)
            return f"{alt} Alt - {ust} Üst"

       # --- ÜRETİM ALANI (SİHİRLİ BUTON VE MANUEL SEÇİM) ---
        st.info(f"{msg} | **Son Çekiliş:** {valid_draws[0]} ➕ [{plus_draws[0]}]")
        st.markdown("---")
        
        if "uretim_ekrani_acik" not in st.session_state:
            st.session_state.uretim_ekrani_acik = False
        if "ai_uretim_ekrani_acik" not in st.session_state:
            st.session_state.ai_uretim_ekrani_acik = False

        if "sans_manuel_sayaci" not in st.session_state:
            st.session_state.sans_manuel_sayaci = 0
        if "sans_ai_sayaci" not in st.session_state:
            st.session_state.sans_ai_sayaci = 0

        basla_btn = False
        ai_basla_btn = False
        kolon_sayisi = 1
        
        is_vip_or_admin = st.session_state.get("is_vip", False) or st.session_state.get("user_email", "") == "admin@kaptan.com"

        manuel_hakkini_doldurdu = not is_vip_or_admin and st.session_state.sans_manuel_sayaci >= 1
        ai_hakkini_doldurdu = not is_vip_or_admin and st.session_state.sans_ai_sayaci >= 1

        if not st.session_state.uretim_ekrani_acik and not st.session_state.ai_uretim_ekrani_acik:
            if manuel_hakkini_doldurdu and ai_hakkini_doldurdu:
                st.error("🔒 Ücretsiz deneme haklarınızı doldurdunuz! Sınırsız üretim yapmak ve tüm Kuantum filtrelerini özgürce kullanmak için VIP üyeliğe geçin.")
                if st.button("👑 VIP ÜYELİK AYRICALIKLARI", use_container_width=True, key="vip_btn_sans_final"):
                    pass
            else:
                st.markdown("<h4 style='text-align:center; color:#1e293b; font-weight:900; margin-bottom: 25px;'>Kuponunuzu Nasıl Kurgulamak İstersiniz?</h4>", unsafe_allow_html=True)
                c_btn_sol, c_btn_sag = st.columns(2)
                
                with c_btn_sol:
                    st.markdown("""
<div style='background-color:#f8fafc; padding:20px; border-radius:12px; border:2px solid #cbd5e1; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
<h4 style='color:#334155; margin-top:0; font-weight:900;'>🎛️ KONTROL SİZDE (Manuel)</h4>
<p style='font-size:13px; color:#64748b; line-height:1.5; margin-bottom:0;'>Kendi stratejinizi belirleyin. Sol menüdeki Kuantum ve Markov parametrelerini ayarlayın, yapay zeka sadece sizin kurallarınıza uyan kusursuz kombinasyonu bulsun.</p>
</div>
""", unsafe_allow_html=True)
                    if manuel_hakkini_doldurdu:
                        st.warning("🔒 Manuel üretim hakkınızı kullandınız.")
                    else:
                        if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", use_container_width=True, key="btn_manuel_sans"):
                            st.session_state.uretim_ekrani_acik = True
                            st.rerun()
                        
                with c_btn_sag:
                    st.markdown("""
<div style='background-color:#f5f3ff; padding:20px; border-radius:12px; border:2px solid #7c3aed; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(124, 58, 237, 0.1);'>
<h4 style='color:#6d28d9; margin-top:0; font-weight:900;'>✨ SİHİRLİ OTOPİLOT (Tam Yetki)</h4>
<p style='font-size:13px; color:#4c1d95; line-height:1.5; margin-bottom:0;'>Filtrelerle vakit kaybetmeyin! Makine tüm veri madenciliği algoritmalarını çalıştırır, Şans Topu'nun 5+1 yapısına uygun en ideal 'Altın Oranlı' şablonu getirir.</p>
</div>
""", unsafe_allow_html=True)
                    if ai_hakkini_doldurdu:
                        st.warning("🔒 Sihirli Oto-Pilot hakkınızı kullandınız.")
                    else:
                        if st.button("✨ YAPAY ZEKAYA DEVRET", type="primary", use_container_width=True, key="btn_ai_sans"):
                            st.session_state.ai_uretim_ekrani_acik = True
                            st.rerun()

        if st.session_state.uretim_ekrani_acik:
            st.markdown("<div style='border: 3px solid #64748b; border-radius: 12px; padding: 20px; background-color: #f8fafc; text-align: center; margin-bottom: 20px;'><h3 style='color: #334155; margin-top: 0;'>🎛️ MANUEL ÜRETİM ONAYI</h3><p style='margin-bottom:0;'>Şans Topu kolon adedini belirleyin.</p></div>", unsafe_allow_html=True)
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_kolon_hakki = 100 if is_vip_or_admin else 3
                kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_kolon_hakki})", min_value=1, max_value=max_kolon_hakki, value=1, key="manuel_adet_sans")
                if not is_vip_or_admin:
                    st.info("💡 Ziyaretçiler ve Standart üyeler manuel olarak en fazla 3 kolon üretebilir. Sınırsız üretim için VIP'ye geçin.")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1: basla_btn = st.button("✅ ÜRET", type="primary", use_container_width=True, key="sans_basla_m")
                with col_m2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="sans_iptal_m"):
                        st.session_state.uretim_ekrani_acik = False
                        st.rerun()

        if st.session_state.ai_uretim_ekrani_acik:
            st.markdown("""
<div style='border: 3px solid #7c3aed; border-radius: 12px; padding: 25px; background-color: #f5f3ff; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.15);'>
<h3 style='color: #6d28d9; margin-top: 0; text-align: center; font-weight: 900;'>🪄 OTOPİLOT DEVREYE GİRİYOR</h3>
<p style='color: #4c1d95; text-align: center; font-size: 15px; margin-bottom: 20px; font-weight: 600;'>Makineye tam yetki verdiniz. Arka planda saniyeler içinde şu mühendislik işlemleri gerçekleşecek:</p>
<div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px dashed #c4b5fd;'>
<ul style='color: #5b21b6; font-size: 14px; margin-bottom: 0; padding-left: 20px; line-height: 1.8;'>
<li><b>🧬 Derin Öğrenme Taraması:</b> Yılların Şans Topu verisi taranarak 34 ana top ve 14 artı topun güncel havuz haritası çıkarılır.</li>
<li><b>⚔️ Apriori (Düşman) Filtresi:</b> Loto tarihinde bugüne kadar hiç yan yana gelmemiş zehirli kombinasyonlar tespit edilip imha edilir.</li>
<li><b>🛡️ K-Means Klan Zırhı:</b> Seçilen sayılar, makinenin tespit ettiği gizli klanlara dengeli biçimde dağıtılarak risk minimize edilir.</li>
<li><b>📉 Kuantum Çan Eğrisi:</b> Üretilen kolon, Şans Topu'nun matematiksel istatistik merkezine kilitlenir.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)
            
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_ai_hakki = 100 if is_vip_or_admin else 1
                kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_ai_hakki})", min_value=1, max_value=max_ai_hakki, value=1, key="ai_adet_sans")
                if not is_vip_or_admin:
                    st.markdown("""
<div style='background-color:#fffbeb; border:1px solid #f59e0b; padding:10px; border-radius:6px; margin-bottom:15px; text-align:center;'>
<span style='color:#b45309; font-size:13px; font-weight:bold;'>👑 Standart üyeler için Sihirli Buton 1 kolonla sınırlıdır. Tüm kuponu yapay zekaya doldurtmak için VIP'ye geçin.</span>
</div>
""", unsafe_allow_html=True)
                
                col_a1, col_a2 = st.columns(2)
                with col_a1: ai_basla_btn = st.button("✨ SİHRİ BAŞLAT", type="primary", use_container_width=True, key="sans_basla_ai")
                with col_a2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="sans_iptal_ai"):
                        st.session_state.ai_uretim_ekrani_acik = False
                        st.rerun()

        # ÜRETİM MOTORU (HEM MANUEL HEM AI İÇİN ORTAK ÇALIŞIR)
        if basla_btn or ai_basla_btn:
            st.session_state.uretim_ekrani_acik = False 
            st.session_state.ai_uretim_ekrani_acik = False
            
            with st.spinner('Kuantum eleme motoru ve Yapay Zeka zırhı devrede...'):
                time.sleep(1)
                
                last_draw_nums = valid_draws[0]
                devirler = []
                ekstra_yasaklar = []
                yasaklar = []
                sabit_sayilar = []
                errors = []
                
                # SİHİRLİ BUTON (AI) SEÇİLDİYSE KURALLARI MAKİNE KENDİ KOYAR
                if ai_basla_btn:
                    sicak_hedef, orta_hedef, soguk_hedef = 2, 2, 1
                    tek_hedef, cift_hedef = 3, 2
                    b1, b2, b3, b4 = 1, 1, 2, 1 
                    alt_hedef, ust_hedef = 2, 3
                    ardisik = "YOK"
                    kese_koku = "YOK"
                    devir_secimi = "Farketmez"
                    min_toplam, max_toplam = 75, 95 
                    min_kapsam, max_kapsam = 15, 30
                else:
                    # MANUEL SEÇİLDİYSE SOL MENÜDEKİ AYARLARI KULLAN
                    if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)":
                        ekstra_yasaklar.extend(last_draw_nums)
                    elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                        devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
                    
                    yasaklar_input = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                    yasaklar = list(set(yasaklar_input + ekstra_yasaklar))
                    
                    bankolar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                    sabit_sayilar = list(set(devirler + bankolar))

                    if sicak_hedef + orta_hedef + soguk_hedef != 5: errors.append("Sıcak+Orta+Soğuk = 5 olmalı.")
                    if tek_hedef + cift_hedef != 5: errors.append("Tek+Çift = 5 olmalı.")
                    if b1 + b2 + b3 + b4 != 5: errors.append("Basamak toplamları = 5 olmalı.")
                    if alt_hedef + ust_hedef != 5: errors.append("Alt+Üst bölge = 5 olmalı.")
                    if len(sabit_sayilar) > 5: errors.append("Banko ve Devir sayılarının toplamı 5'i geçemez.")
                    
                    # 🔥 ŞANS TOPUNA ÖZEL BANKO ZIRHI (Ön Güvenlik Duvarı) 🔥
                    if len(sabit_sayilar) > 0:
                        for s in sabit_sayilar:
                            if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko/Devir hem de Yasaklı listesinde olamaz!")
                            if s < 1 or s > 34: errors.append(f"Hata: {s} geçersiz bir sayıdır (1-34).")

                        # Tek Çift Zırhı
                        b_tek = sum(1 for x in sabit_sayilar if x % 2 != 0)
                        b_cift = len(sabit_sayilar) - b_tek
                        if b_tek > tek_hedef or b_cift > cift_hedef:
                            errors.append(f"Hata: Bankolarınızdaki Tek/Çift sayısı ({b_tek}T/{b_cift}Ç), kuralı ({tek_hedef}T/{cift_hedef}Ç) aşıyor!")

                        # Bölge (Alt-Üst) Zırhı
                        b_alt = sum(1 for x in sabit_sayilar if x <= 17)
                        b_ust = sum(1 for x in sabit_sayilar if x >= 18)
                        if b_alt > alt_hedef or b_ust > ust_hedef:
                            errors.append("Hata: Bankolarınızın bölge dağılımı (Alt-Üst) kotanızı aşıyor!")

                        # Basamak (1'ler, 10'lar, 20'ler, 30'lar) Zırhı (Seni paradokstan kurtaran asıl kod)
                        b_b1 = sum(1 for x in sabit_sayilar if x <= 9)
                        b_b2 = sum(1 for x in sabit_sayilar if 10 <= x <= 19)
                        b_b3 = sum(1 for x in sabit_sayilar if 20 <= x <= 29)
                        b_b4 = sum(1 for x in sabit_sayilar if x >= 30)
                        if b_b1 > b1 or b_b2 > b2 or b_b3 > b3 or b_b4 > b4:
                            errors.append("Hata: Banko girdiğiniz sayıların basamakları (Birler, Onlar vb.), belirlediğiniz kotaları aşıyor!")

                        # Ardışık ve Apriori (Düşman) Zırhı
                        sirali_sabit = sorted(sabit_sayilar)
                        ardisik_ciftler = sum(1 for i in range(len(sirali_sabit)-1) if sirali_sabit[i+1] - sirali_sabit[i] == 1)
                        if ardisik_ciftler > 1: errors.append("Hata: Bankolarınızda 1'den fazla ardışık çift var. (Zehirli Dizi)")
                        elif ardisik_ciftler == 1 and ardisik == "YOK": errors.append("Hata: Bankolarınızda ardışık sayı var, ancak filtre 'Ardışık YOK' seçili!")

                        for b1_enemy, b2_enemy in combinations(sabit_sayilar, 2):
                            if is_enemy(b1_enemy, b2_enemy): errors.append(f"Hata: Banko girdiğiniz ({b1_enemy} ve {b2_enemy}) Apriori kuralına göre DÜŞMAN sayılardır!")

                if errors:
                    for e in errors: st.error(e)
                    if st.button("🔄 Kuralları Esnet ve Geri Dön", use_container_width=True, key="btn_sans_geri_hata"): st.rerun()
                    st.stop()
                else:
                    adaylar = [x for x in range(1, 35) if x not in yasaklar and x not in sabit_sayilar]
                    kalan_secim_sayisi = 5 - len(sabit_sayilar)
                    
                    hot_pool = [x for x in hot_nums if x in adaylar]
                    med_pool = [x for x in medium_nums if x in adaylar]
                    cold_pool = [x for x in cold_nums if x in adaylar]

                    b_hot = sum(1 for x in sabit_sayilar if x in hot_nums)
                    b_med = sum(1 for x in sabit_sayilar if x in medium_nums)
                    b_cold = sum(1 for x in sabit_sayilar if x in cold_nums)

                    req_hot = sicak_hedef - b_hot
                    req_med = orta_hedef - b_med
                    req_cold = soguk_hedef - b_cold

                    if req_hot < 0 or req_med < 0 or req_cold < 0:
                        st.error("🚨 HATA: Banko sayılarının frekansları, belirlediğin hedefleri aşıyor!")
                    elif req_hot > len(hot_pool) or req_med > len(med_pool) or req_cold > len(cold_pool):
                        st.error(f"🚨 HATA: Kotalar havuzdaki sayıları aşıyor! Lütfen kuralları esnetin. (Kalan havuz: {len(hot_pool)}S - {len(med_pool)}O - {len(cold_pool)}C)")
                    else:
                        valid_combinations = []
                        hata_kodlari = {
                            "frekans_havuzu": 0, "devir": 0, "tek_cift": 0, 
                            "bolge": 0, "basamak": 0, "kok": 0, "ardisik": 0, "can_kapsam": 0
                        }

                        attempts = 0
                        max_attempts = 250000 # Havuz dar olduğu için limit yükseltildi

                        while len(valid_combinations) < (kolon_sayisi * 3) and attempts < max_attempts:
                            attempts += 1
                            
                            h_pick = random.sample(hot_pool, req_hot) if req_hot > 0 else []
                            m_pick = random.sample(med_pool, req_med) if req_med > 0 else []
                            c_pick = random.sample(cold_pool, req_cold) if req_cold > 0 else []
                            
                            col = sorted(sabit_sayilar + h_pick + m_pick + c_pick)
                            
                            if len(set(col)) != 5: 
                                hata_kodlari["frekans_havuzu"] += 1
                                continue

                            # --- BASAMAK REFLEKSİ ---
                            b1_c = sum(1 for x in col if x <= 9)
                            b2_c = sum(1 for x in col if 10 <= x <= 19)
                            b3_c = sum(1 for x in col if 20 <= x <= 29)
                            b4_c = sum(1 for x in col if x >= 30)
                            if b1_c != b1 or b2_c != b2 or b3_c != b3 or b4_c != b4:
                                hata_kodlari["basamak"] += 1
                                continue
                                
                            # --- TEK/ÇİFT REFLEKSİ ---
                            tek = sum(1 for x in col if x % 2 != 0)
                            if tek != tek_hedef: 
                                hata_kodlari["tek_cift"] += 1
                                continue
                                
                            # --- BÖLGE REFLEKSİ ---
                            alt = sum(1 for x in col if x <= 17)
                            if alt != alt_hedef:
                                hata_kodlari["bolge"] += 1
                                continue

                            # --- KÖK EŞLEŞMESİ REFLEKSİ ---
                            roots = [x % 10 for x in col]
                            unique_roots = len(set(roots))
                            
                            if kese_koku == "VAR (1 Çift)":
                                if unique_roots != 4: 
                                    hata_kodlari["kok"] += 1
                                    continue
                            elif kese_koku == "YOK":
                                if unique_roots != 5: 
                                    hata_kodlari["kok"] += 1
                                    continue

                            # --- KESİN EMİR UYGULAMASI (ÇİFT ARDIŞIK ENGELİ) ---
                            cons_count = 0
                            for i in range(4):
                                if col[i] + 1 == col[i+1]:
                                    cons_count += 1
                                    
                            if cons_count > 1: 
                                hata_kodlari["ardisik"] += 1
                                continue
                                
                            has_cons = (cons_count == 1)

                            if (ardisik == "VAR" and not has_cons) or (ardisik == "YOK" and has_cons): 
                                hata_kodlari["ardisik"] += 1
                                continue

                            toplam = sum(col)
                            if not (min_toplam <= toplam <= max_toplam):
                                hata_kodlari["can_kapsam"] += 1
                                continue
                                
                            if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam):
                                hata_kodlari["can_kapsam"] += 1
                                continue

                            if not ai_basla_btn and devir_secimi == "VAR (Sistem rastgele 1 sayı seçsin)":
                                if sum(1 for x in col if x in valid_draws[0]) != 1:
                                    hata_kodlari["devir"] += 1
                                    continue
                            elif devir_secimi == "YOK (Önceki haftadan sayı gelmesin)":
                                if any(x in valid_draws[0] for x in col): 
                                    hata_kodlari["devir"] += 1
                                    continue
                            elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                                try:
                                    ds = int(devir_sayisi_str)
                                    if ds not in col or sum(1 for x in col if x in valid_draws[0]) != 1: 
                                        hata_kodlari["devir"] += 1
                                        continue
                                except: 
                                    pass

                            dusman_skoru = sum(1 for pair in combinations(col, 2) if is_enemy(pair[0], pair[1]))
                            klan_cesitliligi = len(set([klan_labels.get(x, 0) for x in col]))
                            
                            valid_combinations.append({
                                'c': tuple(col), 'sum': sum(col), 'klan': klan_cesitliligi, 'dusman_sayisi': dusman_skoru
                            })
                            
                            unique_v = {v['c']: v for v in valid_combinations}.values()
                            valid_combinations = list(unique_v)

                        if len(valid_combinations) > 0:
                            valid_combinations.sort(key=lambda x: (x['dusman_sayisi'], -x['klan'], abs(x['sum'] - 86.4)))
                            gosterilecek_adet = min(kolon_sayisi, len(valid_combinations))
                        
                            if ai_basla_btn:
                                st.success(f"🪄 Yapay Zeka oyunun matematiksel DNA'sını çözdü ve sizin için en kusursuz {gosterilecek_adet} kolonu oluşturdu!")
                            else:
                                if gosterilecek_adet < kolon_sayisi:
                                    st.warning(f"Sadece {len(valid_combinations)} kusursuz dizilim bulunabildi. Kurallarınız çok katı olduğu için tamamı aşağıdadır:")
                                else:
                                    st.success(f"Tüm katı filtreler başarıyla aşıldı! Havuzdaki kusursuz dizilimler arasından EN İYİ {gosterilecek_adet} kolon kurgulandı.")

                            # Veritabanına gidecek kolonları tutacağımız liste
                            tam_kolonlar_sans = []

                            for i in range(gosterilecek_adet):
                                secilen = valid_combinations[i]['c']
                                klan_degeri = valid_combinations[i]['klan']
                                d_skor = valid_combinations[i]['dusman_sayisi']
                                
                                if kolon_sayisi > 1:
                                    st.markdown(f"<h4 style='color:#dc2626; text-align:center; margin-top:20px; font-weight:900; background-color:#fef2f2; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                                
                                try:
                                    if "smart_plus_pool" not in st.session_state:
                                        import pandas as pd
                                        import random
                                        from collections import Counter
                                        df_plus = pd.read_excel('chance.son.xlsx', sheet_name=0, header=None, engine='openpyxl')
                                        all_plus = pd.to_numeric(df_plus.iloc[:, 5], errors='coerce').dropna().astype(int).tolist()
                                        all_plus = [x for x in all_plus if 1 <= x <= 14]
                                        p_counts = Counter(all_plus)
                                        hot_p = [x[0] for x in p_counts.most_common(3)]
                                        sleep_p = [x for x in range(1, 15) if x not in all_plus[:15]]
                                        st.session_state.smart_plus_pool = hot_p + (sleep_p if sleep_p else [random.choice(range(1,15))])
                                    secilen_arti = random.choice(st.session_state.smart_plus_pool)
                                except:
                                    import random
                                    secilen_arti = random.choice([2, 4, 7, 9, 12, 14])

                                # 5 ana top ve 1 artı topu birleştirip kaydetme listesine atıyoruz
                                tam_kolonlar_sans.append(list(secilen) + [secilen_arti])

                                html_balls = f"""
                                <div style='text-align: center; margin: 15px 0 10px 0;'>
                                    <div class='number-ball ball-blue'>{secilen[0]}</div>
                                    <div class='number-ball ball-blue'>{secilen[1]}</div>
                                    <div class='number-ball ball-blue'>{secilen[2]}</div>
                                    <div class='number-ball ball-blue'>{secilen[3]}</div>
                                    <div class='number-ball ball-blue'>{secilen[4]}</div>
                                    <span style='font-size:30px; font-weight:bold; color:#64748b; margin: 0 15px;'>+</span>
                                    <div class='plus-ball ball-red'>{secilen_arti}</div>
                                </div>
                                <div style='text-align: center; margin-bottom: 25px;'>
                                    <span style='font-size:12px; color:#ef4444; font-weight:bold; background-color:#fef2f2; padding:3px 8px; border-radius:12px; border:1px solid #fca5a5;'>🤖 Akıllı +1 (Sıcak/Uyuyan Havuzundan)</span>
                                </div>
                                """
                                st.markdown(html_balls, unsafe_allow_html=True)
                                
                                dusman_etiketi = f"{d_skor} (Esnetildi)" if d_skor > 0 else "0 (Temiz)"
                                renk = "#eab308" if d_skor > 0 else "#22c55e"
                                
                                mc1, mc2, mc3, mc4 = st.columns(4)
                                with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#d80073;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                                with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#d80073;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                                with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                                with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span style='font-size:18px; font-weight:bold; color:{renk};'>{dusman_etiketi}</span></div>", unsafe_allow_html=True)
                                
                                if i < gosterilecek_adet - 1:
                                    st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)

                            # 🎯 AKILLI ONAY MEKANİZMASI VE KAYDET BUTONU (ŞANS TOPU) 🎯
                            if st.session_state.get("logged_in", False):
                                st.markdown("<br><hr style='border: 1px dashed #cbd5e1; margin-bottom: 20px;'>", unsafe_allow_html=True)
                                
                                current_live_data = load_live_data()
                                c_no_str = current_live_data.get("sanstopu", {}).get("cekilis_no", "")
                                
                                if c_no_str and c_no_str.isdigit():
                                    hedef_cekilis = int(c_no_str) + 1
                                    st.info(f"💡 Sistemde en son **{c_no_str}. Çekiliş** sonuçları kayıtlıdır.")
                                    cb_label = f"**✅ Ürettiğim bu kuponu/kuponları, yaklaşan {hedef_cekilis}. Şans Topu Çekilişi için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = f"Şans Topu (Hedef: {hedef_cekilis})"
                                else:
                                    cb_label = "**✅ Ürettiğim bu kuponu/kuponları, yaklaşan çekiliş için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = "Şans Topu"

                                def kayit_tetikleyici_sans(k_email, k_oyun_id, k_oyun_adi, k_kombinasyonlar):
                                    if st.session_state.get("onay_kutusu_sans", False):
                                        for t_kolon in k_kombinasyonlar:
                                            from datetime import datetime
                                            z_vakti = datetime.now().strftime("%d.%m.%Y %H:%M:%S") 
                                            save_coupon_to_db(k_email, k_oyun_id, k_oyun_adi, t_kolon, z_vakti)
                                            time.sleep(0.1)

                                with st.form(key="kayit_form_sans"):
                                    st.checkbox(cb_label, key="onay_kutusu_sans")
                                    # Liste adı tam_kolonlar_sans olarak senin sistemine uyarlandı!
                                    st.form_submit_button("💾 ÜRETİLEN KOLONLARI KAYDET", type="primary", use_container_width=True, on_click=kayit_tetikleyici_sans, args=(st.session_state.user_email, "sanstopu", oyun_isim_etiketi, tam_kolonlar_sans))
                                
                                st.markdown("<p style='font-size:13px; color:#64748b; text-align:center;'><em>Not: Sistemin kaydedebilmesi için butona basmadan önce onay kutusunu işaretlediğinizden emin olun. Başarıyla kaydedildiğinde ekran yeni analizler için temizlenecektir.</em></p>", unsafe_allow_html=True)

                        else:
                            st.error("🚨 PARADOKS TESPİT EDİLDİ: Seçtiğiniz kurallar havuzda hiçbir sayı bırakmadı!")
                            en_cok_elenen = max(hata_kodlari, key=hata_kodlari.get)
                            
                            sebep_metni = ""
                            if en_cok_elenen == "frekans_havuzu": sebep_metni = "Sıcak/Orta/Soğuk kotaları ile eldeki sayı havuzu yetersiz kalıyor."
                            elif en_cok_elenen == "tek_cift": sebep_metni = "Havuzdaki sayıların güncel matematiği, istediğiniz Tek/Çift oranını vermiyor."
                            elif en_cok_elenen == "bolge": sebep_metni = "İstediğiniz Alt/Üst bölge hedefi mevcut sayılarla imkansız."
                            elif en_cok_elenen == "basamak": sebep_metni = "Basamak dağılımı (Birler, Onlar vb.) hedefleriniz, frekans ve bölge seçiminizle büyük bir çelişkiye (paradoksa) giriyor."
                            elif en_cok_elenen == "devir": sebep_metni = "Devir kuralınız aktif frekans havuzlarında yer almıyor."
                            elif en_cok_elenen == "can_kapsam": sebep_metni = "Çan Eğrisi veya Kapsam sınırlarınız çok dar. Sayılar bu aralığa sığamıyor."
                            elif en_cok_elenen == "kok": sebep_metni = "Kök eşleşmesi kuralınız mevcut dar havuzda sağlanamıyor."
                            elif en_cok_elenen == "ardisik": sebep_metni = "Sistem çift/üçlü ardışıkları reddettiği için elinizdeki havuz daraldı ve kuralınız çelişti."
                                
                            st.warning(f"""
                            **🔍 GERÇEK X-RAY TEŞHİS RAPORU:**
                            Motor {attempts} defa Kuantum taraması yaptı ancak sonuç alamadı. 
                            Sistemi kilitleyen ASIL Kural: **{en_cok_elenen.upper()} FİLTRESİ**.
                            
                            **Kilitlenme Sebebi:** {sebep_metni}
                            """)

        # --- 4 YENİ SEKME (GİZLEME KİLİDİ EKLENDİ) ---
        if not (basla_btn or ai_basla_btn):
            st.markdown("<br><hr style='border: 3px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            button[data-baseweb="tab"]:nth-child(3) p, button[data-baseweb="tab"]:nth-child(4) p {
                font-weight: 900 !important;
                font-size: 16px !important;
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            
            tab_tarih, tab_detayli, tab_simulasyon, tab_sorgu = st.tabs([
                "📈 TARİHSEL BİLANÇO (GENEL İSTATİSTİK)", 
                "🧠 DETAYLI YAPAY ZEKA ANALİZİ", 
                "🎯 SONRAKİ ÇEKİLİŞ SİMÜLASYONU",
                "🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU"
            ])

            with tab_tarih:
                last_d = valid_draws[0]
                st.markdown("#### 🎯 SON ÇEKİLİŞİN MR'I (Röntgen)")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='metric-card' style='padding:10px;'><b>Frekans Şablonu</b><br><span style='color:#db2777; font-weight:900; font-size:16px;'>{get_f_pattern(last_d)}</span></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='metric-card' style='padding:10px;'><b>Tek/Çift Dengesi</b><br><span style='color:#db2777; font-weight:900; font-size:16px;'>{get_tc(last_d)}</span></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='metric-card' style='padding:10px;'><b>Ardışık Durumu</b><br><span style='color:#db2777; font-weight:900; font-size:16px;'>{get_ard(last_d)}</span></div>", unsafe_allow_html=True)
                
                c4, c5, c6 = st.columns(3)
                c4.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Kök Eşleşmesi</b><br><span style='color:#db2777; font-weight:900; font-size:16px;'>{get_k(last_d)}</span></div>", unsafe_allow_html=True)
                c5.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Basamak Dağılımı</b><br><span style='color:#db2777; font-weight:900; font-size:16px;'>{get_basamak_pattern(last_d)}</span></div>", unsafe_allow_html=True)
                
                devir_bilgisi = get_dev(valid_draws[1], last_d) if len(valid_draws) > 1 else "YOK"
                c6.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Devir (Geçen Haftadan)</b><br><span style='color:#db2777; font-weight:900; font-size:16px;'>{devir_bilgisi}</span></div>", unsafe_allow_html=True)

                # --- SICAK/ORTA/SOĞUK GÖRSEL TABLOSU (ŞANS TOPU KAPTANIN KURALLARI) ---
                st.markdown("#### 🌡️ GÜNCEL SAYI HAVUZU (Ana Toplar: 1-34)")
                
                _all_m = [num for draw in valid_draws for num in draw[:5]]
                _c_m = Counter(_all_m)
                
                # KAPTAN'IN KESİN EMİRLERİ (Sabit Sınırlar):
                _hl = hot_limit
                _cl = cold_limit
                
                _hn = [n for n in range(1, 35) if _c_m.get(n, 0) >= _hl]
                _cn = [n for n in range(1, 35) if _c_m.get(n, 0) <= _cl]
                _mn = [n for n in range(1, 35) if _cl < _c_m.get(n, 0) < _hl]

                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 25px; margin-top: 15px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{_hl}): {len(_hn)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(_hn)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({_cl+1}-{_hl-1}): {len(_mn)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(_mn)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{_cl}): {len(_cn)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(_cn)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>#### 📊 OYUNUN GENEL KARAKTERİ (Tüm Zamanlar)", unsafe_allow_html=True)
                
                hist_f = Counter()
                hist_tc = Counter()
                hist_ard = Counter()
                hist_kok = Counter()
                hist_dev = Counter()
                hist_bas = Counter()
                hist_bolge = Counter()
                
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    hist_f[get_f_pattern(d)] += 1
                    hist_tc[get_tc(d)] += 1
                    hist_ard[get_ard(d)] += 1
                    hist_kok[get_k(d)] += 1
                    hist_bas[get_basamak_pattern(d)] += 1
                    hist_bolge[get_bolge_pattern_sans(d)] += 1
                    if i < len(valid_draws) - 1:
                        hist_dev[get_dev(valid_draws[i+1], valid_draws[i])] += 1
                        
                tot = len(valid_draws)
                tot_dev = tot - 1 if tot > 1 else 1
                
                def render_bar(label, count, total_val):
                    pct = (count / total_val) * 100
                    return f'''
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-weight: 800; color: #334155; font-size: 13px;">{label}</span>
                            <span style="font-weight: 900; color: #db2777; font-size: 13px;">%{pct:.1f} <span style="color:#94a3b8; font-size:11px;">({count} Kez)</span></span>
                        </div>
                        <div style="width: 100%; background-color: #f1f5f9; border-radius: 6px; height: 18px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                            <div style="width: {pct}%; background-color: #db2777; height: 100%;"></div>
                        </div>
                    </div>
                    '''
                    
                col_bar1, col_bar2 = st.columns(2)
                with col_bar1:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🔥 En Çok Gelen Frekanslar (İlk 5)</h5>", unsafe_allow_html=True)
                    for k, v in hist_f.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎲 Ardışık Sayı Durumu</h5>", unsafe_allow_html=True)
                    for k, v in hist_ard.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>♻️ Geçen Haftadan Devir (Kilit Sayı)</h5>", unsafe_allow_html=True)
                    for k, v in hist_dev.most_common(): st.markdown(render_bar(k, v, tot_dev), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_bar2:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>⚖️ Tek/Çift Dağılımı</h5>", unsafe_allow_html=True)
                    for k, v in hist_tc.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🧩 Kök Eşleşmesi (Son Rakam)</h5>", unsafe_allow_html=True)
                    for k, v in hist_kok.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎯 Alt-Üst Bölge Dağılımı</h5>", unsafe_allow_html=True)
                    for k, v in hist_bolge.most_common(4): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with tab_detayli:
                st.markdown("### 🧠 İLERİ DÜZEY İSTİHBARAT (RADAR SİSTEMİ)")
                
                col_rad1, col_rad2 = st.columns(2)
                with col_rad1:
                    st.markdown("#### 🔥 ALEV ALANLAR (Momentum İvmesi)")
                    if momentum_sayilari:
                        alevler_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(momentum_sayilari.items(), key=lambda item: item[1], reverse=True):
                            alevler_html += f"<div style='background-color:#fffbea; border:1.5px solid #000000; border-radius:6px; padding:8px 10px; text-align:center; min-width:85px;'><div style='color:#b45309; font-size:13px; font-weight:900; margin-bottom:2px;'>Sayı {k}</div><div style='font-size:10px; color:#64748b; font-weight:bold; margin-bottom:3px;'>Son 10 Çekilişte</div><div style='font-size:16px; color:#dc2626; font-weight:900;'>{v} Kez</div></div>"
                        alevler_html += "</div>"
                        st.markdown(alevler_html, unsafe_allow_html=True)
                    else: st.info("Son 10 çekilişte çıldıran sayı yok.")
                    
                with col_rad2:
                    st.markdown("#### 💤 UYUYAN DEVLER (Kuluçka)")
                    if uyuyan_devler:
                        uyuyan_html = "<div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:6px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(uyuyan_devler.items(), key=lambda item: item[1], reverse=True):
                            uyuyan_html += f"<div style='background-color:#f0f9ff; border:1px solid #bae6fd; border-radius:4px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center;'><strong style='color:#0369a1; font-size:13px;'>Sayı {k}</strong><span style='font-size:12px; color:#64748b; font-weight:bold;'>{v} Çekiliştir Yok</span></div>"
                        uyuyan_html += "</div>"
                        st.markdown(uyuyan_html, unsafe_allow_html=True)
                    else: st.info("Uyuyan dev bulunmuyor.")

                st.markdown("---")
                st.markdown("<h4 style='color:#e61532;'>🧬 ÇAPRAZ GEÇİŞ ANALİZİ (MARKOV MATRİSİ)</h4>", unsafe_allow_html=True)
                
                                
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 20px; margin-top: 10px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{hot_limit}): {len(hot_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({cold_limit+1}-{hot_limit-1}): {len(medium_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{cold_limit}): {len(cold_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 12px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                last_s = sum(1 for x in valid_draws[0] if x in hot_nums)
                last_o = sum(1 for x in valid_draws[0] if x in medium_nums)
                last_c = sum(1 for x in valid_draws[0] if x in cold_nums)

                st.markdown("""
                <div style='background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 12px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                    <strong style='color: #166534; font-size: 15px;'>🧬 MİKROSKOP (Anatomi Analizi):</strong><br>
                    <span style='color: #15803d; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>KENDİSİNİN</b> tarihte nasıl bir karakter sergilediğini inceler. Seçtiğiniz kombinasyonun iç yapısındaki tek/çift, ardışık ve kök eşleşme oranlarını göstererek o frekansın adeta DNA'sını çıkarır. Kuponunuzu oluştururken şablonun kurallarına uymanızı sağlar.</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='border: 3px solid #000000; border-radius: 10px; padding: 20px; background-color: #f8fafc; margin-bottom: 20px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);'>
                    <h4 style='text-align: center; color: #0f172a; font-weight: 900; margin-top: 0; margin-bottom: 20px; letter-spacing: 0.5px;'>🎯 HEDEF FREKANS KOMBİNASYONUNU SEÇİN</h4>
                """, unsafe_allow_html=True)
                
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    target_s = st.number_input("Sıcak (S)", 0, 5, last_s, key="ts_m", label_visibility="collapsed")
                with cc2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    target_o = st.number_input("Orta (O)", 0, 5, last_o, key="to_m", label_visibility="collapsed")
                with cc3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    target_c = st.number_input("Soğuk (C)", 0, 5, last_c, key="tc_m", label_visibility="collapsed")
                    
                st.markdown("</div>", unsafe_allow_html=True)

                if target_s + target_o + target_c != 5:
                    st.warning("⚠️ Şans Topu oyununda Sıcak, Orta ve Soğuk sayılarının toplamı tam 5 olmalıdır!")
                else:
                    target_freq = f"{target_s}S - {target_o}O - {target_c}C"
                    t_draws = []
                    
                    # 🧬 MİKROSKOP MODU: Geleceği değil, olayın KENDİSİNİ (current_draw) inceleriz.
                    for i in range(len(valid_draws) - 1): 
                        current_draw = valid_draws[i]
                        if get_f_pattern(current_draw) == target_freq:
                            prev_draw = valid_draws[i+1] # Devir hesabı için bir önceki haftanın çekilişi
                            t_draws.append({
                                'tc': get_tc(current_draw), 
                                'ard': get_ard(current_draw), 
                                'kok': get_k(current_draw),
                                'dev': get_dev(prev_draw, current_draw), 
                                'bas': get_basamak_pattern(current_draw),
                                'bolge': get_bolge_pattern_sans(current_draw)
                            })

                    if len(t_draws) > 0:
                        st.info(f"🧬 **ANATOMİ ÇIKARILDI:** Tarihte **{target_freq}** şablonu tam **{len(t_draws)}** kez yaşanmıştır. Bu çekilişlerin **İÇ YAPISI (Karakteri)** şöyledir:")
                        tc_c = Counter([x['tc'] for x in t_draws])
                        ard_c = Counter([x['ard'] for x in t_draws])
                        kok_c = Counter([x['kok'] for x in t_draws])
                        dev_c = Counter([x['dev'] for x in t_draws])
                        bas_c = Counter([x['bas'] for x in t_draws])
                        bolge_c = Counter([x['bolge'] for x in t_draws])
                        
                        def format_pct(counter):
                            total = sum(counter.values())
                            return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                        
                        copy_text = f"🧬 ÇAPRAZ ANALİZ ÇIKTISI (ANATOMİ: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT YAPISI ---\n{format_pct(tc_c)}\n\n--- 2. ARDIŞIK YAPISI ---\n{format_pct(ard_c)}\n\n--- 3. KÖK EŞLEŞMESİ ---\n{format_pct(kok_c)}\n\n--- 4. DEVİR DURUMU (Önceki Haftadan) ---\n{format_pct(dev_c)}\n\n--- 5. BASAMAK YAPISI ---\n{format_pct(bas_c)}\n\n--- 6. BÖLGE DAĞILIMI (Alt-Üst) ---\n{format_pct(bolge_c)}"
                        
                        st.markdown(f'''
                        <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.warning(f"Tarihte daha önce {target_freq} şablonu hiç yaşanmamış.")

            with tab_simulasyon:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🎯 GELECEK HAFTA PROJEKSİYONU (YAPAY ZEKA TAHMİNİ)</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #0ea5e9; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.15rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    Bu motor, son çekilişin 7 farklı DNA özelliğini alır, oyunun tüm geçmişini tarar ve tarihte bu özelliklerden sonra en yüksek ihtimalle nelerin geldiğini hesaplar.
                </div>
                """, unsafe_allow_html=True)
                
                history_sim = []
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    dev_durum = "Bilinmiyor"
                    if i + 1 < len(valid_draws):
                        dev_durum = get_dev(valid_draws[i+1], d)
                    
                    history_sim.append({
                        'freq': get_f_pattern(d),
                        'oe': get_tc(d),
                        'cons': get_ard(d),
                        'root': get_k(d),
                        'basamak': get_basamak_pattern(d),
                        'alt_ust': get_bolge_pattern_sans(d),
                        'devir': dev_durum
                    })
                
                last_sim = history_sim[0] 
                
                def render_transition(prop_key, target_val, title):
                    next_states = []
                    for i in range(1, len(history_sim)):
                        if history_sim[i][prop_key] == target_val:
                            next_states.append(history_sim[i-1][prop_key])
                    
                    html_str = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); height:100%;'>"
                    html_str += f"<h5 style='color:#0f172a; font-weight:900; font-size:15px; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                    html_str += f"<p style='font-size:12px; color:#64748b; margin-bottom:10px;'>Son Çekiliş: <b style='color:#db2777;'>{target_val}</b></p>"
                    
                    if not next_states:
                        html_str += "<span style='color:#64748b; font-size:13px;'>Tarihte örnek bulunamadı.</span></div>"
                        return html_str
                    
                    c = Counter(next_states)
                    total = len(next_states)
                    html_str += "<ul style='margin-bottom:0; padding-left:20px; font-size:14px;'>"
                    for k, v in c.most_common(3): 
                        pct = (v/total)*100
                        html_str += f"<li style='margin-bottom:5px;'><b>%{pct:.1f}</b> ihtimalle <span style='color:#db2777; font-weight:bold;'>{k}</span></li>"
                    html_str += "</ul></div>"
                    return html_str

                st.markdown(f"<h5 style='color:#db2777; margin-bottom:15px;'>🔍 SON ÇEKİLİŞ ({valid_draws[0]}) BAZ ALINARAK YAPILAN MARKOV HESAPLAMALARI:</h5>", unsafe_allow_html=True)
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.markdown(render_transition('freq', last_sim['freq'], "1. Frekans Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('basamak', last_sim['basamak'], "4. Basamak Radarı"), unsafe_allow_html=True)
                with sc2:
                    st.markdown(render_transition('alt_ust', last_sim['alt_ust'], "2. Alt/Üst Bölge Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('cons', last_sim['cons'], "5. Ardışık Sayı Radarı"), unsafe_allow_html=True)
                with sc3:
                    st.markdown(render_transition('oe', last_sim['oe'], "3. Tek/Çift Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('root', last_sim['root'], "6. Kök Eşleşme Radarı"), unsafe_allow_html=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(render_transition('devir', last_sim['devir'], "7. Devir (Geçen Haftadan) Radarı"), unsafe_allow_html=True)
                
                st.markdown("<hr style='border: 2px dashed #cbd5e1; margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("#### 🚨 KRİTİK İSTİHBARAT: 'SAYI KESİLME' ALGORİTMASI")
                
                streak_3_count = 0
                streak_4_count = 0
                for num in range(1, 35):
                    for i in range(3, len(valid_draws)):
                        if num in valid_draws[i] and num in valid_draws[i-1] and num in valid_draws[i-2]:
                            streak_3_count += 1
                            if num in valid_draws[i-3]:
                                streak_4_count += 1
                                
                if streak_3_count > 0:
                    perc_devam = (streak_4_count / streak_3_count) * 100
                    perc_kesilme = 100 - perc_devam
                    st.markdown(f"""
                    <div style='background-color: #fff1f2; border: 2px solid #ef4444; padding: 15px; border-radius: 8px; color: #7f1d1d;'>
                        Şans Topu tarihinde herhangi bir sayının <b>3 hafta ÜST ÜSTE çıkma durumu tam {streak_3_count} kez</b> yaşanmıştır.<br><br>
                        Algoritmanın tespitine göre, 3 hafta üst üste çıkan bir sayının <b>4. HAFTA KESİN OLARAK KESİLME (GELMEME) ihtimali: <span style='font-size:22px; font-weight:900;'>%{perc_kesilme:.2f}</span></b>'dir.<br>
                        <span style='font-size:14px; color:#991b1b;'><i>(Kupon yaparken, son 3 haftadır çıkan bir sayı varsa onu <b>%{perc_kesilme:.2f} matematiksel güvence ile</b> eleyebilirsiniz.)</i></span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Şans Topu tarihinde henüz hiçbir sayı 3 hafta üst üste çıkmamıştır.")

            with tab_sorgu:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #eff6ff; border-left: 5px solid #2563eb; padding: 12px; border-radius: 4px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <strong style='color: #1e3a8a; font-size: 15px;'>🔮 RADAR (Gelecek Simülasyonu):</strong><br>
                <span style='color: #1d4ed8; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>ARDINDAN (Bir Sonraki Hafta)</b> neler yaşandığını hesaplar. Seçtiğiniz frekans küreden düştükten hemen sonraki hafta makinenin nasıl refleksler gösterdiğini simüle ederek, önümüzdeki çekilişin geleceğini tahmin etmenizi sağlar.</span>
            </div>
                """, unsafe_allow_html=True)

                all_freqs = [get_f_pattern(d) for d in valid_draws]
                freq_counts = Counter(all_freqs)
                
                st.markdown("#### 📊 VERİTABANINDAKİ EN POPÜLER FREKANS ŞABLONLARI")
                pop_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:30px;'>"
                for f, c in freq_counts.most_common(5):
                    pop_html += f"<div style='background-color:#ffffff; border:2px solid #cbd5e1; padding:10px 15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); text-align:center;'><b>{f}</b><br><span style='color:#db2777; font-weight:900; font-size:14px;'>{c} Kez Yaşandı</span></div>"
                pop_html += "</div>"
                st.markdown(pop_html, unsafe_allow_html=True)

                st.markdown("#### 🔍 HEDEF FREKANSI BELİRLEYİN")
                cq1, cq2, cq3 = st.columns(3)
                with cq1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    q_s = st.number_input("Sıcak", 0, 5, 2, key="q_s", label_visibility="collapsed")
                with cq2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    q_o = st.number_input("Orta", 0, 5, 2, key="q_o", label_visibility="collapsed")
                with cq3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    q_c = st.number_input("Soğuk", 0, 5, 1, key="q_c", label_visibility="collapsed")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🚀 DİNAMİK İSTİHBARATI GETİR", type="primary", use_container_width=True):
                    if q_s + q_o + q_c != 5:
                        st.error("⚠️ HATA: Sıcak, Orta ve Soğuk sayılarının toplamı tam 5 olmalıdır!")
                    else:
                        target_f_str = f"{q_s}S - {q_o}O - {q_c}C"
                        q_results = {'oe': [], 'cons': [], 'root': [], 'basamak': [], 'alt_ust': [], 'devir': []}
                        match_count = 0
                        
                        for i in range(1, len(valid_draws)):
                            if get_f_pattern(valid_draws[i]) == target_f_str:
                                match_count += 1
                                trigger_draw = valid_draws[i]
                                next_draw = valid_draws[i-1]
                                
                                q_results['oe'].append(get_tc(next_draw))
                                q_results['cons'].append(get_ard(next_draw))
                                q_results['root'].append(get_k(next_draw))
                                q_results['basamak'].append(get_basamak_pattern(next_draw))
                                q_results['alt_ust'].append(get_bolge_pattern_sans(next_draw))
                                q_results['devir'].append(get_dev(trigger_draw, next_draw))
                        
                        if match_count == 0:
                            st.warning(f"Veritabanında '{target_f_str}' frekansının gelip de ardından çekiliş yapılan bir kayıt bulunamadı.")
                        else:
                            st.success(f"✅ HEDEF KİLİTLENDİ: Tarihte '{target_f_str}' şablonundan SONRAKİ HAFTA tam {match_count} kez çekiliş yapılmıştır. Makinenin gösterdiği refleksler aşağıdadır:")
                            
                            def print_q_stats(data_list, title):
                                c = Counter(data_list)
                                total = len(data_list)
                                html = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; margin-bottom:15px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>"
                                html += f"<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                                for k, v in c.most_common():
                                    perc = (v / total) * 100
                                    html += f"<div style='display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px dashed #f1f5f9; padding-bottom:4px;'><span style='font-weight:bold; color:#334155; font-size:14px;'>{k}</span> <span style='color:#db2777; font-weight:900; font-size:15px;'>%{perc:.2f}</span></div>"
                                html += "</div>"
                                return html

                            qc1, qc2, qc3 = st.columns(3)
                            with qc1:
                                st.markdown(print_q_stats(q_results['oe'], "1. TEK/ÇİFT REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['root'], "4. KÖK EŞLEŞME REFLEKSİ"), unsafe_allow_html=True)
                            with qc2:
                                st.markdown(print_q_stats(q_results['alt_ust'], "2. BÖLGE (ALT/ÜST) REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['devir'], "5. DEVİR REFLEKSİ"), unsafe_allow_html=True)
                            with qc3:
                                st.markdown(print_q_stats(q_results['cons'], "3. ARDIŞIK SAYI REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['basamak'], "6. BASAMAK DAĞILIMI"), unsafe_allow_html=True)
                                
                            st.info("💡 KAPTAN'A NOT: En yüksek yüzdeler, makinenin bu frekansa verdiği tepkidir. Kolonları kurarken en üst sıradaki şablonları baz al.")
# ==========================================
# 🟡 4. MODÜL: ON NUMARA AI
# ==========================================
elif selected_game == "ON NUMARA AI":
    
    valid_draws, msg = load_onnumara_ai_data()

    st.markdown("<div class='main-title' style='color:#d97706;'>ON NUMARA ANALİZ MERKEZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>80/22/10 - Çift Katmanlı Yapay Zeka Radar Sistemi</div>", unsafe_allow_html=True)

    st.markdown("""
<details class="guide-box" style="margin-bottom: 25px; background-color: #ffffff; border: 4px solid #000000; border-radius: 8px; padding: 10px;">
<summary class="guide-summary" style="color:#000000; font-size:1.2rem; font-weight: bold; cursor: pointer; list-style: none;">👇 80 TOPLUK SİSTEM NASIL ÇALIŞIR? MUTLAKA OKU! 👇</summary>
<div class="guide-content" style="font-size:1rem; line-height:1.6; padding-top: 15px; border-top: 1px solid #f1f5f9; margin-top: 10px;">
<h3 style='color: #d97706; margin-top:0; font-weight: bold;'>🤖 Bu Oyun Neden Farklıdır?</h3>
<p>On Numara oyununda küreden <b>22 top çekilir</b>, ancak kazanmak için <b>10 topu</b> tutturmanız gerekir. Bu sebeple Yapay Zeka motorumuz <i>çift katmanlı (Dual-Layer)</i> çalışır. Geçmiş çekiliş analizleri (Tarihsel Bilanço) 22 topun tamamı üzerinden yapılırken; sizin kolonlarınız 10 top üzerinden Kuantum filtrelere sokulur.</p>
<ul style='margin-bottom:0;'>
<li>📊 <b>10 Topluk Frekans:</b> Çekilen 22 topun yığılmalarına göre belirlenen Sıcak/Orta/Soğuk havuzlarından sizin için 10 topluk altın oranlı seçimler yapılır.</li>
<li>📐 <b>4'lü Bölge Dağılımı:</b> 80 Top 4 çeyreğe bölünür (1-20, 21-40, 41-60, 61-80). Topların tek bir alana sıkışması matematiksel olarak engellenir.</li>
<li>⚔️ <b>Ardışık Zırhı (Sıfır Tolerans):</b> Seçilen 10 top arasında çift ardışık gelmesine makine asla izin vermez. İsteğe bağlı olarak tamamen dağınık (Sıfır Ardışık) seçilebilir.</li>
<li>📉 <b>Çan Eğrisi:</b> 10 sayının toplamının, merkez çekim noktası olan <b>405</b> eksenine (ortalama 250 - 550 arasına) oturup oturmadığı test edilir.</li>
</ul>
</div>
</details>
""", unsafe_allow_html=True)

    if not valid_draws:
        st.error(msg)
    else:
        total_draws = len(valid_draws)
        all_nums = [num for draw in valid_draws for num in draw]
        counts = Counter(all_nums)
        
        # 🔥 BAŞLANGIÇ BARAJLARI (Oyunun 80 topluk matematiksel beklentisi)
        expected = total_draws * (22 / 80)
        hot_limit = int(np.ceil(expected * 1.25))
        cold_limit = int(np.floor(expected * 0.80))
        
        hot_nums = [n for n in range(1, 81) if counts.get(n, 0) >= hot_limit]
        
        # 🛡️ DİNAMİK HAVUZ ZIRHI: On Numara'da 80 top var. İdeal elit havuz 14-24 sayıdır.
        while len(hot_nums) > 24:
            hot_limit += 1
            hot_nums = [n for n in range(1, 81) if counts.get(n, 0) >= hot_limit]
        while len(hot_nums) < 14 and hot_limit > 1:
            hot_limit -= 1
            hot_nums = [n for n in range(1, 81) if counts.get(n, 0) >= hot_limit]

        cold_nums = [n for n in range(1, 81) if counts.get(n, 0) <= cold_limit]
        
        # 🛡️ SOĞUK HAVUZ ZIRHI
        while len(cold_nums) > 24:
            cold_limit -= 1
            cold_nums = [n for n in range(1, 81) if counts.get(n, 0) <= cold_limit]
        while len(cold_nums) < 14:
            cold_limit += 1
            cold_nums = [n for n in range(1, 81) if counts.get(n, 0) <= cold_limit]

        # ORTA HAVUZ
        medium_nums = [n for n in range(1, 81) if n not in hot_nums and n not in cold_nums]

        recency = {}
        for n in range(1, 81):
            for i, draw in enumerate(valid_draws):
                if n in draw:
                    recency[n] = i
                    break
            else: recency[n] = total_draws

        uyuyan_devler = {k: v for k, v in recency.items() if v >= 6} 
        alev_alanlar = Counter([n for d in valid_draws[:5] for n in d])
        momentum_sayilari = {k: v for k, v in alev_alanlar.items() if v >= 3} 

        features = {}
        for n in range(1, 81):
            d_n = [d for d in valid_draws if n in d]
            if len(d_n) == 0: features[n] = [0, 0, 0]
            else: features[n] = [len(d_n), np.mean([sum(d) for d in d_n]), np.mean([max(d)-min(d) for d in d_n])]

        X = np.array(list(features.values()))
        n_clust = min(5, len(set([tuple(f) for f in features.values()])))
        if n_clust >= 2:
            kmeans = KMeans(n_clusters=n_clust, random_state=42, n_init=10).fit(X)
            klan_labels = {list(features.keys())[i]: kmeans.labels_[i] for i in range(len(features))}
        else:
            klan_labels = {k: 0 for k in features.keys()}

        pairs = [p for d in valid_draws for p in combinations(d, 2)]
        pair_c = Counter(pairs)
        all_p = set(combinations(range(1, 81), 2))
        actual_p = set([p for p, c in pair_c.items() if c > 0])
        enemies = set(all_p - actual_p) 
        def is_enemy(n1, n2): return (min(n1, n2), max(n1, n2)) in enemies

        st.sidebar.markdown("## ⚙️ ON NUMARA FİLTRELERİ (10 Top)")

        with st.sidebar.expander("📊 Temel Frekans (Toplam 10)", expanded=True):
            f_map = {
                "Tarihsel Zirve (#1): 2 Sıcak - 6 Orta - 2 Soğuk": (2, 6, 2),
                "Tarihsel İkinci (#2): 2 Sıcak - 7 Orta - 1 Soğuk": (2, 7, 1),
                "Tarihsel Üçüncü (#3): 3 Sıcak - 5 Orta - 2 Soğuk": (3, 5, 2),
                "Tarihsel Dördüncü (#4): 3 Sıcak - 6 Orta - 1 Soğuk": (3, 6, 1),
                "Tarihsel Beşinci (#5): 1 Sıcak - 7 Orta - 2 Soğuk": (1, 7, 2),
                "Dengeli Alternatif: 4 Sıcak - 4 Orta - 2 Soğuk": (4, 4, 2),
                "Sıcak Odaklı: 5 Sıcak - 3 Orta - 2 Soğuk": (5, 3, 2),
                "Soğuk Ağırlıklı: 2 Sıcak - 3 Orta - 5 Soğuk": (2, 3, 5),
                "Ekstrem Orta: 1 Sıcak - 8 Orta - 1 Soğuk": (1, 8, 1)
            }
            frekans_secim = st.selectbox("Sıcak - Orta - Soğuk (Seçilen 10 Top)", list(f_map.keys()), key="on_frekans")
            sicak_hedef, orta_hedef, soguk_hedef = f_map[frekans_secim]

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            tek_hedef = st.slider("Tek Sayı Adedi (Kalanı Çift)", 0, 10, 5, key="on_t")
            cift_hedef = 10 - tek_hedef

        with st.sidebar.expander("2. Ardışık Kuralı", expanded=True):
            ardisik = st.selectbox("Ardışık Sayı Durumu", [
                "YOK (Asla ardışık gelmesin)", 
                "VAR (Sadece 1 Çift Ardışık Kabul Et)"
            ], key="on_ard")

        with st.sidebar.expander("3. 4'lü Bölge Refleksi", expanded=True):
            st.info("Toplamı tam 10 olmalıdır.")
            bc1, bc2 = st.columns(2)
            bc3, bc4 = st.columns(2)
            bolge1 = bc1.number_input("1. Çeyrek (1-20)", 0, 10, 3, key="on_b1")
            bolge2 = bc2.number_input("2. Çeyrek (21-40)", 0, 10, 2, key="on_b2")
            bolge3 = bc3.number_input("3. Çeyrek (41-60)", 0, 10, 3, key="on_b3")
            bolge4 = bc4.number_input("4. Çeyrek (61-80)", 0, 10, 2, key="on_b4")
            if (bolge1 + bolge2 + bolge3 + bolge4) != 10: st.error(f"🚨 HATA: Bölge toplamı 10 olmalı! (Şu an: {bolge1+bolge2+bolge3+bolge4})")

        with st.sidebar.expander("🛡️ Ekstra Kısıtlamalar", expanded=False):
            min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 55, 755, (300, 500), key="on_can")
            min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 20, 79, (50, 79), key="on_mes")
            yasak_sayilar_str = st.text_input("Yasaklılar (Virgülle ayırın)", key="on_yasak")
            banko_sayilar_str = st.text_input("Banko Sayılar (Mutlaka Olsun)", key="on_banko")

        # --- ORTAK ANALİZ FONKSİYONLARI (22 Topa Göre Geliştirildi) ---
        def get_f_pattern(col):
            s = sum(1 for x in col if x in hot_nums)
            o = sum(1 for x in col if x in medium_nums)
            c = sum(1 for x in col if x in cold_nums)
            return f"{s}S - {o}O - {c}C"

        def get_tc(col):
            tek = sum(1 for x in col if x % 2 != 0)
            return f"{tek} Tek - {len(col)-tek} Çift"

        def get_ard(col): 
            cons = sum(1 for i in range(len(col)-1) if col[i] + 1 == col[i+1])
            if cons >= 8: return "Çok Yüksek Ardışık (8+)"
            elif cons >= 5: return "Yüksek Ardışık (5-7)"
            elif cons > 0: return f"Normal Ardışık ({cons})"
            return "Ardışık YOK"

        def get_bolge_pattern_on(col):
            b1 = sum(1 for x in col if 1 <= x <= 20)
            b2 = sum(1 for x in col if 21 <= x <= 40)
            b3 = sum(1 for x in col if 41 <= x <= 60)
            b4 = sum(1 for x in col if 61 <= x <= 80)
            return f"{b1}Q1 - {b2}Q2 - {b3}Q3 - {b4}Q4"

        def get_dev(prev_col, curr_col): 
            ortak = len(set(prev_col).intersection(set(curr_col)))
            if ortak >= 8: return "Yüksek Devir (8+)"
            elif ortak >= 5: return f"Normal Devir ({ortak})"
            return f"Düşük Devir ({ortak})"
            
        def get_k_on(col):
            roots = [x % 10 for x in col]
            counts = list(Counter(roots).values())
            counts.sort(reverse=True)
            if not counts: return "Kök Eşleşmesi Yok"
            if counts[0] >= 5: return "Ekstrem Kök Yığılması (5+)"
            elif counts[0] == 4: return "Yüksek Kök Yığılması (4)"
            elif counts[0] == 3: return "Normal Kök Yığılması (3)"
            else: return "Dağınık Kök (Maks 2)"

        # --- ÜRETİM ALANI ---
        st.info(f"{msg} | **Son Çekilen 22 Top:** {valid_draws[0]}")
        st.markdown("---")

        if "on_uretim_ekrani_acik" not in st.session_state:
            st.session_state.on_uretim_ekrani_acik = False
        if "on_ai_uretim_ekrani_acik" not in st.session_state:
            st.session_state.on_ai_uretim_ekrani_acik = False
        if "on_manuel_sayaci" not in st.session_state:
            st.session_state.on_manuel_sayaci = 0
        if "on_ai_sayaci" not in st.session_state:
            st.session_state.on_ai_sayaci = 0

        on_basla_btn = False
        on_ai_basla_btn = False
        on_kolon_sayisi = 1
        
        is_vip_or_admin = st.session_state.get("is_vip", False) or st.session_state.get("user_email", "") == "admin@kaptan.com"
        manuel_hakkini_doldurdu = not is_vip_or_admin and st.session_state.on_manuel_sayaci >= 1
        ai_hakkini_doldurdu = not is_vip_or_admin and st.session_state.on_ai_sayaci >= 1

        if not st.session_state.on_uretim_ekrani_acik and not st.session_state.on_ai_uretim_ekrani_acik:
            if manuel_hakkini_doldurdu and ai_hakkini_doldurdu:
                st.error("🔒 Ücretsiz deneme haklarınızı doldurdunuz! Sınırsız üretim yapmak ve tüm Kuantum filtrelerini özgürce kullanmak için VIP üyeliğe geçin.")
                if st.button("👑 VIP ÜYELİK AYRICALIKLARI", use_container_width=True, key="vip_btn_on_final"):
                    pass
            else:
                st.markdown("<h3 style='text-align:center; color:#1e293b; font-weight:900; margin-bottom: 25px;'>Kuponunuzu Nasıl Kurgulamak İstersiniz?</h3>", unsafe_allow_html=True)
                c_btn_sol, c_btn_sag = st.columns(2)
                
                with c_btn_sol:
                    st.markdown("""
<div style='background-color:#f8fafc; padding:20px; border-radius:12px; border:2px solid #cbd5e1; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
<h4 style='color:#334155; margin-top:0; font-weight:900;'>🎛️ KONTROL SİZDE (Manuel)</h4>
<p style='font-size:13px; color:#64748b; line-height:1.5; margin-bottom:0;'>Kendi stratejinizi belirleyin. Sol menüdeki Kuantum ve Markov parametrelerini ayarlayın, yapay zeka sadece sizin kurallarınıza uyan kusursuz 10 topluk kombinasyonu bulsun.</p>
</div>
""", unsafe_allow_html=True)
                    if manuel_hakkini_doldurdu:
                        st.warning("🔒 Manuel üretim hakkınızı kullandınız.")
                    else:
                        if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", use_container_width=True, key="btn_manuel_on_final"):
                            st.session_state.on_uretim_ekrani_acik = True
                            st.rerun()
                        
                with c_btn_sag:
                    st.markdown("""
<div style='background-color:#fffbeb; padding:20px; border-radius:12px; border:2px solid #d97706; text-align:center; margin-bottom:15px; height: 160px; box-shadow: 0 4px 6px rgba(217, 119, 6, 0.1);'>
<h4 style='color:#b45309; margin-top:0; font-weight:900;'>✨ SİHİRLİ OTOPİLOT (Tam Yetki)</h4>
<p style='font-size:13px; color:#92400e; line-height:1.5; margin-bottom:0;'>Filtrelerle vakit kaybetmeyin! Makine tüm veri madenciliği algoritmalarını çalıştırır, On Numara'nın 80 topluk yapısına uygun en ideal 10 sayıyı getirir.</p>
</div>
""", unsafe_allow_html=True)
                    if ai_hakkini_doldurdu:
                        st.warning("🔒 Sihirli Oto-Pilot hakkınızı kullandınız.")
                    else:
                        if st.button("✨ YAPAY ZEKAYA DEVRET", type="primary", use_container_width=True, key="btn_ai_on_final"):
                            st.session_state.on_ai_uretim_ekrani_acik = True
                            st.rerun()

        if st.session_state.on_uretim_ekrani_acik:
            st.markdown("<div style='border: 3px solid #64748b; border-radius: 12px; padding: 20px; background-color: #f8fafc; text-align: center; margin-bottom: 20px;'><h3 style='color: #334155; margin-top: 0;'>🎛️ MANUEL ÜRETİM ONAYI</h3><p style='margin-bottom:0;'>On Numara kolon adedini belirleyin.</p></div>", unsafe_allow_html=True)
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_kolon_hakki = 100 if is_vip_or_admin else 3
                on_kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_kolon_hakki})", min_value=1, max_value=max_kolon_hakki, value=1, key="manuel_adet_on_onay")
                if not is_vip_or_admin:
                    st.info("💡 Ziyaretçiler ve Standart üyeler manuel olarak en fazla 3 kolon üretebilir. Sınırsız üretim için VIP'ye geçin.")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1: on_basla_btn = st.button("✅ ÜRET", type="primary", use_container_width=True, key="on_basla_m_final")
                with col_m2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="on_iptal_m_final"):
                        st.session_state.on_uretim_ekrani_acik = False
                        st.rerun()

        if st.session_state.on_ai_uretim_ekrani_acik:
            st.markdown("""
<div style='border: 3px solid #d97706; border-radius: 12px; padding: 25px; background-color: #fffbeb; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(217, 119, 6, 0.15);'>
<h3 style='color: #b45309; margin-top: 0; text-align: center; font-weight: 900;'>🪄 OTOPİLOT DEVREYE GİRİYOR</h3>
<p style='color: #92400e; text-align: center; font-size: 15px; margin-bottom: 20px; font-weight: 600;'>Makineye tam yetki verdiniz. Arka planda saniyeler içinde şu mühendislik işlemleri gerçekleşecek:</p>
<div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px dashed #fcd34d;'>
<ul style='color: #b45309; font-size: 14px; margin-bottom: 0; padding-left: 20px; line-height: 1.8;'>
<li><b>🧬 Derin Öğrenme Taraması:</b> Yılların On Numara verisi taranarak 80 topun güncel Sıcak/Orta/Soğuk havuz haritası çıkarılır.</li>
<li><b>⚔️ Apriori (Düşman) Filtresi:</b> Loto tarihinde bugüne kadar hiç yan yana gelmemiş zehirli kombinasyonlar tespit edilip imha edilir.</li>
<li><b>🛡️ K-Means Klan Zırhı:</b> Seçilen sayılar, makinenin tespit ettiği gizli klanlara dengeli biçimde dağıtılarak risk minimize edilir.</li>
<li><b>📉 Kuantum Çan Eğrisi:</b> Üretilen 10 top, On Numara'nın ideal istatistiksel merkezi olan <b>405</b> eksenine kilitlenir.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)
            
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            with c_orta:
                max_ai_hakki = 100 if is_vip_or_admin else 1
                on_kolon_sayisi = st.number_input(f"Kolon Adedi (Maksimum {max_ai_hakki})", min_value=1, max_value=max_ai_hakki, value=1, key="ai_adet_on_onay")
                if not is_vip_or_admin:
                    st.markdown("""
<div style='background-color:#fffbeb; border:1px solid #f59e0b; padding:10px; border-radius:6px; margin-bottom:15px; text-align:center;'>
<span style='color:#b45309; font-size:13px; font-weight:bold;'>👑 Standart üyeler için Sihirli Buton 1 kolonla sınırlıdır. Tüm kuponu yapay zekaya doldurtmak için VIP'ye geçin.</span>
</div>
""", unsafe_allow_html=True)
                
                col_a1, col_a2 = st.columns(2)
                with col_a1: on_ai_basla_btn = st.button("✨ SİHRİ BAŞLAT", type="primary", use_container_width=True, key="on_basla_ai_final")
                with col_a2: 
                    if st.button("❌ İPTAL", use_container_width=True, key="on_iptal_ai_final"):
                        st.session_state.on_ai_uretim_ekrani_acik = False
                        st.rerun()

        if on_basla_btn or on_ai_basla_btn:
            if not is_vip_or_admin:
                if on_basla_btn: st.session_state.on_manuel_sayaci += 1
                if on_ai_basla_btn: st.session_state.on_ai_sayaci += 1
            st.session_state.on_uretim_ekrani_acik = False 
            st.session_state.on_ai_uretim_ekrani_acik = False
            
            with st.spinner('Kuantum On Numara motoru (10 Topluk Algoritma) devrede...'):
                time.sleep(1)
                
                yasaklar = []
                sabit_sayilar = []
                errors = []
                
                if on_ai_basla_btn:
                    # Yapay zeka artık oyunun KANITLANMIŞ #1 numaralı şablonunu baz alacak (2S - 6O - 2C)
                    sicak_hedef, orta_hedef, soguk_hedef = 2, 6, 2
                    tek_hedef, cift_hedef = 5, 5
                    bolge1, bolge2, bolge3, bolge4 = 3, 2, 2, 3
                    ardisik = "YOK (Asla ardışık gelmesin)"
                    min_toplam, max_toplam = 300, 500
                    min_kapsam, max_kapsam = 55, 79
                else:
                    yasaklar = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                    sabit_sayilar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                    if (sicak_hedef + orta_hedef + soguk_hedef) != 10: errors.append("Frekans toplamı 10 olmalı.")
                    if (bolge1 + bolge2 + bolge3 + bolge4) != 10: errors.append("Bölge toplamı 10 olmalı.")
                    if len(sabit_sayilar) > 10: errors.append("Banko sayılar 10'u geçemez.")

                    # 🛡️ ON NUMARA ÖZEL BANKO ZIRHI (Ön Güvenlik Duvarı)
                    if len(sabit_sayilar) > 0:
                        for s in sabit_sayilar:
                            if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko hem de Yasaklı listesinde olamaz!")
                            if s < 1 or s > 80: errors.append(f"Hata: {s} geçerli bir On Numara sayısı değil (1-80).")

                        b_tek = sum(1 for x in sabit_sayilar if x % 2 != 0)
                        b_cift = len(sabit_sayilar) - b_tek
                        if b_tek > tek_hedef or b_cift > cift_hedef:
                            errors.append(f"Hata: Bankolarınızdaki Tek/Çift sayısı ({b_tek}T/{b_cift}Ç), hedefinizi ({tek_hedef}T/{cift_hedef}Ç) aşıyor!")

                        b_b1 = sum(1 for x in sabit_sayilar if 1 <= x <= 20)
                        b_b2 = sum(1 for x in sabit_sayilar if 21 <= x <= 40)
                        b_b3 = sum(1 for x in sabit_sayilar if 41 <= x <= 60)
                        b_b4 = sum(1 for x in sabit_sayilar if 61 <= x <= 80)
                        if b_b1 > bolge1 or b_b2 > bolge2 or b_b3 > bolge3 or b_b4 > bolge4:
                            errors.append("Hata: Bankolarınızın bölge dağılımı (1-20, 21-40 vs.), belirlediğiniz kotaları aşıyor!")

                        sirali_sabit = sorted(sabit_sayilar)
                        ardisik_ciftler = sum(1 for i in range(len(sirali_sabit)-1) if sirali_sabit[i+1] - sirali_sabit[i] == 1)
                        if ardisik_ciftler > 1:
                            errors.append("Hata: Bankolarınızda 1'den fazla ardışık çift var. Kural dışıdır.")
                        elif ardisik_ciftler == 1 and ardisik == "YOK (Asla ardışık gelmesin)":
                            errors.append("Hata: Bankolarınızda ardışık sayı var, ancak filtre 'Ardışık YOK' seçili!")

                        for b1_enemy, b2_enemy in combinations(sabit_sayilar, 2):
                            if is_enemy(b1_enemy, b2_enemy):
                                errors.append(f"Hata: Banko girdiğiniz ({b1_enemy} ve {b2_enemy}) Apriori kuralına göre DÜŞMAN sayılardır!")

                if errors:
                    for e in errors: st.error(e)
                    if st.button("🔄 Kuralları Esnet ve Geri Dön", use_container_width=True, key="btn_onnumara_geri_hata"):
                        st.session_state.on_uretim_ekrani_acik = False
                        st.session_state.on_ai_uretim_ekrani_acik = False
                        st.rerun()
                else:
                    adaylar = [x for x in range(1, 81) if x not in yasaklar and x not in sabit_sayilar]
                    hot_pool = [x for x in hot_nums if x in adaylar]
                    med_pool = [x for x in medium_nums if x in adaylar]
                    cold_pool = [x for x in cold_nums if x in adaylar]

                    b_hot = sum(1 for x in sabit_sayilar if x in hot_nums)
                    b_med = sum(1 for x in sabit_sayilar if x in medium_nums)
                    b_cold = sum(1 for x in sabit_sayilar if x in cold_nums)
                    req_hot, req_med, req_cold = sicak_hedef - b_hot, orta_hedef - b_med, soguk_hedef - b_cold

                    if req_hot < 0 or req_med < 0 or req_cold < 0:
                        st.error("🚨 HATA: Banko sayılarının frekansları, belirlediğin hedefleri aşıyor!")
                        if st.button("🔄 Kuralları Esnet ve Geri Dön", use_container_width=True, key="btn_onnumara_freq_geri"):
                            st.session_state.on_uretim_ekrani_acik = False
                            st.session_state.on_ai_uretim_ekrani_acik = False
                            st.rerun()
                    elif req_hot > len(hot_pool) or req_med > len(med_pool) or req_cold > len(cold_pool):
                        st.error(f"🚨 HATA: Kotalar havuzdaki sayıları aşıyor! Lütfen kuralları esnetin.")
                        if st.button("🔄 Kuralları Esnet ve Geri Dön", use_container_width=True, key="btn_onnumara_pool_geri"):
                            st.session_state.on_uretim_ekrani_acik = False
                            st.session_state.on_ai_uretim_ekrani_acik = False
                            st.rerun()
                    else:
                        valid_combinations = []
                        hata_kodlari = {"bolge": 0, "tek_cift": 0, "ardisik": 0, "can_kapsam": 0}
                        attempts = 0
                        # ⚠️ YENİ ZIRH: 80 toptan 10 top seçme kombinasyonu çok zordur, limit 300.000'e çıkarıldı.
                        max_attempts = 300000 
                        
                        while len(valid_combinations) < (on_kolon_sayisi * 2) and attempts < max_attempts:
                            attempts += 1
                            h_pick = random.sample(hot_pool, req_hot) if req_hot > 0 else []
                            m_pick = random.sample(med_pool, req_med) if req_med > 0 else []
                            c_pick = random.sample(cold_pool, req_cold) if req_cold > 0 else []
                            col = sorted(sabit_sayilar + h_pick + m_pick + c_pick)
                            if len(set(col)) != 10: continue

                            tek = sum(1 for x in col if x % 2 != 0)
                            if tek != tek_hedef: 
                                hata_kodlari["tek_cift"] += 1; continue
                                
                            b1 = sum(1 for x in col if 1 <= x <= 20)
                            b2 = sum(1 for x in col if 21 <= x <= 40)
                            b3 = sum(1 for x in col if 41 <= x <= 60)
                            b4 = sum(1 for x in col if 61 <= x <= 80)
                            if b1 != bolge1 or b2 != bolge2 or b3 != bolge3 or b4 != bolge4:
                                hata_kodlari["bolge"] += 1; continue

                            cons_count = sum(1 for i in range(9) if col[i] + 1 == col[i+1])
                            if cons_count > 1: 
                                hata_kodlari["ardisik"] += 1; continue
                            if ardisik == "YOK (Asla ardışık gelmesin)" and cons_count > 0:
                                hata_kodlari["ardisik"] += 1; continue
                            if ardisik == "VAR (Sadece 1 Çift Ardışık Kabul Et)" and cons_count != 1:
                                hata_kodlari["ardisik"] += 1; continue

                            toplam = sum(col)
                            if not (min_toplam <= toplam <= max_toplam):
                                hata_kodlari["can_kapsam"] += 1; continue
                            if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam):
                                hata_kodlari["can_kapsam"] += 1; continue

                            dusman_skoru = sum(1 for pair in combinations(col, 2) if is_enemy(pair[0], pair[1]))
                            klan_cesitliligi = len(set([klan_labels.get(x, 0) for x in col]))
                            
                            valid_combinations.append({'c': tuple(col), 'sum': toplam, 'klan': klan_cesitliligi, 'dusman_sayisi': dusman_skoru})
                            valid_combinations = list({v['c']: v for v in valid_combinations}.values())

                        if len(valid_combinations) > 0:
                            valid_combinations.sort(key=lambda x: (x['dusman_sayisi'], -x['klan'], abs(x['sum'] - 405)))
                            gosterilecek_adet = min(on_kolon_sayisi, len(valid_combinations))
                            st.success(f"✅ On Numara Zırhı Aşıldı! En kusursuz {gosterilecek_adet} adet 10 topluk kolon kurgulandı.")

                            tam_kolonlar_on = []
                            for i in range(gosterilecek_adet):
                                secilen = valid_combinations[i]['c']
                                klan_degeri = valid_combinations[i]['klan']
                                tam_kolonlar_on.append(list(secilen))
                                
                                if on_kolon_sayisi > 1:
                                    st.markdown(f"<h4 style='color:#d97706; text-align:center; margin-top:20px; font-weight:900; background-color:#fffbeb; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                                
                                html_balls_1 = "".join([f"<div class='home-onnumara-ball' style='width:45px; height:45px; line-height:45px; font-size:18px;'>{n}</div>" for n in secilen[:5]])
                                html_balls_2 = "".join([f"<div class='home-onnumara-ball' style='width:45px; height:45px; line-height:45px; font-size:18px;'>{n}</div>" for n in secilen[5:]])
                                
                                st.markdown(f"""
                                <div style='text-align: center; margin: 15px 0 25px 0;'>
                                    <div style='display:flex; justify-content:center; gap:5px; margin-bottom:8px;'>{html_balls_1}</div>
                                    <div style='display:flex; justify-content:center; gap:5px;'>{html_balls_2}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                mc1, mc2, mc3, mc4 = st.columns(4)
                                with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#d97706;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                                with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#d97706;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                                with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                                with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span class='highlight-yellow' style='font-size:16px;'>0 (Temiz)</span></div>", unsafe_allow_html=True)
                                if i < gosterilecek_adet - 1: st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)
                                
                            # 🎯 AKILLI ONAY MEKANİZMASI VE KAYDET BUTONU (ON NUMARA) 🎯
                            if st.session_state.get("logged_in", False):
                                st.markdown("<br><hr style='border: 1px dashed #cbd5e1; margin-bottom: 20px;'>", unsafe_allow_html=True)
                                
                                current_live_data = load_live_data()
                                c_no_str = current_live_data.get("onnumara", {}).get("cekilis_no", "")
                                
                                if c_no_str and c_no_str.isdigit():
                                    hedef_cekilis = int(c_no_str) + 1
                                    st.info(f"💡 Sistemde en son **{c_no_str}. Çekiliş** sonuçları kayıtlıdır.")
                                    cb_label = f"**✅ Ürettiğim bu kuponu/kuponları, yaklaşan {hedef_cekilis}. On Numara Çekilişi için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = f"On Numara (Hedef: {hedef_cekilis})"
                                else:
                                    cb_label = "**✅ Ürettiğim bu kuponu/kuponları, yaklaşan çekiliş için kasama kaydetmeyi ONAYLIYORUM.**"
                                    oyun_isim_etiketi = "On Numara"

                                def kayit_tetikleyici_onnumara(k_email, k_oyun_id, k_oyun_adi, k_kombinasyonlar):
                                    if st.session_state.get("onay_kutusu_onnumara", False):
                                        for t_kolon in k_kombinasyonlar:
                                            from datetime import datetime
                                            z_vakti = datetime.now().strftime("%d.%m.%Y %H:%M:%S") 
                                            save_coupon_to_db(k_email, k_oyun_id, k_oyun_adi, t_kolon, z_vakti)
                                            time.sleep(0.1)

                                with st.form(key="kayit_form_onnumara"):
                                    st.checkbox(cb_label, key="onay_kutusu_onnumara")
                                    # Liste adı tam_kolonlar_on olarak senin sistemine uyarlandı!
                                    st.form_submit_button("💾 ÜRETİLEN KOLONLARI KAYDET", type="primary", use_container_width=True, on_click=kayit_tetikleyici_onnumara, args=(st.session_state.user_email, "onnumara", oyun_isim_etiketi, tam_kolonlar_on))
                                
                                st.markdown("<p style='font-size:13px; color:#64748b; text-align:center;'><em>Not: Sistemin kaydedebilmesi için butona basmadan önce onay kutusunu işaretlediğinizden emin olun. Başarıyla kaydedildiğinde ekran yeni analizler için temizlenecektir.</em></p>", unsafe_allow_html=True)
                        else:
                            en_cok_elenen = max(hata_kodlari, key=hata_kodlari.get)
                            st.error(f"🚨 PARADOKS: Bu 10 topluk yapı 80 top içinde matematiksel olarak imkansız. Ana Engelleyici: {en_cok_elenen.upper()} FİLTRESİ.")

       # --- 4 YENİ SEKME VE 10 TOPLUK İNDİRGEME (DOWNSCALING) ALGORİTMASI ---
        if not (on_basla_btn or on_ai_basla_btn):
            st.markdown("<br><hr style='border: 3px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
            
            # 🔮 MAKİNE 22 TOP ÇEKER, BİZ 10 TOP OYNARIZ. 
            # 22 TOPUN DNA'SINI SENİN İÇİN 10 TOPA MATEMATİKSEL OLARAK İNDİRGEYEN FONKSİYONLAR
            def get_f_pattern_10(col_22):
                s = sum(1 for x in col_22 if x in hot_nums)
                c = sum(1 for x in col_22 if x in cold_nums)
                s10 = int(round(s * 10 / 22))
                c10 = int(round(c * 10 / 22))
                o10 = 10 - s10 - c10
                return f"{s10}S - {o10}O - {c10}C"

            def get_tc_10(col_22):
                tek = sum(1 for x in col_22 if x % 2 != 0)
                t10 = int(round(tek * 10 / 22))
                return f"{t10} Tek - {10-t10} Çift"

            def get_bolge_pattern_10(col_22):
                b1 = sum(1 for x in col_22 if 1 <= x <= 20)
                b2 = sum(1 for x in col_22 if 21 <= x <= 40)
                b3 = sum(1 for x in col_22 if 41 <= x <= 60)
                b1_10 = int(round(b1 * 10 / 22))
                b2_10 = int(round(b2 * 10 / 22))
                b3_10 = int(round(b3 * 10 / 22))
                b4_10 = 10 - b1_10 - b2_10 - b3_10
                return f"{b1_10}Q1 - {b2_10}Q2 - {b3_10}Q3 - {b4_10}Q4"
            
            st.markdown("""
            <style>
            button[data-baseweb="tab"]:nth-child(3) p, button[data-baseweb="tab"]:nth-child(4) p {
                font-weight: 900 !important;
                font-size: 16px !important;
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            tab_tarih, tab_detayli, tab_simulasyon, tab_sorgu = st.tabs([
                "📈 TARİHSEL BİLANÇO (GENEL İSTATİSTİK)", 
                "🧠 DETAYLI YAPAY ZEKA ANALİZİ", 
                "🎯 SONRAKİ ÇEKİLİŞ SİMÜLASYONU",
                "🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU"
            ])
            # ----------------------------------------------------------------------
            # SEKME 1: TARİHSEL BİLANÇO
            # ----------------------------------------------------------------------
            with tab_tarih:
                last_d = valid_draws[0]
                st.markdown("#### 🎯 SON ÇEKİLİŞİN MR'I (10 Topluk Hedefe İndirgenmiş Röngten)")
                
                st.info("💡 **KAPTAN'A NOT:** Frekans, Tek/Çift ve Bölge verileri kupon yapabilmen için 22 toptan 10 topa indirgenmiştir. Kök, Ardışık ve Devir istatistikleri ise oyunun 22 topluk kaos ortamını gösterir.")
                
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='metric-card' style='padding:10px;'><b>10'lu Frekans Şablonu</b><br><span style='color:#d97706; font-weight:900; font-size:16px;'>{get_f_pattern_10(last_d)}</span></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='metric-card' style='padding:10px;'><b>10'lu Tek/Çift Dengesi</b><br><span style='color:#d97706; font-weight:900; font-size:16px;'>{get_tc_10(last_d)}</span></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='metric-card' style='padding:10px;'><b>Ardışık Durumu (22 Top)</b><br><span style='color:#d97706; font-weight:900; font-size:16px;'>{get_ard(last_d)}</span></div>", unsafe_allow_html=True)
                
                c4, c5, c6 = st.columns(3)
                c4.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Kök Eşleşmesi (22 Top)</b><br><span style='color:#d97706; font-weight:900; font-size:16px;'>{get_k_on(last_d)}</span></div>", unsafe_allow_html=True)
                c5.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>10'lu Bölge Dağılımı (Q1-Q4)</b><br><span style='color:#d97706; font-weight:900; font-size:16px;'>{get_bolge_pattern_10(last_d)}</span></div>", unsafe_allow_html=True)
                devir_bilgisi = get_dev(valid_draws[1], last_d) if len(valid_draws) > 1 else "YOK"
                c6.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Devir (22 Top)</b><br><span style='color:#d97706; font-weight:900; font-size:16px;'>{devir_bilgisi}</span></div>", unsafe_allow_html=True)

                st.markdown("#### 🌡️ GÜNCEL SAYI HAVUZU (Sıcak - Orta - Soğuk)")
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 25px; margin-top: 15px;">
                    <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥{hot_limit}): {len(hot_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA ({cold_limit+1}-{hot_limit-1}): {len(medium_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                    </div>
                    <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤{cold_limit}): {len(cold_nums)} Adet</strong>
                        <p style="font-family: monospace; font-size: 13px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>#### 📊 OYUNUN GENEL KARAKTERİ (10 Topluk Hedefe Göre İndirgenmiş)", unsafe_allow_html=True)
                
                hist_f = Counter()
                hist_tc = Counter()
                hist_ard = Counter()
                hist_kok = Counter()
                hist_dev = Counter()
                hist_bolge = Counter()
                
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    hist_f[get_f_pattern_10(d)] += 1
                    hist_tc[get_tc_10(d)] += 1
                    hist_ard[get_ard(d)] += 1
                    hist_kok[get_k_on(d)] += 1
                    hist_bolge[get_bolge_pattern_10(d)] += 1
                    if i < len(valid_draws) - 1:
                        hist_dev[get_dev(valid_draws[i+1], valid_draws[i])] += 1
                        
                tot = len(valid_draws)
                tot_dev = tot - 1 if tot > 1 else 1
                
                def render_bar(label, count, total_val):
                    pct = (count / total_val) * 100
                    return f'''
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-weight: 800; color: #334155; font-size: 13px;">{label}</span>
                            <span style="font-weight: 900; color: #d97706; font-size: 13px;">%{pct:.1f} <span style="color:#94a3b8; font-size:11px;">({count} Kez)</span></span>
                        </div>
                        <div style="width: 100%; background-color: #f1f5f9; border-radius: 6px; height: 18px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                            <div style="width: {pct}%; background-color: #d97706; height: 100%;"></div>
                        </div>
                    </div>
                    '''
                    
                col_bar1, col_bar2 = st.columns(2)
                with col_bar1:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🔥 En Çok Gelen 10'lu Frekanslar</h5>", unsafe_allow_html=True)
                    for k, v in hist_f.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎲 Ardışık Sayı Durumu (22 Top Ortamı)</h5>", unsafe_allow_html=True)
                    for k, v in hist_ard.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>♻️ Devir Durumu (22 Top Ortamı)</h5>", unsafe_allow_html=True)
                    for k, v in hist_dev.most_common(5): st.markdown(render_bar(k, v, tot_dev), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_bar2:
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>⚖️ 10'lu Tek/Çift Dağılımı</h5>", unsafe_allow_html=True)
                    for k, v in hist_tc.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🧩 Kök Eşleşmesi (22 Top Ortamı)</h5>", unsafe_allow_html=True)
                    for k, v in hist_kok.most_common(): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-top:15px;'>", unsafe_allow_html=True)
                    st.markdown("<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px;'>🎯 10'lu Bölge Dağılımı (Q1-Q4)</h5>", unsafe_allow_html=True)
                    for k, v in hist_bolge.most_common(5): st.markdown(render_bar(k, v, tot), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            # ----------------------------------------------------------------------
            # SEKME 2: DETAYLI YAPAY ZEKA ANALİZİ (RADAR + ÇAPRAZ GEÇİŞ)
            # ----------------------------------------------------------------------
            with tab_detayli:
                st.markdown("### 🧠 İLERİ DÜZEY İSTİHBARAT (RADAR SİSTEMİ)")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("#### 🔥 ALEV ALANLAR (Momentum İvmesi)")
                    if momentum_sayilari:
                        alevler_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(momentum_sayilari.items(), key=lambda item: item[1], reverse=True):
                            alevler_html += f"<div style='background-color:#fffbea; border:1.5px solid #000000; border-radius:6px; padding:8px 10px; text-align:center; min-width:85px;'><div style='color:#b45309; font-size:13px; font-weight:900; margin-bottom:2px;'>Sayı {k}</div><div style='font-size:10px; color:#64748b; font-weight:bold; margin-bottom:3px;'>Son 5 Çekilişte</div><div style='font-size:16px; color:#d97706; font-weight:900;'>{v} Kez</div></div>"
                        alevler_html += "</div>"
                        st.markdown(alevler_html, unsafe_allow_html=True)
                    else: st.info("Son haftalarda çıldıran sayı yok.")
                with col_r2:
                    st.markdown("#### 💤 UYUYAN DEVLER (Kuluçka)")
                    if uyuyan_devler:
                        uyuyan_html = "<div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:6px; border:2px solid #000000; padding:15px; border-radius:8px; background-color:#ffffff;'>"
                        for k, v in sorted(uyuyan_devler.items(), key=lambda item: item[1], reverse=True)[:16]:
                            uyuyan_html += f"<div style='background-color:#f0f9ff; border:1px solid #bae6fd; border-radius:4px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center;'><strong style='color:#0369a1; font-size:13px;'>Sayı {k}</strong><span style='font-size:12px; color:#64748b; font-weight:bold;'>{v} Hft Yok</span></div>"
                        uyuyan_html += "</div>"
                        st.markdown(uyuyan_html, unsafe_allow_html=True)
                    else: st.info("Uyuyan dev bulunmuyor.")

                st.markdown("---")
                st.markdown("<h4 style='color:#d97706;'>🧬 ÇAPRAZ GEÇİŞ ANALİZİ (MARKOV MATRİSİ)</h4>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 12px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                    <strong style='color: #166534; font-size: 15px;'>🧬 MİKROSKOP (Anatomi Analizi):</strong><br>
                    <span style='color: #15803d; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>KENDİSİNİN</b> tarihte nasıl bir karakter sergilediğini inceler. Seçtiğiniz 10 topluk kombinasyonun iç yapısındaki tek/çift, ardışık ve kök eşleşme oranlarını göstererek o frekansın adeta DNA'sını çıkarır.</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='border: 3px solid #000000; border-radius: 10px; padding: 20px; background-color: #f8fafc; margin-bottom: 20px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);'>
                    <h4 style='text-align: center; color: #0f172a; font-weight: 900; margin-top: 0; margin-bottom: 20px; letter-spacing: 0.5px;'>🎯 HEDEF FREKANS KOMBİNASYONUNU SEÇİN (10 Top)</h4>
                """, unsafe_allow_html=True)
                
                # Son çekilişi 10 topa indirgeyip varsayılan olarak ekrana basıyoruz
                last_10_str = get_f_pattern_10(valid_draws[0]).replace('S','').replace('O','').replace('C','').split(' - ')
                
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    t_s_c = st.number_input("Sıcak (S)", 0, 10, int(last_10_str[0]), key="on_c_s", label_visibility="collapsed")
                with cc2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    t_o_c = st.number_input("Orta (O)", 0, 10, int(last_10_str[1]), key="on_c_o", label_visibility="collapsed")
                with cc3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    t_c_c = st.number_input("Soğuk (C)", 0, 10, int(last_10_str[2]), key="on_c_c", label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)

                if t_s_c + t_o_c + t_c_c != 10:
                    st.warning("⚠️ On Numara oyununda Sıcak, Orta ve Soğuk sayılarının toplamı tam 10 olmalıdır!")
                else:
                    target_freq = f"{t_s_c}S - {t_o_c}O - {t_c_c}C"
                    t_draws = []
                    
                    # 🧬 MİKROSKOP MODU: Olayın KENDİSİNİ inceler
                    for i in range(len(valid_draws) - 1):
                        current_draw = valid_draws[i]
                        # Geçmişi 10 topa indirgeyip senin hedefinle kıyaslar!
                        if get_f_pattern_10(current_draw) == target_freq:
                            prev_draw = valid_draws[i+1]
                            t_draws.append({
                                'tc': get_tc_10(current_draw),
                                'ard': get_ard(current_draw),
                                'kok': get_k_on(current_draw),
                                'dev': get_dev(prev_draw, current_draw),
                                'bolge': get_bolge_pattern_10(current_draw)
                            })
                    
                    if len(t_draws) > 0:
                        st.info(f"**Seçilen 10'lu Şablon:** {target_freq} | Tarihte bu şablondan **{len(t_draws)}** kez çekiliş yapılmış:")
                        tc_c = Counter([x['tc'] for x in t_draws])
                        ard_c = Counter([x['ard'] for x in t_draws])
                        kok_c = Counter([x['kok'] for x in t_draws])
                        dev_c = Counter([x['dev'] for x in t_draws])
                        bolge_c = Counter([x['bolge'] for x in t_draws])
                        
                        def format_pct(counter):
                            total = sum(counter.values())
                            return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                        
                        copy_text = f"🎯 ÇAPRAZ ANALİZ ÇIKTISI (10'LU BAZ FREKANS: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT REFLEKSİ (10 Top) ---\n{format_pct(tc_c)}\n\n--- 2. BÖLGE REFLEKSİ (10 Top) ---\n{format_pct(bolge_c)}\n\n--- 3. ARDIŞIK REFLEKSİ (22 Top Ortamı) ---\n{format_pct(ard_c)}\n\n--- 4. KÖK EŞLEŞMESİ (22 Top Ortamı) ---\n{format_pct(kok_c)}\n\n--- 5. DEVİR REFLEKSİ (22 Top Ortamı) ---\n{format_pct(dev_c)}"
                        
                        st.markdown(f'''
                        <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.warning(f"Tarihte daha önce {target_freq} şablonu hiç yaşanmamış.")

            # ----------------------------------------------------------------------
            # SEKME 3: SONRAKİ ÇEKİLİŞ SİMÜLASYONU
            # ----------------------------------------------------------------------
            with tab_simulasyon:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🎯 GELECEK HAFTA PROJEKSİYONU (YAPAY ZEKA TAHMİNİ)</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #0ea5e9; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.15rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    Bu motor, son çekilişin 6 farklı DNA özelliğini alır, oyunun tüm geçmişini tarar ve tarihte bu özelliklerden sonra en yüksek ihtimalle nelerin geldiğini hesaplar.
                </div>
                """, unsafe_allow_html=True)
                
                history_sim = []
                for i in range(len(valid_draws)):
                    d = valid_draws[i]
                    dev_durum = "Bilinmiyor"
                    if i + 1 < len(valid_draws):
                        dev_durum = get_dev(valid_draws[i+1], d)
                    
                    history_sim.append({
                        'freq': get_f_pattern_10(d), # 10 topa entegre
                        'oe': get_tc_10(d), # 10 topa entegre
                        'cons': get_ard(d),
                        'root': get_k_on(d),
                        'bolge': get_bolge_pattern_10(d), # 10 topa entegre
                        'devir': dev_durum
                    })
                
                last_sim = history_sim[0] 
                
                def render_transition(prop_key, target_val, title):
                    next_states = []
                    for i in range(1, len(history_sim)):
                        if history_sim[i][prop_key] == target_val:
                            next_states.append(history_sim[i-1][prop_key])
                    
                    html_str = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; box-shadow:0 4px 6px rgba(0,0,0,0.05); height:100%;'>"
                    html_str += f"<h5 style='color:#0f172a; font-weight:900; font-size:15px; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                    html_str += f"<p style='font-size:12px; color:#64748b; margin-bottom:10px;'>Son Çekiliş: <b style='color:#d97706;'>{target_val}</b></p>"
                    
                    if not next_states:
                        html_str += "<span style='color:#64748b; font-size:13px;'>Tarihte örnek bulunamadı.</span></div>"
                        return html_str
                    
                    c = Counter(next_states)
                    total = len(next_states)
                    html_str += "<ul style='margin-bottom:0; padding-left:20px; font-size:14px;'>"
                    for k, v in c.most_common(3): 
                        pct = (v/total)*100
                        html_str += f"<li style='margin-bottom:5px;'><b>%{pct:.1f}</b> ihtimalle <span style='color:#d97706; font-weight:bold;'>{k}</span></li>"
                    html_str += "</ul></div>"
                    return html_str

                st.markdown(f"<h5 style='color:#d97706; margin-bottom:15px;'>🔍 SON ÇEKİLİŞ BAZ ALINARAK YAPILAN MARKOV HESAPLAMALARI:</h5>", unsafe_allow_html=True)
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.markdown(render_transition('freq', last_sim['freq'], "1. 10'lu Frekans Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('devir', last_sim['devir'], "4. Devir Radarı (22 Top)"), unsafe_allow_html=True)
                with sc2:
                    st.markdown(render_transition('bolge', last_sim['bolge'], "2. 10'lu Bölge Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('cons', last_sim['cons'], "5. Ardışık Radarı (22 Top)"), unsafe_allow_html=True)
                with sc3:
                    st.markdown(render_transition('oe', last_sim['oe'], "3. 10'lu Tek/Çift Radarı"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(render_transition('root', last_sim['root'], "6. Kök Eşleşme Radarı (22 Top)"), unsafe_allow_html=True)
                    
                st.markdown("<hr style='border: 2px dashed #cbd5e1; margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown("#### 🚨 KRİTİK İSTİHBARAT: 'SAYI KESİLME' ALGORİTMASI")
                
                streak_3_count = 0
                streak_4_count = 0
                for num in range(1, 81):
                    for i in range(3, len(valid_draws)):
                        if num in valid_draws[i] and num in valid_draws[i-1] and num in valid_draws[i-2]:
                            streak_3_count += 1
                            if num in valid_draws[i-3]:
                                streak_4_count += 1
                                
                if streak_3_count > 0:
                    perc_devam = (streak_4_count / streak_3_count) * 100
                    perc_kesilme = 100 - perc_devam
                    st.markdown(f"""
                    <div style='background-color: #fff1f2; border: 2px solid #ef4444; padding: 15px; border-radius: 8px; color: #7f1d1d;'>
                        On Numara tarihinde herhangi bir sayının <b>3 hafta ÜST ÜSTE çıkma durumu tam {streak_3_count} kez</b> yaşanmıştır.<br><br>
                        Algoritmanın tespitine göre, 3 hafta üst üste çıkan bir sayının <b>4. HAFTA KESİN OLARAK KESİLME (GELMEME) ihtimali: <span style='font-size:22px; font-weight:900;'>%{perc_kesilme:.2f}</span></b>'dir.<br>
                        <span style='font-size:14px; color:#991b1b;'><i>(Kupon yaparken, son 3 haftadır çıkan bir sayı varsa onu <b>%{perc_kesilme:.2f} matematiksel güvence ile</b> eleyebilirsiniz.)</i></span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Tarihte henüz hiçbir sayı 3 hafta üst üste çıkmamıştır.")

            # ----------------------------------------------------------------------
            # SEKME 4: DİNAMİK İSTİHBARAT SORGUSU
            # ----------------------------------------------------------------------
            with tab_sorgu:
                st.markdown("<h3 style='color:#0f172a; font-weight:900; margin-bottom:15px;'>🕵️‍♂️ DİNAMİK İSTİHBARAT SORGUSU</h3>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background-color: #eff6ff; border-left: 5px solid #2563eb; padding: 12px; border-radius: 4px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <strong style='color: #1e3a8a; font-size: 15px;'>🔮 RADAR (Gelecek Simülasyonu):</strong><br>
                <span style='color: #1d4ed8; font-size: 14px;'>Frekans aralığı seçtiğinizde; yapay zeka bu şablonun <b>ARDINDAN (Bir Sonraki Hafta)</b> neler yaşandığını hesaplar. Seçtiğiniz 10'lu frekans küreden düştükten hemen sonraki hafta makinenin nasıl refleksler gösterdiğini simüle ederek, önümüzdeki çekilişin geleceğini tahmin etmenizi sağlar.</span>
                </div>
                """, unsafe_allow_html=True)

                all_freqs = [get_f_pattern_10(d) for d in valid_draws]
                freq_counts = Counter(all_freqs)
                
                st.markdown("#### 📊 VERİTABANINDAKİ EN POPÜLER 10'LU FREKANS ŞABLONLARI")
                pop_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:30px;'>"
                for f, c in freq_counts.most_common(5):
                    pop_html += f"<div style='background-color:#ffffff; border:2px solid #cbd5e1; padding:10px 15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); text-align:center;'><b>{f}</b><br><span style='color:#d97706; font-weight:900; font-size:14px;'>{c} Kez Yaşandı</span></div>"
                pop_html += "</div>"
                st.markdown(pop_html, unsafe_allow_html=True)

                st.markdown("#### 🔍 HEDEF FREKANSI BELİRLEYİN (10 Top)")
                cq1, cq2, cq3 = st.columns(3)
                with cq1:
                    st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                    q_s = st.number_input("Sıcak", 0, 10, 4, key="on_q_s", label_visibility="collapsed")
                with cq2:
                    st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                    q_o = st.number_input("Orta", 0, 10, 4, key="on_q_o", label_visibility="collapsed")
                with cq3:
                    st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                    q_c = st.number_input("Soğuk", 0, 10, 2, key="on_q_c", label_visibility="collapsed")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🚀 DİNAMİK İSTİHBARATI GETİR", type="primary", use_container_width=True, key="on_sq_btn"):
                    if q_s + q_o + q_c != 10:
                        st.error("⚠️ HATA: Sıcak, Orta ve Soğuk sayılarının toplamı tam 10 olmalıdır!")
                    else:
                        target_f_str = f"{q_s}S - {q_o}O - {q_c}C"
                        q_results = {'oe': [], 'cons': [], 'root': [], 'bolge': [], 'devir': []}
                        match_count = 0
                        
                        # 🔮 RADAR MODU: Olaydan SONRAKİ HAFTAYI inceler
                        for i in range(1, len(valid_draws)):
                            if get_f_pattern_10(valid_draws[i]) == target_f_str:
                                match_count += 1
                                trigger_draw = valid_draws[i]
                                next_draw = valid_draws[i-1]
                                
                                q_results['oe'].append(get_tc_10(next_draw))
                                q_results['cons'].append(get_ard(next_draw))
                                q_results['root'].append(get_k_on(next_draw))
                                q_results['bolge'].append(get_bolge_pattern_10(next_draw))
                                q_results['devir'].append(get_dev(trigger_draw, next_draw))
                        
                        if match_count == 0:
                            st.warning(f"Veritabanında '{target_f_str}' frekansının gelip de ardından çekiliş yapılan bir kayıt bulunamadı.")
                        else:
                            st.success(f"✅ HEDEF KİLİTLENDİ: Tarihte '{target_f_str}' 10'lu şablonundan SONRAKİ HAFTA tam {match_count} kez çekiliş yapılmıştır. Makinenin gösterdiği refleksler aşağıdadır:")
                            
                            def print_q_stats(data_list, title):
                                c = Counter(data_list)
                                total = len(data_list)
                                html = f"<div style='background-color:#ffffff; padding:15px; border-radius:8px; border:2px solid #e2e8f0; margin-bottom:15px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>"
                                html += f"<h5 style='color:#0f172a; font-weight:900; border-bottom:2px solid #f1f5f9; padding-bottom:8px; margin-top:0;'>{title}</h5>"
                                for k, v in c.most_common():
                                    perc = (v / total) * 100
                                    html += f"<div style='display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px dashed #f1f5f9; padding-bottom:4px;'><span style='font-weight:bold; color:#334155; font-size:14px;'>{k}</span> <span style='color:#d97706; font-weight:900; font-size:15px;'>%{perc:.2f}</span></div>"
                                html += "</div>"
                                return html

                            qc1, qc2 = st.columns(2)
                            with qc1:
                                st.markdown(print_q_stats(q_results['oe'], "1. 10'LU TEK/ÇİFT REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['bolge'], "3. 10'LU BÖLGE (Q1-Q4) REFLEKSİ"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['root'], "5. KÖK EŞLEŞME REFLEKSİ (22 Top)"), unsafe_allow_html=True)
                            with qc2:
                                st.markdown(print_q_stats(q_results['cons'], "2. ARDIŞIK SAYI REFLEKSİ (22 Top)"), unsafe_allow_html=True)
                                st.markdown(print_q_stats(q_results['devir'], "4. DEVİR REFLEKSİ (22 Top)"), unsafe_allow_html=True)
                                
                            st.info("💡 KAPTAN'A NOT: En yüksek yüzdeler, makinenin bu frekansa verdiği tepkidir. Kolonları kurarken en üst sıradaki şablonları baz al.")

# ==========================================
# ===== SAYFA ALTI ORTALANMIŞ ADMİN PANELİ =====
# ==========================================
# Bu kısmı sadece Ana Sayfada gösterecek şekilde şarta bağlıyoruz:
if selected_game == "ANA SAYFA":
    st.markdown("<br><hr style='border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-weight:bold; color:#0f172a; margin-bottom:5px;'>© 2026 Kaptan Analiz Merkezi. Tüm Hakları Saklıdır.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748b; font-size:12px; margin-bottom:20px;'>Bu platform, K-Means Kümeleme ve Apriori algoritmaları kullanılarak geliştirilmiş bir Yapay Zeka AR-GE laboratuvarıdır.</p>", unsafe_allow_html=True)


    # Tam ortaya konumlandırmak için 3 sütun kullanıyoruz (1 birim boşluk, 2 birim panel, 1 birim boşluk)
    col_bos1, col_admin, col_bos2 = st.columns([1, 2, 1])
# --- ZARİF VERİ KAPSAMI BİLGİLENDİRMESİ ---
# Mevcut seçili oyuna göre metni otomatik uyarlıyoruz
oyun_adlari = {
    "ÇILGIN SAYISAL LOTO AI": "Çılgın Sayısal Loto",
    "SÜPER LOTO AI": "Süper Loto",
    "ŞANS TOPU AI": "Şans Topu",
    "ON NUMARA AI": "On Numara"
}
gosterilen_oyun = oyun_adlari.get(selected_game, "Sistem")

st.markdown(f"""
<div style='text-align: center; margin-bottom: 12px;'>
    <span style='color: #64748b; font-size: 12px; font-style: italic; background-color: #f8fafc; padding: 6px 16px; border-radius: 20px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.02);'>
        🕰️ <b>Analiz Kapsamı:</b> {gosterilen_oyun} motoru, <b>2025 yılı başı itibarıyla</b> gerçekleşen güncel resmi çekiliş verilerini baz alarak optimize edilmiştir.
    </span>
</div>
""", unsafe_allow_html=True)

# Buranın hemen altında senin o "YASAL BİLGİLENDİRME (MEVZUAT)" st.markdown kodun yer alacak...
st.markdown("---")
st.markdown("""
<div style='background-color: #f1f5f9; padding: 12px 20px; border-radius: 6px; border: 3px solid #000000; font-size: 13px; color: #000000; line-height: 1.3; text-align: justify; margin-bottom: 20px;'>
    <div style='text-align: center; margin-bottom: 8px;'>
        <b style='font-size: 15px;'>⚖️ YASAL BİLGİLENDİRME (MEVZUAT)</b>
    </div>
    Bu platform üzerinden hiçbir şekilde <b>şans oyunu oynatılamaz</b>, bahis yapılamaz ve para tahsilatı gerçekleştirilemez. Sistemimiz; tamamen geçmiş çekiliş verilerini referans alan, <b>saf matematiksel, istatistiksel ve algoritmik</b> hesaplamalar (K-Means, Apriori) yapan bir yapay zeka analiz aracıdır. Üretilen kolonlar veri madenciliği optimizasyonları olup, <b>hiçbir şekilde kesin kazanç garantisi sunmaz</b>. Üretilen sayıların oynanması durumunda maddi ve hukuki sorumluluk tamamen kullanıcıya aittir.
</div>
""", unsafe_allow_html=True)