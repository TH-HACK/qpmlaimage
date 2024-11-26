import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# إعدادات البوت
TELEGRAM_BOT_TOKEN = "7647977575:AAEs0yuy01ogPDheXPwJlD8YD-YHtIyGrQw"  # ضع هنا توكن البوت
PIXABAY_API_KEY = "47213182-534fa9316c4c7adb8cd808bf5"
PIXABAY_IMAGE_URL = "https://pixabay.com/api/"
PIXABAY_VIDEO_URL = "https://pixabay.com/api/videos/"
ADMIN_USER_ID = 5164991393  # استبدل هذا بـ ID المشرف الخاص بك

# تفعيل الـ logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# المتغيرات لتخزين عدد المستخدمين
total_users = 0
active_users = 0
active_user_ids = set()  # لتتبع المستخدمين النشطين باستخدام ID فقط

# دالة start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_users, active_users

    user_id = update.message.from_user.id

    # تحديث عدد المستخدمين الكلي إذا كان المستخدم جديدًا
    if user_id not in active_user_ids:
        total_users += 1

    # تحديث عدد المستخدمين النشطين
    active_user_ids.add(user_id)
    active_users = len(active_user_ids)

    welcome_message = """
    أهلاً بك في بوت! 🖐
    يمكنك البحث🔍 عن صور أو فيديوهات. اختر النوع الذي ترغب في البحث عنه من الأزرار أدناه.
    
    ●●●●●●●●●●●●●●●●●●●
    /help - لعرض التعليمات.
    /about - لمزيد من المعلومات عن البوت.
    /register - لتسجيل نفسك في البوت.
    ●●●●●●●●●●●●●●●●●●●
    """

    # إنشاء الأزرار الخاصة باختيار نوع البحث (صور وفيديوهات)
    buttons = [
        [
            InlineKeyboardButton("صور", callback_data='images'),
            InlineKeyboardButton("فيديوهات", callback_data='videos')
        ],
        [
            InlineKeyboardButton("تواصل مع المطور💬", url="https://t.me/l7l7aj"),
            InlineKeyboardButton("قناة 📱المطور", url="https://youtube.com/@l7aj.1m?si=G2aaF9U_7PkrdCCA")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # إرسال رسالة ترحيب مع الأزرار
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    # إرسال إشعار للمشرف عند دخول مستخدم جديد
    if user_id != ADMIN_USER_ID:  # إذا كان المستخدم ليس المشرف
        await context.bot.send_message(ADMIN_USER_ID, f"مستخدم جديد دخل البوت: {update.message.from_user.username} (ID: {user_id})")

# دالة المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    إليك بعض الأوامر التي يمكنك استخدامها:
    /start - لبدء التفاعل مع البوت.
    /about - معلومات عن البوت.
    /register - لتسجيل نفسك في البوت.
    """
    await update.message.reply_text(help_text)

# دالة حول البوت
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
    هذا البوت خاص بالبحث عن صور وفيديوهات باستخدام الكلمات المفتاحية.
    تم تطويره بواسطة المطور @l7l7aj.
    """
    await update.message.reply_text(about_text)

# دالة تسجيل المستخدمين
async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    await update.message.reply_text(f"تم تسجيلك بنجاح، {username}!")

# دالة لعرض عدد المستخدمين
async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_USER_ID:  # التأكد من أن المستخدم هو المشرف
        await update.message.reply_text(f"عدد المستخدمين الكلي: {total_users}\nعدد المستخدمين النشطين: {active_users}")
    else:
        await update.message.reply_text("أنت لست المشرف!")

# دالة البحث عن الصور عبر Pixabay
async def search_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if query:
        response = requests.get(
            PIXABAY_IMAGE_URL,
            params={
                "key": PIXABAY_API_KEY,
                "q": query,
                "per_page": 5
            }
        )

        # التحقق من استجابة API
        if response.status_code == 200:
            data = response.json()
            if data["hits"]:
                for image in data["hits"]:
                    # إرسال الصورة مع النص الذي يحتوي على المصدر
                    photo_caption = f"المصدر: [Pixabay](https://pixabay.com/)"
                    await update.message.reply_photo(image["webformatURL"], caption=photo_caption, parse_mode="Markdown")
            else:
                await update.message.reply_text("لم يتم العثور على صور.")
        else:
            await update.message.reply_text("حدث خطأ أثناء البحث عن الصور.")
            logger.error(f"Error fetching images from Pixabay: {response.status_code}")
    else:
        await update.message.reply_text("من فضلك أدخل نصًا للبحث عن الصور.")

# دالة البحث عن الفيديوهات عبر Pixabay
async def search_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if query:
        response = requests.get(
            PIXABAY_VIDEO_URL,
            params={
                "key": PIXABAY_API_KEY,
                "q": query,
                "per_page": 5
            }
        )

        # التحقق من استجابة API
        if response.status_code == 200:
            data = response.json()
            if data["hits"]:
                for video in data["hits"]:
                    # إرسال الفيديو مع النص الذي يحتوي على المصدر
                    video_caption = f"المصدر: [Pixabay](https://pixabay.com/)"
                    await update.message.reply_video(video["videos"]["medium"]["url"], caption=video_caption, parse_mode="Markdown")
            else:
                await update.message.reply_text("لم يتم العثور على فيديوهات.")
        else:
            await update.message.reply_text("حدث خطأ أثناء البحث عن الفيديوهات.")
            logger.error(f"Error fetching videos from Pixabay: {response.status_code}")
    else:
        await update.message.reply_text("من فضلك أدخل نصًا للبحث عن الفيديوهات.")

# التعامل مع الضغط على الأزرار لاختيار الصور أو الفيديوهات
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # حفظ نوع البحث في بيانات المستخدم
    context.user_data["search_type"] = data

    # تحديث الرسالة لتأكيد الاختيار
    if data == "images":
        await query.edit_message_text("تم اختيار البحث عن صور. الآن، اكتب كلمة البحث.")
    elif data == "videos":
        await query.edit_message_text("تم اختيار البحث عن فيديوهات. الآن، اكتب كلمة البحث.")

# التعامل مع الرسائل بناءً على نوع البحث (صور أو فيديوهات)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    search_type = user_data.get("search_type")

    if search_type == "images":
        await search_images(update, context)
    elif search_type == "videos":
        await search_videos(update, context)
    else:
        await update.message.reply_text("من فضلك اختر نوع البحث أولاً (صور أو فيديوهات) باستخدام الأزرار.")

# تهيئة البوت
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("register", register_user))
    app.add_handler(CommandHandler("admin", show_users))  # عرض عدد المستخدمين للمشرف
    app.add_handler(CallbackQueryHandler(button))  # التعامل مع الضغط على الأزرار
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # التعامل مع الرسائل

    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
