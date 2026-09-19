"""C-MAPSS FD001 üzerinde kalan faydalı ömür (RUL) tahmini.

Adımlar:
  1. Veriyi oku
  2. Eğitim verisine RUL (bozulmaya kalan çevrim) sütununu ekle
  3. Sabit kalan (bilgi taşımayan) sensörleri ele
  4. İki model eğit: Lineer Regresyon (kıyas) ve Random Forest
  5. Test motorlarının son çevriminden RUL tahmin et, RMSE hesapla
  6. Grafik ve metrikleri sonuclar/ klasörüne kaydet

Çalıştırma:  python src/egitim.py
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # ekran açmadan grafik dosyası üretir
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

KOK = Path(__file__).resolve().parent.parent
KOLONLAR = ["motor", "cevrim", "ayar1", "ayar2", "ayar3"] + [
    f"s{i}" for i in range(1, 22)
]
RUL_SINIR = 125  # Literatürde yaygın: erken dönemde RUL'u bu değerde sabitle


def veri_oku(yol):
    """Boşlukla ayrılmış C-MAPSS dosyasını isimli sütunlarla okur."""
    return pd.read_csv(yol, sep=r"\s+", header=None, names=KOLONLAR)


def rul_ekle(df):
    """Her motor için: RUL = (motorun son çevrimi) - (şu anki çevrim)."""
    son_cevrim = df.groupby("motor")["cevrim"].transform("max")
    df = df.copy()
    df["rul"] = (son_cevrim - df["cevrim"]).clip(upper=RUL_SINIR)
    return df


def ozellik_sec(egitim):
    """Eğitimde hiç değişmeyen sütunları at (öğrenilecek bir şey taşımaz)."""
    adaylar = [k for k in KOLONLAR if k not in ("motor", "cevrim")]
    return [k for k in adaylar if egitim[k].std() > 0]


def rmse(gercek, tahmin):
    return float(np.sqrt(mean_squared_error(gercek, tahmin)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri", default=str(KOK / "data"), help="veri klasörü")
    ap.add_argument("--cikti", default=str(KOK / "sonuclar"), help="sonuç klasörü")
    args = ap.parse_args()

    veri_klasoru = Path(args.veri)
    cikti = Path(args.cikti)
    cikti.mkdir(exist_ok=True)

    egitim_yolu = veri_klasoru / "train_FD001.txt"
    test_yolu = veri_klasoru / "test_FD001.txt"
    rul_yolu = veri_klasoru / "RUL_FD001.txt"
    for yol in (egitim_yolu, test_yolu, rul_yolu):
        if not yol.exists():
            raise SystemExit(
                f"Dosya bulunamadı: {yol}\n"
                "Önce 'python src/indir.py' çalıştır ya da README.md'ye bak."
            )

    # 1-2) Veri ve RUL
    egitim = rul_ekle(veri_oku(egitim_yolu))
    test = veri_oku(test_yolu)
    test_gercek_rul = pd.read_csv(rul_yolu, header=None)[0].to_numpy()

    # 3) Özellikler
    ozellikler = ozellik_sec(egitim)
    print(f"Kullanılan özellik sayısı: {len(ozellikler)}")

    x_egitim = egitim[ozellikler]
    y_egitim = egitim["rul"]

    # Test: her motorun SON çevrimi
    test_son = test.sort_values(["motor", "cevrim"]).groupby("motor").tail(1)
    x_test = test_son[ozellikler]

    # 4) Modeller
    modeller = {
        "Lineer Regresyon": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, random_state=42, n_jobs=-1
        ),
    }

    sonuclar = {}
    tahminler = {}
    for ad, model in modeller.items():
        model.fit(x_egitim, y_egitim)
        tahmin = np.clip(model.predict(x_test), 0, RUL_SINIR)
        sonuclar[ad] = rmse(test_gercek_rul, tahmin)
        tahminler[ad] = tahmin
        print(f"{ad}: RMSE = {sonuclar[ad]:.2f}")

    # 5-6) Kaydet
    with open(cikti / "metrikler.txt", "w", encoding="utf-8") as f:
        for ad, deger in sonuclar.items():
            f.write(f"{ad}: RMSE = {deger:.2f}\n")

    en_iyi = min(sonuclar, key=sonuclar.get)
    plt.figure(figsize=(6, 6))
    plt.scatter(test_gercek_rul, tahminler[en_iyi], alpha=0.6)
    sinir = max(test_gercek_rul.max(), tahminler[en_iyi].max())
    plt.plot([0, sinir], [0, sinir], "r--", label="Mükemmel tahmin")
    plt.xlabel("Gerçek RUL (çevrim)")
    plt.ylabel("Tahmin edilen RUL (çevrim)")
    plt.title(f"{en_iyi} - Test motorları")
    plt.legend()
    plt.tight_layout()
    plt.savefig(cikti / "tahmin_grafik.png", dpi=150)
    print("Sonuçlar kaydedildi:", cikti)


if __name__ == "__main__":
    main()
