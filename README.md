# License-plate-recognition-system
## 工具
* Raspberry Pi4
* 超音波感測器
* pi camera(or 其他camera都可以)
* yolov5(在yolov5_README.md中有git yolov5的相關資訊)
* easyocr
* firebase(這邊可以去firebase建資料庫後有有金鑰)
* flask
## 系統描述
此系統主要是分為client端以及server端，並使用flask來去溝通。
在client端是run在Raspberry Pi4上，主要做的行為是拍攝車子的倒車畫面，透過超音波感測器去偵測車尾以及超音波感測器的距離，到一定距離的時候會去拍攝車尾的畫面，並將拍到的圖片及車位回傳這server端去做辨識。
在server端是run在桌機上，主要做的行為是透過yolov5去辨識client端傳過來的車尾圖片，先去偵測車牌，在近一步去擷取偵測到的車牌，並實施OCR技術將車牌的文字讀取下來，接著server端在將車牌以及client端傳過來的車位，上傳到firebase資料庫。
這邊還有做一個簡單的前端畫面來查詢車位，在此網頁上只要輸入自己的車牌號碼，系統就會去firebase中查詢，並自動回覆車位給使用者。

## 系統功能
* client：偵測距離(超音波感測器)、拍攝照片(camera)
* server：偵測車牌(yolov5)、OCR技術(easyocr)
* database：firebase
* 後端架構：flask
## 資料集
下載處：https://drive.google.com/drive/folders/1JIXJYJIlau_wAgXWVpJqVMvntiyCwFem?usp=sharing
