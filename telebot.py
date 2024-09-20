import logging
import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler
from uuid import uuid4
from functools import wraps


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO

)



'''
this is global variables section 
'''
ADMINS = []

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMINS:
            return
        return await func(update, context, *args, **kwargs)
    return wrapped


def send_action(action):

    '''
    sends actions to the user while processing the commands
    '''

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context, *args, **kwargs)
        return command_func
    return decorator




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="started")
    # print(update.effective_user.id)

@restricted
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = str(uuid4())



    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    text = ''.join(update.message.text)
    

    with open(key, "w") as file:
        file.write(text)





async def inline_caps(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(InlineQueryResultArticle(
        id=str(uuid4()),
        title='Caps',
        input_message_content=InputTextMessageContent(query.upper())
        ))
    await context.bot.answer_inline_query(update.inline_query.id, results)

@restricted
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # download file
    new_file = await update.message.effective_attachment[-1].get_file()
    file = await new_file.download_to_drive()

    return file

@restricted
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    recieves 
    '''
    if (
        not update.message
        or not update.effective_chat
        or (
            not update.message.photo
            and not update.message.video
            and not update.message.document
            and not update.message.sticker
            and not update.message.animation
            )
    ):
        return
    file = await download(update, context)

    if not file :
        await update.message.reply_text("something went wrong, try again")
        return
    
    update.message.reply_text("image downloaded sucessfully")
    









async def unknown(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="you send wrong shit to me you bastard")


if __name__ == '__main__':
    application = ApplicationBuilder().token('7317165974:AAG_jQ67I3dS9xyc32GB_G3qdBsMutD1sE8').build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    photo_handler = MessageHandler(filters.PHOTO, photo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)


    inline_caps_handler = InlineQueryHandler(inline_caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)   
    application.add_handler(inline_caps_handler)
    application.add_handler(photo_handler)

    application.add_handler(unknown_handler)




    application.run_polling()
