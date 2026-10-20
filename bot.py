import telebot
from telebot import types

# ==========================================
# KONFIGURASI (UBAH BAGIAN INI)
# ==========================================
BOT_TOKEN   = "8809177437:AAH8yYsTL0n4_ClzBBv2C3kvKHfnOFCAUWA"
ADMIN_ID    = 8994767068  # Ganti dengan ID Telegram Anda (angka)
DANA_NUMBER = "0895320838048"
HARGA       = 3000
NAMA_TOKO   = "Unband Store"

# Link GitHub dari file budi.html Anda
FILE_URL = "https://github.com/rudista100-cpu/Produk-web/releases/download/v1/budi.html"
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)

def menu_utama():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🛒 Beli File HTML", callback_data="beli"))
    return kb

@bot.message_handler(commands=['start'])
def start(msg):
    teks = (f"👋 Selamat datang di *{NAMA_TOKO}*\n\n"
            f"📄 Produk : File Unband (HTML)\n"
            f"💰 Harga  : Rp {HARGA:,}\n"
            f"💳 Pembayaran : DANA `{DANA_NUMBER}`\n\n"
            f"Klik tombol di bawah untuk membeli.")
    bot.send_message(msg.chat.id, teks, parse_mode="Markdown", reply_markup=menu_utama())

@bot.callback_query_handler(func=lambda c: c.data == "beli")
def proses_beli(call):
    teks = (f"🧾 *INSTRUKSI PEMBAYARAN*\n\n"
            f"1️⃣ Transfer ke DANA:\n`{DANA_NUMBER}`\n"
            f"2️⃣ Nominal: *Rp {HARGA:,}* (harus pas)\n"
            f"3️⃣ Screenshot bukti transfer\n"
            f"4️⃣ Kirim screenshot ke bot ini\n\n"
            f"⚠️ Link file akan dikirim setelah admin verifikasi.")
    bot.send_message(call.message.chat.id, teks, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def terima_bukti(msg):
    user = msg.from_user
    
    if user.id == ADMIN_ID:
        bot.reply_to(msg, "Ini foto bukti transfer dari pembeli. Tunggu user lain ya.")
        return

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Setujui", callback_data=f"ok_{user.id}"),
        types.InlineKeyboardButton("❌ Tolak",   callback_data=f"no_{user.id}")
    )
    caption = (f"💳 *BUKTI PEMBAYARAN BARU*\n\n"
               f"👤 Nama   : {user.first_name}\n"
               f"🆔 User ID: `{user.id}`\n"
               f"🔗 Username: @{user.username if user.username else '-'}\n"
               f"💰 Nominal : Rp {HARGA:,}\n\n"
               f"Cek mutasi DANA sebelum menyetujui!")
               
    bot.send_photo(ADMIN_ID, msg.photo[-1].file_id,
                   caption=caption, parse_mode="Markdown", reply_markup=kb)
                   
    bot.reply_to(msg, "✅ Bukti diterima!\n⏳ Menunggu verifikasi admin.")

@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok_", "no_")))
def aksi_admin(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Anda bukan admin!", show_alert=True)
        return

    aksi, uid = call.data.split("_")
    uid = int(uid)

    if aksi == "ok":
        try:
            teks_kirim = (f"🎉 *PEMBAYARAN DISETUJUI!*\n\n"
                          f"📄 Silakan download file Anda di link berikut:\n"
                          f"{FILE_URL}\n\n"
                          f"Terima kasih sudah berbelanja 🙏")
            bot.send_message(uid, teks_kirim, parse_mode="Markdown", disable_web_page_preview=False)
        except Exception as e:
            bot.send_message(ADMIN_ID, f"⚠️ Gagal kirim pesan ke user {uid}. Error: {e}")

        bot.edit_message_caption(
            caption=call.message.caption + "\n\n✅ *DISETUJUI* → Link terkirim",
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Disetujui ✅")

    elif aksi == "no":
        try:
            bot.send_message(uid, "❌ *PEMBAYARAN DITOLAK*\n\nBukti tidak valid / dana belum masuk.")
        except: pass
        bot.edit_message_caption(
            caption=call.message.caption + "\n\n❌ *DITOLAK*",
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Ditolak ❌")

if __name__ == "__main__":
    print("🤖 Bot berjalan... Silakan cek Telegram Anda.")
    bot.infinity_polling(timeout=30)
