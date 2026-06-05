# 🤖 Hibrit Yapay Zeka Trading Botu - Binance

Binance borsası ile otomatik çalışan, teknik analiz ve makine öğrenmesini birleştiren gelişmiş bir trading botu.

## 🚀 Özellikler

### Teknik Analiz
- **RSI (Relative Strength Index)** - Aşırı alım/satım tespiti
- **MACD** - Trend takibi
- **Bollinger Bands** - Volatilite analizi
- **Moving Averages** - Trend doğrulama

### Makine Öğrenmesi
- **LSTM Neural Network** - Zaman serisi tahmini
- **Random Forest Classifier** - Trend sınıflandırması
- **Ensemble Method** - Her iki modelin ortalama tahmini

### Hibrit Yaklaşım
- %60 Teknik Analiz + %40 ML Modelleri
- Daha güvenilir sinyal üretimi
- Hata toleransı ve çok yönlü analiz

## 📋 Gereksinimler

- Python 3.8+
- Binance hesabı (API Key gerekli)
- pip package manager

## 🔧 Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/tolgamzsimsek-sudo/ai-trading-bot.git
cd ai-trading-bot
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **.env dosyası oluşturun:**
```bash
cp .env.example .env
```

4. **.env dosyasını düzenleyin (API anahtarlarınızı ekleyin):**
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
TRADING_SYMBOL=BTCUSDT
TRADING_TIMEFRAME=5m
DRY_RUN=True  # Canlı işlem için False yapın
```

## 📊 Binance API Key Oluşturma

1. https://www.binance.com/en/user/settings/api-management adresine gidin
2. API Management kısmında "Create API" butonuna tıklayın
3. Label girin (örn: "Trading Bot")
4. Restrictions'tan **"Enable Spot & Margin Trading Only"** seçin
5. Confirm Restrictions'ı tıklayın
6. API Key ve Secret Key'i kopyalayın
7. .env dosyasına yapıştırın

## 🎮 Kullanım

### Dry Run Mode'da Test (Önerilir)
```bash
python bot.py
```

DRY_RUN=True ile bot hiçbir gerçek işlem yapmaz, sadece sinyal üretir.

### Canlı Trading
.env dosyasında `DRY_RUN=False` yapıp botu çalıştırın:
```bash
python bot.py
```

## ⚙️ Ayarlamalar

### config.py içinde değiştirebilirsiniz:

```python
# Trading
TRADING_SYMBOL = 'BTCUSDT'      # Hangi parite
TRADING_TIMEFRAME = '5m'         # Zaman dilimi
TRADING_AMOUNT = 0.001           # İşlem miktarı

# Risk Yönetimi
TAKE_PROFIT_PERCENT = 2.0        # Kar noktası
STOP_LOSS_PERCENT = 1.0          # Zarar durdurma

# Teknik Analiz
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ML Model
ML_EPOCHS = 50                   # Eğitim döngüsü
ML_BATCH_SIZE = 32
```

## 📈 Nasıl Çalışır?

```
1. Veri Çekme
   ↓
2. Teknik Analiz (RSI, MACD, BB, MA)
   ↓
3. ML Tahminleri (LSTM + Random Forest)
   ↓
4. Sinyal Kombinasyonu (Hibrit Yaklaşım)
   ↓
5. BUY/SELL/HOLD Kararı
   ↓
6. İşlem Yürütme
```

## ⚠️ Uyarılar

- **Canlı Trading Riski:** Bot hiçbir şekilde para kaybetmekten korumaz
- **Test Edin:** Canlı işlem yapmadan önce dry-run mode'da kapsamlı test yapın
- **Gözlemleme:** Bot'u periyodik olarak gözlemlemeyi unutmayın
- **Risk Yönetimi:** Küçük miktarlarla başlayın
- **API Güvenliği:** API Key'lerinizi asla paylaşmayın

## 📊 Örnek Çıktı

```
2026-06-05 10:30:45 - INFO - 🤖 Hibrit Trading Bot Başlatıldı
2026-06-05 10:30:45 - INFO - 📊 Symbol: BTCUSDT
2026-06-05 10:30:45 - INFO - ⏱️  Timeframe: 5m
2026-06-05 10:30:45 - INFO - 💰 Amount: 0.001
2026-06-05 10:30:45 - INFO - 🔄 DRY RUN MODE

============================================================
📍 İterasyon #1 - 2026-06-05 10:30:45
============================================================

📈 Pazar analizi başlanıyor...
📊 Teknik Sinyaller - Buy: 3, Sell: 1
🧠 ML modeli çalıştırılıyor...
🎯 ML Tahmini: 0.6245 (>0.5=BUY, <0.5=SELL)

────────────────────────────────────────────────────────
📊 FINAL SINYAL: BUY
💹 FİYAT: 45230.50
────────────────────────────────────────────────────────

🟢 BUY SİNYALİ ALINDI
[DRY RUN] 0.001 BTCUSDT alınacak @ 45230.50

💤 Sonraki kontrol: 300 saniye sonra...
```

## 🔍 Şu Anda Yapılacaklar

- [ ] Risk yönetimi sistemi (Trailing Stop Loss)
- [ ] Backtesting modülü
- [ ] Portfolio yönetimi
- [ ] Telegram bildirim sistemi
- [ ] Grafik görselleştirme
- [ ] Veritabanı entegrasyonu

## 📄 Lisans

MIT License - Serbestçe kullanabilirsiniz

## 🤝 Katkıda Bulunma

Pull request'ler açığız! Büyük değişiklikler için lütfen önce bir issue açın.

## ⚡ Destek

Herhangi bir sorununuz varsa:
- GitHub Issues'de bir issue açın
- E-mail gönderin

---

**Yazı:** tolgamzsimsek-sudo  
**Güncelleme:** Haziran 2026  
**Durum:** 🟢 Aktif Geliştirme
