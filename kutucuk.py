import pygame
import sys
import json
import os

# Ekran genişliği ve yüksekliği
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Kutucuk boyutu
BOX_SIZE = 50

# Renkler
BLACK = (0, 0, 0)

# Boşluklar
rows = 2
columns = 5
row_spacing = [0] * (rows - 1)
col_spacing = [0] * (columns - 1)

# Dosya yolu
areas_file = 'areas.json'

# JSON dosyasından dikdörtgen bilgilerini yükle
def load_areas():
    try:
        with open(areas_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def kutu_ciz(screen, pos):
    pygame.draw.rect(screen, (128, 0, 128), (pos[0], pos[1], BOX_SIZE, BOX_SIZE))

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

def ana():
    pygame.init()
    ekran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Kutucuklar")
    saat = pygame.time.Clock()

    kaydedilen_pozisyonlar_dosyasi = "kaydedilen_pozisyonlar.json"
    areas = load_areas()
    max_kutucuk_sayisi = len(areas)

    kaydedilen_pozisyonlar = json_kontrol_ve_yukle(kaydedilen_pozisyonlar_dosyasi, [])

    secilen_indeks = -1
    bosluk_modu = False
    bosluk_tipi = "sutun"

    while True:
        ekran.fill(BLACK)

        if kaydedilen_pozisyonlar:
            guncel_pozisyonlar = pozisyonlari_guncelle(kaydedilen_pozisyonlar)
            for pos in guncel_pozisyonlar:
                kutu_ciz(ekran, pos)

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
                    if len(kaydedilen_pozisyonlar) < max_kutucuk_sayisi:
                        yeni_pozisyon = (mouse_x, mouse_y)
                        kaydedilen_pozisyonlar.append(yeni_pozisyon)
                        kutu_ciz(ekran, yeni_pozisyon)
                        print(f"Yeni kutucuk eklendi: {yeni_pozisyon}")
                    else:
                        print("Kutucuk ekleme limiti doldu. Daha fazla kutucuk eklenemez.")

        pygame.display.flip()
        saat.tick(60)

if __name__ == "__main__":
    ana()
