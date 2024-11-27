from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Liên kết các kênh
CHANNELS = [
    "@hongtintucvn",
]

# Liên kết đến trò chơi
GAME_LINK = "https://Tai88vin.biz"  # Thay đổi URL đến trò chơi của bạn
SUPPORT_LINK = "https://t.me/ChiPheoSuy"

# Lưu trữ thông tin người dùng
user_data = {}
user_ids = set()  # Dùng set để đảm bảo mỗi user_id chỉ xuất hiện một lần

# ID của admin
admin_id = 5561403663

def create_referral_link(user_id):
    return f"https://t.me/code88vinFREEFIRE_bot?start={user_id}"

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    missing_channels = []
    
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                missing_channels.append(channel)
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra thành viên: {e}")
            await update.message.reply_text("Có lỗi xảy ra khi kiểm tra thành viên. Vui lòng đảm bảo bot là quản trị viên của kênh và bạn đã tham gia.")
            return False

    if missing_channels:
        response_text = "Bạn cần tham gia các kênh sau trước khi sử dụng bot:\n"
        keyboard = []
        for channel in missing_channels:
            response_text += f"- {channel}\n"
            keyboard.append([InlineKeyboardButton("Tham gia", url=f"https://t.me/{channel[1:]}")])

        await update.message.reply_text(response_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return False

    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_membership(update, context):
        user_id = update.effective_user.id
        referral_link = create_referral_link(user_id)

        # Khởi tạo người dùng nếu chưa có
        if user_id not in user_data:
            user_data[user_id] = {'username': update.effective_user.username, 'balance': 0, 'points': 0, 'invited_count': 0}
            user_ids.add(user_id)  # Thêm user_id vào danh sách

        keyboard = [
            [
                InlineKeyboardButton("Tài khoản 👤", callback_data='account'),
                InlineKeyboardButton("Đổi code 🎁", callback_data='withdraw')
            ],
            [
                InlineKeyboardButton("Mời bạn bè 💵", callback_data='invite'),
                InlineKeyboardButton("Link game 🎮", url=GAME_LINK)
            ],
            [
                InlineKeyboardButton("Hỗ trợ 💢", callback_data='support')
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Chào mừng bạn đến với bot! Vui lòng chọn một trong các tùy chọn sau:", reply_markup=reply_markup)

# Hàm để hiển thị thông tin tài khoản người dùng
async def account_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data:
        username = user_data[user_id]['username']
        balance = user_data[user_id]['balance']
        points = user_data[user_id]['points']
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=f"Tên người dùng: @{username}\nSố dư hiện tại: {balance} VND\nĐiểm thưởng: {points} điểm"
        )
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Thông tin tài khoản không có.")

async def withdraw_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "✅ Số Tiền Rút Tối Thiểu 20K\n"
        "👉 Làm Theo Các Lệnh Sau Đây Để Rút Tiền ⚠️\n"
        "👉 Vui Lòng KICK VÀO PHẦN 20000 ✅ là xong nhé"
    )
    keyboard = [[InlineKeyboardButton("20000 ✅", callback_data='confirm_withdraw')]]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_data[user_id]['balance'] >= 20000:
        user_data[user_id]['balance'] -= 20000
        # Gửi thông báo cho admin về lệnh rút tiền
        await context.bot.send_message(
            admin_id,
            f"🔔 Lệnh rút tiền mới:\n"
            f"👤 Người dùng: @{user_data[user_id]['username']}\n"
            f"💵 Số tiền rút: 20K VND\n"
            f"🆔 ID Người dùng: {user_id}\n\n"
            "📣 Admin có thể phản hồi ở đây"
        )
        # Thông báo cho người dùng đã tạo lệnh rút thành công
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Bạn đã tạo lệnh rút code thành công, vui lòng đợi admin duyệt nhé ✅"
        )
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "❌ Bạn không đủ số dư để rút, vui lòng mời bạn bè để có đủ số dư."
        )
async def invite_friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = create_referral_link(user_id)
    message = (
        f"Chia sẻ liên kết mời bạn bè của bạn để nhận thưởng: {referral_link}\n"
        "Mời bạn bè tham gia và nhận thưởng nhé!"
    )
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(message)
   
  # Định nghĩa một hàm mà không có lỗi indent
async def support_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Nếu bạn gặp vấn đề, hãy liên hệ với chúng tôi qua kênh hỗ trợ: "
        f"{SUPPORT_LINK}\n"
        "Chúng tôi sẽ giải đáp các thắc mắc của bạn."
    )
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(message)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(message)
    
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(message)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'withdraw':
        await withdraw_money(update, context)
    elif query.data == 'confirm_withdraw':
        await handle_withdraw(update, context)
    elif query.data == 'account':
        await account_info(update, context)
    elif query.data == 'support':
        await support_info(update, context)
    elif query.data == 'invite':
        await invite_friends(update, context)

# Lệnh broadcast thông báo đến tất cả người dùng
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == admin_id:
        if context.args:
            message = ' '.join(context.args)  # Ghép các tham số vào một thông báo
            for user_id in user_ids:
                try:
                    await context.bot.send_message(user_id, message)
                except Exception as e:
                    logger.error(f"Không thể gửi tin nhắn đến người dùng {user_id}: {e}")
            await update.message.reply_text(f"Đã gửi thông báo đến {len(user_ids)} người dùng.")
        else:
            await update.message.reply_text("Cú pháp: /broadcast <thông_báo>")

    else:
        await update.message.reply_text("Bạn không có quyền thực hiện hành động này.")
        
        # Lệnh phản hồi cho admin
async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == admin_id:  # Kiểm tra xem có phải admin không
        if context.args:
            user_to_respond = int(context.args[0])  # ID người dùng cần phản hồi
            response = ' '.join(context.args[1:])  # Phản hồi từ admin

            if user_to_respond in user_data:
                # Gửi phản hồi đến người dùng
                await context.bot.send_message(
                    user_to_respond,
                    f"🔔 Admin đã phản hồi:\n{response}\n\nLệnh rút tiền của bạn đã được xử lý ✅"
                )
                await update.message.reply_text(f"Đã gửi phản hồi cho @{user_data[user_to_respond]['username']}.")
            else:
                await update.message.reply_text("Người dùng không tồn tại.")
        else:
            await update.message.reply_text("Cú pháp: /adminresponse <user_id> <phản hồi>")
    else:
        await update.message.reply_text("Bạn không có quyền thực hiện hành động này.")

# Lệnh thêm tiền
async def add_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == admin_id:
        if context.args:
            try:
                user_id = int(context.args[0])
                amount = int(context.args[1])

                if user_id in user_data:
                    user_data[user_id]['balance'] += amount
                    await update.message.reply_text(f"Đã cộng {amount} VND cho người dùng @{user_data[user_id]['username']}.")
                else:
                    await update.message.reply_text("Người dùng không tồn tại.")
            except (IndexError, ValueError):
                await update.message.reply_text("Cú pháp: /addmoney <user_id> <số_tiền>")
        else:
            await update.message.reply_text("Cú pháp: /addmoney <user_id> <số_tiền>")

def main():
    app = ApplicationBuilder().token("7717334781:AAE3n9tSn9Cf2Bl6L2S21j7HKhIy8Rrzgg0").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addmoney", add_money))  # Thêm lệnh để cộng tiền
    app.add_handler(CommandHandler("adminresponse", admin_response))  # Thêm lệnh phản hồi admin

    app.run_polling()
    
if __name__ == "__main__":
    main()