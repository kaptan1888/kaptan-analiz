import streamlit as st
import pandas as pd
from collections import Counter
import glob
import numpy as np
from itertools import combinations
from sklearn.cluster import KMeans
import os
import time
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- SAYFA VE VİZYON AYARLARI ---
st.set_page_config(page_title="Kaptan Analiz Merkezi", page_icon="🧿", layout="wide", initial_sidebar_state="expanded")

# --- ÖZEL CSS (PREMIUM GÖRÜNÜM) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-title { color: #0f172a; font-weight: 900; text-align: center; font-size: 2.5rem; margin-bottom: 0px;}
    .sub-title { color: #3b82f6; font-weight: 600; text-align: center; font-size: 1.2rem; margin-top: -10px; margin-bottom: 30px;}
    .metric-card { background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #3b82f6;}
    .number-ball { display: inline-block; width: 60px; height: 60px; line-height: 60px; border-radius: 50%; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; font-size: 24px; font-weight: bold; text-align: center; margin: 0 5px; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.5);}
    .plus-ball { display: inline-block; width: 60px; height: 60px; line-height: 60px; border-radius: 50%; background: linear-gradient(135deg, #b91c1c 0%, #ef4444 100%); color: white; font-size: 24px; font-weight: bold; text-align: center; margin: 0 5px; box-shadow: 0 4px 10px rgba(239, 68, 68, 0.5);}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🧿 KAPTAN ANALİZ MERKEZİ</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Yapay Zeka Destekli Kusursuz Kolon Motoru</div>", unsafe_allow_html=True)

# --- VERİ YÜKLEME VE OTOPİLOT BİRLEŞTİRME ---
@st.cache_data
def load_data():
    files = glob.glob('*.xlsx') + glob.glob('*.xls') + glob.glob('*.csv')
    valid_draws = []
    if not files: return None, "Klasörde veri dosyası bulunamadı!"
    
    main_files = [f for f in files if "otopilot_veriler.csv" not in f]
    
    if main_files:
        file_path = main_files[0]
        try:
            if file_path.endswith('.csv'): df = pd.read_csv(file_path, header=None)
            else: df = pd.read_excel(file_path, header=None)
                
            for index, row in df.iterrows():
                try:
                    nums = pd.to_numeric(row[:5], errors='coerce').dropna().astype(int).tolist()
                    nums = [x for x in nums if 1 <= x <= 34]
                    if len(set(nums)) == 5: valid_draws.append(sorted(nums))
                except: pass
        except Exception as e: return None, f"Hata: {e}"

    oto_draws = []
    if os.path.exists("otopilot_veriler.csv"):
        try:
            df_oto = pd.read_csv("otopilot_veriler.csv", header=None)
            for index, row in df_oto.iterrows():
                try:
                    nums = pd.to_numeric(row[:5], errors='coerce').dropna().astype(int).tolist()
                    nums = [x for x in nums if 1 <= x <= 34]
                    if len(set(nums)) == 5: oto_draws.append(sorted(nums))
                except: pass
            valid_draws = oto_draws + valid_draws
        except: pass

    if not valid_draws: return None, "Geçerli veri yok."
    
    # Kaptana özel detaylı sistem mesajı
    msg = f"🟢 Sistem Aktif | Toplam: {len(valid_draws)} Çekiliş (Ana Dosya: {len(valid_draws)-len(oto_draws)}, Otopilot: {len(oto_draws)})"
    return valid_draws, msg

valid_draws, msg = load_data()
if not valid_draws:
    st.error(msg)
    st.stop()

# --- ANALİZ MOTORU HAZIRLIĞI ---
all_nums = [num for draw in valid_draws for num in draw]
counts = Counter(all_nums)

hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= 26]
cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= 19]
medium_nums = [n for n in range(1, 35) if 20 <= counts.get(n, 0) <= 25]

# Klanlar ve Apriori 
features = {}
for n in range(1, 35):
    d_n = [d for d in valid_draws if n in d]
    if len(d_n) == 0: features[n] = [0, 0, 0]
    else: features[n] = [len(d_n), np.mean([sum(d) for d in d_n]), np.mean([max(d)-min(d) for d in d_n])]

X = np.array(list(features.values()))
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X)
klanlar = {i: [] for i in range(4)}
for i, n in enumerate(features.keys()): klanlar[kmeans.labels_[i]].append(n)

pairs = [p for d in valid_draws for p in combinations(d, 2)]
pair_c = Counter(pairs)
all_p = set(combinations(range(1, 35), 2))
actual_p = set([p for p, c in pair_c.items() if c > 0])
enemies = list(all_p - actual_p)

def is_enemy(n1, n2): return (min(n1, n2), max(n1, n2)) in enemies

# --- SOL MENÜ (KAPTANIN KURALLARI) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2038/2038022.png", width=80)
st.sidebar.markdown("## ⚙️ KONTROL PANELİ")

with st.sidebar.expander("📊 1. Frekans & Tek/Çift", expanded=True):
    col1, col2, col3 = st.columns(3)
    sicak_hedef = col1.number_input("Sıcak", 0, 5, 2)
    orta_hedef = col2.number_input("Orta", 0, 5, 1)
    soguk_hedef = col3.number_input("Soğuk", 0, 5, 2)
    st.markdown("---")
    col4, col5 = st.columns(2)
    tek_hedef = col4.number_input("Tek", 0, 5, 3)
    cift_hedef = col5.number_input("Çift", 0, 5, 2)

with st.sidebar.expander("🔢 2. Basamak Dağılımı", expanded=True):
    col6, col7 = st.columns(2)
    col8, col9 = st.columns(2)
    b1 = col6.number_input("Birler", 0, 5, 2)
    b2 = col7.number_input("Onlar", 0, 5, 1)
    b3 = col8.number_input("Yirmiler", 0, 5, 1)
    b4 = col9.number_input("Otuzlar", 0, 5, 1)

with st.sidebar.expander("🎯 3. Strateji & Kısıtlamalar", expanded=True):
    ardisik = st.selectbox("Ardışık Sayı Durumu", ["YOK", "VAR"])
    kese_koku = st.selectbox("Kök (Son Rakam) Eşleşmesi", ["VAR", "YOK"])
    devir_sayisi_str = st.text_input("Kilit (Devir) Sayısı", "14")
    yasak_sayilar_str = st.text_input("Yasaklılar (Kara Liste)", "1, 7, 13, 29")

with st.sidebar.expander("📐 4. Makro Çerçeve", expanded=False):
    min_toplam, max_toplam = st.slider("Çan Eğrisi (Toplam)", 15, 160, (70, 105))
    min_kapsam, max_kapsam = st.slider("Kapsam (Mesafe)", 4, 33, (20, 33))
    col10, col11 = st.columns(2)
    alt_hedef = col10.number_input("Alt(1-17)", 0, 5, 3)
    ust_hedef = col11.number_input("Üst(18-34)", 0, 5, 2)

# --- ANA EKRAN SEKMELERİ ---
tab1, tab2, tab3 = st.tabs(["🎯 KUSURSUZ KOLON", "📈 YAPAY ZEKA İSTİHBARATI", "⚙️ SİSTEM & OTOPİLOT"])

# ----------------- SEKME 1: KOLON ÜRETİCİ -----------------
with tab1:
    st.info(f"**Durum:** {msg} | **Geçen Hafta (Son Oynanan):** {valid_draws[0]}")
    
    if st.button("🚀 ALGORİTMAYI ÇALIŞTIR VE KOLON ÜRET", type="primary", use_container_width=True):
        with st.spinner('Kuantum eleme motoru devrede. Tarihsel veri işleniyor...'):
            time.sleep(0.5)
            devirler = [int(x.strip()) for x in devir_sayisi_str.split(',') if x.strip().isdigit()]
            yasaklar = [int(x.strip()) for x in yasak_sayilar_str.split(',') if x.strip().isdigit()]
            
            # Kural Kontrolleri
            errors = []
            if sicak_hedef + orta_hedef + soguk_hedef != 5: errors.append("Sıcak+Orta+Soğuk = 5 olmalı.")
            if tek_hedef + cift_hedef != 5: errors.append("Tek+Çift = 5 olmalı.")
            if b1 + b2 + b3 + b4 != 5: errors.append("Basamak toplamları = 5 olmalı.")
            if alt_hedef + ust_hedef != 5: errors.append("Alt+Üst bölge = 5 olmalı.")
            
            if errors:
                for e in errors: st.error(e)
            else:
                adaylar = [x for x in range(1, 35) if x not in yasaklar]
                sabit_sayilar = devirler
                kalan_secim_sayisi = 5 - len(sabit_sayilar)
                kalan_adaylar = [x for x in adaylar if x not in sabit_sayilar]
                
                valid_combinations = []
                
                for comb in combinations(kalan_adaylar, kalan_secim_sayisi):
                    col = sorted(list(sabit_sayilar) + list(comb))
                    
                    bas_1 = sum(1 for x in col if x <= 9)
                    bas_2 = sum(1 for x in col if 10 <= x <= 19)
                    bas_3 = sum(1 for x in col if 20 <= x <= 29)
                    bas_4 = sum(1 for x in col if x >= 30)
                    if bas_1 != b1 or bas_2 != b2 or bas_3 != b3 or bas_4 != b4: continue
                    
                    tek = sum(1 for x in col if x % 2 != 0)
                    cift = 5 - tek
                    if tek != tek_hedef or cift != cift_hedef: continue
                    
                    s = sum(1 for x in col if x in hot_nums)
                    o = sum(1 for x in col if x in medium_nums)
                    c = sum(1 for x in col if x in cold_nums)
                    if s != sicak_hedef or o != orta_hedef or c != soguk_hedef: continue
                    
                    has_cons = any(col[i]+1 == col[i+1] for i in range(4))
                    if (ardisik == "VAR" and not has_cons) or (ardisik == "YOK" and has_cons): continue
                    
                    roots = [x % 10 for x in col]
                    has_root = max(Counter(roots).values()) >= 2
                    if (kese_koku == "VAR" and not has_root) or (kese_koku == "YOK" and has_root): continue
                    
                    enemy_found = False
                    for pair in combinations(col, 2):
                        if is_enemy(pair[0], pair[1]):
                            enemy_found = True
                            break
                    if enemy_found: continue
                    
                    if not (min_toplam <= sum(col) <= max_toplam): continue
                    if not (min_kapsam <= (col[-1] - col[0]) <= max_kapsam): continue
                    
                    alt = sum(1 for x in col if x <= 17)
                    ust = 5 - alt
                    if alt != alt_hedef or ust != ust_hedef: continue
                    
                    valid_combinations.append(col)

                st.markdown("---")
                if len(valid_combinations) > 0:
                    st.success(f"Filtreler başarıyla aşıldı. Tüm kurallara uyan {len(valid_combinations)} kusursuz dizilim bulundu!")
                    secilen = valid_combinations[0]
                    
                    # Dinamik +1 Tahmini (Tahterevalli Mantığı)
                    tek_count = sum(1 for n in secilen if n%2!=0)
                    if tek_count >= 3: plus_one_pred = "8 veya 14 (Çift/Dengeleyici)"
                    elif tek_count <= 2: plus_one_pred = "5 veya 11 (Tek/Sıcak)"
                    else: plus_one_pred = "7 veya 10"

                    # Görsel Toplar
                    html_balls = f"""
                    <div style='text-align: center; margin: 30px 0;'>
                        <div class='number-ball'>{secilen[0]}</div>
                        <div class='number-ball'>{secilen[1]}</div>
                        <div class='number-ball'>{secilen[2]}</div>
                        <div class='number-ball'>{secilen[3]}</div>
                        <div class='number-ball'>{secilen[4]}</div>
                        <span style='font-size:30px; font-weight:bold; color:#64748b; margin: 0 15px;'>+</span>
                        <div class='plus-ball'>?</div>
                    </div>
                    """
                    st.markdown(html_balls, unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; color:#ef4444; font-weight:bold; margin-top:-15px; margin-bottom:30px;'>Makine +1 Tavsiyesi: {plus_one_pred}</div>", unsafe_allow_html=True)
                    
                    # Premium Metrikler
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    ideal_fark = round(sum(secilen) - 86.4, 1)
                    
                    # Geçmiş Testi (Backtest)
                    hit_3 = hit_4 = hit_5 = 0
                    for d in valid_draws:
                        match = len(set(secilen).intersection(set(d)))
                        if match == 3: hit_3 += 1
                        elif match == 4: hit_4 += 1
                        elif match == 5: hit_5 += 1
                    
                    # Güven Skoru Hesaplama
                    klan_cesitliligi = len(set([k for n in secilen for k, v in klanlar.items() if n in v]))
                    guven_skoru = 60 + (klan_cesitliligi * 5) - (abs(ideal_fark) * 0.5)
                    guven_skoru = min(99.9, max(0, round(guven_skoru, 1)))

                    with mc1:
                        st.markdown(f"<div class='metric-card'><b>📉 Çan Eğrisi</b><br><span style='font-size:24px; color:#1e3a8a;'>{sum(secilen)}</span><br><span style='color:gray; font-size:12px;'>İdeale Uzaklık: {ideal_fark}</span></div>", unsafe_allow_html=True)
                    with mc2:
                        st.markdown(f"<div class='metric-card'><b>↔️ Kapsam</b><br><span style='font-size:24px; color:#1e3a8a;'>{secilen[-1] - secilen[0]}</span><br><span style='color:gray; font-size:12px;'>Kullanılan Genişlik</span></div>", unsafe_allow_html=True)
                    with mc3:
                        st.markdown(f"<div class='metric-card'><b>🛡️ Klan Zırhı</b><br><span style='font-size:24px; color:#1e3a8a;'>{klan_cesitliligi} Farklı</span><br><span style='color:gray; font-size:12px;'>Düşman İkili: 0 (Temiz)</span></div>", unsafe_allow_html=True)
                    with mc4:
                        st.markdown(f"<div class='metric-card'><b>🤖 Güven Skoru</b><br><span style='font-size:24px; color:#16a34a;'>%{guven_skoru}</span><br><span style='color:gray; font-size:12px;'>Yapay Zeka Onayı</span></div>", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander("📜 Geriye Dönük Simülasyon (Backtest) Raporu", expanded=False):
                        st.write(f"Eğer bu kusursuz kolonu son **{len(valid_draws)} haftadır** oynuyor olsaydın;")
                        st.write(f"- **5 Bilme:** {hit_5} kez")
                        st.write(f"- **4 Bilme:** {hit_4} kez")
                        st.write(f"- **3 Bilme:** {hit_3} kez")
                        if hit_4 == 0 and hit_5 == 0:
                            st.success("💡 Stratejik Avantaj: Bu 5'li kombinasyon tarihte daha önce hiç tepe yapmamış. İstatistiksel olarak patlamaya / döngüsünü kırmaya çok uygun taze bir dizilimdir.")

                else:
                    st.error("🚨 PARADOKS TESPİT EDİLDİ: Bu kadar katı kuralı aynı anda sağlayan hiçbir sayı kombinasyonu evrende bulunamadı. Lütfen kurallardan birini biraz esnetin.")

# ----------------- SEKME 2: İSTİHBARAT & GRAFİKLER -----------------
with tab2:
    st.markdown("### 📊 Görsel Zeka İstihbaratı")
    st.write("Veritabanındaki çekilişlerin tarihsel davranış modelleri.")
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        # Çan Eğrisi Histogramı
        toplamlar = [sum(d) for d in valid_draws]
        fig_bell = px.histogram(toplamlar, nbins=20, title="Tarihsel Çan Eğrisi (Kolon Toplamları)", 
                                labels={'value': 'Kolon Toplam Değeri'}, color_discrete_sequence=['#3b82f6'])
        fig_bell.add_vline(x=86.4, line_dash="dash", line_color="red", annotation_text="İdeal Merkez (86.4)")
        st.plotly_chart(fig_bell, use_container_width=True)
        
    with g_col2:
        # Sıcaklık Bar Grafiği
        df_freq = pd.DataFrame(counts.items(), columns=['Sayı', 'Frekans']).sort_values(by='Sayı')
        df_freq['Durum'] = ['Sıcak' if x >= 26 else 'Soğuk' if x <= 19 else 'Orta' for x in df_freq['Frekans']]
        color_map = {'Sıcak': '#ef4444', 'Orta': '#f59e0b', 'Soğuk': '#3b82f6'}
        fig_freq = px.bar(df_freq, x='Sayı', y='Frekans', color='Durum', color_discrete_map=color_map, 
                          title="Tüm Sayıların Sıcaklık Haritası")
        st.plotly_chart(fig_freq, use_container_width=True)

    # Güncel Havuzlar
    st.markdown("---")
    st.subheader("🎯 Güncel Operasyon Havuzları")
    c1, c2, c3 = st.columns(3)
    c1.error(f"🔥 **SICAK (≥26):**\n {', '.join(map(str, hot_nums))}")
    c2.warning(f"🟡 **ORTA (20-25):**\n {', '.join(map(str, medium_nums))}")
    c3.info(f"❄️ **SOĞUK (≤19):**\n {', '.join(map(str, cold_nums))}")

# ----------------- SEKME 3: OTOPİLOT -----------------
with tab3:
    st.markdown("### 🔒 Sistem Yöneticisi Paneli (Otopilot)")
    st.write("Veritabanını güvenle güncelle. Orijinal dosyaların korunur.")
    
    admin_pass = st.text_input("Kaptan Yetki Şifresi:", type="password", key="admin_pwd")
    
    if admin_pass == "kaptan":
        st.success("Yetki Onaylandı. Otopilot Devrede.")
        
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Hızlı Veri Enjeksiyonu")
        st.write("Geçen haftanın sonucunu girerek sistemi eğit.")
        yeni_sayilar = st.text_input("Son Çekiliş (5 sayı, araya virgül koy):", placeholder="Örn: 4, 15, 22, 28, 31")
        
        if st.button("💾 Veritabanına Yaz", type="primary"):
            if yeni_sayilar:
                try:
                    nums = [int(x.strip()) for x in yeni_sayilar.split(',') if x.strip().isdigit()]
                    if len(nums) == 5:
                        nums_sorted = sorted(nums)
                        new_df = pd.DataFrame([nums_sorted])
                        if os.path.exists("otopilot_veriler.csv"):
                            existing = pd.read_csv("otopilot_veriler.csv", header=None)
                            new_df = pd.concat([new_df, existing], ignore_index=True)
                        new_df.to_csv("otopilot_veriler.csv", index=False, header=False)
                        st.cache_data.clear()
                        st.success(f"Başarılı! {nums_sorted} öğrenildi. Makine yeniden başlatılıyor...")
                        time.sleep(2)
                        st.rerun()
                    else: st.warning("Lütfen tam 5 sayı girin.")
                except: st.error("Hatalı format.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 📂 Otopilot Hafızası (Eklenen Çekilişler)")
        if os.path.exists("otopilot_veriler.csv"):
            try:
                df_oto_display = pd.read_csv("otopilot_veriler.csv", header=None)
                df_oto_display.columns = [f"Top {i+1}" for i in range(len(df_oto_display.columns))]
                st.dataframe(df_oto_display, use_container_width=True)
                
                if st.button("🗑️ Otopilot Hafızasını Temizle (Sıfırla)"):
                    os.remove("otopilot_veriler.csv")
                    st.cache_data.clear()
                    st.success("Otopilot hafızası tamamen temizlendi! Ana veritabanına dönülüyor...")
                    time.sleep(1.5)
                    st.rerun()
            except:
                st.warning("Kayıtlı veri okunamadı.")
        else:
            st.info("Otopilot hafızası şu an boş. Sisteme henüz manuel veri enjekte edilmedi.")
            
    elif admin_pass != "":
        st.error("Hatalı Şifre!")