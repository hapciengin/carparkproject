import pygame
import sys
import json
import os
import cv2
import numpy as np
from mss import mss
import time
import cvzone

# Ekran genişliği ve yüksekliği
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Kutucuk boyutu
BOX_SIZE = 50

# Renkler
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Boşluklar
rows = 2
columns = 5
row_spacing = [0] * (rows - 1)
col_spacing = [0] * (columns - 1)

width, height = 48, 107

# Yeni ayarlar
val3 = 5  # Yeşil verme ihtimalini artırır
val2 = 14  # Yeşil verme ihtimalini artırır
val1 = 27  # Yeşil verme ihtimalini azaltır
windowOffsetX = 0
windowOffsetY = 0

# Alanları ve başlangıç sayılarını JSON dosyasından yüklemek için fonksiyon
def load_areas():
    with open('areas.json', 'r') as file:
        return json.load(file)

def save_counts(counts):
    with open('counts.json', 'w') as file:
        json.dump(counts, file)

def load_counts():
    if os.path.exists('counts.json'):
        try:
            with open('counts.json', 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {str(i): 0 for i in range(len(areas))}
    else:
        return {str(i): 0 for i in range(len(areas))}

def kutu_ciz(screen, pos, color):
    pygame.draw.rect(screen, color, (pos[0], pos[1], BOX_SIZE, BOX_SIZE))

def pozisyonlari_guncelle(positions):
    yeni_pozisyonlar = []
    for pos in positions:
        x_index = pos[0] // BOX_SIZE
        y_index = pos[1] // BOX_SIZE
        yeni_x = x_index * BOX_SIZE + sum(col_spacing[:x_index])
        yeni_y = y_index * BOX_SIZE + sum(row_spacing[:y_index])
        yeni_pozisyonlar.append((yeni_x, yeni_y))
    return yeni_pozisyonlar

def json_kontrol_ve_yukle(dosya_yolu, varsayilan_veri):
    if not os.path.exists(dosya_yolu):
        with open(dosya_yolu, 'w') as dosya:
            json.dump(varsayilan_veri, dosya)
        return varsayilan_veri
    else:
        try:
            with open(dosya_yolu, 'r') as dosya:
                return json.load(dosya)
        except (FileNotFoundError, json.JSONDecodeError):
            return varsayilan_veri

def check_parking_space(img, img_pro, counts, areas):
    space_counter = 0
    for i, area in enumerate(areas):
        pts1 = np.float32(area)
        pts2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
        
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgCrop = cv2.warpPerspective(img_pro, matrix, (width, height))
        count = cv2.countNonZero(imgCrop)
        
        if count < 700:  # Bu değer ayarlanabilir
            color = (0, 255, 0)
            thickness = 5
            space_counter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.polylines(img, [np.array(area, np.int32)], True, color, thickness)
        cvzone.putTextRect(img, str(count), (area[0][0], area[0][1] - 10), scale=1, thickness=2, offset=0, colorR=color)
        
        # Counts dosyasını güncelle
        counts[str(i)] = count

    cvzone.putTextRect(img, f'Free: {space_counter}/{len(areas)}', (100, 50), scale=3, thickness=5, offset=20, colorR=(0, 200, 0))
    save_counts(counts)  # Güncellenen sayıları dosyaya kaydet

def ana():
    pygame.init()
    ekran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Kutucuklar")
    saat = pygame.time.Clock()

    kaydedilen_pozisyonlar_dosyasi = "kaydedilen_pozisyonlar.json"

    counts = load_counts()
    kaydedilen_pozisyonlar = json_kontrol_ve_yukle(kaydedilen_pozisyonlar_dosyasi, [])

    secilen_indeks = -1
    bosluk_modu = False
    bosluk_tipi = "sutun"

    sct = mss()
    monitor = sct.monitors[1]

    while True:
        # Ekran görüntüsü al
        img_sct = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img_sct, cv2.COLOR_BGRA2BGR)

        # Görüntü işleme
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, val1, val2)
        img_median = cv2.medianBlur(img_threshold, val3)
        img_dilate = cv2.dilate(img_median, np.ones((3, 3), np.uint8), iterations=1)

        # Park alanlarını kontrol et
        check_parking_space(img, img_dilate, counts, areas)

        # Pygame ekranını güncelle
        ekran.fill(BLACK)
        counts = load_counts()

        if kaydedilen_pozisyonlar:
            guncel_pozisyonlar = pozisyonlari_guncelle(kaydedilen_pozisyonlar)
            for i, pos in enumerate(guncel_pozisyonlar):
                count = counts.get(str(i), 0)
                renk = GREEN if count < 700 else RED
                kutu_ciz(ekran, pos, renk)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                with open(kaydedilen_pozisyonlar_dosyasi, 'w') as dosya:
                    json.dump(kaydedilen_pozisyonlar, dosya)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    bosluk_modu = True
                    bosluk_tipi = "sutun"
                    print("Sütun boşluk ekleme modu aktif")
                elif event.key == pygame.K_r:
                    bosluk_modu = True
                    bosluk_tipi = "satir"
                    print("Satır boşluk ekleme modu aktif")
                elif event.key == pygame.K_n:
                    bosluk_modu = False
                    print("Boşluk ekleme modu kapalı")
                elif event.key == pygame.K_UP:
                    if bosluk_modu and secilen_indeks >= 0:
                        if bosluk_tipi == "satir" and secilen_indeks < len(row_spacing):
                            row_spacing[secilen_indeks] += 10
                        elif bosluk_tipi == "sutun" and secilen_indeks < len(col_spacing):
                            col_spacing[secilen_indeks] += 10
                        kaydedilen_pozisyonlar = pozisyonlari_guncelle(kaydedilen_pozisyonlar)
                elif event.key == pygame.K_DOWN:
                    if bosluk_modu and secilen_indeks >= 0:
                        if bosluk_tipi == "satir" and secilen_indeks < len(row_spacing):
                            row_spacing[secilen_indeks] = max(0, row_spacing[secilen_indeks] - 10)
                        elif bosluk_tipi == "sutun" and secilen_indeks < len(col_spacing):
                            col_spacing[secilen_indeks] = max(0, col_spacing[secilen_indeks] - 10)
                        kaydedilen_pozisyonlar = pozisyonlari_guncelle(kaydedilen_pozisyonlar)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if bosluk_modu:
                    if bosluk_tipi == "satir":
                        secilen_indeks = mouse_y // BOX_SIZE
                    elif bosluk_tipi == "sutun":
                        secilen_indeks = mouse_x // BOX_SIZE
                else:
                    if len(kaydedilen_pozisyonlar) < len(counts):
                        yeni_pozisyon = (mouse_x, mouse_y)
                        kaydedilen_pozisyonlar.append(yeni_pozisyon)
                        count = counts.get(str(len(kaydedilen_pozisyonlar) - 1), 0)
                        renk = GREEN if count < 700 else RED
                        kutu_ciz(ekran, yeni_pozisyon, renk)
                        print(f"Yeni kutucuk eklendi: {yeni_pozisyon}, renk: {'Yeşil' if renk == GREEN else 'Kırmızı'}")
                    else:
                        print("Kutucuk ekleme limiti doldu. Daha fazla kutucuk eklenemez.")

        pygame.display.flip()
        saat.tick(60)

        # 1 saniye bekle
        cv2.waitKey(1000)
        
        # Bir sonraki döngü için 1 saniye bekle
        time.sleep(1)

if __name__ == "__main__":
    areas = load_areas()
    ana()
