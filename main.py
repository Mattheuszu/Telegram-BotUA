import telebot
import requests
import webbrowser
from telebot import types
import os
import sqlite3
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from alerts_in_ua import AsyncClient as AsyncAlertsClient
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

name = None

bot = telebot.TeleBot('')
weather_api_key = ''
alerts_api_key = ''
alerts_client = AsyncAlertsClient(token=alerts_api_key)

group_chat_id = 

users = []
alerts_cache = {}

shelter_links = {
    1: ('Вінницька область', 'https://vajr.info/2023/10/21/karta-skhema-ukryttiv-na-vinnychchyni-iak-hromady-porushuiut-prava-zhurnalistiv-ok/'),
    2: ('Волинська область', 'https://rayon.in.ua/news/485969-zakhisni-sporudi-interaktivna-karta-roztashuvannya-skhovishch-na-volini'),
    3: ('Дніпропетровська область', 'https://vchasnoua.com/news/spysok-bomboskhovyshch-donechchyny-de-ukrytysia-u-razi-boiovykh-dii'),
    4: ('Донецька область', 'https://vchasnoua.com/news/spysok-bomboskhovyshch-donechchyny-de-ukrytysia-u-razi-boiovykh-dii'),
    5: ('Житомирська область', 'https://www.google.com/maps/d/u/0/viewer?mid=1CFml6yHssn83O7b_ap6djwJGv7HBrsw&ll=50.259716636255746%2C28.677647237622075&z=13'),
    6: ('Закарпатська область', 'https://carpathia.gov.ua/news/karta-ukrittiv-ta-zahisnih-sporud-zakarpattya'),
    7: ('Запорізька область', 'https://ukryttya.zp.gov.ua/'),
    8: ('Івано-Франківська область', 'https://www.mvk.if.ua/news/57379'),
    9: ('Київська область', 'https://koda.gov.ua/czyvilnyj-front/zahysni-sporudy-tochky-obigrivu/ukryttya/'),
    10: ('Кіровоградська область', 'https://dmitrovka-otg.gov.ua/useful-info/interaktivna-karta-zahisnih-sporud'),
    11: ('Луганська область', 'https://www.google.com/maps/d/u/0/viewer?mid=1j_f6ytqZ9kO67Y0cOjgDfqIPmag&ll=49.70192885437554%2C39.3944645435631&z=9&fbclid=IwAR1mOR3_z_MuRfUePxOG_THQSr36GSOIoUmS2tvcpGAPbv3QxZPiJ3fWun8'),
    12: ('Львівська область', 'https://map.city-adm.lviv.ua/map/main#map=11//49.79121931758962//24.034309387207035&&layer=9635585433681688-1,100//2765617480184367031-1,100'),
    13: ('Миколаївська область', 'https://mkrada.gov.ua/shelters/'),
    14: ('Одеська область', 'https://omr.gov.ua/ua/citizens/map-shelter/'),
    15: ('Полтавська область', 'https://www.google.com/maps/d/u/0/viewer?mid=10wBVAAKCTHdPXYODiUbhjTTrJoY&amp%3Bll=49.60204310930155%2C34.54944381904308&amp%3Bz=12&ll=49.53703680908182%2C34.56731333192668&z=11'),
    16: ('Рівненська область', 'https://7dniv.rv.ua/holovni-novyny/karta-zakhysnykh-sporud-rivnenshchyny/'),
    17: ('Сумська область', 'https://www.google.com/maps/d/u/0/viewer?mid=12U9NWrsOmGKyf6zGQvdY2br4USc7OeFx&hl=ru&ll=50.90906912283643%2C34.79703595&z=13'),
    18: ('Тернопільська область', 'https://giscid.maps.arcgis.com/apps/webappviewer/index.html?id=07691e5aec27459bb282268818419d46&fbclid=IwAR1x_ZVZeNThMuxmnbIOykJdpkxs2Pjuv5Vaz2IclluHusgDh_Bfj4GUxD0'),
    19: ('Харківська область', 'https://www.google.com/maps/d/u/0/viewer?mid=16g3PB0LSZYAsrrAuiXZuxEBVaN0&femb=1&ll=49.643443078822585%2C38.326274299999994&z=7'),
    20: ('Херсонська область', 'https://www.google.com/maps/d/u/0/viewer?mid=20'),
    21: ('Хмельницька область', 'https://www.google.com/maps/d/u/0/viewer?mid=15NSLcOIYzWeSf46DD_Sd8iJJcKM&ll=49.391498589515%2C26.990056440362657&z=11'),
    22: ('Черкаська область', 'https://ck-oda.gov.ua/perelik-zaxisnix-sporud-cherkaskoyi-oblasti/'),
    23: ('Чернівецька область', 'https://bukoda.gov.ua/gromadyanam/interaktivna-karta-zahisnih-sporud-civilnogo-zahistu'),
    24: ('Чернігівська область', 'https://www.google.com/maps/d/u/0/viewer?hl=ru&mid=1VJ4yH6VbKhqRP6Z1W3DB7vKhpXM&ll=51.52010647927098%2C31.276094464404316&z=13'),
    25: ('Автономна Республіка Крим', 'https://www.google.com/maps/d/u/0/viewer?mid=25'),
    26: ('м. Київ', 'https://texty.org.ua/fragments/105181/kyyiv-de-roztashovane-najblyzhche-do-vas-ukryttya-interaktyvna-karta/'),
    27: ('м. Севастополь', 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fternopilcity.gov.ua%2Fnews%2F56976.html&psig=AOvVaw3LPRlWLJlw7--HcmSpE-cz&ust=1717511979690000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCLjJ__XUv4YDFQAAAAAdAAAAABAJ')
}

regions = {
    1: 'Вінницька область',
    2: 'Волинська область',
    3: 'Дніпропетровська область',
    4: 'Донецька область',
    5: 'Житомирська область',
    6: 'Закарпатська область',
    7: 'Запорізька область',
    8: 'Івано-Франківська область',
    9: 'Київська область',
    10: 'Кіровоградська область',
    11: 'Луганська область',
    12: 'Львівська область',
    13: 'Миколаївська область',
    14: 'Одеська область',
    15: 'Полтавська область',
    16: 'Рівненська область',
    17: 'Сумська область',
    18: 'Тернопільська область',
    19: 'Харківська область',
    20: 'Херсонська область',
    21: 'Хмельницька область',
    22: 'Черкаська область',
    23: 'Чернівецька область',
    24: 'Чернігівська область',
    25: 'Автономна Республіка Крим',
    26: 'м. Київ',
    27: 'м. Севастополь'
}

@bot.message_handler(commands=['start'])
def main(message):
    user = {'chat_id': message.chat.id, 'name': message.from_user.first_name}
    if user not in users:
        users.append(user)
    bot.send_message(message.chat.id,
                     f'Привіт, {message.from_user.first_name}! Я повідомлятиму тебе про ракетну загрозу і найближчі сховища.')


scheduler = BackgroundScheduler()
def start_checking_rocket_threat(chat_id):
    scheduler.add_job(check_rocket_threats, 'interval', minutes=1, args=[chat_id])
    scheduler.start()

async def check_rocket_threats(chat_id):
    active_alerts = await alerts_client.get_active_alerts()
    alerts = active_alerts.get_all_alerts()
    rocket_threats = [alert for alert in alerts if 'ракетна' in alert.location_title.lower()]

    if rocket_threats:
        bot.send_message(chat_id, "🚀 УВАГА! Потенційна ракетна загроза!")
        scheduler.remove_all_jobs()  

@bot.message_handler(commands=['rocket_threat'])
def rocket_threat(message):
    bot.send_message(message.chat.id, "🧮 Стежимо для отримання інформації про ракетну загрозу.")
    start_checking_rocket_threat(message.chat.id)

@bot.message_handler(commands=['check_alerts'])
def check_alerts(message):
    asyncio.run(send_alerts_info(message.chat.id))

@bot.message_handler(commands=['site', 'website'])
def site(message):
    webbrowser.open('https://tsn.ua/tags/%D1%80%D0%B0%D0%BA%D0%B5%D1%82%D0%BD%D0%B8%D0%B9%20%D1%83%D0%B4%D0%B0%D1%80')

@bot.message_handler(commands=['shelters'])
def send_shelter_links(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(region_name, callback_data=f'shelter_{uid}') for uid, (region_name, link) in shelter_links.items()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Оберіть вашу область:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('shelter_'))
def shelter_callback(call):
    uid = int(call.data.split('_')[1])
    region_name, link = shelter_links[uid]
    bot.send_message(call.message.chat.id, f'Ось посилання на бомбосховища у {region_name}: {link}')

@bot.message_handler(commands=['account'])
def start_account(message):
    conn = sqlite3.connect('botpython.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, pass TEXT)')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привіт! Зараз тебе зареєструємо! Введіть ваше ім\'я.')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введіть пароль')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('botpython.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name, pass) VALUES (?, ?)", (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список користувачів', callback_data='users'))
    bot.send_message(message.chat.id, 'Користувач був зареєстрований👤', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'users')
def callback(call):
    conn = sqlite3.connect('botpython.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users_data = cur.fetchall()

    info = ''
    for user in users_data:
        info += f'Ім\'я: {user[1]}, пароль: {user[2]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)

@bot.message_handler(commands=['donate'])
def donate(message):
    bot.send_message(message.chat.id,
                     '💙💛 Привіт, було б дуже здорово якщо б ти задонатив для наших хлопців з 3-ОШБ які захищають нашу державу')

    file_path = '3ОШБ.jpg'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'rb') as file:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton('Перейти на сайт', url='https://ab3.army/pro-brigadu/')
            button2 = types.InlineKeyboardButton('Задонатити', url='https://supportazov.com/')
            markup.add(button1, button2)

            bot.send_photo(message.chat.id, file, reply_markup=markup)

@bot.message_handler(commands=['support'])
def support(message):
    bot.send_message(message.chat.id,
                     '💙💛 Привіт, було б дуже здорово якщо б ти задонатив на відновлення інфраструктури для моеї рідної країни')

    file_path = 'ukraine.jpg'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'rb') as file:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton('Перейти на сайт', url='https://www.pravda.com.ua/')
            button2 = types.InlineKeyboardButton('Задонатити', url='https://moveukraine.org/uk/donation/?gad_source=1&gclid=Cj0KCQjw3tCyBhDBARIsAEY0XNkK538FB7LW5I07ksWSЗc8LizdxdHlhLOvr6hsDROdY3THjIJRY8CMaAkt-EALw_wcB')
            markup.add(button1, button2)

            bot.send_photo(message.chat.id, file, reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    safety_tips = (
        "📢 Техніка безпеки під час ракетної загрози:\n"
        "1. Залишайтесь у безпечному місці, подалі від вікон.\n"
        "2. Якщо чуєте сирену або вибухи, негайно перейдіть до укриття.\n"
        "3. Завжди майте при собі документи та необхідні речі.\n"
        "4. Використовуйте засоби індивідуального захисту, якщо вони є.\n"
        "5. Слідкуйте за офіційними повідомленнями та інструкціями.\n"
        "6. Уникайте використання ліфтів під час загрози.\n"
        "7. Залишайтеся на зв'язку з близькими та рідними.\n"
    )
    bot.send_message(message.chat.id,
                     'Привіт! Якщо тобі знадобилася допомога, ось довідка:\n'
                     '/start - Почати роботу з ботом\n'
                     '/help - Отримати техніку безпеки\n'
                     '/site - Відкрити сайт новин\n'
                     '/weather - Дізнатися погоду\n'
                     '/shelters - Дізнатися про укриття в вашій області\n'
                     '/rocket_threat - Отримати інформацію про ракетну загрозу\n'
                     f'{safety_tips}')

@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Привіт! 🏙 Напишіть назву вашого міста 🏙')

admin_password = ""

@bot.message_handler(commands=['send_to_group'])
def request_group_message(message):
    bot.send_message(message.chat.id, 'Введіть пароль адміністратора:')
    bot.register_next_step_handler(message, verify_admin_password)

def verify_admin_password(message):
    if message.text.strip() == admin_password:
        bot.send_message(message.chat.id, 'Пароль вірний. Введіть повідомлення для відправки в групу:')
        bot.register_next_step_handler(message, send_group_message)
    else:
        bot.send_message(message.chat.id, 'Невірний пароль. Доступ заборонено.')

def send_group_message(message):
    if message.content_type == 'text':
        bot.send_message(group_chat_id, message.text)
    elif message.content_type == 'photo':
        bot.send_photo(group_chat_id, message.photo[-1].file_id, caption=message.caption)
    elif message.content_type == 'video':
        bot.send_video(group_chat_id, message.video.file_id, caption=message.caption)
    elif message.content_type == 'audio':
        bot.send_audio(group_chat_id, message.audio.file_id, caption=message.caption)
    else:
        bot.send_message(message.chat.id, 'Тип повідомлення не підтримується.')
    bot.send_message(message.chat.id, 'Повідомлення було відправлено в групу.')

@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id, 'Привіт! 🏙Напишіть назву вашого міста🏙')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric')
    data = json.loads(res.text)

    if res.status_code == 200:
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        feels_like = data["main"]["feels_like"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%Y-%m-%d %H:%M:%S')
        sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%Y-%m-%d %H:%M:%S')

        bot.reply_to(message,
                     f'Погода в місті: {city.title()}\n'
                     f'Температура: {temp}°C\n'
                     f'Відчувається як: {feels_like}°C\n'
                     f'Опис: {weather_desc}\n'
                     f'Вітер: {wind_speed} м/с\n'
                     f'Вологість: {humidity}%\n'
                     f'Схід сонця: {sunrise}\n'
                     f'Захід сонця: {sunset}')

        if temp < 0:
            additional_info = "На вулиці мороз! ❄️"
            image = 'snowy.jpeg'
        elif "rain" in weather_desc.lower():
            additional_info = "Зараз дощ. 🌧️"
            image = 'rainy.jpg'
        elif temp > 30:
            additional_info = "Дуже спекотно! 🌞"
            image = 'sunshine.jpg'
        else:
            additional_info = "Погода гарна! 😊"
            image = 'oblachno.jpg'

        with open(image, 'rb') as file:
            bot.send_photo(message.chat.id, file)

    else:
        bot.reply_to(message, 'Сталася помилка під час отримання даних про погоду')

async def send_alerts_info(chat_id):
    active_alerts = await alerts_client.get_active_alerts()
    alerts = active_alerts.get_all_alerts()
    alerts_by_region = {region: [] for region in regions.values()}

    for alert in alerts:
        location_title = alert.location_title
        if location_title in alerts_by_region:
            alerts_by_region[location_title].append(alert)

    message = "🚨 <b>Статус тривог по областях:</b> 🚨\n\n"
    for region, alerts in alerts_by_region.items():
        message += f"<b>{region}:</b> {'Є тривога' if alerts else 'Тривог немає'}\n"

    bot.send_message(chat_id, message, parse_mode='HTML')

@bot.message_handler()
def info(message):
    if message.text in ['Слава Україні', 'Слава Украине']:
        bot.send_message(message.chat.id, f'Героям Слава! {message.from_user.first_name} {message.from_user.last_name}')
    elif message.text in ['Слава Нації', 'Слава Нации']:
        bot.send_message(message.chat.id, 'Смерть ворогам!')
    elif message.text in ['Путин', 'Путін']:
        bot.send_message(message.chat.id, 'Хуйло!')

bot.polling(none_stop=True)