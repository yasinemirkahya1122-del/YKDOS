<div align="center">

# 🚀 YKDOS
### Telegram-Powered Infinite Cloud Storage System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Telegram-API-26A6E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/License-MIT-FFD700.svg?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <b>Telegram'ın sınırsız bulut altyapısını kişisel depolama alanınıza dönüştüren, çoklu bot destekli ve modern web arayüzlü dosya yönetim sistemi.</b>
</p>

</div>

---

## 💡 YKDOS Nedir?

**YKDOS**, Telegram'ın sunduğu sınırsız depolama alanını kendi kişisel bulut sunucunuz gibi kullanmanızı sağlayan Python tabanlı bir sistemdir. Dosyalarınızı Telegram kanallarında/gruplarında güvenle saklar, web arayüzü üzerinden hızlıca yükleme ve indirme yapmanıza olanak tanır.

---

## ✨ Öne Çıkan Özellikler

* ♾️ **Sınırsız Depolama:** Telegram altyapısını kullanarak kotasız dosya saklama.
* 🤖 **Çoklu Bot Load-Balancing (`get_next_bot`):** Birden fazla bot ekleyerek API limitlerine takılmadan yükleme yapabilme.
* 📦 **1 GB Parça Limit Desteği:** Tek seferde 1 GB'a kadar devasa dosyaları sorunsuz yükleme.
* ⚡ **FastAPI & SQLite Altyapısı:** Yüksek performanslı API end-point'leri ve hafif veritabanı takibi.
* 🎨 **Karanlık Tema Web Arayüzü:** Modern, mobil uyumlu ve şık `YKDOS.html` dashboard'u.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Repoyu Klonlayın
```bash
git clone https://github.com/KULLANICI_ADINIZ/ykdos.git
cd ykdos
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Sistemi Başlatın
```bash
python app.py
```

> **Not:** İlk çalıştırmada interaktif CLI ekranı sizi karşılayacak. Buradan Telegram Bot Token(lar)ınızı ve hedef Kanal/Grup ID'nizi girerek kurulumu birkaç saniyede tamamlayabilirsiniz.

---

## ⚙️ Yapılandırma (`config.json`)

Kurulum tamamlandıktan sonra bot konfigürasyonu kök dizindeki `config.json` dosyasında saklanır:

```json
{
    "bot_tokens": [
        "123456789:ABCdefGHIjklMNOpqrsTUVwxyZ",
        "987654321:ZYXwvuTSRqpoNMLkjihGFEDcba"
    ],
    "chat_id": "-100123456789",
    "current_bot_index": 0
}
```

---

## ⚠️ Sorumluluk Reddi (Disclaimer)

Bu yazılım eğitim, araştırma ve kişisel kullanım amacıyla geliştirilmiştir. Telegram API politikalarındaki güncellemeler, kanal kısıtlamaları veya 3. taraf servis durumlarında yaşanabilecek **muhtemel dosya/veri kayıplarından yazılım geliştiricisi sorumlu tutulamaz**. Kritik verilerinizi her zaman yerel ortamınızda yedekli tutmanız tavsiye edilir.

---

## 📜 Lisans

Bu proje **MIT Lisansı** ile korunmaktadır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.

<div align="center">
  <sub>Developed with ❤️ by <b>Yasin Emir KAHYA</b></sub>
</div>
