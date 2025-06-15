# ---------------------- FLAPPY BIRD - 2 OYUNCULU DETAYLI AÇIKLAMALI KOD ----------------------

import pygame  # Pygame, Python'da 2D oyun geliştirmek için kullanılan popüler bir kütüphanedir.
from pygame.locals import *  # Pygame içinde sık kullanılan sabitleri (örneğin QUIT, KEYDOWN) içe aktarır.
import random  # Rastgele sayılar üretmek için kullanılır (örneğin boruların ve bonusların yüksekliği için).

# Pygame kütüphanesi başlatılır.
pygame.init()

# FPS (frame per second) ayarı için saat nesnesi oluşturulur.
clock = pygame.time.Clock()
fps = 60  # Oyun saniyede 60 kare ile çalışacaktır.

# Ekran boyutları belirlenir.
screen_width = 864
screen_height = 936

# Oyun ekranı oluşturulur.
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird - 2 Oyunculu')  # Oyun penceresinin başlığı belirlenir.

# Skor yazıları için yazı tipi ayarlanır.
font = pygame.font.SysFont('Bauhaus 93', 60)

# Renkler tanımlanır.
white = (255, 255, 255)
yellow = (255, 255, 0)  # YENI: 2. oyuncunun skorunu ayırt etmek için sarı renk.

# Oyunla ilgili temel değişkenler tanımlanır.
ground_scroll = 0  # Zemin kayması için.
scroll_speed = 4  # Oyun içindeki tüm objelerin sola kayma hızı.
flying = False  # Oyun başlangıcında kuşlar uçmaz.
game_over = False  # Oyun bitiş durumu.
pipe_gap = 150  # Üst ve alt borular arasındaki boşluk.

pipe_frequency = 1500  # Boruların çıkış sıklığı (ms cinsinden)
last_pipe = pygame.time.get_ticks() - pipe_frequency  # Oyun başladığında hemen boru üretmek için geriden başlatılır.

bonus_frequency = 10000  # YENI: Kalkan bonusu 10 saniyede bir çıkar.
last_bonus = pygame.time.get_ticks() - bonus_frequency  # YENI: İlk bonus hemen çıksın diye zamanı geriden başlatılır.

# Oyun görselleri yüklenir.
bg = pygame.image.load('img/bg.png')  # Arka plan görseli.
ground_img = pygame.image.load('img/ground.png')  # Zemin görseli.
button_img = pygame.image.load('img/restart.png')  # Yeniden başlatma butonu.
shield_bonus_img = pygame.image.load('img/shield.png')  # YENI: Kalkan bonusu için görsel.

# Skorları yazdırmak için fonksiyon.
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Oyunu sıfırlayan fonksiyon.
def reset_game():
    pipe_group.empty()  # Tüm borular silinir.
    bonus_group.empty()  # YENI: Sahnedeki tüm bonuslar temizlenir.
    for bird in bird_group:
        bird.alive = True
        bird.score = 0
        bird.shield = False  # YENI: Kalkan pasif hale getirilir.
        bird.vel = 0
        # Oyuncuya göre kuş pozisyonu belirlenir.
        if bird.player == 1:
            bird.rect.center = [100, screen_height // 2 - 50]
        else:
            bird.rect.center = [100, screen_height // 2 + 50]
    return 0

# Kuşun görsellerini yükleyen fonksiyon.
def get_bird_images(player):
    normal, shielded = [], []
    for num in range(1, 4):
        if player == 1:
            normal_img = pygame.image.load(f"img/bird{num}.png").convert_alpha()
        else:
            normal_img = pygame.image.load(f"img/bird{num}_yellow.png").convert_alpha()
        shielded_img = pygame.image.load(f"img/bird{num}_blue.png").convert_alpha()
        normal.append(normal_img)
        shielded.append(shielded_img)
    return normal, shielded

# ---------------------- BIRD SINIFI ----------------------
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, player, control):
        super().__init__()
        self.player = player  # Oyuncu 1 mi 2 mi
        self.control = control  # Kontrol tipi (mouse ya da klavye)
        self.score = 0
        self.alive = True
        self.clicked = False
        self.vel = 0
        self.index = 0
        self.counter = 0
        self.images_normal, self.images_shielded = get_bird_images(player)  # Kuşun normal ve kalkanlı görselleri.
        self.image = self.images_normal[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.shield = False  # YENI: Başlangıçta kalkan kapalı.
        self.shield_time = 0
        self.shield_duration = 5000  # YENI: Kalkan 5 saniye boyunca aktif kalır.

    def update(self):
        if self.alive:
            # YENI: Kalkan süresi bittiyse kapatılır.
            if self.shield and pygame.time.get_ticks() - self.shield_time > self.shield_duration:
                self.shield = False

            self.vel = min(self.vel + 0.5, 8)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

            # Kontroller
            if self.control == "mouse":
                if pygame.mouse.get_pressed()[0] and not self.clicked:
                    self.clicked = True
                    self.vel = -10
                if not pygame.mouse.get_pressed()[0]:
                    self.clicked = False
            elif self.control == "keyboard":
                keys = pygame.key.get_pressed()
                if keys[K_UP] and not self.clicked:
                    self.clicked = True
                    self.vel = -10
                if not keys[K_UP]:
                    self.clicked = False

            # Kanat çırpma animasyonu
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images_normal)

            base = self.images_shielded if self.shield else self.images_normal
            self.image = pygame.transform.rotate(base[self.index], self.vel * -2)
        else:
            # Kuş öldüyse yere doğru bakar.
            self.image = pygame.transform.rotate(self.images_normal[self.index], -90)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

# ---------------------- PIPE SINIFI ----------------------
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, pos):
        super().__init__()
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        if pos == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        else:
            self.rect.topleft = [x, y + pipe_gap // 2]
        self.scored = set()  # YENI: Boruyu geçen kuşları takip eder.

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# ---------------------- SHIELDBONUS SINIFI (YENI) ----------------------
class ShieldBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = shield_bonus_img  # Bonusun görseli atanır.
        self.rect = self.image.get_rect(center=(x, y))  # Bonusun pozisyonu ayarlanır.

    def update(self):
        self.rect.x -= scroll_speed  # Bonus sola kayar.
        if self.rect.right < 0:
            self.kill()  # Ekrandan çıkarsa silinir.

# ---------------------- BUTTON SINIFI ----------------------
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))  # Butonun pozisyonu.

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()  # Mouse'un pozisyonu alınır.
        if self.rect.collidepoint(pos):  # Eğer butonun üzerindeyse
            if pygame.mouse.get_pressed()[0]:  # Ve tıklanmışsa
                action = True
        screen.blit(self.image, self.rect.topleft)
        return action

# ---------------------- ANA OYUN DÖNGÜSÜ (while run) DETAYLI AÇIKLAMALI ----------------------

# Sprite grupları oluşturulur. Bu gruplar oyun nesnelerini kolayca yönetmek için kullanılır.
pipe_group = pygame.sprite.Group()
bonus_group = pygame.sprite.Group()  # YENI: Kalkan bonuslarının bulunduğu grup
bird_group = pygame.sprite.Group()

# İki oyuncunun kuşları tanımlanır ve gruba eklenir.
player1 = Bird(100, screen_height // 2 - 50, 1, "mouse")  # Oyuncu 1 - mouse ile kontrol
player2 = Bird(100, screen_height // 2 + 50, 2, "keyboard")  # Oyuncu 2 - klavye ile kontrol
bird_group.add(player1, player2)

# Yeniden başlatma butonu tanımlanır.
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# Ana oyun döngüsü başlatılır.
run = True
while run:
    clock.tick(fps)  # Oyun her saniye 60 kez güncellenir (FPS).

    screen.blit(bg, (0, 0))  # Arka plan çizilir.
    pipe_group.draw(screen)  # Tüm borular çizilir.
    bonus_group.draw(screen)  # YENI: Tüm bonuslar çizilir.
    bird_group.draw(screen)  # Kuşlar çizilir.
    bird_group.update()  # Kuşların hareketi ve animasyonu güncellenir.

    screen.blit(ground_img, (ground_scroll, 768))  # Zemin çizilir.

    # Skor kontrolü yapılır (sadece alt borular üzerinden geçince).
    for pipe in pipe_group:
        if pipe.position == -1:
            for bird in bird_group:
                if bird.alive and bird.rect.left > pipe.rect.right and bird not in pipe.scored:
                    bird.score += 1
                    pipe.scored.add(bird)

    # Skorlar ekrana yazdırılır.
    for bird in bird_group:
        draw_text(str(bird.score), font, white if bird.player == 1 else yellow,
                  50 if bird.player == 1 else screen_width - 100, 20)

    # YENI: Bonuslara çarpma kontrolü (kalkan alma)
    for bird in bird_group:
        if bird.alive and pygame.sprite.spritecollide(bird, bonus_group, True):
            bird.shield = True  # Kuşa kalkan verilir.
            bird.shield_time = pygame.time.get_ticks()  # Kalkanın verildiği zaman kaydedilir.

    # Çarpışma kontrolleri yapılır.
    for bird in bird_group:
        if bird.alive:
            if bird.rect.top < 0 or pygame.sprite.spritecollide(bird, pipe_group, False):
                if bird.shield:
                    # YENI: Kuşun kalkanı varsa boruya çarptığında boru yok edilir.
                    for pipe in pipe_group:
                        if bird.rect.colliderect(pipe.rect):
                            pipe.kill()
                    bird.shield = False  # Kalkan bir kez kullanılınca yok olur.
                else:
                    bird.alive = False  # Kuş ölür
            if bird.rect.bottom >= 768:
                bird.alive = False  # Zemine çarpan kuş ölür.

    # Tüm kuşlar öldüyse oyun biter.
    if all(not bird.alive for bird in bird_group):
        game_over = True

    # Oyun başladıysa ve bitmediyse
    if flying and not game_over:
        time_now = pygame.time.get_ticks()

        # Boruların oluşturulması
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, -1)
            top_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # YENI: Bonus üretimi
        if time_now - last_bonus > bonus_frequency:
            valid_bonus = False
            attempts = 0
            temp_bonus = None
            while not valid_bonus and attempts < 10:
                bonus_y = random.randint(100, 600)
                temp_bonus = ShieldBonus(screen_width, bonus_y)
                valid_bonus = True
                for pipe in pipe_group:
                    if temp_bonus.rect.colliderect(pipe.rect):  # Bonus boruyla çakışıyorsa iptal edilir.
                        valid_bonus = False
                        break
                attempts += 1
            if temp_bonus:
                bonus_group.add(temp_bonus)  # Bonus sahneye eklenir.
            last_bonus = time_now  # Bonus zamanı sıfırlanır.

        # Tüm objeler güncellenir.
        pipe_group.update()
        bonus_group.update()

        # Zemin hareketi sağlanır.
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    # Oyun bittiyse ve butona tıklanırsa yeniden başlatılır.
    if game_over:
        if button.draw():
            game_over = False
            reset_game()
            flying = False

    # Oyun olayları (tıklama, tuş basımı) kontrol edilir.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  # Pencere kapatılırsa oyun döngüsü sona erer.
        if not flying and not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                flying = True  # Fare tıklaması ile oyun başlar.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                flying = True  # Klavye ile de oyun başlatılabilir.

    # Ekran güncellenir.
    pygame.display.update()

# Oyun bittiğinde Pygame kapatılır.
pygame.quit()
