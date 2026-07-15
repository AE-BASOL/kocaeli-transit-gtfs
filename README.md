# 🚌 Kocaeli Transit to Google Maps (GTFS & GTFS-RT)

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![GTFS](https://img.shields.io/badge/Format-GTFS-success?style=for-the-badge)
![GTFS-RT](https://img.shields.io/badge/Format-GTFS--Realtime-ff69b4?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

Bu proje, Kocaeli Büyükşehir Belediyesi'ne ait E-Komobil ve UlaşımPark sistemlerindeki kapalı toplu taşıma verilerini otomatik olarak kazıyıp (crawling) dünyaca kabul görmüş **Google Transit (GTFS ve GTFS-Realtime)** standartlarına dönüştüren otomatize bir sistemdir.

Temel amacı, Kocaeli halkının otobüs ve tramvayları **Google Haritalar (Google Maps)** üzerinden canlı olarak takip edebilmesini sağlamaktır.

---

## ✨ Özellikler (Features)

*   **🚀 Işık Hızında Canlı Veri Çekimi:** Python `ThreadPoolExecutor` kullanılarak 381 farklı otobüs/minibüs hattındaki yüzlerce aracın anlık GPS koordinatları, eşzamanlı (multithreading) işlemlerle yalnızca **15-20 saniye** içinde taranır.
*   **🚋 Akçaray Tramvay Botu:** UlaşımPark'ın web sitesindeki ASP.NET Anti-Forgery token (güvenlik) bariyeri otomatik olarak aşılarak tramvay hatlarının (T1, T2, T3) durakları ve sefer saatleri kusursuzca kazınır.
*   **🗺️ Otomatik GTFS Üretimi:** Toplanan ham `.json` verileri (hatlar, duraklar, güzergah koordinatları), Google Maps'in rotalama için kullandığı statik `gtfs.zip` formatına dönüştürülür.
*   **📡 Canlı GTFS-Realtime (.pb):** Otobüslerin hareketleri, Google'ın resmi kütüphanesi kullanılarak her saniye güncellenen `vehicle_positions.pb` (Protocol Buffers) formatına işlenir.

---

## 🏗️ Mimari ve Klasör Yapısı

Sistem, iki ana bileşenden oluşur: **Crawler** (Veri Toplayıcı) ve **GTFS Builder** (Veri Dönüştürücü).

```text
├── data/
│   ├── raw/                 # Statik ham veriler (24 saatte bir güncellenir)
│   │   ├── routes.json      # Tüm Kocaeli otobüs/minibüs hatları
│   │   ├── stops.json       # Tüm durak koordinatları
│   │   ├── shapes.json      # Harita üzerindeki çizim koordinatları (yol çizgileri)
│   │   └── trams.json       # Akçaray durak ve sefer saatleri
│   ├── processed/           # Dinamik veriler
│   │   └── live_buses.json  # 60 saniyede bir güncellenen anlık GPS konumları
│   └── gtfs/                # Çıktı klasörü (Google'a gönderilecek dosyalar)
│       ├── gtfs.zip         # Google Maps STATİK paketi (agency, routes, vb.)
│       └── vehicle_positions.pb # Google Maps CANLI konum paketi (Protobuf)
├── src/
│   ├── crawler/
│   │   ├── ekomobil.py      # E-komobil şifreli API bypass aracı
│   │   ├── web_scraper.py   # UlaşımPark Tramvay web kazıyıcısı
│   │   └── main_crawler.py  # Sonsuz döngüde çalışan beyin (Orchestrator)
│   └── gtfs/
│       ├── builder.py       # JSON verilerini statik gtfs.zip'e dönüştürür
│       └── rt_builder.py    # Canlı otobüs JSON'unu .pb dosyasına çevirir
```

---

## 🛠️ Kurulum (Installation)

Sistemi kendi bilgisayarında/sunucunda çalıştırmak için aşağıdaki adımları izle:

1. Projeyi klonla ve dizine gir:
   ```bash
   git clone https://github.com/KULLANICI_ADIN/Kocaeli-Transit-Google-Maps.git
   cd Kocaeli-Transit-Google-Maps
   ```

2. Python sanal ortamını (Virtual Environment) oluştur ve aktif et:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux için
   # .venv\Scripts\activate   # Windows için
   ```

3. Gerekli kütüphaneleri (Dependencies) yükle:
   ```bash
   pip install requests beautifulsoup4 gtfs-realtime-bindings
   ```

---

## 🚀 Kullanım (Usage)

### 1. Crawler'ı (Veri Toplayıcıyı) Başlatmak
Tüm sistemi otomatik pilotta çalıştırmak için:
```bash
python src/crawler/main_crawler.py
```
*Bu komut önce `data/raw/` içine statik verileri (hatlar, duraklar vb.) indirecek, ardından sonsuz bir döngüye girerek her 60 saniyede bir canlı otobüs konumlarını çekecek ve otomatik olarak `vehicle_positions.pb` dosyasını güncelleyecektir.*

### 2. Statik GTFS (.zip) Dosyasını Üretmek
Toplanan statik ham verilerden (`routes.json`, `stops.json` vs.) Google Maps için standart `gtfs.zip` dosyasını oluşturmak istersen:
```bash
python src/gtfs/builder.py
```
*Çıktı `data/gtfs/gtfs.zip` konumunda belirecektir.*

---

## ⚠️ Yasal Uyarı
Bu proje Kocaeli Büyükşehir Belediyesi, UlaşımPark veya E-Komobil'in resmi bir ürünü **değildir**. Sistem, vatandaşların hayatını kolaylaştırmak amacıyla tamamen bağımsız geliştirilmiş bir açık kaynak projedir. Sistemin aşırı sıklıkta çalıştırılması (rate-limit) IP engeline takılabilir, lütfen sunucuları yormayacak periyotlarla (örn. 60 sn) çalıştırın.
