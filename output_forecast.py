# インストールした discord.py を読み込む
from discord.ext import tasks
import discord
import cv2
import datetime
import json
import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 自分のBotのアクセストークンに置き換えてください
TOKEN = 'YOUR_TOKEN'

def choose_number(month, day):
    csv_data = pd.read_csv('number/number.csv', encoding='utf-8')
    if month//10 == 1:
        num1='number/1.png'
    else:
        num1='number/space.png'
    num2 = csv_data.loc[month%10, 'file']
    num3 = 'number/slash.png'
    if day//10 != 0:
        num4 = csv_data.loc[day//10, 'file']
    else:
        num4 = 'number/space.png'
    num5 = csv_data.loc[day%10, 'file']
    day_array = [num1, num2, num3, num4, num5]
    return day_array

# 接続に必要なオブジェクトを生成
client = discord.Client()
channel_sent = None
# 起動時に動作する処理

#@tasks.loop(minutes=1)
@tasks.loop(hours=24)
async def send_message():
    url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/010000.json'
    csv_data = pd.read_csv('publishingOffice.csv', encoding='utf-8')
    csv_data2 = pd.read_csv('code_to_pic.csv', encoding='utf-8')
    print(csv_data2.loc[1, 'file'])
    #print(csv_data)
    Codes = np.zeros(13)
    #print(office)
    res = urllib.request.urlopen(url)
    # json_loads() でPythonオブジェクトに変換
    data = json.loads(res.read().decode('utf-8'))
    dt_now = datetime.datetime.now()
    dt_hour = dt_now.hour

    for i in range(13):
        print(csv_data.loc[i, 'Location'])
        if dt_hour<13 and dt_hour>5:
            print(data[csv_data.loc[i, 'Number']]["srf"]["timeSeries"][0]["areas"]["weatherCodes"][0])
            Codes[i]=data[csv_data.loc[i, 'Number']]["srf"]["timeSeries"][0]["areas"]["weatherCodes"][0]
        else:         
            print(data[csv_data.loc[i, 'Number']]["srf"]["timeSeries"][0]["areas"]["weatherCodes"][1])
            Codes[i]=data[csv_data.loc[i, 'Number']]["srf"]["timeSeries"][0]["areas"]["weatherCodes"][1]
        print( )
    list_files = []
    list_imgs = []
    img_japan = cv2.imread('1.png')
    for i in range(len(Codes)):
        temp_code = Codes[i]
        for j in range(118):
            if csv_data2.loc[j, 'code'] == temp_code:
                list_files.append(csv_data2.loc[j, 'file'])
    for i in range(13):
        img_tmp=cv2.imread(list_files[i])
        height, width = img_tmp.shape[:2]
        X = csv_data.loc[i,'x']
        Y = csv_data.loc[i,'y']
        img_japan[Y:Y+height, X:X+width] = img_tmp
    # 日付書き足し機能
    if dt_hour>=13:
        img_day=cv2.imread('number/tomorrow.png')
        height, width = img_day.shape[:2]
        img_japan[0:height, 20:width+20] = img_day
        dt_tomorrow = dt_now + datetime.timedelta(days=1)
        day_array = choose_number(dt_tomorrow.month ,dt_tomorrow.day)
        # print(dt_tomorrow.date)
        for j in range(5):
            file = day_array[j]
            img_num = cv2.imread(file)
            height_n, width_n = img_num.shape[:2]
            img_japan[80:height_n+80, j*40:width_n+j*40] = img_num
    else:
        img_day=cv2.imread('number/today.png')
        height, width = img_day.shape[:2]
        img_japan[0:height, 20:width+20] = img_day
        # print(dt_now.date)   
        day_array = choose_number(dt_now.month ,dt_now.day)
        for j in range(5):
            file = day_array[j]
            img_num = cv2.imread(file)
            height_n, width_n = img_num.shape[:2]
            img_japan[80:height_n+80, j*40:width_n+j*40] = img_num

    cv2.imwrite('new.jpg',img_japan)

    print(list_files)

    await channel_sent.send(file=discord.File('new.jpg'))

    

@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    global channel_sent 
    channel_sent = client.get_channel("YOUR_CHANNEL_ID") #お天気チャンネルのIDを入力して下さい。

    send_message.start() #定期実行するメソッドの後ろに.start()をつける

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)

