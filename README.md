# Uçak Motorlarında Kalan Faydalı Ömür (RUL) Tahmini

NASA C-MAPSS turbofan motor veri seti ile, sensör ölçümlerinden bir motorun **bozulmasına kaç çevrim kaldığını** tahmin eden makine öğrenmesi projesi.

> **Durum:** Başlangıç aşaması. Şu an temel modeller (Lineer Regresyon ve Random Forest) hazır. Sonuçlar ve geliştirme planı aşağıda.

## Amaç

Öngörücü bakım (predictive maintenance): Arıza olmadan önce hangi motora ne zaman bakım yapılması gerektiğini veriye bakarak tahmin etmek. Bu, hem plansız duruşları hem de gereksiz bakım maliyetini azaltmayı hedefler.

## Veri

- **Kaynak:** [NASA C-MAPSS Jet Engine Simulated Data](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data)
- Bu projede **FD001** alt kümesi kullanılıyor (tek arıza türü, tek çalışma koşulu).
- Her satır bir motorun bir çevrimdeki ölçümü: motor no, çevrim, 3 ayar, 21 sensör.
- Veri dosyaları büyük olduğu için GitHub'a yüklenmez (`.gitignore`).

Kaynak makale: A. Saxena, K. Goebel, D. Simon, N. Eklund, *Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation*, PHM08, 2008.

## Klasör yapısı

```
rul-tahmini/
├── data/            # veri dosyaları buraya iner (GitHub'a yüklenmez)
├── src/
│   ├── indir.py     # veriyi NASA'dan indirir
│   └── egitim.py    # modelleri eğitir, sonuçları üretir
├── sonuclar/        # metrikler ve grafikler
├── requirements.txt
└── README.md
```

## Kurulum ve çalıştırma

Python 3.9 veya üstü gerekir.

```bash
pip install -r requirements.txt
python src/indir.py      # veriyi indirir
python src/egitim.py     # modelleri eğitir
```

`indir.py` çalışmazsa veriyi elle indir:
1. https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data adresinden `CMAPSSData.zip` dosyasını indir.
2. Zip'i aç, içindeki `train_FD001.txt`, `test_FD001.txt` ve `RUL_FD001.txt` dosyalarını `data/` klasörüne koy.

### Google Colab'de çalıştırma

```python
!git clone https://github.com/KULLANICI_ADIN/rul-tahmini.git
%cd rul-tahmini
!pip install -r requirements.txt
!python src/indir.py
!python src/egitim.py
```

## Yöntem

1. Her eğitim motoru için `RUL = son çevrim - mevcut çevrim` hesaplanır. Erken dönemde RUL en fazla 125'e sabitlenir (bu literatürde sık kullanılan bir yaklaşımdır).
2. Eğitimde hiç değişmeyen sabit sensörler çıkarılır.
3. İki model eğitilir: **Lineer Regresyon** (kıyas noktası) ve **Random Forest**.
4. Test motorlarının **son çevrimi** kullanılarak RUL tahmin edilir ve NASA'nın verdiği gerçek RUL değerleriyle **RMSE** hesaplanır.

## Sonuçlar

*Buraya `python src/egitim.py` çalıştırdıktan sonra `sonuclar/metrikler.txt` dosyasındaki değerleri ve `sonuclar/tahmin_grafik.png` grafiğini ekle.*

| Model | RMSE (çevrim) |
|---|---|
| Lineer Regresyon | _buraya yaz_ |
| Random Forest | _buraya yaz_ |

## Yapılacaklar

- [ ] Zaman serisi modeli (LSTM veya 1D-CNN) ekle ve basit modellerle karşılaştır
- [ ] Pencereleme / hareketli ortalama ile özellik üretimi
- [ ] FD002-FD004 alt kümelerinde dene
- [ ] Tahminleri **bakım planlamasına** bağla: arıza riski ve maliyeti dengeleyen bakım zamanı optimizasyonu (endüstri mühendisliği katmanı)
- [ ] Sonuçları ve yöntemi raporla

## Yazarlar

- [Adın Soyadın] - Endüstri Mühendisliği
- Danışman: [Hocanın adı]

## Lisans

Kod için MIT lisansı önerilir (GitHub'da depo oluştururken seçebilirsin). Veri seti NASA'ya aittir.
