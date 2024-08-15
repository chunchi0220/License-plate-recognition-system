import os
import time
import picamera
import RPi.GPIO as GPIO
import requests

# 設置超音波感測器的腳位
TRIG_PIN = 19
ECHO_PIN = 21

# 設置拍照保存路徑
SAVE_PATH = '/home/n96111095/final_project/image'  # 保存照片的文件夾路徑

# 目標電腦的IP地址和端口
TARGET_IP = '140.116.226.210'  # 目標電腦的實際IP地址
TARGET_PORT = 5000  # 目標電腦的實際端口號

# camera的基本設定
def initialize_camera():
    camera = picamera.PiCamera()
    # 可跟根據需要設置鏡頭參數，例如分辨率、旋轉等
    camera.rotation = 180
    return camera

# GPIO的初始化
def initialize_ultrasonic_sensor():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

#偵測並計算距離
def measure_distance():
    # 發送超音波訊號
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # 等待接收超音波返回訊號
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # 計算距離
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

# 擷取照片
def capture_photo(camera,count):
    # 构建照片文件名
    # timestamp = time.strftime("%Y%m%d_%H%M%S")
    # file_name = f"photo_{timestamp}.jpg"
    
    file_name = f"img{count}.jpg"

    file_path = os.path.join(SAVE_PATH, file_name)

    # 拍攝照片並保存
    camera.capture(file_path)
    print(f"Captured photo: {file_name}")

    return file_path

# 發送照片和信息(車位)到目標電腦
def send_photo_and_info(photo_path, info):
    url = f"http://{TARGET_IP}:{TARGET_PORT}/upload"  # 目標電腦的實際URL

    files = {'photo': open(photo_path, 'rb')}
    data = {'info': info}

    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        # result = response.json()
        print(response.text)
    else:
        print('請求發送失敗')


def main():
    # 初始化camera和超音波感測器
    camera = initialize_camera()
    initialize_ultrasonic_sensor()

    count = 1

    try:
        while True:
            distance = measure_distance()
            print(f"Distance: {distance} cm")
            
            if distance < 10:  # 超音波距離小於10厘米時拍照
                photo_path = capture_photo(camera,count)
                info = 'A037'
                count += 1

                send_photo_and_info(photo_path, info)

            
            time.sleep(1)  # 每隔1秒進行一次距離測量

    finally:
        # 釋放資源
        camera.close()
        GPIO.cleanup()

if __name__ == '__main__':
    main()