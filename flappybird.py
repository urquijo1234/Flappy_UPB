import pygame
import random
import os
import asyncio

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy UPB")

# Cargar imágenes
background_img = pygame.image.load("assets/J PIXEL.jpg")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

bird_img = pygame.image.load("assets/bird.png")
bird_img = pygame.transform.scale(bird_img, (40, 40))

pipe_up_img = pygame.image.load("assets/pipeup.png")
pipe_down_img = pygame.image.load("assets/pipedown.png")
point_sound = pygame.mixer.Sound("assets/point.mp3")
jump_sound = pygame.mixer.Sound("assets/jump.mp3")
death_sound = pygame.mixer.Sound("assets/death.mp3") 
pipe_width = 52
pipe_gap = 280
pipe_speed = 3 # velocidad base

# Variables del juego
gravity = 0.25
bird_y = HEIGHT // 2
bird_x = 50
velocity = 0
prev_bird_y = bird_y
tubes = []
score = 0
high_score = 0
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 48)  # Fuente más grande para el título
small_font = pygame.font.Font(None, 28)  # Fuente más pequeña
clock = pygame.time.Clock()
fps = 30
response_factor = 0.01

game_state = "menu"  # Estados: "menu", "playing", "game_over"

# Cargar high score desde archivo si existe
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            try:
                return int(file.read())
            except:
                return 0
    return 0

# Guardar high score en archivo
def save_high_score(score):
    with open("highscore.txt", "w") as file:
        file.write(str(score))

# Cargar high score al inicio
high_score = load_high_score()

def calculate_slope():
    global prev_bird_y, bird_y
    delta_t = 1 / fps
    delta_y = bird_y - prev_bird_y
    m = delta_y / delta_t
    prev_bird_y = bird_y
    return abs(m)

def create_tube():
    m = calculate_slope()
    neutral_y = HEIGHT // 2
    noise = random.randint(-50, 50)  # Ruido controlado
    responsive_y = neutral_y - int(m * response_factor) + noise
    min_gap_y = 100
    max_gap_y = HEIGHT - pipe_gap - 100
    gap_y = max(min_gap_y, min(max_gap_y, responsive_y))
    tubes.append({"x": WIDTH, "gap_y": gap_y, "scored": False})

  

def reset_game():
    global bird_y, velocity, tubes, prev_bird_y, score, pipe_speed, game_state
    bird_y = HEIGHT // 2
    velocity = 0
    tubes.clear()
    prev_bird_y = bird_y
    score = 0
    pipe_speed = 1
    for _ in range(3):
        create_tube()
        tubes[-1]["scored"] = True
    game_state = "playing"

# Mostrar pantalla de inicio
def show_menu():
    # Fondo semitransparente para el texto
    s = pygame.Surface((WIDTH - 50, 200), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))  # Negro semitransparente
    screen.blit(s, (25, HEIGHT//2 - 100))

    # Texto del título
    title_text = title_font.render("BIENVENIDO A", True, (255, 255, 255))
    title_text2 = title_font.render("FLAPPY UPB", True, (255, 255, 255))
    instruction_text = font.render("PRESIONE ENTER", True, (255, 255, 255))
    instruction_text2 = font.render("PARA JUGAR", True, (255, 255, 255))
    high_score_text = small_font.render(f"Récord: {high_score}", True, (255, 255, 255))

    # Centrar textos
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
    title2_rect = title_text2.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
    instr_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
    instr2_rect = instruction_text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 70))
    hs_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 110))

    screen.blit(title_text, title_rect)
    screen.blit(title_text2, title2_rect)
    screen.blit(instruction_text, instr_rect)
    screen.blit(instruction_text2, instr2_rect)
    screen.blit(high_score_text, hs_rect)

# Mostrar pantalla de game over
def show_game_over():
    # Fondo semitransparente para el texto
    s = pygame.Surface((350, 150), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))  # Negro semitransparente
    screen.blit(s, (25, HEIGHT//2 - 75))

    # Texto de game over
    text_line1 = font.render("Game Over!", True, (255, 255, 255))
    text_line2 = font.render(f"Puntuación: {score}", True, (255, 255, 255))
    text_line3 = font.render(f"Récord: {high_score}", True, (255, 255, 255))
    text_line4 = small_font.render("Presione R para reiniciar", True, (255, 255, 255))

    # Centrar textos
    text1_rect = text_line1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    text2_rect = text_line2.get_rect(center=(WIDTH//2, HEIGHT//2))
    text3_rect = text_line3.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    text4_rect = text_line4.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))

    screen.blit(text_line1, text1_rect)
    screen.blit(text_line2, text2_rect)
    screen.blit(text_line3, text3_rect)
    screen.blit(text_line4, text4_rect)

# Crear primeros tubos (marcados como ya puntuados para que no sumen puntos)
for _ in range(3):
    create_tube()
    tubes[-1]["scored"] = True  # Marcar como ya puntuados para que no sumen

running = True
while running:
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and game_state == "menu":
                reset_game()
            if event.key == pygame.K_SPACE and game_state == "playing":
                velocity = -7
                jump_sound.play()
            if event.key == pygame.K_r and game_state == "game_over":
                reset_game()

    if game_state == "menu":
        show_menu()
    elif game_state == "playing":
        velocity += gravity
        bird_y += velocity

        for tube in tubes:
            tube["x"] -= pipe_speed
            screen.blit(pipe_down_img, (tube["x"], tube["gap_y"] - pipe_down_img.get_height()))
            screen.blit(pipe_up_img, (tube["x"], tube["gap_y"] + pipe_gap))

                       # Detectar si el pájaro ha pasado el tubo (solo si no estaba marcado)
            if not tube.get("scored", False) and tube["x"] + pipe_width < bird_x:
                score += 1
                point_sound.play()  # <-- Reproducir sonido
                tube["scored"] = True

                # Aumentar velocidad cada 3 puntos
                if score % 5 == 0 and pipe_speed < 8 :
                    pipe_speed += 0.5

                # Actualizar high score si es necesario
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

        # Agregar nuevo tubo si el último está lejos
        if tubes[-1]["x"] < WIDTH - 200:
            create_tube()

        # Eliminar tubos fuera de pantalla
        tubes = [tube for tube in tubes if tube["x"] > -pipe_width]

        # Dibujar pájaro
        screen.blit(bird_img, (bird_x, bird_y))

        # Colisión con tubos
        for tube in tubes:
            if (bird_x + 40 > tube["x"] and bird_x < tube["x"] + pipe_width and
                    (bird_y < tube["gap_y"] or bird_y + 40 > tube["gap_y"] + pipe_gap)):
                death_sound.play
                game_state = "game_over"
    
        # Colisión con el suelo o el techo
        if bird_y >= HEIGHT - 40 or bird_y <= 0:
            death_sound.play
            game_state = "game_over"
            

        # Dibujar puntaje actual y high score
        score_text = font.render(f"Puntuación: {score}", True, (255, 255, 255))
        high_score_text = small_font.render(f"Récord: {high_score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
    elif game_state == "game_over":
        show_game_over()

    pygame.display.update()
    clock.tick(fps)

pygame.quit()