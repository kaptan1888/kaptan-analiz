import pandas as pd
from collections import Counter
import sys
import re

print("="*75)
print("🕵️‍♂️ KAPTAN'IN DİNAMİK İSTİHBARAT SORGU MOTORU BAŞLATILIYOR...")
print("="*75)

# 1. KAPTAN'IN KESİN EŞİKLERİ
HOT_THRESHOLD = 28
COLD_THRESHOLD = 19

# 2. Veri Yükleme (Sadece chance.son.xlsx ve Sayfa 1)
try:
    df = pd.read_excel('chance.son.xlsx', sheet_name=0, header=None, engine='openpyxl')
except Exception as e:
    print(f"HATA: {e}")
    print("Lütfen 'chance.son.xlsx' dosyasının bu kod ile aynı klasörde olduğundan emin ol.")
    sys.exit()

valid_draws = []
for index, row in df.iterrows():
    try:
        # Sadece A ve E sütunları arası (ilk 5 sayı)
        nums = pd.to_numeric(row[:5], errors='coerce').dropna().astype(int).tolist()
        nums = [x for x in nums if 1 <= x <= 34]
        if len(set(nums)) == 5:
            valid_draws.append(sorted(nums))
    except:
        continue

if not valid_draws:
    print("Hata: Geçerli çekiliş bulunamadı.")
    sys.exit()

total_draws = len(valid_draws)

# 3. Güncel Havuzları Belirleme
all_nums = [num for draw in valid_draws for num in draw]
counts = Counter(all_nums)

hot_nums = [n for n in range(1, 35) if counts.get(n, 0) >= HOT_THRESHOLD]
cold_nums = [n for n in range(1, 35) if counts.get(n, 0) <= COLD_THRESHOLD]
medium_nums = [n for n in range(1, 35) if COLD_THRESHOLD < counts.get(n, 0) < HOT_THRESHOLD]

# 4. Yardımcı Fonksiyonlar
def get_freq_tuple(lst):
    s = sum(1 for x in lst if x in hot_nums)
    o = sum(1 for x in lst if x in medium_nums)
    c = sum(1 for x in lst if x in cold_nums)
    return (s, o, c)

def get_oe(lst):
    t = sum(1 for x in lst if x%2!=0)
    return f"{t} Tek - {5-t} Çift"

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
    return f"{b} B - {o} O - {y} Y - {ot} Ot"

def get_alt_ust(lst):
    alt = sum(1 for x in lst if x <= 17)
    ust = sum(1 for x in lst if x >= 18)
    return f"{alt} Alt - {ust} Üst"

def get_devir(prev_lst, curr_lst):
    return "VAR" if set(prev_lst).intersection(set(curr_lst)) else "YOK"

# 5. Mevcut Frekansları Hesapla ve Ekrana Bas
all_freqs = [get_freq_tuple(d) for d in valid_draws]
freq_counts = Counter(all_freqs)

print("\n📊 VERİTABANINDAKİ EN POPÜLER FREKANS ŞABLONLARI:")
for f, c in freq_counts.most_common(5):
    print(f"  -> {f[0]} Sıcak - {f[1]} Orta - {f[2]} Soğuk ({c} Kez Yaşandı)")

print("\n" + "="*75)
print("Lütfen analiz etmek istediğiniz frekans şablonunu girin.")
print("Kullanım Örneği: 2 Sıcak, 2 Orta, 1 Soğuk için ekrana 2-2-1 yazın.")
user_input = input("Frekans Girin (S-O-C): ")

# Kullanıcı girdisini çözümle
try:
    nums = re.findall(r'\d+', user_input)
    if len(nums) < 3:
        raise ValueError("Yetersiz rakam")
    target_s, target_o, target_c = int(nums[0]), int(nums[1]), int(nums[2])
    if target_s + target_o + target_c != 5:
        print("\n⚠️ DİKKAT: Girdiğiniz sayıların toplamı 5 etmiyor! Yine de analiz yapılıyor...\n")
except:
    print("\n❌ Hatalı giriş yaptınız! Program kapatılıyor. Lütfen 2-2-1 gibi araya tire koyarak yazın.")
    sys.exit()

target_tuple = (target_s, target_o, target_c)
print(f"\n🔍 HEDEF KİLİTLENDİ: {target_s} Sıcak - {target_o} Orta - {target_c} Soğuk")
print("="*75)

# 6. Çapraz Analiz Motoru Devrede
results = {
    'oe': [],
    'cons': [],
    'root': [],
    'basamak': [],
    'alt_ust': [],
    'devir': []
}

# valid_draws listesinde 0. index en yeni çekiliştir.
# i. çekiliş hedef frekansa uyuyorsa, bir sonraki hafta olan çekiliş (i-1)'dir.
match_count = 0
for i in range(1, len(valid_draws)):
    if get_freq_tuple(valid_draws[i]) == target_tuple:
        match_count += 1
        trigger_draw = valid_draws[i]    # Bu frekansı veren çekiliş
        next_draw = valid_draws[i-1]     # Bir sonraki (hedef) çekiliş
        
        results['oe'].append(get_oe(next_draw))
        results['cons'].append(get_cons(next_draw))
        results['root'].append(get_root(next_draw))
        results['basamak'].append(get_basamak(next_draw))
        results['alt_ust'].append(get_alt_ust(next_draw))
        results['devir'].append(get_devir(trigger_draw, next_draw))

if match_count == 0:
    print(f"\nVeritabanında {target_s}S - {target_o}O - {target_c}C frekansının gelip de ardından çekiliş yapılan bir kayıt bulunamadı.")
    sys.exit()

def print_stats(data_list, title):
    c = Counter(data_list)
    total = len(data_list)
    print(f"\n--- {title} ---")
    for k, v in c.most_common():
        perc = (v / total) * 100
        print(f"  -> {k}: %{perc:.2f}")

print(f"\n✅ RAPOR HAZIR! Tarihte bu frekans şablonundan SONRAKİ HAFTA tam {match_count} kez çekiliş yapılmıştır. Makinenin refleksleri şöyledir:")

print_stats(results['oe'], "1. TEK / ÇİFT REFLEKSİ")
print_stats(results['alt_ust'], "2. ALT (1-17) / ÜST (18-34) BÖLGE REFLEKSİ")
print_stats(results['cons'], "3. ARDIŞIK SAYI REFLEKSİ")
print_stats(results['root'], "4. KÖK EŞLEŞMESİ REFLEKSİ")
print_stats(results['devir'], "5. DEVİR REFLEKSİ (Geçen haftadan sayı var mı?)")
print_stats(results['basamak'], "6. BASAMAK DAĞILIMI REFLEKSİ (Birler - Onlar - Yirmiler - Otuzlar)")

print("\n" + "="*75)
print("💡 KAPTAN'A NOT: En yüksek yüzdeler, makinenin bu frekansa verdiği tepkidir.")
print("Kolonları kurarken yukarıdaki 1. sıradaki şablonları baz al.")
print("="*75)