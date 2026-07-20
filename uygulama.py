import streamlit as st
import pandas as pd
from collections import Counter
import glob
import numpy as np
from itertools import combinations
import random
from sklearn.cluster import KMeans
import os
import time
import requests
import cloudscraper  
from bs4 import BeautifulSoup
import re
import base64
import sqlite3
import hashlib

from streamlit_option_menu import option_menu # YENİ MODERN MENÜ MODÜLÜ

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yapay Zeka Loto Analiz Merkezi", page_icon="🧿", layout="wide")

# --- EVRENSEL CSS VE WHITE-LABEL (İZ SİLME) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} /* Sağ üstteki menüyü gizler */
    header {visibility: hidden;} /* Deploy butonunu gizler */
    footer {visibility: hidden;} /* Streamlit yazısını gizler */
    .stDeployButton {display:none;}
    
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
    
    /* SEKME (TAB) BAŞLIKLARI ÖZEL TASARIMI */
    button[data-baseweb="tab"] p { font-weight: 900 !important; font-size: 17px !important; letter-spacing: 0.5px !important; }
    
    /* ANA EKRANDAKİ KOLON ADEDİ KUTUSUNU DEVLEŞTİRME VE VURGULAMA */
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInput"] div[data-baseweb="input"] {
        border: 3px solid #1e3a8a !important; 
        border-radius: 8px !important;
        background-color: #ffffff !important;
        padding: 4px !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInput"] input {
        font-size: 28px !important; 
        font-weight: 900 !important; 
        color: #dc2626 !important; 
        text-align: center !important; 
    }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepUp"], 
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepDown"] {
        background-color: #f1f5f9 !important;
        width: 45px !important; 
        border-radius: 6px !important;
    }
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepUp"] svg, 
    [data-testid="stMainBlockContainer"] [data-testid="stNumberInputStepDown"] svg {
        fill: #1e3a8a !important; 
        width: 22px !important;
        height: 22px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM HAFIZASI (KASA VE VIP KONTROLÜ) ---
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

if "saved_coupons" not in st.session_state:
    st.session_state.saved_coupons = []
# ==========================================
# 0. PROFESYONEL VERİTABANI & CRM MİMARİSİ
# ==========================================
def init_db():
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    # Kullanıcılar Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE,
                  password TEXT,
                  is_vip INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Kişisel Kupon Kasası Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS coupons
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_email TEXT,
                  game_id TEXT,
                  game_name TEXT,
                  nums TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

# Uygulama açılır açılmaz veritabanını hazırla
init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    try:
        conn = sqlite3.connect('kuantum_users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError: # Email zaten kayıtlıysa
        return False

def verify_user(email, password):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    c.execute("SELECT is_vip FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user # Eğer doğruysa (is_vip,), yanlışsa None döner

def save_coupon_to_db(email, game_id, game_name, nums, timestamp):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    # Listeyi text formatına (örn: "5,12,34,45,67,89") çevirerek kaydediyoruz
    nums_str = ",".join(map(str, nums))
    c.execute("INSERT INTO coupons (user_email, game_id, game_name, nums, timestamp) VALUES (?, ?, ?, ?, ?)",
              (email, game_id, game_name, nums_str, timestamp))
    conn.commit()
    conn.close()

def get_user_coupons(email):
    conn = sqlite3.connect('kuantum_users.db')
    c = conn.cursor()
    c.execute("SELECT game_id, game_name, nums, timestamp FROM coupons WHERE user_email=? ORDER BY id DESC", (email,))
    coupons = c.fetchall()
    conn.close()
    
    # Veritabanından gelen stringleri tekrar listeye çeviriyoruz
    parsed_coupons = []
    for cp in coupons:
        nums_list = [int(n) for n in cp[2].split(",")]
        parsed_coupons.append({
            "game": cp[0], "game_name": cp[1], "nums": nums_list, "timestamp": cp[3]
        })
    return parsed_coupons

# --- YENİ SİSTEM HAFIZASI ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

# --- VERİ ÇEKME FONKSİYONLARI (DOKUNULMADI) ---
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
            
    try:
        if data['sayisal']['nums']:
            fp = 'çlgn_sysl.xlsx'
            if os.path.exists(fp):
                df = pd.read_excel(fp)
                m = re.search(r'\[(\d+)\]', data['sayisal']['date'])
                if m:
                    cno = int(m.group(1))
                    if cno not in df['Cekilis_No'].values:
                        t = re.search(r'-\s*(.*)', data['sayisal']['date'])
                        tarih = t.group(1).strip() if t else data['sayisal']['date']
                        nums = data['sayisal']['nums']
                        nr = {'Cekilis_No': cno, 'Tarih': tarih, 
                              'T1': int(nums[0]), 'T2': int(nums[1]), 'T3': int(nums[2]), 
                              'T4': int(nums[3]), 'T5': int(nums[4]), 'T6': int(nums[5]),
                              'Joker': int(data['sayisal'].get('plus', 0)) if str(data['sayisal'].get('plus', '')).isdigit() else "-",
                              'SuperStar': int(data['sayisal'].get('superstar', 0)) if str(data['sayisal'].get('superstar', '')).isdigit() else "-"}
                        df = pd.concat([pd.DataFrame([nr]), df], ignore_index=True)
                        df.to_excel(fp, index=False)
                        
        if data['sans']['nums']:
            fp = 'şns_topu.xlsx'
            if os.path.exists(fp):
                df = pd.read_excel(fp)
                m = re.search(r'\[(\d+)\]', data['sans']['date'])
                if m:
                    cno = int(m.group(1))
                    if cno not in df['Cekilis_No'].values:
                        t = re.search(r'-\s*(.*)', data['sans']['date'])
                        tarih = t.group(1).strip() if t else data['sans']['date']
                        nums = data['sans']['nums']
                        nr = {'Cekilis_No': cno, 'Tarih': tarih, 
                              'T1': int(nums[0]), 'T2': int(nums[1]), 'T3': int(nums[2]), 
                              'T4': int(nums[3]), 'T5': int(nums[4]),
                              'Arti': int(data['sans'].get('plus', 0)) if str(data['sans'].get('plus', '')).isdigit() else "-"}
                        df = pd.concat([pd.DataFrame([nr]), df], ignore_index=True)
                        df.to_excel(fp, index=False)
                        
        if data['super']['nums']:
            fp = 'süper.xlsx'
            if os.path.exists(fp):
                df = pd.read_excel(fp)
                m = re.search(r'\[(\d+)\]', data['super']['date'])
                if m:
                    cno = int(m.group(1))
                    if cno not in df['Cekilis_No'].values:
                        t = re.search(r'-\s*(.*)', data['super']['date'])
                        tarih = t.group(1).strip() if t else data['super']['date']
                        nums = data['super']['nums']
                        nr = {'Cekilis_No': cno, 'Tarih': tarih, 
                              'T1': int(nums[0]), 'T2': int(nums[1]), 'T3': int(nums[2]), 
                              'T4': int(nums[3]), 'T5': int(nums[4]), 'T6': int(nums[5])}
                        df = pd.concat([pd.DataFrame([nr]), df], ignore_index=True)
                        df.to_excel(fp, index=False)
                        
        if data['onnumara']['nums'] and len(data['onnumara']['nums']) >= 22:
            fp = 'onnumara.xlsx'
            if os.path.exists(fp):
                df = pd.read_excel(fp)
                m = re.search(r'\[(\d+)\]', data['onnumara']['date'])
                if m:
                    cno = int(m.group(1))
                    if cno not in df['Cekilis_No'].values:
                        t = re.search(r'-\s*(.*)', data['onnumara']['date'])
                        tarih = t.group(1).strip() if t else data['onnumara']['date']
                        nums = data['onnumara']['nums']
                        nr = {'Cekilis_No': cno, 'Tarih': tarih}
                        for i in range(22):
                            nr[f'T{i+1}'] = int(nums[i])
                        df = pd.concat([pd.DataFrame([nr]), df], ignore_index=True)
                        df.to_excel(fp, index=False)
    except Exception:
        pass 
        
    return data

def parse_archive_row(row_vals, req_count, max_val):
    cno = "?"
    tarih = "?"
    nums_raw = []
    
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
            if 1 <= n <= max_val and n not in balls:
                balls.append(n)
        except: pass
        
    if len(balls) >= req_count:
        main_balls = sorted(balls[:req_count])
        plus = "-"
        ss = "-"
        if len(balls) > req_count: plus = balls[req_count]
        if len(balls) > req_count + 1: ss = balls[req_count + 1]
            
        return {
            "Cekilis_No": cno,
            "Tarih": tarih,
            "nums": main_balls,
            "plus": plus,
            "superstar": ss,
            "display_name": f"🗄️ {cno}. Çekiliş [{tarih}]" if cno != "?" else "🗄️ Arşiv Kaydı"
        }
    return None

def load_universal_archive(filepath, max_val, req_count):
    records = []
    if not os.path.exists(filepath): return records
    try:
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath, sheet_name=0, header=None)
            for _, row in df.iterrows():
                row_str = str(row.values).lower()
                if any(x in row_str for x in ['tarih', 'hafta', 'sayı', 'cekilis', 't1', 'numara']): continue
                parsed = parse_archive_row(list(row.values), req_count, max_val)
                if parsed: records.append(parsed)
        else:
            return records
            
        try:
            records.sort(key=lambda x: int(''.join(filter(str.isdigit, str(x['Cekilis_No'])))) if ''.join(filter(str.isdigit, str(x['Cekilis_No']))) else 0, reverse=True)
        except: pass
    except Exception: pass
    return records

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
                else:
                    continue
            except: pass
            
    try:
        records.sort(key=lambda x: int(''.join(filter(str.isdigit, str(x['Cekilis_No'])))) if ''.join(filter(str.isdigit, str(x['Cekilis_No']))) else 0, reverse=True)
    except: pass
    
    return records

def load_sayisal_archive(): return load_game_archive(['çlgn_sysl.xlsx'], 6, 90)
def load_sans_archive(): return load_game_archive(['şns_topu.xlsx'], 5, 34)
def load_super_archive(): return load_game_archive(['süper.xlsx'], 6, 60)
def load_onnumara_archive(): return load_game_archive(['onnumara.xlsx'], 22, 80)

@st.cache_data
def load_super_loto_data():
    try:
        df = pd.read_excel('süper.xlsx', sheet_name=0, header=None, engine='openpyxl')
        valid_draws = []
        for index, row in df.iterrows():
            try:
                nums = pd.to_numeric(row[:6], errors='coerce').dropna().astype(int).tolist()
                nums = [x for x in nums if 1 <= x <= 60]
                if len(set(nums)) == 6:
                    valid_draws.append(sorted(nums))
            except:
                pass
        if not valid_draws:
            return None, "HATA: Excel dosyasında geçerli Süper Loto çekilişi bulunamadı."
        
        return valid_draws, f"✅ Veritabanı Yüklendi: {len(valid_draws)} Çekiliş (Süper Loto)"
    except Exception as e:
        return None, f"Veri yükleme hatası: {e}"

@st.cache_data(ttl=5)
def load_sans_topu_data():
    valid_draws = []
    fp = 'chance.son.xlsx'
    
    if os.path.exists(fp):
        try:
            df = pd.read_excel(fp, sheet_name=0, header=None)
            df_clean = df.iloc[:, :5]
            for _, row in df_clean.iterrows():
                row_vals = list(row.values)
                balls = []
                for val in row_vals:
                    try:
                        n = int(float(str(val).replace(',', '.').strip()))
                        if 1 <= n <= 34:
                            balls.append(n)
                    except:
                        pass
                if len(balls) == 5:
                    t = tuple(sorted(balls))
                    if list(t) not in valid_draws: 
                        valid_draws.append(list(t))
        except Exception:
            pass
            
    if os.path.exists('otopilot_veriler.csv'):
        try:
            df = pd.read_csv('otopilot_veriler.csv', header=None)
            for _, row in df.iterrows():
                parsed = parse_archive_row(list(row.values), 5, 34)
                if parsed:
                    t = tuple(parsed['nums'])
                    if list(t) not in valid_draws: 
                        valid_draws.insert(0, list(t))
        except: pass
            
    if not valid_draws: 
        return None, "Şans Topu veri tabanı (chance.son.xlsx) okunamadı veya geçerli çekiliş bulunamadı."
    return valid_draws, f"🟢 Şans Topu Motoru Aktif | Kayıtlı Çekiliş: {len(valid_draws)}"

@st.cache_data(ttl=5)
def load_sayisal_ai_data():
    valid_draws = []
    records = load_sayisal_archive()
    for item in records:
        t = tuple(item['nums'])
        if list(t) not in valid_draws: valid_draws.append(list(t))
        
    if os.path.exists('otopilot_veriler.csv'):
        try:
            df = pd.read_csv('otopilot_veriler.csv', header=None)
            for _, row in df.iterrows():
                parsed = parse_archive_row(list(row.values), 6, 90)
                if parsed:
                    t = tuple(parsed['nums'])
                    if list(t) not in valid_draws: valid_draws.insert(0, list(t))
        except: pass
            
    if not valid_draws: return None, "Sayısal Loto veri tabanı bulunamadı veya format hatalı."
    return valid_draws, f"🟢 Sayısal Kuantum Motoru Aktif | Kayıtlı Çekiliş: {len(valid_draws)}"


# --- MODERN YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: 900; margin-bottom: 0;'>🧿 KUANTUM AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px; margin-bottom: 25px;'>Akıllı Loto Filtreleme Motoru</p>", unsafe_allow_html=True)

    selected_menu_opt = option_menu(
        menu_title=None,
        options=["Ana Sayfa", "Kuponlarım", "Çılgın Sayısal Loto", "Süper Loto", "Şans Topu", "On Numara", "VIP Giriş Merkezi"],
        icons=["house-door-fill", "ticket-detailed", "dice-6-fill", "bullseye", "star-fill", "hash", "gem"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "--hover-color": "#f1f5f9", "color": "#334155", "font-weight": "600", "border-radius": "8px"},
            "nav-link-selected": {"background-color": "#1e3a8a", "color": "white", "icon-color": "white", "font-weight": "bold"},
        }
    )
    
    st.markdown("<hr style='margin:15px 0; border: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
    
    if st.session_state.is_vip:
        st.markdown("<div style='text-align:center; background-color:#ecfdf5; padding:12px; border-radius:8px; border:2px solid #10b981;'><strong style='color:#059669; font-size:16px;'>💎 VIP ÜYE AKTİF</strong><br><span style='font-size:13px; color:#047857; font-weight:bold;'>Sınırsız Üretim Devrede</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; background-color:#fef2f2; padding:12px; border-radius:8px; border:2px solid #ef4444;'><strong style='color:#b91c1c; font-size:16px;'>👤 STANDART ÜYE</strong><br><span style='font-size:13px; color:#991b1b; font-weight:bold;'>Maks. 3 Kolon Üretimi</span><br><span style='font-size:11px; color:#ef4444;'>Sınırı kaldırmak için VIP girişi yapın.</span></div>", unsafe_allow_html=True)

# Arka plandaki alt kodlarınla %100 uyumlu olması için isim eşleştirmesi:
if selected_menu_opt == "Ana Sayfa": selected_game = "ANA SAYFA"
elif selected_menu_opt == "Kuponlarım": selected_game = "KUPONLARIM"  # <-- YENİ EKLENEN SATIR
elif selected_menu_opt == "Çılgın Sayısal Loto": selected_game = "ÇILGIN SAYISAL LOTO AI"
elif selected_menu_opt == "Süper Loto": selected_game = "SÜPER LOTO AI"
elif selected_menu_opt == "Şans Topu": selected_game = "ŞANS TOPU AI"
elif selected_menu_opt == "On Numara": selected_game = "ON NUMARA AI"
elif selected_menu_opt == "VIP Giriş Merkezi": selected_game = "VIP GİRİŞ MERKEZİ"

# ==========================================
# 👤 MÜŞTERİ YÖNETİMİ VE ÜYELİK PANELİ
# ==========================================
if selected_game == "VIP GİRİŞ MERKEZİ":
    st.markdown("<div class='main-title' style='color:#1e3a8a;'>👤 ÜYELİK VE VIP PORTAL</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#64748b;'>Sisteme Giriş Yapın veya Ücretsiz Hesap Oluşturun</div>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<div style='background-color:white; padding:25px; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            
            tab_login, tab_register = st.tabs(["🔑 Giriş Yap", "📝 Ücretsiz Kayıt Ol"])
            
            with tab_login:
                login_email = st.text_input("E-posta Adresi:", key="login_email")
                login_pass = st.text_input("Şifre:", type="password", key="login_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sisteme Giriş Yap", type="primary", use_container_width=True):
                    if login_email and login_pass:
                        # Kaptan için özel arka kapı (Admin VIP Girişi)
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
                            else:
                                st.error("🚨 Hatalı E-posta veya Şifre!")
                    else:
                        st.warning("Lütfen tüm alanları doldurun.")
                        
            with tab_register:
                reg_email = st.text_input("E-posta Adresi:", key="reg_email")
                reg_pass = st.text_input("Şifre Belirleyin:", type="password", key="reg_pass")
                reg_pass2 = st.text_input("Şifreyi Tekrar Girin:", type="password", key="reg_pass2")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Hesap Oluştur", type="primary", use_container_width=True):
                    if reg_email and reg_pass and reg_pass2:
                        if reg_pass != reg_pass2:
                            st.error("🚨 Şifreler uyuşmuyor!")
                        elif len(reg_pass) < 6:
                            st.error("🚨 Şifre en az 6 karakter olmalıdır.")
                        else:
                            success = create_user(reg_email, reg_pass)
                            if success:
                                st.success("🎉 Hesabınız başarıyla oluşturuldu! Şimdi 'Giriş Yap' sekmesinden giriş yapabilirsiniz.")
                            else:
                                st.error("🚨 Bu e-posta adresi zaten sistemde kayıtlı!")
                    else:
                        st.warning("Lütfen tüm alanları doldurun.")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # --- GİRİŞ YAPMIŞ KULLANICI İÇİN KONTROL PANELİ (DASHBOARD) ---
        st.success(f"Hoş geldiniz, **{st.session_state.user_email}**")
        
        c_dash1, c_dash2 = st.columns(2)
        with c_dash1:
            if st.session_state.is_vip:
                st.markdown("<div class='metric-card' style='border-top: 4px solid #10b981; padding:25px;'><b>Üyelik Durumu</b><br><span style='font-size:24px; color:#10b981; font-weight:900;'>💎 VIP ÜYE</span><br><span style='font-size:14px; color:#64748b;'>Tüm Yapay Zeka Kilitleri Açık</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='metric-card' style='border-top: 4px solid #ef4444; padding:25px;'><b>Üyelik Durumu</b><br><span style='font-size:24px; color:#ef4444; font-weight:900;'>👤 STANDART ÜYE</span><br><span style='font-size:14px; color:#64748b;'>Maksimum 3 Kolon / VIP'ye Geçin</span></div>", unsafe_allow_html=True)
        with c_dash2:
            st.markdown("<div class='metric-card' style='border-top: 4px solid #d97706; padding:25px;'><b>Kasa Durumu</b><br><span style='font-size:24px; color:#d97706; font-weight:900;'>KORUMADA</span><br><span style='font-size:14px; color:#64748b;'>Kayıtlı Kuponlarınız Veritabanında Güvende</span></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("🚪 Güvenli Çıkış Yap", type="secondary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_email = ""
                st.session_state.is_vip = False
                st.rerun()

# --- ANA SAYFA ---
live_data = get_live_results()

if selected_game == "ANA SAYFA":
    # --- YEPYENİ KOMUTA MERKEZİ KARŞILAMA ALANI ---
    st.markdown("""
        <div style="background: linear-gradient(to right, #0f172a, #1e3a8a); padding: 35px 30px; border-radius: 15px; margin-bottom: 35px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); border-left: 6px solid #3b82f6;">
            <h1 style="color: #ffffff; margin: 0; font-weight: 900; letter-spacing: 1px; font-size: 2.2rem;">🌐 YAPAY ZEKA ALGORİTMALARI</h1>
            <p style="color: #94a3b8; font-size: 17px; margin: 8px 0 0 0; font-weight: 500;">Canlı Çekiliş Sonuçları ve Kuantum Arşiv Senkronizasyonu</p>
        </div>
    """, unsafe_allow_html=True)
    
    sayisal_archive = load_sayisal_archive()
    sans_archive = load_sans_archive()
    super_archive = load_super_archive()
    onnumara_archive = load_onnumara_archive()

    def determine_status(game_key, archive_data):
        if not archive_data: return "⏳ Arşiv Boş", [], "-", "-", ""
        latest_arc = archive_data[0]
        try:
            next_no = int(''.join(filter(str.isdigit, str(latest_arc['Cekilis_No'])))) + 1
            next_title = f"⏳ {next_no}. Çekiliş Bekleniyor..."
        except: next_title = "⏳ Yeni Çekiliş Bekleniyor..."
            
        bot_nums = live_data[game_key]['nums']
        if bot_nums:
            bot_nums_str = sorted([str(int(x)) for x in bot_nums])
            arc_nums_str = sorted([str(int(x)) for x in latest_arc['nums']][:len(bot_nums)])
            if bot_nums_str == arc_nums_str:
                return next_title, latest_arc['nums'], latest_arc.get('plus', '-'), latest_arc.get('superstar', '-'), ""
            else:
                return live_data[game_key]['date'], bot_nums, live_data[game_key].get('plus', '-'), live_data[game_key].get('superstar', '-'), live_data[game_key]['prize_html']
        else:
            return next_title, latest_arc['nums'], latest_arc.get('plus', '-'), latest_arc.get('superstar', '-'), ""

    c_left, c_right = st.columns(2)
    
    # 🔴 ÇILGIN SAYISAL LOTO VİTRİNİ
    with c_left:
        s_date, s_nums, s_plus, s_ss, s_prize = determine_status("sayisal", sayisal_archive)
        s_status = f"<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:4px 8px; border-radius:6px;'>🟢 {live_data['sayisal']['status']}</span>" if "Canlı" in live_data['sayisal']['status'] and live_data['sayisal']['nums'] else "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:4px 8px; border-radius:6px;'>🔴 Bekleniyor</span>"
        
        sayisal_opts = [f"🌐 Güncel Ekran"]
        if sayisal_archive: sayisal_opts.extend([item['display_name'] for item in sayisal_archive])
        if "ana_sayisal_idx" not in st.session_state: st.session_state.ana_sayisal_idx = 0
            
        if st.session_state.ana_sayisal_idx > 0:
            arc_data = sayisal_archive[st.session_state.ana_sayisal_idx - 1]
            s_nums, s_plus, s_ss = arc_data['nums'], arc_data['plus'], arc_data['superstar']
            s_date = arc_data['display_name']
            s_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:4px 8px; border-radius:6px;'>🗄️ Arşiv</span>"
            s_prize = ""

        sayisal_html = "".join([f"<div class='home-ball ball-blue'>{n}</div>" for n in s_nums]) if s_nums else "<span style='color:#94a3b8; font-style:italic;'>Veri Akışı Bekleniyor...</span>"
        plus_html = f"<div class='home-ball ball-green'>{s_plus}</div>" if s_plus != "-" else ""
        ss_html = f"<div class='home-ball ball-red'>{s_ss}</div>" if s_ss != "-" else ""
        
        st.markdown(f"""
        <div style='background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-top: 5px solid #e61532; margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px dashed #f1f5f9; padding-bottom: 12px; margin-bottom: 20px;'>
                <span style='font-size: 1.2rem; font-weight: 900; color: #e61532;'>ÇILGIN SAYISAL LOTO</span>
                <span style='font-size: 0.85rem;'>{s_status}</span>
            </div>
            <div style='text-align: center; color: #475569; font-weight: 700; margin-bottom: 20px; font-size:15px;'>{s_date}</div>
            <div style='text-align: center; margin-bottom: 20px;'>
                {sayisal_html} <span style='font-size: 24px; color: #cbd5e1; font-weight: 900; margin: 0 8px;'>+</span> {plus_html}
            </div>
            <div style='text-align: center; background-color:#f8fafc; padding:10px; border-radius:8px;'>
                <span style='color: #e61532; font-weight: 900; margin-right: 15px; font-size: 1.1rem;'>SÜPERSTAR</span>{ss_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        h_col1, h_col2 = st.columns([1, 3])
        with h_col1:
            if st.button("◀ Önceki", key="ana_prev_btn_sayisal_v2", use_container_width=True, disabled=(st.session_state.ana_sayisal_idx >= len(sayisal_opts)-1)):
                st.session_state.ana_sayisal_idx += 1
                st.rerun()
        with h_col2:
            sel = st.selectbox("Arşiv Seçimi", options=sayisal_opts, index=st.session_state.ana_sayisal_idx, key="ana_sel_sayisal_v2", label_visibility="collapsed")
            if sayisal_opts.index(sel) != st.session_state.ana_sayisal_idx:
                st.session_state.ana_sayisal_idx = sayisal_opts.index(sel)
                st.rerun()

        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if s_prize: st.markdown(s_prize, unsafe_allow_html=True)
            else: st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor.")

    # 🔵 SÜPER LOTO VİTRİNİ
    with c_right:
        su_date, su_nums, _, _, su_prize = determine_status("super", super_archive)
        su_status = f"<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:4px 8px; border-radius:6px;'>🟢 {live_data['super']['status']}</span>" if "Canlı" in live_data['super']['status'] and live_data['super']['nums'] else "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:4px 8px; border-radius:6px;'>🔴 Bekleniyor</span>"
        
        super_opts = [f"🌐 Güncel Ekran"]
        if super_archive: super_opts.extend([item['display_name'] for item in super_archive])
        if "ana_super_idx" not in st.session_state: st.session_state.ana_super_idx = 0
        
        if st.session_state.ana_super_idx > 0:
            arc_data = super_archive[st.session_state.ana_super_idx - 1]
            su_nums = arc_data['nums']
            su_date = arc_data['display_name']
            su_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:4px 8px; border-radius:6px;'>🗄️ Arşiv</span>"
            su_prize = ""

        super_html = "".join([f"<div class='home-ball ball-green'>{n}</div>" for n in su_nums]) if su_nums else "<span style='color:#94a3b8; font-style:italic;'>Veri Akışı Bekleniyor...</span>"
        
        st.markdown(f"""
        <div style='background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-top: 5px solid #059669; margin-bottom: 15px; height: 268px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px dashed #f1f5f9; padding-bottom: 12px; margin-bottom: 20px;'>
                <span style='font-size: 1.2rem; font-weight: 900; color: #059669;'>SÜPER LOTO</span>
                <span style='font-size: 0.85rem;'>{su_status}</span>
            </div>
            <div style='text-align: center; color: #475569; font-weight: 700; margin-bottom: 30px; font-size:15px;'>{su_date}</div>
            <div style='text-align: center; margin-bottom: 20px;'>
                {super_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        h_col1_su, h_col2_su = st.columns([1, 3])
        with h_col1_su:
            if st.button("◀ Önceki", key="ana_prev_btn_super_v3", use_container_width=True, disabled=(st.session_state.ana_super_idx >= len(super_opts)-1)):
                st.session_state.ana_super_idx += 1
                st.rerun()
        with h_col2_su:
            sel_su = st.selectbox("Arşiv Seçimi", options=super_opts, index=st.session_state.ana_super_idx, key="ana_sel_super_v3", label_visibility="collapsed")
            if super_opts.index(sel_su) != st.session_state.ana_super_idx:
                st.session_state.ana_super_idx = super_opts.index(sel_su)
                st.rerun()

        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if su_prize: st.markdown(su_prize, unsafe_allow_html=True)
            else: st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    c_left2, c_right2 = st.columns(2)
    
    # 🟢 ŞANS TOPU VİTRİNİ
    with c_left2:
        st_date, st_nums, st_plus, _, st_prize = determine_status("sans", sans_archive)
        st_status = f"<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:4px 8px; border-radius:6px;'>🟢 {live_data['sans']['status']}</span>" if "Canlı" in live_data['sans']['status'] and live_data['sans']['nums'] else "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:4px 8px; border-radius:6px;'>🔴 Bekleniyor</span>"
        
        sans_opts = [f"🌐 Güncel Ekran"]
        if sans_archive: sans_opts.extend([item['display_name'] for item in sans_archive])
        if "ana_sans_idx" not in st.session_state: st.session_state.ana_sans_idx = 0
        
        if st.session_state.ana_sans_idx > 0:
            arc_data = sans_archive[st.session_state.ana_sans_idx - 1]
            st_nums, st_plus = arc_data['nums'], arc_data['plus']
            st_date = arc_data['display_name']
            st_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:4px 8px; border-radius:6px;'>🗄️ Arşiv</span>"
            st_prize = ""

        sans_html = "".join([f"<div class='home-ball ball-blue'>{n}</div>" for n in st_nums]) if st_nums else "<span style='color:#94a3b8; font-style:italic;'>Veri Akışı Bekleniyor...</span>"
        splus_html = f"<div class='home-ball ball-red'>{st_plus}</div>" if st_plus != "-" else ""
        
        st.markdown(f"""
        <div style='background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-top: 5px solid #0ea5e9; margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px dashed #f1f5f9; padding-bottom: 12px; margin-bottom: 20px;'>
                <span style='font-size: 1.2rem; font-weight: 900; color: #0ea5e9;'>ŞANS TOPU</span>
                <span style='font-size: 0.85rem;'>{st_status}</span>
            </div>
            <div style='text-align: center; color: #475569; font-weight: 700; margin-bottom: 20px; font-size:15px;'>{st_date}</div>
            <div style='text-align: center; margin-bottom: 20px;'>
                {sans_html} <span style='font-size: 24px; color: #cbd5e1; font-weight: 900; margin: 0 8px;'>+</span> {splus_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        h_col1_s, h_col2_s = st.columns([1, 3])
        with h_col1_s:
            if st.button("◀ Önceki", key="ana_prev_btn_sans_v2", use_container_width=True, disabled=(st.session_state.ana_sans_idx >= len(sans_opts)-1)):
                st.session_state.ana_sans_idx += 1
                st.rerun()
        with h_col2_s:
            sel_s = st.selectbox("Arşiv Seçimi", options=sans_opts, index=st.session_state.ana_sans_idx, key="ana_sel_sans_v2", label_visibility="collapsed")
            if sans_opts.index(sel_s) != st.session_state.ana_sans_idx:
                st.session_state.ana_sans_idx = sans_opts.index(sel_s)
                st.rerun()

        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if st_prize: st.markdown(st_prize, unsafe_allow_html=True)
            else: st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor.")

    # 🟠 ON NUMARA VİTRİNİ
    with c_right2:
        on_date, on_nums, _, _, on_prize = determine_status("onnumara", onnumara_archive)
        on_status = f"<span style='color: #10b981; font-weight:800; background:#ecfdf5; padding:4px 8px; border-radius:6px;'>🟢 {live_data['onnumara']['status']}</span>" if "Canlı" in live_data['onnumara']['status'] and live_data['onnumara']['nums'] else "<span style='color: #dc2626; font-weight:800; background:#fef2f2; padding:4px 8px; border-radius:6px;'>🔴 Bekleniyor</span>"
        
        on_opts = [f"🌐 Güncel Ekran"]
        if onnumara_archive: on_opts.extend([item['display_name'] for item in onnumara_archive])
        if "ana_on_idx" not in st.session_state: st.session_state.ana_on_idx = 0
        
        if st.session_state.ana_on_idx > 0:
            arc_data = onnumara_archive[st.session_state.ana_on_idx - 1]
            on_nums = arc_data['nums']
            on_date = arc_data['display_name']
            on_status = "<span style='color: #64748b; font-weight:800; background:#f1f5f9; padding:4px 8px; border-radius:6px;'>🗄️ Arşiv</span>"
            on_prize = ""

        if on_nums:
            onnumara_html_1 = "".join([f"<div class='home-onnumara-ball'>{n}</div>" for n in on_nums[:11]])
            onnumara_html_2 = "".join([f"<div class='home-onnumara-ball'>{n}</div>" for n in on_nums[11:]])
            onnumara_html = f"{onnumara_html_1}<div style='height: 6px;'></div>{onnumara_html_2}"
        else:
            onnumara_html = "<span style='color:#94a3b8; font-style:italic;'>Veri Akışı Bekleniyor...</span>"
            
        st.markdown(f"""
        <div style='background: white; border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-top: 5px solid #d97706; margin-bottom: 15px; height: 236px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px dashed #f1f5f9; padding-bottom: 12px; margin-bottom: 20px;'>
                <span style='font-size: 1.2rem; font-weight: 900; color: #d97706;'>ON NUMARA</span>
                <span style='font-size: 0.85rem;'>{on_status}</span>
            </div>
            <div style='text-align: center; color: #475569; font-weight: 700; margin-bottom: 20px; font-size:15px;'>{on_date}</div>
            <div style='text-align: center; margin-bottom: 15px;'>
                {onnumara_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        h_col1_o, h_col2_o = st.columns([1, 3])
        with h_col1_o:
            if st.button("◀ Önceki", key="ana_prev_btn_on_v2", use_container_width=True, disabled=(st.session_state.ana_on_idx >= len(on_opts)-1)):
                st.session_state.ana_on_idx += 1
                st.rerun()
        with h_col2_o:
            sel_on = st.selectbox("Arşiv Seçimi", options=on_opts, index=st.session_state.ana_on_idx, key="ana_sel_on_v2", label_visibility="collapsed")
            if on_opts.index(sel_on) != st.session_state.ana_on_idx:
                st.session_state.ana_on_idx = on_opts.index(sel_on)
                st.rerun()

        with st.expander("💰 Kazananlar ve İkramiye Tablosu"):
            if on_prize: st.markdown(on_prize, unsafe_allow_html=True)
            else: st.info("Bu çekilişin ikramiye detayları arşivde bulunmuyor.")
# ==========================================
# 🔴 1. MODÜL: ÇILGIN SAYISAL LOTO
# ==========================================
# ==========================================
# ==========================================
# 🎫 KUPONLARIM & KAZANÇ MERKEZİ (VERİTABANI BAĞLANTILI)
# ==========================================
elif selected_game == "KUPONLARIM":
    st.markdown("<div class='main-title' style='color:#d97706;'>🎫 KUPONLARIM & KAZANÇ MERKEZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>Kişisel Kuantum Kasanız ve Otomatik İkramiye Tarayıcı</div>", unsafe_allow_html=True)
    
    # KULLANICI GİRİŞ YAPMADIYSA KASAYI GÖREMEZ
    if not st.session_state.logged_in:
        st.markdown("<div style='text-align:center; padding:40px; background-color:#f1f5f9; border-radius:12px; border:2px dashed #cbd5e1;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#475569;'>🔒 Kasanız Kilitli</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; font-size:16px;'>Kuponlarınızı güvenle saklamak ve kazançlarınızı otomatik taramak için sisteme giriş yapmalısınız.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.warning("👈 Lütfen sol menüden 'VIP Giriş Merkezi'ne tıklayarak giriş yapın veya ücretsiz hesap oluşturun.")
    
    # KULLANICI GİRİŞ YAPTIYSA VERİTABANINDAN KUPONLARINI ÇEK
    else:
        user_coupons = get_user_coupons(st.session_state.user_email)
        
        if not user_coupons:
            st.info("Kasanızda henüz kayıtlı bir kolon bulunmuyor. Sol menüden oyun seçip Kuantum motoruyla kolon üreterek 'Kasaya Kaydet' butonuna basabilirsiniz.")
        else:
            st.markdown(f"<div style='background-color:#ecfdf5; padding:10px; border-radius:8px; border:1px solid #10b981; margin-bottom:20px;'><strong style='color:#059669;'>👤 Kasa Sahibi:</strong> {st.session_state.user_email} <br> <strong style='color:#059669;'>🎫 Toplam Kayıtlı Kupon:</strong> {len(user_coupons)} Adet</div>", unsafe_allow_html=True)
            
            for idx, c in enumerate(user_coupons):
                g_id = c['game']
                g_name = c['game_name']
                nums = c['nums']
                ts = c['timestamp']
                
                # Canlı sonuçları çekip eşleştirme
                live = live_data[g_id]['nums'] if g_id in live_data else []
                live_plus = str(live_data[g_id].get('plus', '-')) if g_id in live_data else '-'
                matches = [n for n in nums[:(5 if g_id=='sans' else 6)] if n in live]
                
                is_plus_match = False
                if g_id == 'sans' and len(nums) == 6:
                    if str(nums[5]) == live_plus: is_plus_match = True
                        
                match_count = len(matches)
                status_color = "#64748b" 
                status_text = "Çekiliş Bekleniyor..."
                
                if live:
                    if g_id == 'sans':
                        status_text = f"🎯 {match_count} + {'1' if is_plus_match else '0'} Bildiniz!"
                        if match_count >= 3 or (match_count >= 1 and is_plus_match): status_color = "#10b981" 
                        else: status_color = "#ef4444" 
                    else:
                        status_text = f"🎯 {match_count} Bildiniz!"
                        if match_count >= 3: status_color = "#10b981"
                        else: status_color = "#ef4444"
                
                balls_html = ""
                for n in nums[:(5 if g_id=='sans' else 6)]:
                    bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)" if n in matches else "linear-gradient(135deg, #94a3b8 0%, #64748b 100%)"
                    balls_html += f"<div class='home-ball' style='background:{bg}; width:40px; height:40px; line-height:40px; font-size:16px;'>{n}</div>"
                    
                if g_id == 'sans' and len(nums) == 6:
                    bg_p = "linear-gradient(135deg, #10b981 0%, #059669 100%)" if is_plus_match else "linear-gradient(135deg, #94a3b8 0%, #64748b 100%)"
                    balls_html += f"<span style='font-size:20px; color:#cbd5e1; font-weight:bold; margin:0 5px;'>+</span><div class='home-ball' style='background:{bg_p}; width:40px; height:40px; line-height:40px; font-size:16px; border-color:#fca5a5;'>{nums[5]}</div>"

                st.markdown(f"""
                <div style='background-color: white; border: 2px solid {status_color}; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 10px;'>
                        <strong style='color: {status_color}; font-size:1.1rem;'>{g_name}</strong>
                        <span style='color: #94a3b8; font-size:0.85rem;'>{ts}</span>
                    </div>
                    <div style='text-align: center; margin-bottom: 15px;'>{balls_html}</div>
                    <div style='text-align: center; font-weight: 900; color: {status_color}; font-size:1.2rem; background-color: #f8fafc; padding: 8px; border-radius: 6px;'>{status_text}</div>
                </div>
                """, unsafe_allow_html=True)

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

    valid_draws, msg = load_sayisal_ai_data()

    if not valid_draws:
        st.error(msg)
    else:
        total_draws = len(valid_draws)
        all_nums = [num for draw in valid_draws for num in draw]
        counts = Counter(all_nums)
        
        expected = total_draws * (6 / 90)
        hot_limit = int(np.ceil(expected * 1.35))
        cold_limit = int(np.floor(expected * 0.75))
        
        hot_nums = [n for n in range(1, 91) if counts.get(n, 0) >= hot_limit]
        cold_nums = [n for n in range(1, 91) if counts.get(n, 0) <= cold_limit]
        medium_nums = [n for n in range(1, 91) if cold_limit < counts.get(n, 0) < hot_limit]

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
        all_p = set(combinations(range(1, 91), 2))
        actual_p = set([p for p, c in pair_c.items() if c > 0])
        enemies = set(all_p - actual_p) 

        def is_enemy(n1, n2):
            return (min(n1, n2), max(n1, n2)) in enemies

        st.sidebar.markdown("## ⚙️ SAYISAL LOTO FİLTRELERİ")

        with st.sidebar.expander("📊 0. Temel Frekans", expanded=True):
            sc1, sc2, sc3 = st.columns(3)
            s_hedef = sc1.number_input("Sıcak", 0, 6, 2, key="ss_s")
            o_hedef = sc2.number_input("Orta", 0, 6, 3, key="ss_o")
            c_hedef = sc3.number_input("Soğuk", 0, 6, 1, key="ss_c")

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            tc1, tc2 = st.columns(2)
            tek_hedef = tc1.number_input("Tek", 0, 6, 3, key="ss_t")
            cift_hedef = tc2.number_input("Çift", 0, 6, 3, key="ss_ct")

        with st.sidebar.expander("2. Ardışık & 3. Kök Refleksi", expanded=True):
            c_strat1, c_strat2 = st.columns(2)
            ardisik = c_strat1.selectbox("Ardışık Sayı", ["YOK", "VAR"], key="ss_ard")
            kese_koku = c_strat2.selectbox("Kök Eşleşmesi", ["VAR (1 Çift)", "YOK"], key="ss_kok")

        with st.sidebar.expander("4. Devir Refleksi", expanded=True):
            devir_secimi = st.selectbox("Devir (Önceki Haftadan)", [
                "Farketmez", 
                "YOK (Önceki haftadan sayı gelmesin)", 
                "VAR (Sistem rastgele 1 sayı seçsin)", 
                "VAR (Sayıyı ben seçeceğim)"
            ], key="ss_devir_sec")
            
            devir_sayisi_str = ""
            if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                st.info(f"Geçen Haftanın Sayıları: {valid_draws[0]}")
                devir_sayisi_str = st.text_input("Devredecek sayıyı girin:", key="ss_devir_sayi")

        with st.sidebar.expander("5. Bölge Refleksi (Alt-Orta-Üst)", expanded=True):
            bc1, bc2, bc3 = st.columns(3)
            bolge1 = bc1.number_input("Alt (1-30)", 0, 6, 2, key="ss_b1")
            bolge2 = bc2.number_input("Orta (31-60)", 0, 6, 2, key="ss_b2")
            bolge3 = bc3.number_input("Üst (61-90)", 0, 6, 2, key="ss_b3")

        with st.sidebar.expander("🛡️ Ekstra Kısıtlamalar (Çan vb.)", expanded=False):
            min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 21, 525, (200, 340), key="ss_can")
            min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 5, 89, (35, 75), key="ss_mes")
            yasak_sayilar_str = st.text_input("Yasaklılar (Virgülle ayırın)", key="ss_yasak")
            banko_sayilar_str = st.text_input("Banko Sayılar (Mutlaka Olsun)", key="ss_banko")

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

        def get_bolge_pattern(col):
            b1 = sum(1 for x in col if 1 <= x <= 30)
            b2 = sum(1 for x in col if 31 <= x <= 60)
            b3 = sum(1 for x in col if 61 <= x <= 90)
            return f"{b1}A - {b2}O - {b3}U"
            
        def get_k(col):
            roots = [x % 10 for x in col]
            counts = list(Counter(roots).values())
            counts.sort(reverse=True)
            if counts == [1, 1, 1, 1, 1, 1]: return "Eşleşme Yok"
            elif counts == [2, 1, 1, 1, 1]: return "1 Çift Kök"
            else: return "Çoklu/Çifte Kök"

        # --- ÜRETİM ALANI (EN ÜSTTE VE ORTADA) ---
        st.info(f"{msg} | **Son Çekiliş:** {valid_draws[0]}")
        st.markdown("---")

        if "sayisal_uretim_ekrani_acik" not in st.session_state:
            st.session_state.sayisal_uretim_ekrani_acik = False

        if "sayisal_aktif_kuponlar" not in st.session_state:
            st.session_state.sayisal_aktif_kuponlar = []

        sayisal_basla_btn = False
        sayisal_kolon_sayisi = 1

        if not st.session_state.sayisal_uretim_ekrani_acik:
            c_btn_sol, c_btn_orta, c_btn_sag = st.columns([1, 2, 1])
            with c_btn_orta:
                if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", type="primary", use_container_width=True, key="sayisal_btn_1"):
                    st.session_state.sayisal_uretim_ekrani_acik = True
                    st.rerun() 
        
        if st.session_state.sayisal_uretim_ekrani_acik:
            st.markdown("""
                <div style='border: 3px solid #1e3a8a; border-radius: 12px; padding: 20px; background-color: #f8fafc; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.15); margin-bottom: 20px;'>
                    <h3 style='color: #1e3a8a; margin-top: 0; font-weight: 900; text-align: center; letter-spacing: 1px;'>🤖 KUSURSUZ ÜRETİM ONAYI</h3>
                    <p style='color: #334155; text-align: center; font-size: 16px; font-weight: 600; margin-bottom: 0px;'>Yapay Zeka'nın sizin için kaç adet Çılgın Sayısal Loto kolonu üretmesini istersiniz?</p>
                </div>
            """, unsafe_allow_html=True)
            
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            
            with c_orta:
                st.markdown("<div style='background-color:#1e3a8a; border:2px solid #0f172a; padding:10px; border-radius:8px; text-align:center; font-weight:900; color:#ffffff; font-size:16px; margin-bottom:5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); letter-spacing: 1px;'>🔢 KOLON ADEDİ SEÇİN</div>", unsafe_allow_html=True)
                sayisal_kolon_sayisi = st.number_input("Kolon Adedi", min_value=1, max_value=10, value=1, label_visibility="collapsed", key="sayisal_kolon_adet")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                sayisal_basla_btn = st.button("✅ MOTORU ATEŞLE VE ÜRET", type="primary", use_container_width=True, key="sayisal_btn_basla")
            with col_btn2:
                iptal_btn = st.button("❌ İPTAL", use_container_width=True, key="sayisal_btn_iptal")
                
            if iptal_btn:
                st.session_state.sayisal_uretim_ekrani_acik = False
                st.rerun()

        if sayisal_basla_btn:
            st.session_state.sayisal_uretim_ekrani_acik = False 
            with st.spinner('Kuantum eleme motoru ve Yapay Zeka zırhı devrede...'):
                time.sleep(0.5)
                
                last_draw_nums = valid_draws[0]
                devirler = []
                ekstra_yasaklar = []
                
                if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)":
                    ekstra_yasaklar.extend(last_draw_nums)
                elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                    devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
                
                yasaklar_input = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                yasaklar = list(set(yasaklar_input + ekstra_yasaklar))
                
                bankolar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                sabit_sayilar = list(set(devirler + bankolar))
                
                errors = []
                if s_hedef + o_hedef + c_hedef != 6: errors.append("Sıcak+Orta+Soğuk = 6 olmalı.")
                if tek_hedef + cift_hedef != 6: errors.append("Tek+Çift = 6 olmalı.")
                if bolge1 + bolge2 + bolge3 != 6: errors.append("Alt+Orta+Üst Bölge toplamı 6 olmalı.")
                if len(sabit_sayilar) > 6: errors.append("Banko ve Devir sayılarının toplamı 6'yı geçemez.")
                for s in sabit_sayilar:
                    if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko/Devir hem de Yasaklı listesinde olamaz!")
                
                if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                    for d in devirler:
                        if d not in last_draw_nums:
                            errors.append(f"Hata: Girdiğiniz '{d}' sayısı geçen haftanın çekilişinde yok! Lütfen geçerli bir devir sayısı girin: {last_draw_nums}")

                if errors:
                    for e in errors: st.error(e)
                else:
                    adaylar = [x for x in range(1, 91) if x not in yasaklar and x not in sabit_sayilar]
                    kalan_secim_sayisi = 6 - len(sabit_sayilar)
                    
                    hot_pool = [x for x in hot_nums if x in adaylar]
                    med_pool = [x for x in medium_nums if x in adaylar]
                    cold_pool = [x for x in cold_nums if x in adaylar]

                    b_hot = sum(1 for x in sabit_sayilar if x in hot_nums)
                    b_med = sum(1 for x in sabit_sayilar if x in medium_nums)
                    b_cold = sum(1 for x in sabit_sayilar if x in cold_nums)

                    req_hot = s_hedef - b_hot
                    req_med = o_hedef - b_med
                    req_cold = c_hedef - b_cold

                    if req_hot < 0 or req_med < 0 or req_cold < 0:
                        st.error("🚨 HATA: Banko sayılarının frekansları, belirlediğin hedefleri aşıyor!")
                    elif req_hot > len(hot_pool) or req_med > len(med_pool) or req_cold > len(cold_pool):
                        st.error(f"🚨 HATA: Kotalar havuzdaki sayıları aşıyor! (Sıcak havuzda {len(hot_pool)}, Orta havuzda {len(med_pool)}, Soğuk havuzda {len(cold_pool)} sayı kaldı)")
                    else:
                        candidates = []
                        valid_combinations = []
                        attempts = 0
                        
                        while len(candidates) < 100000 and attempts < 200000:
                            attempts += 1
                            h_pick = random.sample(hot_pool, req_hot) if req_hot > 0 else []
                            m_pick = random.sample(med_pool, req_med) if req_med > 0 else []
                            c_pick = random.sample(cold_pool, req_cold) if req_cold > 0 else []
                            col = sorted(sabit_sayilar + h_pick + m_pick + c_pick)
                            if len(set(col)) == 6:
                                candidates.append(tuple(col))
                        
                        candidates = list(set(candidates))
                        
                        for col in candidates:
                            if devir_secimi == "VAR (Sistem rastgele 1 sayı seçsin)":
                                ortak_sayi_adedi = sum(1 for x in col if x in last_draw_nums)
                                if ortak_sayi_adedi != 1: 
                                    continue

                            b1 = sum(1 for x in col if 1 <= x <= 30)
                            b2 = sum(1 for x in col if 31 <= x <= 60)
                            b3 = sum(1 for x in col if 61 <= x <= 90)
                            if b1 != bolge1 or b2 != bolge2 or b3 != bolge3: continue
                            
                            tek = sum(1 for x in col if x % 2 != 0)
                            cift = 6 - tek
                            if tek != tek_hedef or cift != cift_hedef: continue
                            
                            has_cons = any(col[i]+1 == col[i+1] for i in range(5))
                            if (ardisik == "VAR" and not has_cons) or (ardisik == "YOK" and has_cons): continue
                            
                            roots = [x % 10 for x in col]
                            r_counts = list(Counter(roots).values())
                            r_counts.sort(reverse=True)
                            
                            if kese_koku == "VAR (1 Çift)":
                                if r_counts != [2, 1, 1, 1, 1]: continue
                            else:
                                if r_counts != [1, 1, 1, 1, 1, 1]: continue
                            
                            enemy_found = False
                            for pair in combinations(col, 2):
                                if is_enemy(pair[0], pair[1]):
                                    enemy_found = True
                                    break
                            if enemy_found: continue
                            
                            if not (min_toplam <= sum(col) <= max_toplam): continue
                            if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam): continue
                            
                            klan_cesitliligi = len(set([klan_labels[x] for x in col if x in klan_labels]))
                            valid_combinations.append({
                                'c': col, 'sum': sum(col), 'klan': klan_cesitliligi
                            })

                        if len(valid_combinations) > 0:
                            valid_combinations.sort(key=lambda x: (-x['klan'], abs(x['sum'] - 273)))
                            
                            gosterilecek_adet = min(sayisal_kolon_sayisi, len(valid_combinations))
                        
                            if gosterilecek_adet < sayisal_kolon_sayisi:
                                st.warning(f"Sadece {len(valid_combinations)} kusursuz dizilim bulunabildi. Kurallarınız çok katı olduğu için {sayisal_kolon_sayisi} adet kolon oluşturulamadı. Bulunanların tamamı aşağıdadır:")
                            else:
                                st.success(f"Tüm ağır filtreler aşıldı! Havuzdaki {len(valid_combinations)} kusursuz dizilim arasından EN İYİ {gosterilecek_adet} kolon seçildi.")

                            for i in range(gosterilecek_adet):
                                secilen = valid_combinations[i]['c']
                                klan_degeri = valid_combinations[i]['klan']
                                
                                if sayisal_kolon_sayisi > 1:
                                    st.markdown(f"<h4 style='color:#dc2626; text-align:center; margin-top:20px; font-weight:900; background-color:#fef2f2; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                                
                                html_balls = f"""
                                <div style='text-align: center; margin: 15px 0 25px 0;'>
                                    <div class='number-ball ball-red'>{secilen[0]}</div>
                                    <div class='number-ball ball-red'>{secilen[1]}</div>
                                    <div class='number-ball ball-red'>{secilen[2]}</div>
                                    <div class='number-ball ball-red'>{secilen[3]}</div>
                                    <div class='number-ball ball-red'>{secilen[4]}</div>
                                    <div class='number-ball ball-red'>{secilen[5]}</div>
                                </div>
                                """
                                st.markdown(html_balls, unsafe_allow_html=True)
                                
                                mc1, mc2, mc3, mc4 = st.columns(4)
                                with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#e61532;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                                with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#e61532;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                                with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                                with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span class='highlight-yellow' style='font-size:16px;'>0 (Temiz)</span></div>", unsafe_allow_html=True)
                                
                                if i < gosterilecek_adet - 1:
                                    st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)
                        else:
                            st.error("🚨 PARADOKS TESPİT EDİLDİ: Bu kadar katı kuralı aynı anda sağlayan hiçbir sayı evrende bulunamadı. Kurallardan birini esnetin.")

        # --- 4 YENİ SEKME (CSS İLE SİMSİYAH VE KALIN YAPILANDIRILMIŞ) ---
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
            c1.markdown(f"<div class='metric-card' style='padding:10px;'><b>Frekans Şablonu</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_f_pattern(last_d)}</span></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card' style='padding:10px;'><b>Tek/Çift Dengesi</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_tc(last_d)}</span></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-card' style='padding:10px;'><b>Ardışık Durumu</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_ard(last_d)}</span></div>", unsafe_allow_html=True)
            
            c4, c5, c6 = st.columns(3)
            c4.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Kök Eşleşmesi</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_k(last_d)}</span></div>", unsafe_allow_html=True)
            c5.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Bölge Dağılımı (Alt-Orta-Üst)</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{get_bolge_pattern(last_d)}</span></div>", unsafe_allow_html=True)
            
            devir_bilgisi = get_dev(valid_draws[1], last_d) if len(valid_draws) > 1 else "YOK"
            c6.markdown(f"<div class='metric-card' style='padding:10px; margin-top:10px;'><b>Devir (Geçen Haftadan)</b><br><span style='color:#e61532; font-weight:900; font-size:16px;'>{devir_bilgisi}</span></div>", unsafe_allow_html=True)
            
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
                    for k, v in sorted(uyuyan_devler.items(), key=lambda item: item[1], reverse=True):
                        uyuyan_html += f"<div style='background-color:#f0f9ff; border:1px solid #bae6fd; border-radius:4px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center;'><strong style='color:#0369a1; font-size:13px;'>Sayı {k}</strong><span style='font-size:12px; color:#64748b; font-weight:bold;'>{v} Çekiliştir Yok</span></div>"
                    uyuyan_html += "</div>"
                    st.markdown(uyuyan_html, unsafe_allow_html=True)
                else: st.info("Uyuyan dev bulunmuyor.")

            st.markdown("---")
            st.markdown("<h4 style='color:#e61532;'>🧬 ÇAPRAZ GEÇİŞ ANALİZİ (MARKOV MATRİSİ)</h4>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0ea5e9; padding: 12px 15px; margin-bottom: 15px; border-radius: 4px; color: #334155; font-size: 0.90rem; line-height: 1.5;'>
                Frekansları seçin; <b>Yapay Zeka motoru</b> sizin için bu frekansın tarihte kaç kez yaşandığını, bu frekans geldiğinde <b>tek/çift</b> yüzdesini, <b>kök eşleşme</b>, önceki haftadan <b>devir</b> yüzdelerini, <b>ardışık ve alt/orta/üst bölge</b> yüzdelerini sizin için hesaplasın.
            </div>
            """, unsafe_allow_html=True)
            
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
            <div style='border: 3px solid #000000; border-radius: 10px; padding: 20px; background-color: #f8fafc; margin-bottom: 20px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);'>
                <h4 style='text-align: center; color: #0f172a; font-weight: 900; margin-top: 0; margin-bottom: 20px; letter-spacing: 0.5px;'>🎯 HEDEF FREKANS KOMBİNASYONUNU SEÇİN</h4>
            """, unsafe_allow_html=True)
            
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.markdown("<div style='background-color:#fef2f2; border:2px solid #ef4444; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#b91c1c; font-size:16px; margin-bottom:5px;'>🔥 SICAK (S)</div>", unsafe_allow_html=True)
                target_s = st.number_input("Sıcak (S)", 0, 6, last_s, key="ts_m_sayisal", label_visibility="collapsed")
            with cc2:
                st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                target_o = st.number_input("Orta (O)", 0, 6, last_o, key="to_m_sayisal", label_visibility="collapsed")
            with cc3:
                st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                target_c = st.number_input("Soğuk (C)", 0, 6, last_c, key="tc_m_sayisal", label_visibility="collapsed")
                
            st.markdown("</div>", unsafe_allow_html=True)

            if target_s + target_o + target_c != 6:
                st.warning("⚠️ Sıcak, Orta ve Soğuk sayılarının toplamı tam 6 olmalıdır!")
            else:
                target_freq = f"{target_s}S - {target_o}O - {target_c}C"
                t_draws = []
                for i in range(1, len(valid_draws)):
                    if get_f_pattern(valid_draws[i]) == target_freq:
                        next_d = valid_draws[i-1]
                        t_draws.append({
                            'tc': get_tc(next_d), 'ard': get_ard(next_d), 'kok': get_k(next_d),
                            'dev': get_dev(valid_draws[i], next_d), 'bolge': get_bolge_pattern(next_d)
                        })

                if len(t_draws) > 0:
                    st.info(f"**Seçilen Şablon:** {target_freq} | Tarihte bu şablondan sonra **{len(t_draws)}** kez çekiliş yapılmış:")
                    tc_c = Counter([x['tc'] for x in t_draws])
                    ard_c = Counter([x['ard'] for x in t_draws])
                    kok_c = Counter([x['kok'] for x in t_draws])
                    dev_c = Counter([x['dev'] for x in t_draws])
                    bolge_c = Counter([x['bolge'] for x in t_draws])
                    
                    def format_pct(counter):
                        total = sum(counter.values())
                        return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                    
                    copy_text = f"🎯 ÇAPRAZ ANALİZ ÇIKTISI (BAZ FREKANS: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT REFLEKSİ ---\n{format_pct(tc_c)}\n\n--- 2. ARDIŞIK REFLEKSİ ---\n{format_pct(ard_c)}\n\n--- 3. KÖK EŞLEŞMESİ REFLEKSİ ---\n{format_pct(kok_c)}\n\n--- 4. DEVİR REFLEKSİ ---\n{format_pct(dev_c)}\n\n--- 5. BÖLGE REFLEKSİ (Alt-Orta-Üst) ---\n{format_pct(bolge_c)}"
                    
                    st.markdown(f'''
                    <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.warning(f"Tarihte daha önce {target_freq} şablonu yaşanıp ardından çekiliş yapılmamış.")

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
            <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #8b5cf6; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.10rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                Makinenin sinir uçlarına bağlanın. Veritabanındaki en popüler şablonları inceleyin ve kendi belirlediğiniz frekans senaryosunun ardından yaşanacakları simüle edin.
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
                q_s = st.number_input("Sıcak", 0, 6, 2, key="sq_s", label_visibility="collapsed")
            with cq2:
                st.markdown("<div style='background-color:#f0f9ff; border:2px solid #3b82f6; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#1d4ed8; font-size:16px; margin-bottom:5px;'>🔵 ORTA (O)</div>", unsafe_allow_html=True)
                q_o = st.number_input("Orta", 0, 6, 3, key="sq_o", label_visibility="collapsed")
            with cq3:
                st.markdown("<div style='background-color:#fefce8; border:2px solid #eab308; padding:8px; border-radius:6px; text-align:center; font-weight:900; color:#a16207; font-size:16px; margin-bottom:5px;'>❄️ SOĞUK (C)</div>", unsafe_allow_html=True)
                q_c = st.number_input("Soğuk", 0, 6, 1, key="sq_c", label_visibility="collapsed")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 DİNAMİK İSTİHBARATI GETİR", type="primary", use_container_width=True, key="sq_btn"):
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

        # --- SAYFA SONU (ALT) ÜRETİM BUTONU ---
        st.markdown("<br><hr style='border: 2px dashed #cbd5e1; margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        if not st.session_state.sayisal_uretim_ekrani_acik:
            st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; font-weight:bold; margin-bottom:15px;'>Tüm analizleri incelediyseniz motoru ateşleyebilirsiniz 👇</p>", unsafe_allow_html=True)
            c_alt_sol, c_alt_orta, c_alt_sag = st.columns([1, 2, 1])
            with c_alt_orta:
                if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", type="primary", use_container_width=True, key="alt_uretim_btn_sayisal"):
                    st.session_state.sayisal_uretim_ekrani_acik = True
                    st.rerun()# 🟢 3. MODÜL: ŞANS TOPU
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
<strong>💡 Strateji Önerisi:</strong> Sol menüden kurallarını (Ardışık, Tek/Çift, Kilit Sayı vb.) katı bir şekilde belirle. Ardından motoru ateşle! Eğer kuralların çok çelişiyorsa makine paradoksa girer ve "Kolon Bulunamadı" der. Kurallarını esneterek, <b>sadece tüm bu devasa filtreleri aşan o yegâne kolona</b> ulaşana kadar denemeye devam et.
</div>
</div>
</details>
""", unsafe_allow_html=True)

    valid_draws, msg = load_sans_topu_data()

    if not valid_draws:
        st.error(msg)
    else:
        total_draws = len(valid_draws)
        all_nums = [num for draw in valid_draws for num in draw]
        counts = Counter(all_nums)

        # ŞANS TOPU SABİT KAPTAN KURALI ENTEGRE EDİLDİ
        hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= 26]
        cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= 19]
        medium_nums = [n for n in range(1, 35) if 20 <= counts.get(n, 0) <= 25]

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

        st.sidebar.markdown("## ⚙️ ŞANS TOPU FİLTRELERİ")

        with st.sidebar.expander("📊 Temel Frekans", expanded=True):
            col1, col2, col3 = st.columns(3)
            sicak_hedef = col1.number_input("Sıcak", 0, 5, 2)
            orta_hedef = col2.number_input("Orta", 0, 5, 2)
            soguk_hedef = col3.number_input("Soğuk", 0, 5, 1)

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            col4, col5 = st.columns(2)
            tek_hedef = col4.number_input("Tek", 0, 5, 3)
            cift_hedef = col5.number_input("Çift", 0, 5, 2)

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

        with st.sidebar.expander("6. Bölge Refleksi (Alt-Üst)", expanded=True):
            col10, col11 = st.columns(2)
            alt_hedef = col10.number_input("Alt(1-17)", 0, 5, 2)
            ust_hedef = col11.number_input("Üst(18-34)", 0, 5, 3)

        with st.sidebar.expander("🛡️ Ekstra Kısıtlamalar (Çan vb.)", expanded=False):
            min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 15, 160, (65, 107))
            min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 4, 33, (18, 29))
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
            b1 = sum(1 for x in col if x <= 9)
            b2 = sum(1 for x in col if 10 <= x <= 19)
            b3 = sum(1 for x in col if 20 <= x <= 29)
            b4 = sum(1 for x in col if x >= 30)
            return f"{b1}B - {b2}O - {b3}Y - {b4}Ot"
            
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

        # --- ÜRETİM ALANI (EN ÜSTTE ORTALANMIŞ) ---
        st.info(f"{msg} | **Son Çekiliş:** {valid_draws[0]}")
        st.markdown("---")
        
        if "uretim_ekrani_acik" not in st.session_state:
            st.session_state.uretim_ekrani_acik = False

        basla_btn = False
        kolon_sayisi = 1

        if not st.session_state.uretim_ekrani_acik:
            c_btn_sol, c_btn_orta, c_btn_sag = st.columns([1, 2, 1])
            with c_btn_orta:
                if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", type="primary", use_container_width=True):
                    st.session_state.uretim_ekrani_acik = True
                    st.rerun() 
        
        if st.session_state.uretim_ekrani_acik:
            st.markdown("""
                <div style='border: 3px solid #1e3a8a; border-radius: 12px; padding: 20px; background-color: #f8fafc; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.15); margin-bottom: 20px;'>
                    <h3 style='color: #1e3a8a; margin-top: 0; font-weight: 900; text-align: center; letter-spacing: 1px;'>🤖 KUSURSUZ ÜRETİM ONAYI</h3>
                    <p style='color: #334155; text-align: center; font-size: 16px; font-weight: 600; margin-bottom: 0px;'>Yapay Zeka'nın sizin için kaç adet kolon üretmesini istersiniz?</p>
                </div>
            """, unsafe_allow_html=True)
            
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            
            with c_orta:
                st.markdown("<div style='background-color:#1e3a8a; border:2px solid #0f172a; padding:10px; border-radius:8px; text-align:center; font-weight:900; color:#ffffff; font-size:16px; margin-bottom:5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); letter-spacing: 1px;'>🔢 KOLON ADEDİ SEÇİN</div>", unsafe_allow_html=True)
                kolon_sayisi = st.number_input("Kolon Adedi", min_value=1, max_value=10, value=1, label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                basla_btn = st.button("✅ MOTORU ATEŞLE VE ÜRET", type="primary", use_container_width=True)
            with col_btn2:
                iptal_btn = st.button("❌ İPTAL", use_container_width=True)
                
            if iptal_btn:
                st.session_state.uretim_ekrani_acik = False
                st.rerun()

        if basla_btn:
            st.session_state.uretim_ekrani_acik = False 
            with st.spinner('Kuantum eleme motoru ve Yapay Zeka zırhı devrede...'):
                time.sleep(0.5)
                
                last_draw_nums = valid_draws[0]
                devirler = []
                ekstra_yasaklar = []
                
                if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)":
                    ekstra_yasaklar.extend(last_draw_nums)
                elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                    devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
                
                yasaklar_input = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                yasaklar = list(set(yasaklar_input + ekstra_yasaklar))
                
                bankolar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                sabit_sayilar = list(set(devirler + bankolar))
                
                errors = []
                if sicak_hedef + orta_hedef + soguk_hedef != 5: errors.append("Sıcak+Orta+Soğuk = 5 olmalı.")
                if tek_hedef + cift_hedef != 5: errors.append("Tek+Çift = 5 olmalı.")
                if b1 + b2 + b3 + b4 != 5: errors.append("Basamak toplamları = 5 olmalı.")
                if alt_hedef + ust_hedef != 5: errors.append("Alt+Üst bölge = 5 olmalı.")
                if len(sabit_sayilar) > 5: errors.append("Banko ve Devir sayılarının toplamı 5'i geçemez.")
                for s in sabit_sayilar:
                    if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko/Devir hem de Yasaklı listesinde olamaz!")
                
                if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                    for d in devirler:
                        if d not in last_draw_nums:
                            errors.append(f"Hata: Girdiğiniz '{d}' sayısı geçen haftanın çekilişinde yok! Lütfen geçerli bir devir sayısı girin: {last_draw_nums}")

                if errors:
                    for e in errors: st.error(e)
                else:
                    adaylar = [x for x in range(1, 35) if x not in yasaklar and x not in sabit_sayilar]
                    kalan_secim_sayisi = 5 - len(sabit_sayilar)
                    
                    valid_combinations = []
                    for comb in combinations(adaylar, kalan_secim_sayisi):
                        col = sorted(sabit_sayilar + list(comb))
                        
                        if devir_secimi == "VAR (Sistem rastgele 1 sayı seçsin)":
                            ortak_sayi_adedi = sum(1 for x in col if x in last_draw_nums)
                            if ortak_sayi_adedi != 1: 
                                continue

                        bas_1 = sum(1 for x in col if x <= 9)
                        bas_2 = sum(1 for x in col if 10 <= x <= 19)
                        bas_3 = sum(1 for x in col if 20 <= x <= 29)
                        bas_4 = sum(1 for x in col if x >= 30)
                        if bas_1 != b1 or bas_2 != b2 or bas_3 != b3 or bas_4 != b4: continue
                        
                        tek = sum(1 for x in col if x % 2 != 0)
                        if tek != tek_hedef or (5 - tek) != cift_hedef: continue
                        
                        s = sum(1 for x in col if x in hot_nums)
                        o = sum(1 for x in col if x in medium_nums)
                        c = sum(1 for x in col if x in cold_nums)
                        if s != sicak_hedef or o != orta_hedef or c != soguk_hedef: continue
                        
                        has_cons = any(col[i]+1 == col[i+1] for i in range(4))
                        if (ardisik == "VAR" and not has_cons) or (ardisik == "YOK" and has_cons): continue
                        
                        roots = [x % 10 for x in col]
                        r_counts = list(Counter(roots).values())
                        r_counts.sort(reverse=True)
                        if kese_koku == "VAR (1 Çift)":
                            if r_counts != [2, 1, 1]: continue
                        else:
                            if r_counts != [1, 1, 1, 1, 1]: continue
                        
                        if any(is_enemy(pair[0], pair[1]) for pair in combinations(col, 2)): continue
                        if not (min_toplam <= sum(col) <= max_toplam): continue
                        if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam): continue
                        
                        alt = sum(1 for x in col if x <= 17)
                        if alt != alt_hedef or (5 - alt) != ust_hedef: continue
                        
                        valid_combinations.append({
                            'c': col, 'sum': sum(col), 'klan': len(set([klan_labels[x] for x in col if x in klan_labels]))
                        })

                    if len(valid_combinations) > 0:
                        valid_combinations.sort(key=lambda x: (-x['klan'], abs(x['sum'] - 86.4)))
                        
                        gosterilecek_adet = min(kolon_sayisi, len(valid_combinations))
                    
                        if gosterilecek_adet < kolon_sayisi:
                            st.warning(f"Sadece {len(valid_combinations)} kusursuz dizilim bulunabildi. Kurallarınız çok katı olduğu için {kolon_sayisi} adet kolon oluşturulamadı. Bulunanların tamamı aşağıdadır:")
                        else:
                            st.success(f"Tüm ağır filtreler aşıldı! Havuzdaki {len(valid_combinations)} kusursuz dizilim arasından EN İYİ {gosterilecek_adet} kolon seçildi.")

                        for i in range(gosterilecek_adet):
                            secilen = valid_combinations[i]['c']
                            klan_degeri = valid_combinations[i]['klan']
                            
                            if kolon_sayisi > 1:
                                st.markdown(f"<h4 style='color:#dc2626; text-align:center; margin-top:20px; font-weight:900; background-color:#fef2f2; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                            
                            # --- YAPAY ZEKA +1 SEÇİM MOTORU ---
                            try:
                                # Analizi sistemi yormamak için sadece üretim anında 1 kez yapıyoruz
                                if "smart_plus_pool" not in st.session_state:
                                    import pandas as pd
                                    import random
                                    from collections import Counter
                                    
                                    # 6. Sütun (index 5) Şans Topundaki +1 sayılardır
                                    df_plus = pd.read_excel('chance.son.xlsx', sheet_name=0, header=None, engine='openpyxl')
                                    all_plus = pd.to_numeric(df_plus.iloc[:, 5], errors='coerce').dropna().astype(int).tolist()
                                    all_plus = [x for x in all_plus if 1 <= x <= 14]
                                    
                                    p_counts = Counter(all_plus)
                                    # KURAL 1: Tarihin en çok çıkan 3 "Sıcak" artı sayısı
                                    hot_p = [x[0] for x in p_counts.most_common(3)]
                                    
                                    # KURAL 2: Son 15 haftada gelmeyen "Uyuyan" artı sayılar
                                    recent_p = all_plus[:15]
                                    sleep_p = [x for x in range(1, 15) if x not in recent_p]
                                    
                                    # Havuzu birleştir (Sıcaklar ve Uyuyanlar)
                                    st.session_state.smart_plus_pool = hot_p + (sleep_p if sleep_p else [random.choice(range(1,15))])
                                
                                # Kesişen seçkin havuzdan bu kolona özel akıllı seçim yap
                                secilen_arti = random.choice(st.session_state.smart_plus_pool)
                            except:
                                # Eğer dosyadan +1 okumada bir sorun olursa, standart altın oran sayılarından seç
                                import random
                                secilen_arti = random.choice([2, 4, 7, 9, 12, 14])

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
                            
                            mc1, mc2, mc3, mc4 = st.columns(4)
                            with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#d80073;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                            with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#d80073;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                            with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                            with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span class='highlight-yellow' style='font-size:16px;'>0 (Temiz)</span></div>", unsafe_allow_html=True)
                            
                            if i < gosterilecek_adet - 1:
                                st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)
                    else:
                        st.error("🚨 PARADOKS TESPİT EDİLDİ: Bu kadar katı kuralı aynı anda sağlayan hiçbir sayı evrende bulunamadı. Kurallardan birini esnetin.")

       # --- 4 YENİ SEKME ---
        st.markdown("<br><hr style='border: 3px solid #e2e8f0; margin-bottom: 25px;'>", unsafe_allow_html=True)
        
        # 3. ve 4. Sekmeleri diğerleriyle aynı kalınlıkta ve siyah yapmak için CSS müdahalesi
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
            
            st.markdown("""
            <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0ea5e9; padding: 12px 15px; margin-bottom: 15px; border-radius: 4px; color: #334155; font-size: 0.90rem; line-height: 1.5;'>
                Frekansları seçin; <b>Yapay Zeka motoru</b> sizin için bu frekansın tarihte kaç kez yaşandığını, bu frekans geldiğinde <b>tek/çift</b> yüzdesini, <b>kök eşleşme</b> (rakamların sonu aynı olan sayılar örn: 15-25), önceki haftadan <b>devir</b> yüzdelerini, <b>ardışık, basamak ve alt/üst bölge</b> yüzdelerini sizin için hesaplasın.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-bottom: 20px; margin-top: 10px;">
                <div style="flex: 1; background-color: #fff5f5; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <strong style="color: #c53030; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔥 SICAK (≥26): {len(hot_nums)} Adet</strong>
                    <p style="font-family: monospace; font-size: 12px; color: #742a2a; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(hot_nums)))}</p>
                </div>
                <div style="flex: 1; background-color: #ebf8ff; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <strong style="color: #2b6cb0; font-size: 0.90rem; display: block; margin-bottom: 5px;">🔵 ORTA (20-25): {len(medium_nums)} Adet</strong>
                    <p style="font-family: monospace; font-size: 12px; color: #2c5282; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(medium_nums)))}</p>
                </div>
                <div style="flex: 1; background-color: #fefbeb; border: 2px solid #000000; border-radius: 6px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <strong style="color: #b7791f; font-size: 0.90rem; display: block; margin-bottom: 5px;">❄️ SOĞUK (≤19): {len(cold_nums)} Adet</strong>
                    <p style="font-family: monospace; font-size: 12px; color: #744210; margin: 0; line-height: 1.6;">{', '.join(map(str, sorted(cold_nums)))}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            last_s = sum(1 for x in valid_draws[0] if x in hot_nums)
            last_o = sum(1 for x in valid_draws[0] if x in medium_nums)
            last_c = sum(1 for x in valid_draws[0] if x in cold_nums)
            
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
                st.warning("⚠️ Sıcak, Orta ve Soğuk sayılarının toplamı tam 5 olmalıdır!")
            else:
                target_freq = f"{target_s}S - {target_o}O - {target_c}C"
                t_draws = []
                for i in range(1, len(valid_draws)):
                    if get_f_pattern(valid_draws[i]) == target_freq:
                        next_d = valid_draws[i-1]
                        t_draws.append({
                            'tc': get_tc(next_d), 'ard': get_ard(next_d), 'kok': get_k(next_d),
                            'dev': get_dev(valid_draws[i], next_d), 'bas': get_basamak_pattern(next_d),
                            'bolge': get_bolge_pattern_sans(next_d)
                        })

                if len(t_draws) > 0:
                    st.info(f"**Seçilen Şablon:** {target_freq} | Tarihte bu şablondan sonra **{len(t_draws)}** kez çekiliş yapılmış:")
                    tc_c = Counter([x['tc'] for x in t_draws])
                    ard_c = Counter([x['ard'] for x in t_draws])
                    kok_c = Counter([x['kok'] for x in t_draws])
                    dev_c = Counter([x['dev'] for x in t_draws])
                    bas_c = Counter([x['bas'] for x in t_draws])
                    bolge_c = Counter([x['bolge'] for x in t_draws])
                    
                    def format_pct(counter):
                        total = sum(counter.values())
                        return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                    
                    copy_text = f"🎯 ÇAPRAZ ANALİZ ÇIKTISI (BAZ FREKANS: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT REFLEKSİ ---\n{format_pct(tc_c)}\n\n--- 2. ARDIŞIK REFLEKSİ ---\n{format_pct(ard_c)}\n\n--- 3. KÖK EŞLEŞMESİ REFLEKSİ ---\n{format_pct(kok_c)}\n\n--- 4. DEVİR REFLEKSİ ---\n{format_pct(dev_c)}\n\n--- 5. BASAMAK REFLEKSİ ---\n{format_pct(bas_c)}\n\n--- 6. BÖLGE REFLEKSİ (Alt-Üst) ---\n{format_pct(bolge_c)}"
                    
                    st.markdown(f'''
                    <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.warning(f"Tarihte daha önce {target_freq} şablonu yaşanıp ardından çekiliş yapılmamış.")

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
            <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #8b5cf6; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.10rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                Makinenin sinir uçlarına bağlanın. Veritabanındaki en popüler şablonları inceleyin ve kendi belirlediğiniz frekans senaryosunun ardından yaşanacakları simüle edin.
Örneğin son çekilişteki frekans aralıklarını altta belirtin ve bu frekans aralığından sonra gelen tüm istatistikleri inceleyin
            </div>
            """, unsafe_allow_html=True)

            # 1. Popüler Frekanslar
            all_freqs = [get_f_pattern(d) for d in valid_draws]
            freq_counts = Counter(all_freqs)
            
            st.markdown("#### 📊 VERİTABANINDAKİ EN POPÜLER FREKANS ŞABLONLARI")
            pop_html = "<div style='display:flex; flex-wrap:wrap; gap:10px; margin-bottom:30px;'>"
            for f, c in freq_counts.most_common(5):
                pop_html += f"<div style='background-color:#ffffff; border:2px solid #cbd5e1; padding:10px 15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.05); text-align:center;'><b>{f}</b><br><span style='color:#db2777; font-weight:900; font-size:14px;'>{c} Kez Yaşandı</span></div>"
            pop_html += "</div>"
            st.markdown(pop_html, unsafe_allow_html=True)

            # 2. İnteraktif Sorgu Alanı
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
            
            # SORGULA BUTONU
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
# --- SAYFA SONU (ALT) ÜRETİM BUTONU ---
        st.markdown("<br><hr style='border: 2px dashed #cbd5e1; margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        if not st.session_state.uretim_ekrani_acik:
            st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; font-weight:bold; margin-bottom:15px;'>Tüm analizleri incelediyseniz motoru ateşleyebilirsiniz 👇</p>", unsafe_allow_html=True)
            c_alt_sol, c_alt_orta, c_alt_sag = st.columns([1, 2, 1])
            with c_alt_orta:
                # Butonun hata vermemesi için özel 'key' atandı
                if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", type="primary", use_container_width=True, key="alt_uretim_btn_sans_topu"):
                    st.session_state.uretim_ekrani_acik = True
                    st.rerun()

# ==========================================
# 🔵 2. MODÜL: SÜPER LOTO
# ==========================================
elif selected_game == "SÜPER LOTO AI":
    
    # --- İZOLE VERİ OKUMA MOTORU (HATA İHTİMALİ SIFIRLANDI) ---
    if "sl_data" not in st.session_state:
        try:
            import pandas as pd
            df = pd.read_excel('süper.xlsx', sheet_name=0, header=None, engine='openpyxl')
            v_draws = []
            for index, row in df.iterrows():
                try:
                    # Satırdaki metinleri/boşlukları yut, sadece rakamları çıkar
                    clean_row = pd.to_numeric(row, errors='coerce').dropna().astype(int).tolist()
                    # Sadece 1 ile 60 arasındaki geçerli Süper Loto sayılarını süz
                    clean_nums = [x for x in clean_row if 1 <= x <= 60]
                    clean_unique = list(set(clean_nums))
                    # Eğer elde temiz 6 sayı kaldıysa, çekiliş geçerlidir
                    if len(clean_unique) >= 6:
                        v_draws.append(sorted(clean_unique[:6]))
                except:
                    pass
            
            if v_draws:
                st.session_state.sl_data = v_draws
                st.session_state.sl_msg = f"✅ Veritabanı Yüklendi: {len(v_draws)} Çekiliş (Süper Loto)"
            else:
                st.session_state.sl_data = None
                st.session_state.sl_msg = "🚨 HATA: 'süper.xlsx' okundu ancak içinde 1-60 arası tam 6 sayılık bir satır dizilimi bulunamadı."
        except Exception as e:
            st.session_state.sl_data = None
            st.session_state.sl_msg = f"🚨 KRİTİK HATA: 'süper.xlsx' dosyası bulunamadı veya açılamıyor. Hata Kodu: {e}"

    valid_draws = st.session_state.sl_data
    msg = st.session_state.sl_msg

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
<strong>💡 Strateji Önerisi:</strong> Sol menüden kurallarını mantıklı bir çerçevede kur. Motoru ateşle! Filtreleri aşan o yegâne kolona ulaşana kadar denemeye devam et.
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
        
        expected = total_draws * (6 / 60)
        hot_limit = int(np.ceil(expected * 1.35))
        cold_limit = int(np.floor(expected * 0.75))
        
        hot_nums = [n for n in range(1, 61) if counts.get(n, 0) >= hot_limit]
        cold_nums = [n for n in range(1, 61) if counts.get(n, 0) <= cold_limit]
        medium_nums = [n for n in range(1, 61) if cold_limit < counts.get(n, 0) < hot_limit]

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

        st.sidebar.markdown("## ⚙️ SÜPER LOTO FİLTRELERİ")

        with st.sidebar.expander("📊 0. Temel Frekans", expanded=True):
            sc1, sc2, sc3 = st.columns(3)
            s_hedef = sc1.number_input("Sıcak", 0, 6, 2, key="sl_s")
            o_hedef = sc2.number_input("Orta", 0, 6, 3, key="sl_o")
            c_hedef = sc3.number_input("Soğuk", 0, 6, 1, key="sl_c")

        with st.sidebar.expander("1. Tek/Çift Refleksi", expanded=True):
            tc1, tc2 = st.columns(2)
            tek_hedef = tc1.number_input("Tek", 0, 6, 3, key="sl_t")
            cift_hedef = tc2.number_input("Çift", 0, 6, 3, key="sl_ct")

        with st.sidebar.expander("2. Ardışık & 3. Kök Refleksi", expanded=True):
            c_strat1, c_strat2 = st.columns(2)
            ardisik = c_strat1.selectbox("Ardışık Sayı", ["YOK", "VAR"], key="sl_ard")
            kese_koku = c_strat2.selectbox("Kök Eşleşmesi", ["VAR (1 Çift)", "YOK"], key="sl_kok")

        with st.sidebar.expander("4. Devir Refleksi", expanded=True):
            devir_secimi = st.selectbox("Devir (Önceki Haftadan)", [
                "Farketmez", 
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

        # --- ÜRETİM ALANI (EN ÜSTTE VE ORTADA) ---
        st.info(f"{msg} | **Son Çekiliş:** {valid_draws[0]}")
        st.markdown("---")

        if "sl_uretim_ekrani_acik" not in st.session_state:
            st.session_state.sl_uretim_ekrani_acik = False

        sl_basla_btn = False
        sl_kolon_sayisi = 1

        if not st.session_state.sl_uretim_ekrani_acik:
            c_btn_sol, c_btn_orta, c_btn_sag = st.columns([1, 2, 1])
            with c_btn_orta:
                if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", type="primary", use_container_width=True, key="sl_btn_1"):
                    st.session_state.sl_uretim_ekrani_acik = True
                    st.rerun() 
        
        if st.session_state.sl_uretim_ekrani_acik:
            st.markdown("""
                <div style='border: 3px solid #1e3a8a; border-radius: 12px; padding: 20px; background-color: #f8fafc; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.15); margin-bottom: 20px;'>
                    <h3 style='color: #1e3a8a; margin-top: 0; font-weight: 900; text-align: center; letter-spacing: 1px;'>🤖 KUSURSUZ ÜRETİM ONAYI</h3>
                    <p style='color: #334155; text-align: center; font-size: 16px; font-weight: 600; margin-bottom: 0px;'>Yapay Zeka'nın sizin için kaç adet Süper Loto kolonu üretmesini istersiniz?</p>
                </div>
            """, unsafe_allow_html=True)
            
            c_bos1, c_orta, c_bos2 = st.columns([1, 1.5, 1])
            
            with c_orta:
                st.markdown("<div style='background-color:#1e3a8a; border:2px solid #0f172a; padding:10px; border-radius:8px; text-align:center; font-weight:900; color:#ffffff; font-size:16px; margin-bottom:5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); letter-spacing: 1px;'>🔢 KOLON ADEDİ SEÇİN</div>", unsafe_allow_html=True)
                sl_kolon_sayisi = st.number_input("Kolon Adedi", min_value=1, max_value=10, value=1, label_visibility="collapsed", key="sl_kolon_adet")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                sl_basla_btn = st.button("✅ MOTORU ATEŞLE VE ÜRET", type="primary", use_container_width=True, key="sl_btn_basla")
            with col_btn2:
                iptal_btn = st.button("❌ İPTAL", use_container_width=True, key="sl_btn_iptal")
                
            if iptal_btn:
                st.session_state.sl_uretim_ekrani_acik = False
                st.rerun()

        if sl_basla_btn:
            st.session_state.sl_uretim_ekrani_acik = False 
            with st.spinner('Kuantum eleme motoru ve Yapay Zeka zırhı devrede...'):
                time.sleep(0.5)
                
                last_draw_nums = valid_draws[0]
                devirler = []
                ekstra_yasaklar = []
                
                if devir_secimi == "YOK (Önceki haftadan sayı gelmesin)":
                    ekstra_yasaklar.extend(last_draw_nums)
                elif devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                    devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
                
                yasaklar_input = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
                yasaklar = list(set(yasaklar_input + ekstra_yasaklar))
                
                bankolar = [int(x.strip()) for x in banko_sayilar_str.split(',') if x.strip().isdigit()]
                sabit_sayilar = list(set(devirler + bankolar))
                
                errors = []
                if s_hedef + o_hedef + c_hedef != 6: errors.append("Sıcak+Orta+Soğuk = 6 olmalı.")
                if tek_hedef + cift_hedef != 6: errors.append("Tek+Çift = 6 olmalı.")
                if bolge1 + bolge2 + bolge3 != 6: errors.append("Alt+Orta+Üst Bölge toplamı 6 olmalı.")
                if len(sabit_sayilar) > 6: errors.append("Banko ve Devir sayılarının toplamı 6'yı geçemez.")
                for s in sabit_sayilar:
                    if s in yasaklar: errors.append(f"Hata: {s} sayısı hem Banko/Devir hem de Yasaklı listesinde olamaz!")
                
                if devir_secimi == "VAR (Sayıyı ben seçeceğim)":
                    for d in devirler:
                        if d not in last_draw_nums:
                            errors.append(f"Hata: Girdiğiniz '{d}' sayısı geçen haftanın çekilişinde yok! Lütfen geçerli bir devir sayısı girin: {last_draw_nums}")

                if errors:
                    for e in errors: st.error(e)
                else:
                    adaylar = [x for x in range(1, 61) if x not in yasaklar and x not in sabit_sayilar]
                    kalan_secim_sayisi = 6 - len(sabit_sayilar)
                    
                    hot_pool = [x for x in hot_nums if x in adaylar]
                    med_pool = [x for x in medium_nums if x in adaylar]
                    cold_pool = [x for x in cold_nums if x in adaylar]

                    b_hot = sum(1 for x in sabit_sayilar if x in hot_nums)
                    b_med = sum(1 for x in sabit_sayilar if x in medium_nums)
                    b_cold = sum(1 for x in sabit_sayilar if x in cold_nums)

                    req_hot = s_hedef - b_hot
                    req_med = o_hedef - b_med
                    req_cold = c_hedef - b_cold

                    if req_hot < 0 or req_med < 0 or req_cold < 0:
                        st.error("🚨 HATA: Banko sayılarının frekansları, belirlediğin hedefleri aşıyor!")
                    elif req_hot > len(hot_pool) or req_med > len(med_pool) or req_cold > len(cold_pool):
                        st.error(f"🚨 HATA: Kotalar havuzdaki sayıları aşıyor! (Sıcak havuzda {len(hot_pool)}, Orta havuzda {len(med_pool)}, Soğuk havuzda {len(cold_pool)} sayı kaldı)")
                    else:
                        candidates = []
                        valid_combinations = []
                        attempts = 0
                        
                        while len(candidates) < 100000 and attempts < 200000:
                            attempts += 1
                            h_pick = random.sample(hot_pool, req_hot) if req_hot > 0 else []
                            m_pick = random.sample(med_pool, req_med) if req_med > 0 else []
                            c_pick = random.sample(cold_pool, req_cold) if req_cold > 0 else []
                            col = sorted(sabit_sayilar + h_pick + m_pick + c_pick)
                            if len(set(col)) == 6:
                                candidates.append(tuple(col))
                        
                        candidates = list(set(candidates))
                        
                        for col in candidates:
                            if devir_secimi == "VAR (Sistem rastgele 1 sayı seçsin)":
                                ortak_sayi_adedi = sum(1 for x in col if x in last_draw_nums)
                                if ortak_sayi_adedi != 1: 
                                    continue

                            b1 = sum(1 for x in col if 1 <= x <= 20)
                            b2 = sum(1 for x in col if 21 <= x <= 40)
                            b3 = sum(1 for x in col if 41 <= x <= 60)
                            if b1 != bolge1 or b2 != bolge2 or b3 != bolge3: continue
                            
                            tek = sum(1 for x in col if x % 2 != 0)
                            cift = 6 - tek
                            if tek != tek_hedef or cift != cift_hedef: continue
                            
                            has_cons = any(col[i]+1 == col[i+1] for i in range(5))
                            if (ardisik == "VAR" and not has_cons) or (ardisik == "YOK" and has_cons): continue
                            
                            roots = [x % 10 for x in col]
                            r_counts = list(Counter(roots).values())
                            r_counts.sort(reverse=True)
                            
                            if kese_koku == "VAR (1 Çift)":
                                if r_counts != [2, 1, 1, 1, 1]: continue
                            else:
                                if r_counts != [1, 1, 1, 1, 1, 1]: continue
                            
                            enemy_found = False
                            for pair in combinations(col, 2):
                                if is_enemy(pair[0], pair[1]):
                                    enemy_found = True
                                    break
                            if enemy_found: continue
                            
                            if not (min_toplam <= sum(col) <= max_toplam): continue
                            if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam): continue
                            
                            klan_cesitliligi = len(set([klan_labels[x] for x in col if x in klan_labels]))
                            valid_combinations.append({
                                'c': col, 'sum': sum(col), 'klan': klan_cesitliligi
                            })

                        if len(valid_combinations) > 0:
                            valid_combinations.sort(key=lambda x: (-x['klan'], abs(x['sum'] - 183)))
                            
                            gosterilecek_adet = min(sl_kolon_sayisi, len(valid_combinations))
                        
                            if gosterilecek_adet < sl_kolon_sayisi:
                                st.warning(f"Sadece {len(valid_combinations)} kusursuz dizilim bulunabildi. Kurallarınız çok katı olduğu için {sl_kolon_sayisi} adet kolon oluşturulamadı. Bulunanların tamamı aşağıdadır:")
                            else:
                                st.success(f"Tüm ağır filtreler aşıldı! Havuzdaki {len(valid_combinations)} kusursuz dizilim arasından EN İYİ {gosterilecek_adet} kolon seçildi.")

                            for i in range(gosterilecek_adet):
                                secilen = valid_combinations[i]['c']
                                klan_degeri = valid_combinations[i]['klan']
                                
                                if sl_kolon_sayisi > 1:
                                    st.markdown(f"<h4 style='color:#059669; text-align:center; margin-top:20px; font-weight:900; background-color:#ecfdf5; padding:5px; border-radius:5px;'>✨ KOLON {i+1}</h4>", unsafe_allow_html=True)
                                
                                html_balls = f"""
                                <div style='text-align: center; margin: 15px 0 25px 0;'>
                                    <div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[0]}</div>
                                    <div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[1]}</div>
                                    <div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[2]}</div>
                                    <div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[3]}</div>
                                    <div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[4]}</div>
                                    <div class='number-ball' style='background-color:#059669; color:white; border-color:#047857;'>{secilen[5]}</div>
                                </div>
                                """
                                st.markdown(html_balls, unsafe_allow_html=True)
                                
                                mc1, mc2, mc3, mc4 = st.columns(4)
                                with mc1: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>📉 Çan Eğrisi</b><br><span style='font-size:20px; color:#059669;'>{sum(secilen)}</span></div>", unsafe_allow_html=True)
                                with mc2: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>↔️ Kapsam</b><br><span style='font-size:20px; color:#059669;'>{secilen[-1] - secilen[0]}</span></div>", unsafe_allow_html=True)
                                with mc3: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🛡️ Klan Zırhı</b><br><span style='font-size:20px; color:#5a9bd5;'>{klan_degeri} Farklı</span></div>", unsafe_allow_html=True)
                                with mc4: st.markdown(f"<div class='metric-card' style='padding:10px;'><b>🤖 Düşman Testi</b><br><span class='highlight-yellow' style='font-size:16px;'>0 (Temiz)</span></div>", unsafe_allow_html=True)
                                
                                if i < gosterilecek_adet - 1:
                                    st.markdown("<hr style='border: 1px dashed #cbd5e1; margin: 30px 0;'>", unsafe_allow_html=True)
                        else:
                            st.error("🚨 PARADOKS TESPİT EDİLDİ: Bu kadar katı kuralı aynı anda sağlayan hiçbir sayı evrende bulunamadı. Kurallardan birini esnetin.")

        # --- 4 YENİ SEKME (CSS İLE SİMSİYAH VE KALIN YAPILANDIRILMIŞ) ---
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
            
            st.markdown("""
            <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0ea5e9; padding: 12px 15px; margin-bottom: 15px; border-radius: 4px; color: #334155; font-size: 0.90rem; line-height: 1.5;'>
                Frekansları seçin; <b>Yapay Zeka motoru</b> sizin için bu frekansın tarihte kaç kez yaşandığını, bu frekans geldiğinde <b>tek/çift</b> yüzdesini, <b>kök eşleşme</b>, önceki haftadan <b>devir</b> yüzdelerini, <b>ardışık ve alt/orta/üst bölge</b> yüzdelerini sizin için hesaplasın.
            </div>
            """, unsafe_allow_html=True)
            
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
                st.warning("⚠️ Sıcak, Orta ve Soğuk sayılarının toplamı tam 6 olmalıdır!")
            else:
                target_freq = f"{target_s}S - {target_o}O - {target_c}C"
                t_draws = []
                for i in range(1, len(valid_draws)):
                    if get_f_pattern(valid_draws[i]) == target_freq:
                        next_d = valid_draws[i-1]
                        t_draws.append({
                            'tc': get_tc(next_d), 'ard': get_ard(next_d), 'kok': get_k(next_d),
                            'dev': get_dev(valid_draws[i], next_d), 'bolge': get_bolge_pattern_sl(next_d)
                        })

                if len(t_draws) > 0:
                    st.info(f"**Seçilen Şablon:** {target_freq} | Tarihte bu şablondan sonra **{len(t_draws)}** kez çekiliş yapılmış:")
                    tc_c = Counter([x['tc'] for x in t_draws])
                    ard_c = Counter([x['ard'] for x in t_draws])
                    kok_c = Counter([x['kok'] for x in t_draws])
                    dev_c = Counter([x['dev'] for x in t_draws])
                    bolge_c = Counter([x['bolge'] for x in t_draws])
                    
                    def format_pct(counter):
                        total = sum(counter.values())
                        return "\n".join([f"- {k}: %{round((v/total)*100, 2)}" for k, v in counter.most_common()])
                    
                    copy_text = f"🎯 ÇAPRAZ ANALİZ ÇIKTISI (BAZ FREKANS: {target_freq} - {len(t_draws)} Kez Yaşandı)\n\n--- 1. TEK/ÇİFT REFLEKSİ ---\n{format_pct(tc_c)}\n\n--- 2. ARDIŞIK REFLEKSİ ---\n{format_pct(ard_c)}\n\n--- 3. KÖK EŞLEŞMESİ REFLEKSİ ---\n{format_pct(kok_c)}\n\n--- 4. DEVİR REFLEKSİ ---\n{format_pct(dev_c)}\n\n--- 5. BÖLGE REFLEKSİ (Alt-Orta-Üst) ---\n{format_pct(bolge_c)}"
                    
                    st.markdown(f'''
                    <div style="background-color: #ffffff; padding: 20px; border: 2px solid #000000; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <pre style="color: #000000; font-weight: 800; font-size: 15px; font-family: Consolas, monospace; background: transparent; border: none; margin: 0; padding: 0;">{copy_text}</pre>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.warning(f"Tarihte daha önce {target_freq} şablonu yaşanıp ardından çekiliş yapılmamış.")

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
            <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #8b5cf6; padding: 18px 20px; margin-bottom: 25px; border-radius: 6px; color: #000000; font-size: 1.10rem; font-weight: 700; line-height: 1.6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                Makinenin sinir uçlarına bağlanın. Veritabanındaki en popüler şablonları inceleyin ve kendi belirlediğiniz frekans senaryosunun ardından yaşanacakları simüle edin.
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

        # --- SAYFA SONU (ALT) ÜRETİM BUTONU ---
        st.markdown("<br><hr style='border: 2px dashed #cbd5e1; margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        if not st.session_state.sl_uretim_ekrani_acik:
            st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; font-weight:bold; margin-bottom:15px;'>Tüm analizleri incelediyseniz motoru ateşleyebilirsiniz 👇</p>", unsafe_allow_html=True)
            c_alt_sol, c_alt_orta, c_alt_sag = st.columns([1, 2, 1])
            with c_alt_orta:
                if st.button("🚀 YAPAY ZEKA ÖĞRENMESİYLE KUSURSUZ KOLONU ÜRET", type="primary", use_container_width=True, key="alt_uretim_btn_super"):
                    st.session_state.sl_uretim_ekrani_acik = True
                    st.rerun()
# ==========================================
# 🟡 4. MODÜL: ON NUMARA
# ==========================================
elif selected_game == "ON NUMARA AI":
    st.markdown("<div class='main-title' style='color:#0096d6;'>ON NUMARA ANALİZİ</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title' style='color:#1e293b;'>80 Topluk Kapsamlı Frekans Radarı</div>", unsafe_allow_html=True)
    st.markdown("<div class='game-card'><h2 style='color: #0096d6;'>🛠️ Modül İnşa Aşamasında</h2><p style='color: #64748b; font-size: 18px;'>On Numara, 80 toptan 22'sinin çekildiği istatistiksel olarak tamamen farklı bir canavardır.</p></div>", unsafe_allow_html=True)

st.markdown("""
    <div class='footer-text'>
        <strong>© 2026 Kaptan Analiz Merkezi. Tüm Hakları Saklıdır.</strong><br>
        <span style='font-size: 0.85rem;'>Bu platform, K-Means Kümeleme ve Apriori algoritmaları kullanılarak geliştirilmiş bir Yapay Zeka AR-GE laboratuvarıdır.</span>
    </div>
""", unsafe_allow_html=True)

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
    
    with col_admin:
        # st.sidebar.expander yerine st.expander kullanıyoruz ki ana sayfada çıksın
        with st.expander("🔒 Admin - Otopilot", expanded=False):
            st.markdown("<p style='font-size: 13px; color: #64748b; text-align: center;'>Veritabanını buradan güncelleyin.</p>", unsafe_allow_html=True)
            admin_pass = st.text_input("Şifre:", type="password", key="admin_pwd")
            if admin_pass == "kaptan":
                st.success("Otopilot Aktif!")
                yeni_sayilar = st.text_input("Sayılar (Örn: 4, 15, 22, 28, 31):")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("💾 Kaydet", use_container_width=True):
                        if yeni_sayilar:
                            try:
                                nums = [int(x.strip()) for x in yeni_sayilar.split(',') if x.strip().isdigit()]
                                if len(nums) >= 5:
                                    nums_sorted = sorted(nums)
                                    new_df = pd.DataFrame([nums_sorted])
                                    if os.path.exists("otopilot_veriler.csv"):
                                        existing = pd.read_csv("otopilot_veriler.csv", header=None)
                                        new_df = pd.concat([new_df, existing], ignore_index=True)
                                    new_df.to_csv("otopilot_veriler.csv", index=False, header=False)
                                    st.cache_data.clear()
                                    st.success(f"Başarılı! Sisteme işlendi.")
                                    time.sleep(1.5)
                                    st.rerun()
                                else: st.warning("Eksik sayı.")
                            except: st.error("Hatalı format.")
                with c_btn2:
                    if os.path.exists("otopilot_veriler.csv"):
                        if st.button("🗑️ Sıfırla", use_container_width=True):
                            os.remove("otopilot_veriler.csv")
                            st.cache_data.clear()
                            st.success("Temizlendi!")
                            time.sleep(1.5)
                            st.rerun()