import html
import random

import KuramaRobot.modules.truth_and_dare_string as fun
from KuramaRobot import dispatcher
from KuramaRobot.modules.helper_funcs.chat_status import is_user_admin
from KuramaRobot.modules.helper_funcs.extraction import extract_user
from telegram import ParseMode, Update
from KuramaRobot.modules.disable import DisableAbleCommandHandler
from telegram.ext import CallbackContext, run_async
from KuramaRobot.modules.helper_funcs.chat_status import (is_user_admin)
from KuramaRobot.modules.helper_funcs.extraction import extract_user



def truth(update: Update, context: CallbackContext):
    update.effective_message.reply_text(random.choice(fun.TRUTH))

def dare(update: Update, context: CallbackContext):
    update.effective_message.reply_text(random.choice(fun.DARE))
    
def simp(update: Update, context: CallbackContext):
    update.effective_message.reply_text(random.choice(fun.SIMP))
    
    
TRUTH_HANDLER = DisableAbleCommandHandler("truth", truth, run_async=True)
DARE_HANDLER = DisableAbleCommandHandler("dare", dare, run_async=True)
SIMP_HANDLER = DisableAbleCommandHandler("simp", simp, run_async=True)

dispatcher.add_handler(TRUTH_HANDLER)
dispatcher.add_handler(SIMP_HANDLER)
