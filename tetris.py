import pygame
import random

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
BORDER_WIDTH = 4
BLOCK_MARGIN = 1
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8) + BORDER_WIDTH * 2
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT + BORDER_WIDTH * 2

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Tetris")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Color schemes
COLOR_SCHEMES = {
    "Classic": {
        "background": BLACK,
        "border": GRAY,
        "text": WHITE,
        "shapes": [CYAN, YELLOW, MAGENTA, RED, GREEN, BLUE, ORANGE]
    },
    "Pastel": {
        "background": (230, 230, 250),
        "border": (200, 200, 220),
        "text": (70, 70, 90),
        "shapes": [(173, 216, 230), (255, 240, 245), (255, 182, 193), (255, 218, 185), (152, 251, 152), (175, 238, 238), (221, 160, 221)]
    },
    "Neon": {
        "background": (10, 10, 10),
        "border": (30, 30, 30),
        "text": (255, 255, 255),
        "shapes": [(0, 255, 255), (255, 255, 0), (255, 0, 255), (255, 50, 50), (50, 255, 50), (50, 50, 255), (255, 165, 0)]
    }
}

# Difficulty levels
DIFFICULTY_LEVELS = {
    "Easy": 0.5,
    "Medium": 0.35,
    "Hard": 0.2
}

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

# Add these constants near the top of the file
LEVEL_MODE_LINES_PER_LEVEL = 10
MAX_LEVEL = 15

# Add a new game mode selection function
def select_game_mode():
    return select_option(["Infinite Mode", "Level Mode"], "Select Game Mode")

def draw_text_centered(text, font, color, surface, y_offset=0):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
    surface.blit(text_obj, text_rect)

def select_option(options, title):
    selected = 0
    while True:
        screen.fill(BLACK)
        draw_text_centered(title, font, WHITE, screen, -100)
        
        for i, option in enumerate(options):
            color = RED if i == selected else WHITE
            draw_text_centered(option, font, color, screen, i * 50)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if (j, i) in locked_positions:
                color = locked_positions[(j, i)]
                grid[i][j] = color
    return grid

def draw_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(screen, grid[i][j], 
                             (j*BLOCK_SIZE + BORDER_WIDTH + BLOCK_MARGIN, 
                              i*BLOCK_SIZE + BORDER_WIDTH + BLOCK_MARGIN, 
                              BLOCK_SIZE - BLOCK_MARGIN*2, 
                              BLOCK_SIZE - BLOCK_MARGIN*2))

def get_shape(shape_colors):
    return random.choice(SHAPES), random.choice(shape_colors)

def valid_space(shape, grid, offset):
    accepted_pos = [[(j, i) for j in range(GRID_WIDTH) if grid[i][j] == BLACK] for i in range(GRID_HEIGHT)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape, offset)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def convert_shape_format(shape, offset):
    positions = []
    for i, row in enumerate(shape):
        for j, column in enumerate(row):
            if column == 1:
                positions.append((offset['x'] + j, offset['y'] + i))
    return positions

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc

def draw_next_shapes(shapes, colors, current_scheme):
    font = pygame.font.Font(None, 30)
    label = font.render('Next Shapes', 1, current_scheme["text"])

    sx = BLOCK_SIZE * (GRID_WIDTH + 1) + BORDER_WIDTH
    sy = BLOCK_SIZE * 2
    
    screen.blit(label, (sx + 10, sy - 30))
    
    for index, (shape, color) in enumerate(zip(shapes, colors)):
        for i, row in enumerate(shape):
            for j, column in enumerate(row):
                if column == 1:
                    pygame.draw.rect(screen, color, 
                                     (sx + j*BLOCK_SIZE + BLOCK_MARGIN, 
                                      sy + i*BLOCK_SIZE + BLOCK_MARGIN + index*BLOCK_SIZE*2.5, 
                                      BLOCK_SIZE - BLOCK_MARGIN*2, 
                                      BLOCK_SIZE - BLOCK_MARGIN*2))

def draw_score_and_top_score(score, top_score, current_scheme):
    font = pygame.font.Font(None, 30)
    score_label = font.render(f'Score: {score}', 1, current_scheme["text"])
    top_score_label = font.render(f'Top Score: {top_score}', 1, current_scheme["text"])
    sx = BLOCK_SIZE * (GRID_WIDTH + 1) + BORDER_WIDTH
    sy = BLOCK_SIZE * 16
    screen.blit(score_label, (sx + 10, sy))
    screen.blit(top_score_label, (sx + 10, sy + 40))

def draw_border(current_scheme):
    pygame.draw.rect(screen, current_scheme["border"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), BORDER_WIDTH)
    pygame.draw.rect(screen, current_scheme["border"], (0, 0, BLOCK_SIZE * GRID_WIDTH + BORDER_WIDTH * 2, SCREEN_HEIGHT), BORDER_WIDTH)

def draw_game_over(score, top_score, current_scheme):
    screen.fill(current_scheme["background"])
    font = pygame.font.Font(None, 48)
    game_over_text = font.render('GAME OVER', True, current_scheme["text"])
    score_text = font.render(f'Score: {score}', True, current_scheme["text"])
    top_score_text = font.render(f'Top Score: {top_score}', True, current_scheme["text"])
    play_again_text = font.render('Press SPACE to play again', True, current_scheme["text"])
    quit_text = font.render('Press Q to quit', True, current_scheme["text"])

    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(top_score_text, (SCREEN_WIDTH//2 - top_score_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    screen.blit(play_again_text, (SCREEN_WIDTH//2 - play_again_text.get_width()//2, SCREEN_HEIGHT//2 + 150))
    screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 200))
    pygame.display.update()

def draw_pause_screen(current_scheme):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    screen.blit(s, (0, 0))
    font = pygame.font.Font(None, 48)
    pause_text = font.render('PAUSED', True, current_scheme["text"])
    screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2))
    pygame.display.update()

# Add a new function to draw the current level
def draw_level(level, current_scheme):
    font = pygame.font.Font(None, 30)
    level_label = font.render(f'Level: {level}', 1, current_scheme["text"])
    sx = BLOCK_SIZE * (GRID_WIDTH + 1) + BORDER_WIDTH
    sy = BLOCK_SIZE * 18
    screen.blit(level_label, (sx + 10, sy))

# Modify the main function to include game mode selection
def main():
    top_score = 0
    
    while True:
        game_mode = select_game_mode()
        if game_mode is None:
            return

        color_scheme = select_option(list(COLOR_SCHEMES.keys()), "Select Color Scheme")
        if color_scheme is None:
            return
        current_scheme = COLOR_SCHEMES[color_scheme]
        
        if game_mode == "Infinite Mode":
            difficulty_name = select_option(list(DIFFICULTY_LEVELS.keys()), "Select Difficulty")
            if difficulty_name is None:
                return
            difficulty = DIFFICULTY_LEVELS[difficulty_name]
            game_over, score = gameLoop(top_score, difficulty, current_scheme, game_mode)
        else:  # Level Mode
            game_over, score = gameLoop(top_score, 0.5, current_scheme, game_mode)  # Start with easiest difficulty
        
        top_score = max(score, top_score)
        
        if game_over:
            draw_game_over(score, top_score, current_scheme)
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            return
        else:
            pygame.quit()
            return

# Modify the gameLoop function to handle level mode
def gameLoop(top_score, difficulty, current_scheme, game_mode):
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece, current_color = get_shape(current_scheme["shapes"])
    next_pieces = [get_shape(current_scheme["shapes"]) for _ in range(5)]
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = difficulty
    level_time = 0
    score = 0
    paused = False
    level = 1
    lines_cleared = 0

    offset = {'x': GRID_WIDTH // 2 - len(current_piece[0]) // 2, 'y': 0}

    while run:
        if not paused:
            grid = create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick()

            if game_mode == "Infinite Mode":
                if level_time/1000 > 5:
                    level_time = 0
                    if fall_speed > 0.15:
                        fall_speed -= 0.005
            else:  # Level Mode
                if lines_cleared >= LEVEL_MODE_LINES_PER_LEVEL:
                    level += 1
                    lines_cleared = 0
                    fall_speed = max(difficulty - (level - 1) * 0.02, 0.15)

            if fall_time/1000 > fall_speed:
                fall_time = 0
                offset['y'] += 1
                if not(valid_space(current_piece, grid, offset)) and offset['y'] > 0:
                    offset['y'] -= 1
                    change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, score

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not paused:
                    offset['x'] -= 1
                    if not(valid_space(current_piece, grid, offset)):
                        offset['x'] += 1
                if event.key == pygame.K_RIGHT and not paused:
                    offset['x'] += 1
                    if not(valid_space(current_piece, grid, offset)):
                        offset['x'] -= 1
                if event.key == pygame.K_DOWN and not paused:
                    offset['y'] += 1
                    if not(valid_space(current_piece, grid, offset)):
                        offset['y'] -= 1
                if event.key == pygame.K_UP and not paused:
                    rotated_piece = list(zip(*current_piece[::-1]))
                    if valid_space(rotated_piece, grid, offset):
                        current_piece = rotated_piece
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        draw_pause_screen(current_scheme)

        if not paused:
            shape_pos = convert_shape_format(current_piece, offset)

            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    grid[y][x] = current_color

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_color
                current_piece, current_color = next_pieces.pop(0)
                next_pieces.append(get_shape(current_scheme["shapes"]))
                offset = {'x': GRID_WIDTH // 2 - len(current_piece[0]) // 2, 'y': 0}
                change_piece = False
                cleared_rows = clear_rows(grid, locked_positions)
                score += cleared_rows * 10
                lines_cleared += cleared_rows

            screen.fill(current_scheme["background"])
            draw_border(current_scheme)
            draw_grid(grid)
            draw_next_shapes([shape for shape, color in next_pieces], [color for shape, color in next_pieces], current_scheme)
            draw_score_and_top_score(score, top_score, current_scheme)
            if game_mode == "Level Mode":
                draw_level(level, current_scheme)
            pygame.display.update()

            if check_lost(locked_positions) or (game_mode == "Level Mode" and level > MAX_LEVEL):
                return True, score

    return False, score

main()