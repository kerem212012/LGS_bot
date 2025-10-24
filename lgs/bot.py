import os
import random
import sys

import django
from telebot import types

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgs_bot.settings')
django.setup()

import telebot
from environs import Env
from lgs.models import *

env = Env()
env.read_env()
bot = telebot.TeleBot(env.str("TG_TOKEN"))
user_state = {}
user_data = {}


def create_user(tg_id, name):
    CustomUser.objects.update_or_create(tg_id=tg_id, first_name=name, username=tg_id)


def start_question(message, subject):
    user_id = message.chat.id
    user_data[user_id] = {}
    user_data[user_id]["subject"] = subject
    user_state[user_id] = "question"
    bot.send_message(user_id, text="Soru'nun fotosunu at!")




@bot.message_handler(func=lambda msg: msg.chat.id in user_state,content_types=['photo','text'])
def handle_add_steps(message):
    markup = types.InlineKeyboardMarkup()
    user_id = message.chat.id
    state = user_state.get(user_id)
    if state == "question":
        user_data[user_id]["question"] = message.photo[-1].file_unique_id
        file_path = bot.get_file(message.photo[-1].file_id).file_path
        file = bot.download_file(file_path)
        with open(f"../media/{message.photo[-1].file_unique_id}.png", "wb") as code:
            code.write(file)
        user_state[user_id] = "right_a"
        bot.send_message(user_id, text="Doğru cevabı yaz:")
    if state == "right_a":
        user_data[user_id]["right_a"] = message.text.strip()
        user_state[user_id] = "wrong_a"
        bot.send_message(user_id, text="1.Yanlış cevabı yaz:")
    if state == "wrong_a":
        user_data[user_id]["wrong_a"] = message.text.strip()
        user_state[user_id] = "wrong_a_2"
        bot.send_message(user_id, text="2.Yanlış cevabı yaz:")
    if state == "wrong_a_2":
        user_data[user_id]["wrong_a_2"] = message.text.strip()
        user_state[user_id] = "wrong_a_3"
        bot.send_message(user_id, text="3.Yanlış cevabı yaz:")
    if state == "wrong_a_3":
        user_data[user_id]["wrong_a_3"] = message.text.strip()
        del user_state[user_id]
        info = user_data[user_id]
        Quiz.objects.create(question=f"{info["question"]}.png", right_answer=info["right_a"], wrong_answer_1=info["wrong_a"],
                            wrong_answer_2=info["wrong_a_2"], wrong_answer_3=info["wrong_a_3"], subject=Subject.objects.get(id=info["subject"]))
        code_btn = types.InlineKeyboardButton(text="Geri", callback_data="panel")
        markup.row(code_btn)
        bot.send_message(message.chat.id, "Soruyu ekledin!", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"{message.photo} a")
    markup = types.InlineKeyboardMarkup()
    create_user(message.chat.id, message.chat.first_name)
    bot.send_message(message.chat.id, text=f"Merhaba!{message.chat.first_name}")
    start_btn = types.InlineKeyboardButton(text="Başla", callback_data="start")
    markup.row(start_btn)
    user = CustomUser.objects.get(tg_id=message.chat.id)
    if user.admin:
        code_btn = types.InlineKeyboardButton(text="Admin Paneli", callback_data="panel")
        markup.row(code_btn)
    info_btn = types.InlineKeyboardButton(text="İnfo", callback_data="info")
    markup.row(info_btn)
    bot.send_message(message.chat.id, "Hadi başlayalım!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "main":
        markup = types.InlineKeyboardMarkup()
        bot.send_message(call.message.chat.id, text=f"Merhaba!{call.message.chat.first_name}")
        start_btn = types.InlineKeyboardButton(text="Başla", callback_data="start")
        markup.row(start_btn)
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        if user.admin:
            code_btn = types.InlineKeyboardButton(text="Admin Paneli", callback_data="panel")
            markup.row(code_btn)
        info_btn = types.InlineKeyboardButton(text="İnfo", callback_data="info")
        markup.row(info_btn)
        bot.send_message(call.message.chat.id, "Hadi başlayalım!", reply_markup=markup)
    if call.data == "panel":
        markup = types.InlineKeyboardMarkup()
        add_q_btn = types.InlineKeyboardButton(text="Soru Ekle", callback_data="add_q")
        del_q_btn = types.InlineKeyboardButton(text="Soru Sil", callback_data="list_q")
        back_btn = types.InlineKeyboardButton(text="Back", callback_data="main")
        markup.row(add_q_btn)
        markup.row(del_q_btn)
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Bir şey seç:", reply_markup=markup)
    if call.data == "list_q":
        markup = types.InlineKeyboardMarkup()
        for question in Quiz.objects.all():
            time =question.created_at
            del_q_btn = types.InlineKeyboardButton(text=f"{time.hour}:{time.minute}:{time.second} {time.day}/{time.month}/{time.year}", callback_data=f"del_q|{question.id}")
            markup.row(del_q_btn)
        back_btn = types.InlineKeyboardButton(text="Back", callback_data="panel")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Silmek için seç:", reply_markup=markup)

    if call.data.split("|", 1)[0] == "del_q":
        markup = types.InlineKeyboardMarkup()
        question=Quiz.objects.get(id=call.data.split("|", 1)[1])
        question.delete()
        back_btn = types.InlineKeyboardButton(text="Back",callback_data="panel")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Soruyu sildin!", reply_markup=markup)

    if call.data == "start":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Her şey", callback_data=f"quiz")
        markup.row(btn)
        bot.send_message(call.message.chat.id, "Bir şey seç:", reply_markup=markup)
    if call.data == "quiz":
        markup = types.InlineKeyboardMarkup()
        question = random.choice(Quiz.objects.all())
        answers = [question.wrong_answer_1, question.right_answer, question.wrong_answer_2, question.wrong_answer_3]
        for _ in range(4):
            answer = random.choice(answers)
            if answer == question.right_answer:
                btn = types.InlineKeyboardButton(text=answer, callback_data=f"right|{question.id}")
            else:
                btn = types.InlineKeyboardButton(text=answer, callback_data=f"wrong|{question.id}")
            markup.row(btn)
            answers.remove(answer)
        bot.send_photo(call.message.chat.id, photo=question.question, reply_markup=markup)
    if call.data.split("|", 1)[0] == "right":
        markup = types.InlineKeyboardMarkup()
        question = Quiz.objects.get(id=call.data.split("|", 1)[1])
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        user.corrects += 1
        user.save()
        continue_btn = types.InlineKeyboardButton(text="Devam et", callback_data=f"quiz")
        quit_btn = types.InlineKeyboardButton(text="Çık", callback_data="main")
        markup.row(continue_btn)
        markup.row(quit_btn)
        bot.send_message(call.message.chat.id,
                         text=f"Tebrikler!Doğru yaptın cevap:{question.right_answer}",
                         reply_markup=markup)
    if call.data.split("|", 1)[0] == "wrong":
        markup = types.InlineKeyboardMarkup()
        question = Quiz.objects.get(id=call.data.split("|", 1)[1])
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        user.wrongs += 1
        user.save()
        continue_btn = types.InlineKeyboardButton(text="Continue", callback_data=f"quiz")
        quit_btn = types.InlineKeyboardButton(text="Quit", callback_data="main")
        markup.row(continue_btn)
        markup.row(quit_btn)
        bot.send_message(call.message.chat.id,
                         text=f"Hayır!Yanlış yaptın doğru cevap:{question.right_answer}",
                         reply_markup=markup)
    if call.data == "add_q":
        markup = types.InlineKeyboardMarkup()
        for subject in Subject.objects.all():
            btn = types.InlineKeyboardButton(text=subject.title, callback_data=f"add_q_2|{subject.id}")
            markup.row(btn)
        bot.send_message(call.message.chat.id, "Bir ders seç:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "add_q_2":
        start_question(call.message, call.data.split("|", 1)[1])


bot.infinity_polling()
