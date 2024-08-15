import subprocess
import easyocr
from firebase import firebase
import datetime
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore, db
from flask import Flask, request
import json
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import sys

# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://carboard-22172-default-rtdb.firebaseio.com/'
# })

#用車牌找停車位置
def search_location(license_num):
    return db.reference('/'+license_num+'/location').get()

#不存在車牌=False
def isExists(license_num):
    if db.reference('/'+license_num).get()==None:
        return False
    else:
        return True

#更新資料
def update_time(license_num):
    doc={
        'latest_time' : str(datetime.datetime.now())
    }
    #fdb.put('/', license_num, doc)
    ref = db.reference('/')
    ref.child(license_num).update(doc)
    
#建立初始資料，寫入資料庫(車牌、車位編號、讀取系統時間)
def ocr2db(license_num, location):
    doc={
        'license_num':license_num,
        'location' : location,
        'ocr_time' : str(datetime.datetime.now())
    }
    #fdb.put('/', license_num, doc)
    ref = db.reference('/')
    ref.child(license_num).set(doc)

# 載入 yolov5 的 detect.py 去辨識目標
def run_detect_py(img):
    #  detect.py 的路徑
    detect_py_path = 'yolov5-master/detect.py'
    #  模型的 best.pt 的路徑
    weight='d:/yolov5-master/finalproject/yolov5-master/runs/train/exp57/weights/best.pt'
    result_recognition='d:/yolov5-master/finalproject'
    #  定義指令
    command = ['python', detect_py_path,'--weights',weight,'--source', img,'--save-txt','--hide-labels','--hide-conf','--project',result_recognition]
    #  執行 python detect.py --weights weight --source img --save-txt --hide-labels --hide-conf --project result_recognition
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"An error occurred: {stderr.decode('utf-8', errors='ignore')}")
    else:
        print(f"Detection completed successfully!")

    #  加入ocr功能去取得圖片中的車牌
    istxt=img.replace('jpg','txt')
    image_path = f"prediction/{img}"
    labels_txt=img.replace('jpg','txt')
    reader = easyocr.Reader(['en'])
    if os.path.isfile(f"prediction/labels/{istxt}"):
        final_img=catch_label(image_path,labels_txt)
        result = reader.readtext(final_img,paragraph=True,text_threshold=0.8,detail=0)
    else:
        result = reader.readtext(image_path,paragraph=True,text_threshold=0.8,detail=0)
    print(result)
    #  將文字中的空白鍵刪除
    result="".join(result[0].split())
    print(result)
    return result

def catch_label(img_path,labels_txt):
    # 原始圖像
    image = cv2.imread(f"d:/yolov5-master/finalproject/{img_path}")
    # 原始圖像的寬度和高度
    image_width = image.shape[1]
    image_height = image.shape[0]
    # 車牌位置的相對比例
    labels_path=f"d:/yolov5-master/finalproject/prediction/labels/{labels_txt}"
    f =open(labels_path,'r')
    line =f.readline()
    predlab=line[1:].split()
    rel_x, rel_y, rel_w, rel_h = predlab[0], predlab[1], predlab[2], predlab[3]
    rel_x = float(rel_x)
    rel_y = float(rel_y)
    rel_w = float(rel_w)
    rel_h = float(rel_h)
    # 轉換為絕對像素值
    x = int(rel_x * image_width)
    y = int(rel_y * image_height)
    w = int(rel_w * image_width)
    h = int(rel_h * image_height)
    x=int(x-(w)/2)
    y=int(y-(h)/2)
    # 車牌位置 (x, y, w, h)
    plate_x = x
    plate_y = y
    plate_w = w
    plate_h = h
    # 使用車牌位置擷取車牌區域
    plate_region = image[plate_y:plate_y+plate_h, plate_x:plate_x+plate_w]
    # 顯示擷取的車牌區域
    return plate_region

app = Flask(__name__)
@app.route('/upload', methods=['POST'])

def upload():
    # 檢查是否有上傳的檔案
    if 'photo' in request.files:
        file = request.files['photo']

        # 獲取檔案相關資訊
        fileName = file.filename
        fileType = file.content_type
        fileSize = file.content_length
        file.save(fileName)  # 將檔案保存到指定目錄

        # 獲取其他POST數據(車位號碼)
        data = request.form['info']
        imgname=fileName
        location=data
        # 呼叫執行 detect.py,並將回傳結果設為license_num
        license_num=run_detect_py(imgname)
        ocr2db(license_num,location)
        # 在這裡處理你的數據和檔案
        return '檔案上傳成功！ 車位號碼：' + data
    
    else:
        return '請選擇一個檔案！'
    


if __name__=="__main__":
    # firebase 的初始化，並啟用 firebase
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://carboard-22172-default-rtdb.firebaseio.com/'
})
    app.run(host = "0.0.0.0", port = 5000)
    # location=15
    # a='30cbd90256617c2f.jpg'
    # license_num=run_detect_py(a)
    # ocr2db(license_num,location)