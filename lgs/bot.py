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

def start_subject(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    user_state[user_id] = "s_name"
    bot.send_message(user_id, text="Ders adını yaz:")

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
    if state == "s_name":
        user_data[user_id]["s_name"] = message.text.strip()
        user_state[user_id] = "description"
        bot.send_message(user_id, text="Açıklamasını yaz yaz:")
    if state == "description":
        user_data[user_id]["description"] = message.text.strip()
        del user_state[user_id]
        info = user_data[user_id]
        Subject.objects.create(title=info["s_name"],description=info["description"])
        code_btn = types.InlineKeyboardButton(text="Geri", callback_data="panel")
        markup.row(code_btn)
        bot.send_message(message.chat.id, "Ders ekledin!", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
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
        add_s_btn = types.InlineKeyboardButton(text="Ders Ekle", callback_data="add_s")
        del_s_btn = types.InlineKeyboardButton(text="Ders Sil", callback_data="list_s")
        score_btn = types.InlineKeyboardButton(text="Birisi'nin Skoruna Bak", callback_data="list")
        back_btn = types.InlineKeyboardButton(text="Back", callback_data="main")
        markup.row(add_q_btn)
        markup.row(del_q_btn)
        markup.row(add_s_btn)
        markup.row(del_s_btn)
        markup.row(score_btn)
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
    if call.data == "list_s":
        markup = types.InlineKeyboardMarkup()
        for subject in Subject.objects.all():
            del_s_btn = types.InlineKeyboardButton(text=f"{subject.title}", callback_data=f"del_s|{subject.id}")
            markup.row(del_s_btn)
        back_btn = types.InlineKeyboardButton(text="Back", callback_data="panel")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Silmek için seç:", reply_markup=markup)
    if call.data == "list":
        markup = types.InlineKeyboardMarkup()
        for user in CustomUser.objects.all():
            if user.tg_id == call.message.chat.id:
                btn = types.InlineKeyboardButton(text=f"Siz", callback_data=f"score|{user.id}")

            else:
                btn = types.InlineKeyboardButton(text=f"{user.first_name}", callback_data=f"score|{user.id}")
            markup.row(btn)
        bot.send_message(call.message.chat.id, "Kullanıcı Seçin:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "score":
        markup = types.InlineKeyboardMarkup()
        user=CustomUser.objects.get(id=call.data.split("|", 1)[1])
        back_btn = types.InlineKeyboardButton(text="Geri", callback_data="panel")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, f"{user.first_name}\nYanlışlar:{user.wrongs}\nDoğrular:{user.corrects}", reply_markup=markup)
    if call.data.split("|", 1)[0] == "del_q":
        markup = types.InlineKeyboardMarkup()
        question=Quiz.objects.get(id=call.data.split("|", 1)[1])
        question.delete()
        back_btn = types.InlineKeyboardButton(text="Geri",callback_data="panel")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Soruyu sildin!", reply_markup=markup)
    if call.data.split("|", 1)[0] == "del_s":
        markup = types.InlineKeyboardMarkup()
        subject=Subject.objects.get(id=call.data.split("|", 1)[1])
        subject.delete()
        back_btn = types.InlineKeyboardButton(text="Geri",callback_data="panel")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Ders sildin!", reply_markup=markup)

    if call.data == "start":
        markup = types.InlineKeyboardMarkup()
        for subject in Subject.objects.all():
            btn = types.InlineKeyboardButton(text=subject.title, callback_data=f"filter|{subject.id}")
            markup.row(btn)
        btn = types.InlineKeyboardButton(text="Her şey", callback_data=f"quiz")
        markup.row(btn)
        bot.send_message(call.message.chat.id, "Bir şey seç:", reply_markup=markup)
    if call.data == "quiz":
        markup = types.InlineKeyboardMarkup()
        question = random.choice(Quiz.objects.all())
        symbols = ["A","B","C","D"]
        answers = [question.wrong_answer_1, question.right_answer, question.wrong_answer_2, question.wrong_answer_3]
        for i in range(len(answers)):
            for j in range(len(symbols)):
                if answers[j] == symbols[i]:
                    answer = answers[j]

            if answer == question.right_answer:
                btn = types.InlineKeyboardButton(text=answer, callback_data=f"right|{question.id}")
            else:
                btn = types.InlineKeyboardButton(text=answer, callback_data=f"wrong|{question.id}")
            markup.row(btn)
        bot.send_photo(call.message.chat.id, photo=question.question, reply_markup=markup)
    if call.data.split("|", 1)[0] == "filter":
        markup = types.InlineKeyboardMarkup()
        question = random.choice(Quiz.objects.filter(subject=call.data.split("|", 1)[1]))
        symbols = ["A", "B", "C", "D"]
        answers = [question.wrong_answer_1, question.right_answer, question.wrong_answer_2, question.wrong_answer_3]

        for i in range(len(answers)):
            for j in range(len(symbols)):
                if answers[j] == symbols[i]:
                    answer = answers[j]
            if answer == question.right_answer:
                btn = types.InlineKeyboardButton(text=answer, callback_data=f"f_right|{question.id}")
            else:
                btn = types.InlineKeyboardButton(text=answer, callback_data=f"f_wrong|{question.id}")
            markup.row(btn)
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
        continue_btn = types.InlineKeyboardButton(text="Devam et", callback_data=f"quiz")
        quit_btn = types.InlineKeyboardButton(text="Çık", callback_data="main")
        markup.row(continue_btn)
        markup.row(quit_btn)
        bot.send_message(call.message.chat.id,
                         text=f"Hayır!Yanlış yaptın doğru cevap:{question.right_answer}",
                         reply_markup=markup)
    if call.data.split("|", 1)[0] == "f_wrong":
        markup = types.InlineKeyboardMarkup()
        question = Quiz.objects.get(id=call.data.split("|", 1)[1])
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        user.wrongs += 1
        user.save()
        continue_btn = types.InlineKeyboardButton(text="Devam et", callback_data=f"filter|{question.subject.id}")
        quit_btn = types.InlineKeyboardButton(text="Çık", callback_data="main")
        markup.row(continue_btn)
        markup.row(quit_btn)
        bot.send_message(call.message.chat.id,
                         text=f"Hayır!Yanlış yaptın doğru cevap:{question.right_answer}",
                         reply_markup=markup)
    if call.data.split("|", 1)[0] == "f_right":
        markup = types.InlineKeyboardMarkup()
        question = Quiz.objects.get(id=call.data.split("|", 1)[1])
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        user.corrects += 1
        user.save()
        continue_btn = types.InlineKeyboardButton(text="Devam et", callback_data=f"filter|{question.subject.id}")
        quit_btn = types.InlineKeyboardButton(text="Çık", callback_data="main")
        markup.row(continue_btn)
        markup.row(quit_btn)
        bot.send_message(call.message.chat.id,
                         text=f"Tebrikler!Doğru yaptın cevap:{question.right_answer}",
                         reply_markup=markup)
    if call.data == "add_q":
        markup = types.InlineKeyboardMarkup()
        for subject in Subject.objects.all():
            btn = types.InlineKeyboardButton(text=subject.title, callback_data=f"add_q_2|{subject.id}")
            markup.row(btn)
        bot.send_message(call.message.chat.id, "Bir ders seç:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "add_q_2":
        start_question(call.message, call.data.split("|", 1)[1])
    if call.data == "add_s":
        start_subject(call.message)

bot.infinity_polling()
