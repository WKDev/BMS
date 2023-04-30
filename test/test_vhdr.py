import cv2
import numpy as np
CAMERA_IP = "169.254.202.73"
OVERLAY = "on"
ENCODING = "mjpg"
url = f"rtsp://{CAMERA_IP}/{ENCODING}?overlay={OVERLAY}"

cap = cv2.VideoCapture(url)


# 톤 조절 커브 생성
while True:
    good, frame = cap.read()
    origin = frame.copy()
    ldr_img = frame
    num_curves = 4
    curves = []
    for i in range(num_curves):
        curve = np.zeros((256,), dtype=np.float32)
        for j in range(256):
            curve[j] = 255.0 * pow(float(j) / 255.0, float(i + 1) / num_curves)
        curves.append(curve)

    # 톤 컨버전 이미지 생성
    images = []
    for curve in curves:
        image = cv2.LUT(ldr_img, curve)
        images.append(image)

    # 이미지 가중 평균 계산
    num_images = len(images)
    sum_image = np.zeros(images[0].shape, dtype=np.float32)
    for i in range(num_images):
        sum_image += images[i].astype(np.float32)
    hdr_img = sum_image / float(num_images)

    # VHDR 이미지 저장
    # cv2.imwrite('output_image.jpg', hdr_img)
    cv2.imshow("vhdr", hdr_img)
    cv2.imshow("origin", origin)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()