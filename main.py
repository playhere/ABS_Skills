import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer

# Define screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game display surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the window title
pygame.display.set_caption("Simple Pygame Game")

# Create a Clock object to control the frame rate
clock = pygame.time.Clock()

# --- Asset Directories ---
IMAGE_DIR = "assets/images/"
SOUND_DIR = "assets/sounds/" # Already defined, kept for context
# --- End Asset Directories ---

# Define Dinosaur class
class Dinosaur:
    def __init__(self, initial_x, ground_y_offset):
        self.initial_x = initial_x
        self.ground_y_offset = ground_y_offset # e.g., SCREEN_HEIGHT - ground_y_offset
        self.color = (0, 0, 0)  # Fallback color
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1
        
        try:
            self.image = pygame.image.load(IMAGE_DIR + "dinosaur.png").convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.bottomleft = (initial_x, self.ground_y_offset)
        except pygame.error as e:
            print(f"Warning: Could not load dinosaur.png: {e}. Using fallback rectangle.")
            self.image = None
            self.width = 50  # Fallback width
            self.height = 50 # Fallback height
            self.rect = pygame.Rect(initial_x, ground_y_offset - self.height, self.width, self.height)
        
        self.initial_y_pos = self.rect.y # Store initial y position for landing after jump

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = -20  # Negative for upward movement

    def update(self):
        if self.is_jumping:
            self.rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            if self.rect.y >= self.initial_y_pos: # Check if landed
                self.rect.y = self.initial_y_pos
                self.is_jumping = False
                self.jump_velocity = 0

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

import random

# Define Obstacle class
class Obstacle:
    def __init__(self, screen_width, screen_height_minus_ground_offset):
        self.screen_width = screen_width
        self.ground_y_offset = screen_height_minus_ground_offset # e.g. SCREEN_HEIGHT - 10
        self.color = (255, 0, 0)  # Fallback color
        self.speed = 5 # Default speed, can be overridden

        try:
            self.image = pygame.image.load(IMAGE_DIR + "cactus.png").convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.bottomright = (screen_width, self.ground_y_offset)
        except pygame.error as e:
            print(f"Warning: Could not load cactus.png: {e}. Using fallback rectangle.")
            self.image = None
            # Use random dimensions only if image fails to load
            self.width = random.choice([20, 40])
            self.height = random.choice([40, 60, 80])
            self.rect = pygame.Rect(screen_width, self.ground_y_offset - self.height, self.width, self.height)
            self.rect.right = screen_width # Ensure it starts off-screen

    def update(self):
        self.rect.x -= self.speed

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

    def get_rect(self): # This method is now consistently returning self.rect
        return self.rect

# Create an instance of the Dinosaur
# Position the dinosaur considering its height and a 10px margin from the bottom
dinosaur = Dinosaur(50, SCREEN_HEIGHT - 10) # ground_y_offset is SCREEN_HEIGHT - 10

# Obstacle settings
obstacles = []
obstacle_spawn_timer = 0
obstacle_spawn_delay = 120 # Spawn a new obstacle every 120 frames (2 seconds at 60 FPS)

# Obstacle settings
# ... (obstacle_spawn_timer, obstacle_spawn_delay remain the same)

# Score
score = 0
game_font = pygame.font.Font(None, 36) # Font for displaying score
game_active = True # Game state, becomes False on collision

# Initial Game State Values (for reset)
INITIAL_OBSTACLE_SPEED = 5
INITIAL_SCORE_TO_NEXT_LEVEL = 50

# Game Levels and Difficulty
level = 1
obstacle_speed = INITIAL_OBSTACLE_SPEED
score_to_next_level = INITIAL_SCORE_TO_NEXT_LEVEL
level_up_score_increment = 50 # How much the threshold increases per level

# Fonts
game_font = pygame.font.Font(None, 36) # Font for displaying score and level
game_over_font = pygame.font.Font(None, 72) # Larger font for "Game Over"

# --- Sound Effect Setup ---
# (SOUND_DIR is already defined above with IMAGE_DIR)
try:
    jump_sound = pygame.mixer.Sound(SOUND_DIR + "jump.wav")
except pygame.error as e:
    print(f"Warning: Could not load sound file {SOUND_DIR}jump.wav: {e}")
    jump_sound = None

try:
    game_over_sound = pygame.mixer.Sound(SOUND_DIR + "game_over.wav")
except pygame.error as e:
    print(f"Warning: Could not load sound file {SOUND_DIR}game_over.wav: {e}")
    game_over_sound = None

try:
    level_up_sound = pygame.mixer.Sound(SOUND_DIR + "level_up.wav")
except pygame.error as e:
    print(f"Warning: Could not load sound file {SOUND_DIR}level_up.wav: {e}")
    level_up_sound = None

# Optional: Background Music (placeholder)
# try:
#     pygame.mixer.music.load(SOUND_DIR + "background_music.ogg")
#     pygame.mixer.music.set_volume(0.3) # Adjust volume (0.0 to 1.0)
#     pygame.mixer.music.play(-1) # -1 means loop indefinitely
# except pygame.error as e:
#     print(f"Warning: Could not load background music {SOUND_DIR}background_music.ogg: {e}")
# --- End Sound Effect Setup ---

def reset_game():
    global score, level, obstacle_speed, score_to_next_level, game_active, obstacles, dinosaur, obstacle_spawn_timer
    score = 0
    level = 1
    obstacle_speed = INITIAL_OBSTACLE_SPEED
    score_to_next_level = INITIAL_SCORE_TO_NEXT_LEVEL
    obstacles.clear()
    # Reset dinosaur position based on its rect and initial setup
    dinosaur.rect.bottomleft = (dinosaur.initial_x, dinosaur.ground_y_offset)
    dinosaur.initial_y_pos = dinosaur.rect.y # Re-cache initial y for jump logic
    dinosaur.is_jumping = False
    dinosaur.jump_velocity = 0
    obstacle_spawn_timer = 0
    game_active = True

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_active:
                if event.key == pygame.K_SPACE:
                    dinosaur.jump()
                    if jump_sound:
                        jump_sound.play()
            else: # Game is not active (Game Over state)
                if event.key == pygame.K_r:
                    reset_game() # reset_game() is already defined

    if game_active: # Moved the game logic into this block
        # Update game state
        dinosaur.update()

    # Obstacle spawning
    obstacle_spawn_timer += 1
    if obstacle_spawn_timer >= obstacle_spawn_delay and game_active:
        # Pass SCREEN_HEIGHT - 10 as the ground_y_offset for obstacles
        new_obstacle = Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT - 10)
        new_obstacle.speed = obstacle_speed
        obstacles.append(new_obstacle)
        obstacle_spawn_timer = 0

    # Update and draw obstacles
    for obstacle in list(obstacles):
        if game_active:
            obstacle.update()
        if obstacle.rect.right < 0: # Check if obstacle is off-screen to the left
            obstacles.remove(obstacle)

    # Fill the screen with a default color (white)
    screen.fill((255, 255, 255))  # White color

    # Draw the dinosaur
    dinosaur.draw(screen)

    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)

    # Collision detection
    # dinosaur.rect is now the source of truth for dinosaur's collision area
    if game_active:
        for obstacle in obstacles:
            # obstacle.get_rect() returns obstacle.rect, which is image-based if loaded
            if dinosaur.rect.colliderect(obstacle.get_rect()):
                print("Collision!")
                if game_over_sound:
                    game_over_sound.play()
                game_active = False

    # Score increment
    if game_active:
        for obstacle in obstacles:
            # Check if obstacle has passed the dinosaur's left edge (dinosaur.rect.x)
            if not hasattr(obstacle, 'scored') and obstacle.rect.right < dinosaur.rect.x:
                score += 10
                obstacle.scored = True
    
    
    # Level progression
    if score >= score_to_next_level and game_active:
        level += 1
        obstacle_speed += 1 # Increase obstacle speed
        score_to_next_level += level_up_score_increment * level
        print(f"Level Up! Level: {level}, Speed: {obstacle_speed}, Next Level at: {score_to_next_level} points")
        if level_up_sound:
            level_up_sound.play()

    # Drawing operations (happen whether game is active or over)
    # screen.fill((255, 255, 255)) already done before this block in the original code

    # Draw dinosaur and obstacles (already done before this block in original)
    # dinosaur.draw(screen)
    # for obstacle in obstacles:
    #    obstacle.draw(screen)

    if game_active:
        # Display Score and Level
        score_surface = game_font.render(f"Score: {score}", True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(10, 10))
        screen.blit(score_surface, score_rect)
        
        level_surface = game_font.render(f"Level: {level}", True, (0, 0, 0))
        level_rect = level_surface.get_rect(topleft=(10, score_rect.bottom + 5))
        screen.blit(level_surface, level_rect)
    else:
        # Display Game Over messages
        game_over_text = game_over_font.render("Game Over", True, (0, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)

        final_score_text = game_font.render(f"Final Score: {score}", True, (0, 0, 0))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(final_score_text, final_score_rect)

        restart_text = game_font.render("Press R to Restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
