import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# إعدادات البوت
TELEGRAM_BOT_TOKEN = "7647977575:AAEs0yuy01ogPDheXPwJlD8YD-YHtIyGrQw"
UNSPLASH_API_KEY = "g8BHvdo-mU87N6CAurG8EFTxbIS3EneRjvanzcBOs6E"
UNSPLASH_URL = "https://api.unsplash.com/search/photos"
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
    يمكنك البحث🔍 عن صور🖼 فقط قم بكتابة اي كلمة💬 مثل *شمس☀️ ،  قمر🌑 ، طبيعة🏞 * من الاحسن باللغة الانجليزيا 🔤
    
    ●●●●●●●●●●●●●●●●●
    /help - لعرض التعليمات.
    /about - لمزيد من المعلومات عن البوت.
    /register - لتسجيل نفسك في البوت.
    ●●●●●●●●●●●●●●●●●●●
    """

    # إنشاء الأزرار الخاصة بالتواصل مع المطور وقناته
    buttons = [
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

# دالة البحث عن الصور عبر Unsplash (كما كانت سابقًا)
async def search_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if query:
        # إجراء طلب إلى API Unsplash للحصول على الصور
        response = requests.get(
            UNSPLASH_URL,
            params={
                "query": query,
                "client_id": UNSPLASH_API_KEY,
                "per_page": 5  # الحد من النتائج إلى 5 صور فقط
            }
        )

        # التحقق من استجابة API
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                for photo in data["results"]:
                    # إرسال الصور للمستخدم
                    await update.message.reply_photo(photo["urls"]["regular"])
            else:
                await update.message.reply_text("لم يتم العثور على صور.")
        else:
            await update.message.reply_text("حدث خطأ أثناء البحث عن الصور.")
            logger.error(f"Error fetching images from Unsplash: {response.status_code}")
    else:
        await update.message.reply_text("من فضلك أدخل نصًا للبحث عن الصور.")

# دالة حول البوت
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
    هذا البوت خاص بي البحث عن صور 
    يمكنك استخدامه للبحث عن صور باستخدام الكلمات المفتاحية.
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

# تهيئة البوت
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("register", register_user))
    app.add_handler(CommandHandler("admin", show_users))  # عرض عدد المستخدمين للمشرف
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_photos))  # استخدام الفلتر للبحث عن الصور

    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
