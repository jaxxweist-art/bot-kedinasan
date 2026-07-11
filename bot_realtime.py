import os
import sys
import json
import time
import threading
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# ==============================================================================
# MUAT KONFIGURASI
# ==============================================================================
def muat_konfigurasi():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Gagal memuat config.json: {e}")
        sys.exit(1)

konfig = muat_konfigurasi()
TOKEN = konfig["telegram"]["token"]
CHAT_ID = konfig["telegram"]["chat_id"]

if TOKEN == "8048219675:AAHGtRVVkhcwVmZ-b5p0ThOJBmhD0bNqIy":
    print("[!] Ganti Token Telegram di config.json dulu!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# ==============================================================================
# MESIN REAL-TIME PEMANTAU KEDINASAN (BKN & STAN) - JANGAN DIHAPUS!
# ==============================================================================
SITUS_KEDINASAN = [
    {"nama": "BKN", "url": "https://bkn.go.id", "file_simpan": "status_bkn.txt"},
    {"nama": "STAN", "url": "https://pknstan.ac.id", "file_simpan": "status_stan.txt"}
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def kirim_alert(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}, timeout=10)

def pantau_kedinasan_realtime():
    """Mesin yang berjalan 24 jam mengecek web STAN & BKN setiap 15 menit"""
    print("[*] Mesin Real-Time BKN & STAN diaktifkan...")
    while True:
        for situs in SITUS_KEDINASAN:
            try:
                respons = requests.get(situs["url"], headers=HEADERS, timeout=15)
                if respons.status_code == 200:
                    soup = BeautifulSoup(respons.text, 'html.parser')
                    teks_sekarang = soup.get_text()[:2000].strip()
                    
                    if os.path.exists(situs["file_simpan"]):
                        with open(situs["file_simpan"], "r", encoding="utf-8") as f:
                            teks_lama = f.read()
                        
                        if teks_sekarang != teks_lama:
                            pesan = f"🚨 *WASPADA {situs['nama']} BERUBAH!* 🚨\n\nSistem mendeteksi ada tulisan atau tombol baru di website resmi. Segera cek: {situs['url']}"
                            kirim_alert(pesan)
                            with open(situs["file_simpan"], "w", encoding="utf-8") as f:
                                f.write(teks_sekarang)
                    else:
                        with open(situs["file_simpan"], "w", encoding="utf-8") as f:
                            f.write(teks_sekarang)
            except Exception as e:
                print(f"[!] Error cek {situs['nama']}: {e}")
        time.sleep(900) # Tidur 15 menit

# ==============================================================================
# BOT TELEGRAM INTERAKTIF
# ==============================================================================
@bot.message_handler(commands=['start'])
def menu_utama(message):
    teks = "🤖 *Bot Tracker Real-Time Aktif!*\n\nSaya sedang memantau BKN & STAN di latar belakang. Apa yang ingin kamu cek manual sekarang?"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Cek Status BKN & STAN", callback_data="cek_kedinasan"),
        types.InlineKeyboardButton("🏫 Cek Info Universitas Nasional", callback_data="list_univ")
    )
    bot.send_message(message.chat.id, teks, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def respon_tombol(call):
    konfig_terbaru = muat_konfigurasi()
    
    if call.data == "cek_kedinasan":
        bkn = "✅ Terkoneksi (Memantau)" if os.path.exists("status_bkn.txt") else "Menunggu tarikan data pertama..."
        stan = "✅ Terkoneksi (Memantau)" if os.path.exists("status_stan.txt") else "Menunggu tarikan data pertama..."
        teks = f"🔥 *STATUS MESIN SCRAPER:*\n\n*BKN:* {bkn}\n*STAN:* {stan}\n\n_Bot akan otomatis spam chat ini jika web mereka berubah!_"
        bot.answer_callback_query(call.id, "Status dimuat!")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=teks, parse_mode="Markdown")

    elif call.data == "list_univ":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for kode, data in konfig_terbaru["universitas_pantau"].items():
            markup.add(types.InlineKeyboardButton(data["nama"], callback_data=f"univ_{kode}"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Pilih kampus untuk dianalisis datanya:", reply_markup=markup)

    elif call.data.startswith("univ_"):
        kode_univ = call.data.split("_")[1]
        kampus = konfig_terbaru["universitas_pantau"][kode_univ]
        
        # LOGIKA JUJUR: Kalau data belum ada, bilang belum ada.
        if kampus["data_jurusan"] is None:
            teks = (
                f"🏫 *{kampus['nama']}*\n\n"
                f"⚠️ *Peringatan Sistem:*\n"
                f"Saat ini *BELUM ADA DATA* pendaftaran atau rasio keketatan yang dibuka secara publik oleh pihak kampus.\n\n"
                f"Sistem tidak dapat menarik data real-time karena pendaftaran belum dimulai atau data dirahasiakan oleh panitia.\n\n"
                f"🔗 *Cek manual di:* {kampus['url_pendaftaran']}"
            )
        else:
            teks = f"Data untuk {kampus['nama']} tersedia." # Persiapan kalau nanti datanya beneran udah ada
            
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=teks, parse_mode="Markdown")

if __name__ == "__main__":
    # Menjalankan pemantau BKN & STAN di belakang layar
    thread_kedinasan = threading.Thread(target=pantau_kedinasan_realtime, daemon=True)
    thread_kedinasan.start()
    
    kirim_alert("✅ *Sistem Bot Real-Time Dinyalakan Ulang!*")
    print("[*] Bot berjalan... Tekan Ctrl+C untuk mematikan.")
    bot.infinity_polling()