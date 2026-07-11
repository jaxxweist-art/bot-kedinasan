# 📖 CARA KERJA SISTEM BOT REAL-TIME (VERSI JUJUR)

## 1. Bagaimana Bot Memantau BKN & STAN?
Bot ini memiliki sebuah "Mesin Latar Belakang" (Background Thread). Mesin ini sama sekali tidak peduli dengan chat Telegram kamu. Tugasnya hanya satu: **Buka web BKN dan STAN setiap 15 menit.** Jika ada perubahan titik, koma, atau ada tombol "PENDAFTARAN DIBUKA" yang muncul di website mereka, mesin ini akan langsung menabrak Telegram API dan mengebom HP kamu dengan pesan waspada.

## 2. Mengapa Data Universitas Dibilang "Belum Ada"?
Karena kita bermain dengan fakta. Website resmi SNPMB atau pendaftaran Mandiri universitas (seperti Unhas) tidak menyediakan tautan data terbuka (Open API) untuk publik sebelum masa pendaftaran benar-benar dimulai.
Jika kamu mengklik Unhas di bot ini, bot akan secara jujur memberitahu kamu bahwa data belum ada, dan memberikan tautan resmi agar kamu bisa mengeceknya secara manual.

## 3. Cara Menjalankan
1. Taruh `config.json` dan `bot_realtime.py` di folder yang sama.
2. Ganti token di `config.json`.
3. Buka terminal, pastikan library sudah terinstall (`pip install pyTelegramBotAPI beautifulsoup4 requests`).
4. Ketik: `python bot_realtime.py`.
5. Chat bot kamu dengan perintah `/start`.