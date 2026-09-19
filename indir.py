"""NASA C-MAPSS veri setini indirip data/ klasörüne açar.

Çalıştırma:  python src/indir.py
İndirme olmazsa README.md'deki "elle indirme" adımlarına bak.
"""
import urllib.request
import zipfile
from pathlib import Path

URL = "https://data.nasa.gov/docs/legacy/CMAPSSData.zip"
VERI_KLASORU = Path(__file__).resolve().parent.parent / "data"


def main():
    VERI_KLASORU.mkdir(exist_ok=True)
    zip_yolu = VERI_KLASORU / "CMAPSSData.zip"

    print("İndiriliyor:", URL)
    try:
        urllib.request.urlretrieve(URL, zip_yolu)
    except Exception as hata:
        print("İndirme başarısız:", hata)
        print("Dosyayı elle indirip data/ klasörüne koy (README.md'ye bak).")
        return

    with zipfile.ZipFile(zip_yolu) as z:
        z.extractall(VERI_KLASORU)
    print("Tamam. data/ klasöründeki dosyalar:")
    for dosya in sorted(VERI_KLASORU.glob("*.txt")):
        print(" -", dosya.name)


if __name__ == "__main__":
    main()
