
import time
import random
import humanize

from typing import Optional
from datetime import datetime
from telegram import Message, User
from telegram import MessageEntity, ParseMode
from telegram.error import BadRequest
from telegram.ext import Filters, MessageHandler, run_async

from KuramaRobot import dispatcher
from KuramaRobot.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
from KuramaRobot.modules.redis.afk_redis import start_afk, end_afk, is_user_afk, afk_reason
from KuramaRobot import REDIS
from KuramaRobot.modules.users import get_user_id

from KuramaRobot.modules.helper_funcs.alternate import send_message
from KuramaRobot.modules.helper_funcs.readable_time import get_readable_time

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


def afk(update, context):
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user
    if not user:  # ignore channels
        return

    if user.id == 777000:
        return
    start_afk_time = time.time()
    reason = args[1] if len(args) >= 2 else "none"
    start_afk(update.effective_user.id, reason)
    REDIS.set(f'afk_time_{update.effective_user.id}', start_afk_time)
    fname = update.effective_user.first_name
    try:
        options = [
          "{} is now busy with their partner oops i forgot he/she does not have a partner 🌚 sed life!",
          "{}is dead everyone spam f in the chat to pay respect",
          "{} is now dead rip",
          "{} buye buyee no one will miss u ",
          "oii {} where are u going ",
          "{} is now afk sed life ",
          "{} has left us now there will be peace",
          "{} has left us letsss parrtttyyyy",
          "{} The greatest piroo is now afk sed loife",
          "{} has left the chamt 🌚🌚🌚!",
          "{} has left the world and is now on a higher place spam f guys",
          "{} boi boi i will miss u meowww",
          "{} bui bui cutu come back soon oke",
          "{} bye baby come soon oke",
          "{} i will miss you come soon ok cutie",

        ]
        chosen_option = random.choice(options)
        update.effective_message.reply_text(chosen_option.format(fname))
    except BadRequest:
        pass

def no_longer_afk(update, context):
    user = update.effective_user
    message = update.effective_message
    if not user:  # ignore channels
        return

    if not is_user_afk(user.id):  #Check if user is afk or not
        return
    end_afk_time = get_readable_time((time.time() - float(REDIS.get(f'afk_time_{user.id}'))))
    REDIS.delete(f'afk_time_{user.id}')
    res = end_afk(user.id)
    if res:
        if message.new_chat_members:  # dont say msg
            return
        firstname = update.effective_user.first_name
        try:
            options = [
                "{} hey darling welcome back",
                "{} welcome back my dear i was waiting for u",
                "{} hey there cutiepie welcome back",
                "{} Is now back from the dead meow!",
                "{} where have u been i missed you a lot",
                "heyy {} where have you beenn i was so worried ",
                "oii {} where were u bissh everyone missed you",
                "hey {} babe ur backk so lets go on a date",
                "{} is now here what are ur other two wishes",
                "{} Is here nothing to fear just drink beer meow!",
                "{} The greatest piroo declared by madara is back !",
                "{} is bamck in the chamt 🌚🌚🌚!",
                "{} is finally here!",
                "Welcome back!i missed you 🥺❤️ {}",
                "Where is {}?\nIn my heart 🥺❤️!",
                "hey there cutupie welcome back",
                "{} is welcome back hottie 🌚🌚🌚!",
                "{} where have u been bisshh i missed a u lot",
                "{} i missed u {} 🥺❤️ welcome back",
                "{} are u okay where were u i was missing u",
            ]
            chosen_option = random.choice(options)
            update.effective_message.reply_text(
                chosen_option.format(firstname),
            )
        except BaseException:
            pass
            



def reply_afk(update, context):
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION])

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(message.text[ent.offset:ent.offset +
                                                   ent.length])
                if not user_id:
                    # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                    return

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

                try:
                    chat = context.bot.get_chat(user_id)
                except BadRequest:
                    print("Error: Could not fetch userid {} for AFK module".
                          format(user_id))
                    return
                fst_name = chat.first_name

            else:
                return

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update, context, user_id, fst_name, userc_id):
    if is_user_afk(user_id):
        reason = afk_reason(user_id)
        since_afk = get_readable_time((time.time() - float(REDIS.get(f'afk_time_{user_id}'))))
        if int(userc_id) == int(user_id):
            return
        if reason == "none":
            res = "{} is Dead!\nLast Liveliness: {} Ago.".format(fst_name, since_afk)
        else:
            res = "{} is afk!\nReason: {}\nLast seen: {} Ago.".format(fst_name, reason, since_afk)

        update.effective_message.reply_text(res)


def __user_info__(user_id):
    is_afk = is_user_afk(user_id)
    text = ""
    if is_afk:
        since_afk = get_readable_time((time.time() - float(REDIS.get(f'afk_time_{user_id}'))))
        text = "This user is currently afk (away from keyboard)."
        text += f"\nLast Seen: {since_afk} Ago."
       
    else:
        text = "This user currently isn't afk (not away from keyboard)."
    return text

def __stats__():
    return f"• {len(REDIS.keys())} Total Keys in Redis Database."

def __gdpr__(user_id):
    end_afk(user_id)


AFK_HANDLER = DisableAbleCommandHandler("afk", afk, run_async=True)
AFK_REGEX_HANDLER = MessageHandler(Filters.regex("(?i)brb"), afk)
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.chat_type.groups, no_longer_afk, run_async=True)
AFK_REPLY_HANDLER = MessageHandler(Filters.all & Filters.chat_type.groups, reply_afk, run_async=True)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)
