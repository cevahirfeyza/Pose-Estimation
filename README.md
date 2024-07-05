Pose Estimation ile Hareket Analizi

Bu proje, insan hareketlerini analiz etmek için Pose Estimation (poz tahmini) kullanır. Mediapipe kütüphanesi ve OpenCV ile birlikte kullanılarak geliştirilmiştir. Proje, bir video dosyasından canlı olarak insan hareketlerini izleyerek belirli hareketleri tanımlar ve ekrana yazdırır.

Özellikler
Eğilme Kontrolü: Kullanıcının eğilip eğilmediğini tespit eder.
Ayak Mesafesi Kontrolü: Ayakların belirli bir mesafeden uzak olup olmadığını kontrol eder.
Hız Kontrolü: Yürüme hızını değerlendirir.
Koşu Adımı Kontrolü: Koşu adımlarını tespit eder.
Merdiven İnme Kontrolü: Merdiven inerken yapılan hareketleri tespit eder.
Çömelmek Kontrolü: Çömelme hareketlerini değerlendirir.
Kullanım
Gereksinimler

Python 3.x
OpenCV (pip install opencv-python)
Mediapipe (pip install mediapipe)
Video Dosyası

video1.mp4 adında bir video dosyası proje kök dizininde olmalıdır.

Kodu çalıştırmak için Anaconda veya Python sanal ortamında python pose_estimation.py komutunu kullanın.

Q tuşuna basarak uygulamayı kapatın.


Notlar
Projenin daha doğru sonuçlar vermesi için, doğru konumlandırılmış ve net bir video kaynağı kullanın.
Eğer hareket tanımı belirlenen eşik değerlerine göre aşılırsa, ilgili mesajlar ekranda görüntülenecektir.
