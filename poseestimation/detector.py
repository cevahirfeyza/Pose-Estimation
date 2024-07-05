import cv2
import mediapipe as mp
import time
import math

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Yeni dosya yolu
import os

video_path = 'C:/Users/feyza/Desktop/poseestimation/video/video1.mp4'
if os.path.exists(video_path):
    print("Video dosyası mevcut.")
else:
    print("Video dosyası bulunamadı.")



cap = cv2.VideoCapture(video_path)
pTime = 0
threshold_angle = 15 # Eğilme kontrolü için eşik değeri
threshold_distance = 50 # Ayak mesafesi kontrolü için eşik değeri
threshold_speed = 8 # Hız kontrolü için eşik değeri
threshold_jogging_height = 0.2 # Koşu adımı kontrolü için eşik değeri
threshold_stair_height = 0.01 # Merdiven inme kontrolü için eşik değeri
threshold_squat_height = 0.05 # Çömelmek kontrolü için eşik değeri

# Önceki ayak konumları
prev_left_ankle = None
prev_right_ankle = None

# Eklenen değişkenler
stair_counter = 0
show_stair_text = False
stair_text_duration = 2
stair_text_start_time = 0
frames_since_stair_detection = 0

while True:
    start_time = time.time()

    success, img = cap.read()
    if not success:
        print("Görüntü okuma başarısız!")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    # Eğer vücut konumu tespit edilmişse
    if results.pose_landmarks:
        # Vücut konumlarını çizim üzerine işle
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

        # Sol ve sağ ayak konumlarını al
        left_ankle = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_ANKLE]
        right_ankle = results.pose_landmarks.landmark[mpPose.PoseLandmark.RIGHT_ANKLE]

        # Önceki karede ayak konumları mevcutsa ve merdiven metni gösterilmiyorsa ve 120 saniyeden fazla süredir merdiven metni gösterilmiyorsa
        if prev_left_ankle is not None and not show_stair_text and (time.time() - stair_text_start_time > 120):
            # Sol ve sağ ayak hızlarını hesapla
            left_ankle_speed = left_ankle.x - prev_left_ankle.x
            right_ankle_speed = right_ankle.x - prev_right_ankle.x
            average_ankle_speed = (left_ankle_speed + right_ankle_speed) / 2

            # Ortalama ayak hızına göre durumu değerlendir
            if average_ankle_speed > threshold_speed:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Hizli Yuruyor", (30, 200), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 255), 5)
            elif average_ankle_speed < -threshold_speed:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Yavas Yuruyor", (30, 200), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 255), 5)
            else:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Normal Yuruyor", (30, 200), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)

        # Vücut açısı için eşik değeri
        threshold_body_angle = 180

        # Sol kalça ve sol ayak konumlarını al
        left_hip = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HIP]
        left_ankle = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_ANKLE]

        # Ayak ve kalça arasındaki açıyı hesapla
        angle_radians = math.atan2(left_ankle.y - left_hip.y, left_ankle.x - left_hip.x)
        angle_degrees = abs(math.degrees(angle_radians))




        # Önceki ayak konumlarını güncelle
        prev_left_ankle = left_ankle
        prev_right_ankle = right_ankle

        # Sol ve sağ topuk konumlarını elde et
        left_heel = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HEEL]
        right_heel = results.pose_landmarks.landmark[mpPose.PoseLandmark.RIGHT_HEEL]

        # Sol ve sağ ayak bileği yüksekliklerini hesapla
        left_ankle_height = left_ankle.y * img.shape[0] - left_heel.y * img.shape[0]
        right_ankle_height = right_ankle.y * img.shape[0] - right_heel.y * img.shape[0]

        # Eğer sol veya sağ ayak bileği belirli bir yükseklik eşiğinin üzerindeyse
        if left_ankle_height > threshold_jogging_height or right_ankle_height > threshold_jogging_height:
            # Ayak hızına göre koşu durumunu değerlendir
            if average_ankle_speed > threshold_speed:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Hizli Kosar Adim", (30, 400), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), 5)
            elif average_ankle_speed < -threshold_speed:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Yavas Kosar Adim", (30, 400), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), 5)
            else:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Normal Kosar Adim", (30, 400), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 165, 0), 5)

        # Sol kalça ve sol ayak bileği arasındaki dikey mesafeyi hesapla
        hip_knee_distance = left_ankle.y * img.shape[0] - results.pose_landmarks.landmark[
            mpPose.PoseLandmark.LEFT_HIP].y * img.shape[0]

        # Sağ ayak bileği ve sol ayak bileği arasındaki dikey mesafeyi hesapla
        knee_ankle_distance = right_ankle.y * img.shape[0] - left_ankle.y * img.shape[0]

        # Eğer her iki mesafe de belirli bir eşik değerinden büyükse
        if hip_knee_distance > threshold_distance and knee_ankle_distance > threshold_distance:
            # Sol kalça ve sol ayak bileği arasındaki açıyı hesapla
            angle_radians = math.atan2(left_ankle.y - results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HIP].y,
                                       left_ankle.x - results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HIP].x)
            angle_degrees = math.degrees(angle_radians)

            # Eğer açı belirli bir eşik değerinden büyükse
            if abs(angle_degrees) > threshold_angle:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Egilmis", (30, 350), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)
            else:
                font_size = int(2 * (img.shape[0] / 600))
                cv2.putText(img, "Ayakta", (30, 300), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)
        else:
            # Eğer mesafelerden biri belirli bir eşik değerinden küçükse
            font_size = int(2 * (img.shape[0] / 600))
            cv2.putText(img, "Ayakta", (30, 300), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)


        # Sol ve sağ topuk noktalarını elde et
        left_heel = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HEEL]
        right_heel = results.pose_landmarks.landmark[mpPose.PoseLandmark.RIGHT_HEEL]

        # Sol ve sağ ayak bileği yüksekliklerini hesapla
        left_ankle_height = left_ankle.y * img.shape[0] - left_heel.y * img.shape[0]
        right_ankle_height = right_ankle.y * img.shape[0] - right_heel.y * img.shape[0]

        # Eğer sol veya sağ ayak bileği belirli bir eşik değerinden yüksekse
        if left_ankle_height > threshold_stair_height or right_ankle_height > threshold_stair_height:
            # Eğer ortalama ayak bileği hızı belirli bir eşik değerinden küçükse
            if average_ankle_speed < -threshold_speed:
                stair_text = "Hizli Merdiven Iniyor"
                stair_counter += 1
                show_stair_text = True
                stair_text_start_time = time.time()
            elif average_ankle_speed > -threshold_speed:
                stair_text = "Yavas Merdiven Iniyor"
                stair_counter += 1
                show_stair_text = True
                stair_text_start_time = time.time()
            else:
                # Eğer merdiven bilgisi zaten gösterilmiyorsa
                if not show_stair_text:
                    font_size = int(2 * (img.shape[0] / 600))
                    cv2.putText(img, "Normal Yuruyor", (30, 200), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)
        else:
            # Eğer sol veya sağ ayak bileği belirli bir eşik değerinden yüksek değilse
            font_size = int(2 * (img.shape[0] / 600))
            cv2.putText(img, "Normal Yuruyor", (30, 200), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)

        # Eğer merdiven metni gösteriliyorsa
        if show_stair_text:
            # Merdiven tespitinden bu yana geçen çerçeve sayısını sıfırla
            frames_since_stair_detection = 0

            # Yazı tipi boyutunu belirle
            font_size = int(2 * (img.shape[0] / 600))

            # Merdiven metnini görüntü üzerine yerleştir
            cv2.putText(img, stair_text, (30, 600), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), 5)

            # Merdiven metni gösterilme süresi boyunca geçen süreyi hesapla
            elapsed_time_stair_text = time.time() - stair_text_start_time

            # Eğer belirli bir süre geçtiyse
            if elapsed_time_stair_text >= stair_text_duration:
                # Merdiven metni gösterme flag'ini kapat
                show_stair_text = False

                # Çerçeve sayacını sıfırla
                stair_counter = 0

        # Sol ve sağ omuz, sol ve sağ kalça noktalarını elde et
        left_shoulder = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = results.pose_landmarks.landmark[mpPose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HIP]
        right_hip = results.pose_landmarks.landmark[mpPose.PoseLandmark.RIGHT_HIP]

        # Sol omuzdan sağ omuza, sol kalçadan sağ kalça açısını hesapla
        angle_radians = math.atan2(right_shoulder.y - left_shoulder.y, right_shoulder.x - left_shoulder.x) - math.atan2(
            right_hip.y - left_hip.y, right_hip.x - left_hip.x)
        angle_degrees = abs(math.degrees(angle_radians))


        # Hızlı çömelme durumu kontrolü
        left_hip = results.pose_landmarks.landmark[mpPose.PoseLandmark.LEFT_HIP]
        right_hip = results.pose_landmarks.landmark[mpPose.PoseLandmark.RIGHT_HIP]

        # Kalçaların yerden olan minimum mesafesini hesapla
        hip_distance_to_ground = min(left_hip.y, right_hip.y) * img.shape[0]

        # Eğer kalçaların yerden olan mesafesi belirtilen eşik değerinden küçükse
        if hip_distance_to_ground < threshold_squat_height:
            # Yazı tipi boyutunu belirle
            font_size = int(2 * (img.shape[0] / 600))

            # Eğer ortalama ayak hızı belirtilen eşik hızdan küçükse
            if average_ankle_speed < -threshold_speed:
                # Eğer hızlı çömelme durumu ise ekrana "Hızlı Çömeliyor" mesajını yazdır
                cv2.putText(img, "Hizli Çömeliyor", (30, 500), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 0, 0), 5)
            else:
                # Eğer yavaş çömelme durumu ise ekrana "Yavasca Çömeliyor" mesajını yazdır
                cv2.putText(img, "Yavasca Çömeliyor", (30, 500), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 165, 0), 5)

        # Yavaşça çömelme durumu kontrolü
        hip_distance_to_ground = min(left_hip.y, right_hip.y) * img.shape[0]

        # Eğer kalçaların yerden olan mesafesi belirtilen eşik değerinden küçükse
        if hip_distance_to_ground < threshold_squat_height:
            # Yazı tipi boyutunu belirle
            font_size = int(2 * (img.shape[0] / 600))

            # Eğer yavaş çömelme durumu ise ekrana "Yavasca Çömeliyor" mesajını yazdır
            cv2.putText(img, "Yavasca Çömeliyor", (30, 500), cv2.FONT_HERSHEY_PLAIN, font_size, (255, 165, 0), 5)

        # Aksi durumda (eğer kişi yerde uzanıyorsa)
        else:
            # Yazı tipi boyutunu belirle
            font_size = int(2 * (img.shape[0] / 600))



            # Yazı tipi boyutunu belirle (bu satırın tekrarı, fakat isteğe bağlı olarak farklı mesajlar ekleyebilirsiniz)
            font_size = int(2 * (img.shape[0] / 600))

            # Ekrana "Ayakta" mesajını yazdır
            cv2.putText(img, "Ayakta", (30, 300), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 255, 0), 5)

    # Eğer merdiven metni gösteriliyorsa
    if show_stair_text:
        # Merdiven metninin gösterildiği kare sayısını artır
        frames_since_stair_detection += 1

        # Merdiven metninin belirli bir süre boyunca gösterilip gösterilmediğini kontrol et
        if frames_since_stair_detection >= 600:
            # Merdiven metni gösterimini kapat ve kare sayısını sıfırla
            show_stair_text = False
            frames_since_stair_detection = 0

    # Geçen süreyi hesapla ve konsola yazdır
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Toplam geçen süreyi hesapla
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Yazı tipi boyutunu belirle
    font_size = int(2 * (img.shape[0] / 600))

    # Geçen süreyi ekrana yazdır
    cv2.putText(img, f"Gecen Sure: {elapsed_time:.5f} saniye", (10, 500), cv2.FONT_HERSHEY_PLAIN, font_size,
                (0, 255, 255), 4)

    # İmajı pencerede göster
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()