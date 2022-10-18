import random
import threading
from typing import Union

from KuramaRobot.modules.helper_funcs.msg_types import Types
from KuramaRobot.modules.sql import BASE, SESSION
from sqlalchemy import Boolean, Column, String, UnicodeText, Integer, BigInteger

DEFAULT_WELCOME = "Hey {first}, how are you?"
DEFAULT_GOODBYE = "Nice knowing ya!"

DEFAULT_WELCOME_MESSAGES = [
    "{first} hey babee welcome to the group!",  #Discord welcome messages copied
    "hey {first} Anyone who says Disneyland is the happiest place on the earth has clearly never stood next to you.",
    "Hey {first}, tie your shoes! I don’t want you falling for anyone else.",
    "Hey {first}, Heaven must be missing an angel since you’re here with me.",
    "Hey {first},I’m lost. Can you give me directions to your heart?",
    "Hey {first} Is your name Wi-Fi? ‘Cause I’m feeling a connection.",
    "Hey you {first} I was blinded by your beauty; I’m going to need your name and phone number for insurance purposes.",
    "{first}Did you just come out of the oven? Because demn you’re hot.",
    "{first} hey are you taken or can i call you mine",
    "{first} hi cutiepie i hope you will stay",
    "{first} your hand looks heavy let me hold it",
    "{first} baby is here nothing to fear",
    "{first} I hope you know CPR, because you just took my breath away!",
    "{first}  aside from taking my breath away, what do you do for a living?",
    "{first} Are you a parking ticket? ‘Cause you’ve got ‘fine’ written all over you.",
    "{first} Your eyes are like the ocean; I could swim in them all day.",
    "{first} I never believed in love at first sight, but that was before I saw you.",
    "{first} I was wondering if you could tell me: If you’re here, who’s running Heaven?",
    "hey! {first} I was wondering if you’re an artist because you were so good at drawing me in.",
    "{first} Do you have a map? I just got lost in your eyes.",
    "hey {first} Do You know what you would look really beautiful in? My arms.",
    "{first} I would never play hide and seek with you because someone like you is impossible to find.",
    "{first} just showed up. Hold my beer.",
    "hey {first} I always thought happiness started with an ‘h,’ but it turns out mine starts with ‘u.’",
 "hey {first} I believe in following my dreams. Can I have your Instagram?",
]

DEFAULT_GOODBYE_MESSAGES = [
    "{first} whyy did you leave me alone cutie",
    "{first}i will miss you cutiepie",
    "{first} please dont go we did not even talk",
    "{first} imma start crying now",
    "{first} nooo please don't go whhyyy curse you",
    "{first}how could u do this to me",
    "{first} i need you please don't go",
    "{first} you left me alone curse you",
    "{first} baby please don't go",
    "{first} last left the chat ",
    "get lost you weakling",
    "{first} how could u do this to me i trusted u with my life ",
]

class Welcome(BASE):
    __tablename__ = "welcome_pref"
    chat_id = Column(String(14), primary_key=True)
    should_welcome = Column(Boolean, default=True)
    should_goodbye = Column(Boolean, default=True)
    custom_content = Column(UnicodeText, default=None)

    custom_welcome = Column(
        UnicodeText,
        default=random.choice(DEFAULT_WELCOME_MESSAGES),
    )
    welcome_type = Column(Integer, default=Types.TEXT.value)

    custom_leave = Column(UnicodeText, default=random.choice(DEFAULT_GOODBYE_MESSAGES))
    leave_type = Column(Integer, default=Types.TEXT.value)

    clean_welcome = Column(BigInteger)

    def __init__(self, chat_id, should_welcome=True, should_goodbye=True):
        self.chat_id = chat_id
        self.should_welcome = should_welcome
        self.should_goodbye = should_goodbye

    def __repr__(self):
        return "<Chat {} should Welcome new users: {}>".format(
            self.chat_id,
            self.should_welcome,
        )


class WelcomeButtons(BASE):
    __tablename__ = "welcome_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url
        self.same_line = same_line


class GoodbyeButtons(BASE):
    __tablename__ = "leave_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url
        self.same_line = same_line


class WelcomeMute(BASE):
    __tablename__ = "welcome_mutes"
    chat_id = Column(String(14), primary_key=True)
    welcomemutes = Column(UnicodeText, default=False)

    def __init__(self, chat_id, welcomemutes):
        self.chat_id = str(chat_id)  # ensure string
        self.welcomemutes = welcomemutes


class WelcomeMuteUsers(BASE):
    __tablename__ = "human_checks"
    user_id = Column(BigInteger, primary_key=True)
    chat_id = Column(String(14), primary_key=True)
    human_check = Column(Boolean)

    def __init__(self, user_id, chat_id, human_check):
        self.user_id = user_id  # ensure string
        self.chat_id = str(chat_id)
        self.human_check = human_check


class CleanServiceSetting(BASE):
    __tablename__ = "clean_service"
    chat_id = Column(String(14), primary_key=True)
    clean_service = Column(Boolean, default=True)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)

    def __repr__(self):
        return "<Chat used clean service ({})>".format(self.chat_id)


Welcome.__table__.create(checkfirst=True)
WelcomeButtons.__table__.create(checkfirst=True)
GoodbyeButtons.__table__.create(checkfirst=True)
WelcomeMute.__table__.create(checkfirst=True)
WelcomeMuteUsers.__table__.create(checkfirst=True)
CleanServiceSetting.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()
WELC_BTN_LOCK = threading.RLock()
LEAVE_BTN_LOCK = threading.RLock()
WM_LOCK = threading.RLock()
CS_LOCK = threading.RLock()


def welcome_mutes(chat_id):
    try:
        welcomemutes = SESSION.query(WelcomeMute).get(str(chat_id))
        if welcomemutes:
            return welcomemutes.welcomemutes
        return False
    finally:
        SESSION.close()


def set_welcome_mutes(chat_id, welcomemutes):
    with WM_LOCK:
        prev = SESSION.query(WelcomeMute).get((str(chat_id)))
        if prev:
            SESSION.delete(prev)
        welcome_m = WelcomeMute(str(chat_id), welcomemutes)
        SESSION.add(welcome_m)
        SESSION.commit()


def set_human_checks(user_id, chat_id):
    with INSERTION_LOCK:
        human_check = SESSION.query(WelcomeMuteUsers).get((user_id, str(chat_id)))
        if not human_check:
            human_check = WelcomeMuteUsers(user_id, str(chat_id), True)

        else:
            human_check.human_check = True

        SESSION.add(human_check)
        SESSION.commit()

        return human_check


def get_human_checks(user_id, chat_id):
    try:
        human_check = SESSION.query(WelcomeMuteUsers).get((user_id, str(chat_id)))
        if not human_check:
            return None
        human_check = human_check.human_check
        return human_check
    finally:
        SESSION.close()


def get_welc_mutes_pref(chat_id):
    welcomemutes = SESSION.query(WelcomeMute).get(str(chat_id))
    SESSION.close()

    if welcomemutes:
        return welcomemutes.welcomemutes

    return False


def get_welc_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return (
            welc.should_welcome,
            welc.custom_welcome,
            welc.custom_content,
            welc.welcome_type,
        )
    # Welcome by default.
    return True, random.choice(DEFAULT_WELCOME_MESSAGES), None, Types.TEXT


def get_gdbye_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_goodbye, welc.custom_leave, welc.leave_type
    # Welcome by default.
    return True, random.choice(DEFAULT_GOODBYE_MESSAGES), Types.TEXT


def set_clean_welcome(chat_id, clean_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id))

        curr.clean_welcome = int(clean_welcome)

        SESSION.add(curr)
        SESSION.commit()


def get_clean_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()

    if welc:
        return welc.clean_welcome

    return False


def set_welc_preference(chat_id, should_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_welcome=should_welcome)
        else:
            curr.should_welcome = should_welcome

        SESSION.add(curr)
        SESSION.commit()


def set_gdbye_preference(chat_id, should_goodbye):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_goodbye=should_goodbye)
        else:
            curr.should_goodbye = should_goodbye

        SESSION.add(curr)
        SESSION.commit()


def set_custom_welcome(
    chat_id,
    custom_content,
    custom_welcome,
    welcome_type,
    buttons=None,
):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_welcome or custom_content:
            welcome_settings.custom_content = custom_content
            welcome_settings.custom_welcome = custom_welcome
            welcome_settings.welcome_type = welcome_type.value

        else:
            welcome_settings.custom_welcome = random.choice(DEFAULT_WELCOME_MESSAGES)
            welcome_settings.welcome_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with WELC_BTN_LOCK:
            prev_buttons = (
                SESSION.query(WelcomeButtons)
                .filter(WelcomeButtons.chat_id == str(chat_id))
                .all()
            )
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url, same_line in buttons:
                button = WelcomeButtons(chat_id, b_name, url, same_line)
                SESSION.add(button)

        SESSION.commit()


def get_custom_welcome(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = random.choice(DEFAULT_WELCOME_MESSAGES)
    if welcome_settings and welcome_settings.custom_welcome:
        ret = welcome_settings.custom_welcome

    SESSION.close()
    return ret


def set_custom_gdbye(chat_id, custom_goodbye, goodbye_type, buttons=None):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_goodbye:
            welcome_settings.custom_leave = custom_goodbye
            welcome_settings.leave_type = goodbye_type.value

        else:
            welcome_settings.custom_leave = random.choice(DEFAULT_GOODBYE_MESSAGES)
            welcome_settings.leave_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with LEAVE_BTN_LOCK:
            prev_buttons = (
                SESSION.query(GoodbyeButtons)
                .filter(GoodbyeButtons.chat_id == str(chat_id))
                .all()
            )
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url, same_line in buttons:
                button = GoodbyeButtons(chat_id, b_name, url, same_line)
                SESSION.add(button)

        SESSION.commit()


def get_custom_gdbye(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = random.choice(DEFAULT_GOODBYE_MESSAGES)
    if welcome_settings and welcome_settings.custom_leave:
        ret = welcome_settings.custom_leave

    SESSION.close()
    return ret


def get_welc_buttons(chat_id):
    try:
        return (
            SESSION.query(WelcomeButtons)
            .filter(WelcomeButtons.chat_id == str(chat_id))
            .order_by(WelcomeButtons.id)
            .all()
        )
    finally:
        SESSION.close()


def get_gdbye_buttons(chat_id):
    try:
        return (
            SESSION.query(GoodbyeButtons)
            .filter(GoodbyeButtons.chat_id == str(chat_id))
            .order_by(GoodbyeButtons.id)
            .all()
        )
    finally:
        SESSION.close()


def clean_service(chat_id: Union[str, int]) -> bool:
    try:
        chat_setting = SESSION.query(CleanServiceSetting).get(str(chat_id))
        if chat_setting:
            return chat_setting.clean_service
        return False
    finally:
        SESSION.close()


def set_clean_service(chat_id: Union[int, str], setting: bool):
    with CS_LOCK:
        chat_setting = SESSION.query(CleanServiceSetting).get(str(chat_id))
        if not chat_setting:
            chat_setting = CleanServiceSetting(chat_id)

        chat_setting.clean_service = setting
        SESSION.add(chat_setting)
        SESSION.commit()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Welcome).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)

        with WELC_BTN_LOCK:
            chat_buttons = (
                SESSION.query(WelcomeButtons)
                .filter(WelcomeButtons.chat_id == str(old_chat_id))
                .all()
            )
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        with LEAVE_BTN_LOCK:
            chat_buttons = (
                SESSION.query(GoodbyeButtons)
                .filter(GoodbyeButtons.chat_id == str(old_chat_id))
                .all()
            )
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        SESSION.commit()
