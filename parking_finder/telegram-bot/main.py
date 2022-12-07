import telebot
import io
import os
# import csv
import numpy as np
import cv2
from flask import Flask, request
from telebot import types

from PIL import Image
from parking_finder import APP_ROOT
from parking_finder.detection.predictor import SpotPredictor

token = '5678611388:AAEUlVDQKe0IwVvIwf71TdI2LurgK5G0VfQ'
bot = telebot.TeleBot(token)
spot_predictor = SpotPredictor()
app = Flask(__name__)
grid = np.genfromtxt(APP_ROOT / 'detection' / 'grid.csv', delimiter='\t')
# grid = csv.reader()
# grid = []
# with open('grid.csv', 'r') as f:
#     for line in f:
#         grid.append(list(map(int, line.strip().split('\t'))))
# grid = np.array(grid)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, это бот 4Parking!')

    markup = types.ReplyKeyboardMarkup()
    buttonA = types.KeyboardButton('Сколько свободных мест?')

    markup.row(buttonA)
    # markup.row(buttonC)

    # bot.send_message(message.chat.id, 'It works!', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Сколько свободных мест?':
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        cap = cv2.VideoCapture('rtsp://admin1:admin1@95.165.88.221:25000/stream1')# rtsp://admin1:admin1@192.168.1.5:554/stream1')

        ret, frame = cap.read()
        n, m, _ = frame.shape
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)[280:820, m // 4: 3 * m // 4, :]

        img = np.asarray(img)
        is_available, d_coords = spot_predictor.frame_processing(img, grid)

        bot.send_message(message.from_user.id, f"Свободных мест: {np.sum(is_available)}")
        # for coord in d_coords:
        #     cv2.rectangle(img, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)
        # pass
    else:
        bot.send_message(message.from_user.id, "Привет, это бот 4Parking!")


# @bot.message_handler(content_types= ["photo"])
# def verifyUser(message):
#     print ("Got photo")
#     percent = userFace.verify(message.photo, config.photoToCompare)
#     bot.send_message(message.chat.id, "Percentage: " + str(percent))
@bot.message_handler(content_types=["photo"])
def photo(message):
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    img = np.asarray(Image.open(io.BytesIO(downloaded_file)))

    is_available, d_coords = spot_predictor.frame_processing(img, grid)

    # bot.send_message(message.from_user.id, f"{is_available}, {d_coords}")

    bot.send_message(message.from_user.id, f"Свободных мест: {np.sum(is_available)}")


@app.route("/" + token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200



    # with open("image.jpg", 'wb') as new_file:
    #     new_file.write(downloaded_file)

# def getData(json_string):
#     updates = telebot.types.Update.de_json(json_string)
#     bot.process_new_updates([updates])

# app.run()
# bot.remove_webhook()
# bot.set_webhook('http://0.0.0.0:5000/' + token)
# app.run()
bot.polling(none_stop=True, interval=0)
