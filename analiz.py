import pandas as pd
from collections import Counter
import sys

print("="*70)
print("KAPTAN'IN KATI KURALLI ANALİZ MOTORU BAŞLATILIYOR...")
print("Hedef Veri Tabanı: chance.son.xlsx")
print("="*70)

# KAPTAN'IN KESİN EŞİKLERİ
HOT_THRESHOLD = 28
COLD_THRESHOLD = 19

# Dosyayı yükle
try:
    df = pd.read_excel('chance.son.xlsx', header=None, engine='openpyxl')
except Exception as e:
    print(f"KRİTİK HATA: {e}")
    print("Lütfen 'chance.son.xlsx' dosyasının analiz.py ile aynı klasörde olduğundan emin ol.")
    sys.exit()

# Geçerli çekilişleri topla (Varsayım: En son çekiliş en üstte veya ilk satırda)
valid_draws = []
for index, row in df.iterrows():
    try:
        nums = pd.to_numeric(row[:5], errors='coerce').dropna().astype(int).tolist()
        nums = [x for x in nums if 1 <= x <= 34]
        if len(set(nums)) == 5:
            valid_draws.append(sorted(nums))
    except Exception:
        pass

total_draws = len(valid_draws)
if total_draws == 0:
    print("HATA: Okunabilir geçerli bir çekiliş bulunamadı.")
    sys.exit()

all_nums = [num for draw in valid_draws for num in draw]
counts = Counter(all_nums)

# DİNAMİK HAVUZLARI OLUŞTUR
hot_nums = [num for num in range(1, 35) if counts.get(num, 0) >= HOT_THRESHOLD]
cold_nums = [num for num in range(1, 35) if counts.get(num, 0) <= COLD_THRESHOLD]
medium_nums = [num for num in range(1, 35) if COLD_THRESHOLD < counts.get(num, 0) < HOT_THRESHOLD]

def get_freq_pattern(lst):
    s = sum(1 for x in lst if x in hot_nums)
    o = sum(1 for x in lst if x in medium_nums)
    c = sum(1 for x in lst if x in cold_nums)
    return f"{s} Sıcak - {o} Orta - {c} Soğuk"

def is_consecutive(lst):
    return any(lst[i]+1 == lst[i+1] for i in range(len(lst)-1))

def get_oe(lst):
    t = sum(1 for x in lst if x%2!=0)
    c = sum(1 for x in lst if x%2==0)
    return f"{t} Tek - {c} Çift"

def get_root_match(lst):
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

history = []
for i in range(len(valid_draws)):
    d = valid_draws[i]
    carryover = False
    if i < len(valid_draws) - 1:
        prev_d = valid_draws[i+1]
        carryover = len(set(d).intersection(set(prev_d))) > 0
        
    history.append({
        'freq': get_freq_pattern(d),
        'cons': "VAR" if is_consecutive(d) else "YOK",
        'oe': get_oe(d),
        'root': get_root_match(d),
        'basamak': get_basamak(d),
        'carry': "VAR" if carryover else "YOK"
    })

def print_perc(counter, total, title, limit=10):
    print(f"\n--- {title} ---")
    for k, v in counter.most_common(limit):
        perc = (v / total) * 100
        print(f"{k}: %{perc:.2f}")

print(f"\n1. GÜNCEL HAVUZ DAĞILIMI (Toplam {total_draws} Çekiliş Baz Alınmıştır)")
print(f"🔥 SICAK (>= {HOT_THRESHOLD} Çıkış) ({len(hot_nums)} Adet): {hot_nums}")
print(f"🟡 ORTA ({COLD_THRESHOLD+1}-{HOT_THRESHOLD-1} Çıkış) ({len(medium_nums)} Adet): {medium_nums}")
print(f"❄️ SOĞUK (<= {COLD_THRESHOLD} Çıkış) ({len(cold_nums)} Adet): {cold_nums}")

print_perc(Counter([x['freq'] for x in history]), total_draws, "2. FREKANS ŞABLONU YÜZDELERİ")
print_perc(Counter([x['oe'] for x in history]), total_draws, "3. TEK/ÇİFT DENGESİ YÜZDELERİ")
print_perc(Counter([x['cons'] for x in history]), total_draws, "4. ARDIŞIK SAYI YÜZDELERİ")
print_perc(Counter([x['root'] for x in history]), total_draws, "5. KÖK EŞLEŞMESİ YÜZDELERİ")
print_perc(Counter([x['carry'] for x in history[:-1]]), total_draws - 1 if total_draws > 1 else 1, "6. DEVİR (GEÇEN HAFTADAN SAYI) YÜZDELERİ")
print_perc(Counter([x['basamak'] for x in history]), total_draws, "7. BASAMAK DAĞILIMI YÜZDELERİ")

last_draw = valid_draws[0]
print(f"\n" + "="*70)
print(f"🎯 SON ÇEKİLİŞ ({last_draw}) ŞABLONU")
print("="*70)
print(f"Frekans Dağılımı : {get_freq_pattern(last_draw)}")
print(f"Tek/Çift Dengesi : {get_oe(last_draw)}")
print(f"Ardışık Durumu   : {'VAR' if is_consecutive(last_draw) else 'YOK'}")
print(f"Kök Eşleşmesi    : {get_root_match(last_draw)}")
print(f"Basamak Dağılımı : {get_basamak(last_draw)}")
print("="*70)
print("KAPTAN'A NOT: Lütfen bu konsol çıktısını kopyala ve yapay zekaya ilet.")