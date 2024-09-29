import cv2 #Thư viện OpenCV
import Jetson.GPIO as GPIO
import mediapipe as mp #Thư viện phát hiện cử chỉ tay
import numpy as np
import math 
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)  # led

# mp.solutions các giải pháp trong thư viện Mediapipe
mp_hands = mp.solutions.hands #hands hàm gọi giải pháp theo dõi tay
mp_drawing = mp.solutions.drawing_utils #drawing_utils đc dùng để vẽ các landmarks
#mp_drawing_style = mp.solutions.drawing_styles

hands = mp_hands.Hands(max_num_hands = 1, min_detection_confidence = 0.7)
#Hands là một lớp trong module hands, được thiết kế để xử lý việc phát hiện bàn tay và các điểm đặc trưng của bàn tay.
#max_num_hands = 1 chỉ phát hiện và theo dõi 1 bàn tay trong 1 khung hình
# min_detection_confidence = 0.7 Với độ tin cậy là 70%

vid_cap = cv2.VideoCapture(0)# Mở webcam
input_pin = 33

while True:
    ret, image = vid_cap.read() #Đọc khung hình từ webcam
    #ret là một biến boolean cho biết liệu khung hình có được đọc thành công hay không
    #image là khung hình đã đọc được

    if not ret: #khung hình ko đc đọc
        print("Không thể nhận diện khung hình từ webcam")
        break
    
    lat_anh = cv2.flip(image, 1) # Lật khung hình theo trục dọc

    black_image = cv2.bitwise_not(lat_anh) #Hàm bitwise_not biến đổi các giá trị ngược lại trong không gian 8-bit
    black_image = cv2.subtract(black_image, black_image) #Hàm subtract lấy giá trị của từng điểm ảnh của 2 ảnh từ đi
    #Nếu là image1 và image2 cùng 1 ảnh kết quả là một ảnh toàn màu đen.

    image_rgb = cv2.cvtColor(lat_anh, cv2.COLOR_BGR2RGB) # Chuyển đổi khung hình từ BGR sang RGB
    results = hands.process(image_rgb) # Xử lý khung hình để phát hiện bàn tay

    if results.multi_hand_landmarks: # Nếu phát hiện thấy bàn tay
        for hand in results.multi_hand_landmarks: # Duyệt qua từng bàn tay được phát hiện
            mp_drawing.draw_landmarks(black_image, hand, mp_hands.HAND_CONNECTIONS)
            #draw_landmarks là module drawing_utils của MediaPipe. 
            #cung cấp các hàm để vẽ các điểm đặc trưng (landmarks) và các kết nối giữa chúng lên hình ảnh

            for i,lm in enumerate(hand.landmark): # Duyệt qua từng điểm đặc trưng của bàn tay
                if i == 4:# Điểm đặc trưng số 4 (đầu ngón tay cái)
                    h,w,c = image_rgb.shape # Lấy kích thước khung hình
                    cx,cy = int(lm.x*w),int(lm.y*h) # Tính tọa độ điểm đặc trưng trên khung hình
                    p1 = (cx,cy) # Lưu tọa độ điểm đặc trưng
                    cv2.circle(image_rgb,(cx,cy),10,[0,0,255],cv2.FILLED) # Vẽ hình tròn tại điểm đặc trưng
if i == 8: # Điểm đặc trưng số 8 (đầu ngón tay trỏ)
                    cx,cy = int(lm.x*w), int(lm.y*h) # Tính tọa độ điểm đặc trưng trên khung hình
                    p2 = (cx,cy) # Lưu tọa độ điểm đặc trưng
                    cv2.circle(image_rgb,(cx,cy),10,[0,0,255],cv2.FILLED) # Vẽ hình tròn tại điểm đặc trưng
        cv2.line(image_rgb,p1,p2,[255,0,0],2) # Vẽ đường thẳng nối giữa hai điểm đặc trưng

        distance = math.sqrt((p2[0] - p1[0])**2 +(p2[1] - p1[1])**2) # Tính khoảng cách giữa hai điểm
        if distance < 50: # Nếu khoảng cách nhỏ hơn 50
            GPIO.output (33, GPIO.LOW)
            time.sleep(0.5)
            print('tat den')
        else: # Nếu khoảng cách lớn hơn hoặc bằng 50
            GPIO.output (33, GPIO.HIGH)
            time.sleep(0.5)
            print('bat den')

    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR) # Chuyển đổi khung hình từ RGB sang BGR
    cv2.imshow('Hand', black_image) # Hiển thị khung hình
    if cv2.waitKey(1)&0xFF == 27: # Kiểm tra nếu phím 'esc' được nhấn
        break
# Giải phóng webcam và đóng các cửa sổ
vid_cap.release()
cv2.destroyAllWindows()