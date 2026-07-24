import pandas as pd
from collections import Counter
import sys

print("="*70)
print("KAPTAN'IN GELECEK PROJEKSİYONU (ÇAPRAZ ANALİZ MOTORU)")
print("="*70)

# 1. Veri Yükleme
try:
    df = pd.read_excel('chance.son.xlsx', header=None, engine='openpyxl')
except Exception as e:
    print(f"HATA: {e}")
    sys.exit()

valid_draws = []
for index, row in df.iterrows():
    try:
        nums = pd.to_numeric(row[:5], errors='coerce').dropna().astype(int).tolist()
        nums = [x for x in nums if 1 <= x <= 34]
        if len(set(nums)) == 5:
            valid_draws.append(sorted(nums))
    except:
        pass

if not valid_draws:
    print("Hata: Geçerli çekiliş bulunamadı.")
    sys.exit()

# 2. Güncel Havuzları Belirleme
all_nums = [num for draw in valid_draws for num in draw]
counts = Counter(all_nums)

HOT_THRESHOLD = 28
COLD_THRESHOLD = 19

hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= HOT_THRESHOLD]
cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= COLD_THRESHOLD]
medium_nums = [n for n in range(1, 35) if COLD_THRESHOLD < counts.get(n, 0) < HOT_THRESHOLD]

# 3. Yardımcı Fonksiyonlar
def get_freq(lst):
    s = sum(1 for x in lst if x in hot_nums)
    o = sum(1 for x in lst if x in medium_nums)
    c = sum(1 for x in lst if x in cold_nums)
    return f"{s} Sıcak - {o} Orta - {c} Soğuk"

def get_oe(lst):
    t = sum(1 for x in lst if x%2!=0)
    c = sum(1 for x in lst if x%2==0)
    return f"{t} Tek - {c} Çift"

def get_cons(lst):
    return "VAR" if any(lst[i]+1 == lst[i+1] for i in range(len(lst)-1)) else "YOK"

def get_root(lst):
    r_counts = Counter([x % 10 for x in lst]).values()
    m = max(r_counts) if r_counts else 0
    if m <= 1: return "Eşleşme Yok"
    elif m == 2: return "2'li Eşleşme (Tek Çift Kök)"
    else: return "3'lü+ Eşleşme / Çifte Kök"

def get_basamak(lst):
    b = sum(1 for x in lst if 1<=x<=9)
    o = sum(1 for x in lst if 10<=x<=19)
    y = sum(1 for x in lst if 20<=x<=29)
    ot = sum(1 for x in lst if 30<=x<=34)
    return f"{b} Birler - {o} Onlar - {y} Yirmiler - {ot} Otuzlar"

def get_alt_ust(lst):
    alt = sum(1 for x in lst if x <= 17)
    ust = sum(1 for x in lst if x >= 18)
    return f"{alt} Alt - {ust} Üst"

# 4. Geçmişi Şablonlama (Devir ve Alt/Üst Eklendi)
history = []
for i in range(len(valid_draws)):
    d = valid_draws[i]
    
    # Devir Durumu (Geçmiş haftadaki çekiliş ile ortak sayı var mı?)
    devir_durumu = "Bilinmiyor"
    if i + 1 < len(valid_draws):
        prev_d = valid_draws[i+1]
        devir_durumu = "VAR" if set(d).intersection(set(prev_d)) else "YOK"

    history.append({
        'draw': d,
        'freq': get_freq(d),
        'oe': get_oe(d),
        'cons': get_cons(d),
        'root': get_root(d),
        'basamak': get_basamak(d),
        'alt_ust': get_alt_ust(d),
        'devir': devir_durumu
    })

# valid_draws[0] en son çekiliş, valid_draws[1] bir önceki
last = history[0]

# 5. Çapraz Analiz Fonksiyonu
def analyze_transition(property_key, target_value, title):
    print(f"\n--- {title} ---")
    print(f"Durum: Son çekilişte '{target_value}' gerçekleşti.")
    next_states = []
    # i=0 en son çekiliş, onu atla. 
    # i. çekiliş target_value ise, i-1. çekiliş (sonraki) listeye eklenir.
    for i in range(1, len(history)):
        if history[i][property_key] == target_value:
            next_states.append(history[i-1][property_key])
    
    if not next_states:
        print("Tarihte bu durumdan sonra gelen bir kayıt bulunamadı.")
        return
        
    c = Counter(next_states)
    total = len(next_states)
    print(f"Tarihsel Refleks (Toplam {total} kez bu durum yaşandı ve ardından şunlar geldi):")
    for k, v in c.most_common(5):
        print(f"  -> %{(v/total)*100:.2f} ihtimalle : {k}")

# Analizleri Çalıştır
print(f"BAZ ALINAN SON ÇEKİLİŞ: {last['draw']}")

analyze_transition('freq', last['freq'], "1. FREKANS GEÇİŞ ANALİZİ")
analyze_transition('alt_ust', last['alt_ust'], "2. ALT / ÜST BÖLGE GEÇİŞ ANALİZİ")
analyze_transition('oe', last['oe'], "3. TEK/ÇİFT DENGESİ GEÇİŞ ANALİZİ")
analyze_transition('basamak', last['basamak'], "4. BASAMAK GEÇİŞ ANALİZİ")
analyze_transition('cons', last['cons'], "5. ARDIŞIK SAYI GEÇİŞ ANALİZİ")
analyze_transition('root', last['root'], "6. KÖK EŞLEŞMESİ GEÇİŞ ANALİZİ")
analyze_transition('devir', last['devir'], "7. DEVİR (GEÇEN HAFTADAN SAYI) GEÇİŞ ANALİZİ")

# 8. Genel Devir Çıkıp/Çıkmama İstatistiği
print(f"\n--- 8. GENEL DEVİR İSTATİSTİĞİ (Tüm Tarih) ---")
all_devir = [h['devir'] for h in history if h['devir'] != "Bilinmiyor"]
devir_counts = Counter(all_devir)
total_devir = len(all_devir)
if total_devir > 0:
    print(f"Oyunun tarihinde ({total_devir} çekilişte) Devir Çıkıp/Çıkmama Oranları:")
    for k, v in devir_counts.most_common():
        print(f"  -> {k} : %{(v/total_devir)*100:.2f} ({v} Kez)")

# 9. Özel Devir Analizi (3 Haftalık Seri)
print(f"\n--- 9. ÖZEL DEVİR ANALİZİ (3 Hafta Üst Üste Çıkma) ---")
streak_3_count = 0
streak_4_count = 0

for num in range(1, 35):
    for i in range(3, len(valid_draws)):
        # i, i-1, i-2 çekilişlerinde varsa (Geçmişten günümüze 3 hafta)
        if num in valid_draws[i] and num in valid_draws[i-1] and num in valid_draws[i-2]:
            streak_3_count += 1
            # 4. hafta (i-3) gelmiş mi?
            if num in valid_draws[i-3]:
                streak_4_count += 1

print(f"Tarih boyunca herhangi bir sayının 3 hafta ÜST ÜSTE çıkma durumu {streak_3_count} kez yaşandı.")
if streak_3_count > 0:
    perc = (streak_4_count / streak_3_count) * 100
    print(f"Bu 3 haftalık serilerin ardından, sayının 4. HAFTA DA DEVRETME (gelme) ihtimali: %{perc:.2f}")
    print(f"Yani %{100-perc:.2f} ihtimalle o sayı 4. hafta KESİNLİKLE KESİLİR (Gelmez).")

print("\n" + "="*70)
print("KAPTAN'A NOT: Lütfen bu çıktıyı kopyala ve bana yolla.")