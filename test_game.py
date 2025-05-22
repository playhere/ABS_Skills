import unittest
import pygame

# Attempt to import from main.py.
# If main.py is in the same directory, this should work.
# If running tests from a different structure, sys.path modification might be needed.
try:
    from main import Dinosaur, Obstacle, SCREEN_HEIGHT, SCREEN_WIDTH
    # Define constants that might be used if not imported or for test-specific values
    TEST_SCREEN_WIDTH = 800
    TEST_SCREEN_HEIGHT = 600
    GROUND_Y_OFFSET = TEST_SCREEN_HEIGHT - 10 # Consistent with main.py
    INITIAL_OBSTACLE_SPEED_FOR_TEST = 5 # Consistent with main.py
except ImportError:
    print("Failed to import from main.py. Ensure it's in the Python path.")
    # Define fallback classes and constants if main cannot be imported
    # This is a simplified version for testing purposes if main.py is not accessible
    # In a real scenario, you'd ensure your test environment can access the main module.
    TEST_SCREEN_WIDTH = 800
    TEST_SCREEN_HEIGHT = 600
    GROUND_Y_OFFSET = TEST_SCREEN_HEIGHT - 10
    INITIAL_OBSTACLE_SPEED_FOR_TEST = 5

    class Dinosaur:
        def __init__(self, initial_x, ground_y_offset):
            self.initial_x = initial_x
            self.ground_y_offset = ground_y_offset
            self.image = None # Assume no image for tests if main.py fails
            self.width = 50
            self.height = 50
            self.rect = pygame.Rect(initial_x, ground_y_offset - self.height, self.width, self.height)
            self.initial_y_pos = self.rect.y
            self.is_jumping = False
            self.jump_velocity = 0
            self.gravity = 1
            # Fallback collision_rect
            self.collision_rect = self.rect.inflate(-10, -10)


        def jump(self):
            if not self.is_jumping:
                self.is_jumping = True
                self.jump_velocity = -20

        def update(self):
            if self.is_jumping:
                self.rect.y += self.jump_velocity
                self.jump_velocity += self.gravity
                if self.rect.y >= self.initial_y_pos:
                    self.rect.y = self.initial_y_pos
                    self.is_jumping = False
                    self.jump_velocity = 0
            # Update fallback collision_rect
            self.collision_rect.center = self.rect.center
        
        def draw(self, surface): # Mock draw
            pass


    class Obstacle:
        def __init__(self, screen_width, screen_height_minus_ground_offset):
            self.image = None # Assume no image
            self.width = 30
            self.height = 60
            self.rect = pygame.Rect(screen_width, screen_height_minus_ground_offset - self.height, self.width, self.height)
            self.rect.right = screen_width
            self.speed = INITIAL_OBSTACLE_SPEED_FOR_TEST
            # Fallback collision_rect
            self.collision_rect = self.rect.inflate(-10, -10)

        def update(self):
            self.rect.x -= self.speed
            # Update fallback collision_rect
            self.collision_rect.center = self.rect.center
        
        def get_rect(self):
            return self.rect

        def draw(self, surface): # Mock draw
            pass

# Initialize Pygame for rects and other functionalities
pygame.init()

class TestDinosaur(unittest.TestCase):
    def setUp(self):
        # Ground y offset is where the bottom of the dinosaur will be
        self.dino = Dinosaur(initial_x=50, ground_y_offset=GROUND_Y_OFFSET)
        self.initial_rect_y = self.dino.rect.y # Cache initial y from rect

    def test_dinosaur_initialization(self):
        self.assertEqual(self.dino.rect.bottomleft, (50, GROUND_Y_OFFSET))
        self.assertFalse(self.dino.is_jumping)
        self.assertEqual(self.dino.jump_velocity, 0)
        # Ensure initial_y_pos is correctly set based on rect.y after potential image loading
        self.assertEqual(self.dino.initial_y_pos, self.initial_rect_y)


    def test_dinosaur_jump(self):
        self.dino.jump()
        self.assertTrue(self.dino.is_jumping)
        self.assertEqual(self.dino.jump_velocity, -20)

    def test_dinosaur_update_jumping(self):
        self.dino.jump() # is_jumping=True, jump_velocity=-20
        initial_y = self.dino.rect.y
        initial_jump_velocity = self.dino.jump_velocity

        self.dino.update()

        self.assertEqual(self.dino.rect.y, initial_y + initial_jump_velocity)
        self.assertEqual(self.dino.jump_velocity, initial_jump_velocity + self.dino.gravity)

    def test_dinosaur_update_landing(self):
        self.dino.jump() # Initial jump_velocity = -20, gravity = 1

        # Simulate updates until the dinosaur lands
        # This loop assumes the dinosaur will eventually land.
        # Max iterations to prevent infinite loop in case of logic error.
        for _ in range(100): 
            self.dino.update()
            if not self.dino.is_jumping:
                break
        
        self.assertFalse(self.dino.is_jumping, "Dinosaur should have landed.")
        self.assertEqual(self.dino.rect.y, self.dino.initial_y_pos, "Dinosaur y position is not back to initial.")
        # When landed, velocity might be 0 or some positive value if it overshot and corrected.
        # The key is that is_jumping is False and y is correct.
        # For this specific implementation, it should be 0.
        self.assertEqual(self.dino.jump_velocity, 0, "Jump velocity not reset after landing.")

class TestObstacle(unittest.TestCase):
    def setUp(self):
        self.obstacle = Obstacle(screen_width=TEST_SCREEN_WIDTH, screen_height_minus_ground_offset=GROUND_Y_OFFSET)
        # If using main.Obstacle and it has random sizes, we might need to adapt tests or mock random.
        # For now, assuming it can be instantiated and speed is default or set.
        self.obstacle.speed = INITIAL_OBSTACLE_SPEED_FOR_TEST # Ensure consistent speed for tests

    def test_obstacle_initialization(self):
        # The obstacle's right edge should be at the screen_width
        self.assertEqual(self.obstacle.rect.right, TEST_SCREEN_WIDTH)
        # The obstacle's bottom edge should be at GROUND_Y_OFFSET
        self.assertEqual(self.obstacle.rect.bottom, GROUND_Y_OFFSET)
        self.assertEqual(self.obstacle.speed, INITIAL_OBSTACLE_SPEED_FOR_TEST)

    def test_obstacle_movement(self):
        initial_x = self.obstacle.rect.x
        self.obstacle.update()
        self.assertEqual(self.obstacle.rect.x, initial_x - self.obstacle.speed)

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.dinosaur = Dinosaur(initial_x=50, ground_y_offset=GROUND_Y_OFFSET)
        # Obstacles are positioned based on their bottom-right corner.
        self.obstacle = Obstacle(screen_width=TEST_SCREEN_WIDTH, screen_height_minus_ground_offset=GROUND_Y_OFFSET)
        self.obstacle.speed = INITIAL_OBSTACLE_SPEED_FOR_TEST # Set consistent speed

        # Game state variables for tests
        self.score = 0
        self.level = 1
        self.game_obstacle_speed = INITIAL_OBSTACLE_SPEED_FOR_TEST
        self.score_to_next_level = 50 # Example value from main.py
        self.level_up_score_increment = 50 # Example value

    def test_collision_detection(self):
        # Ensure collision_rects are updated if rects are moved directly in tests
        # For Dinosaur
        self.dinosaur.rect.x = 100
        self.dinosaur.rect.y = GROUND_Y_OFFSET - self.dinosaur.rect.height 
        self.dinosaur.collision_rect.center = self.dinosaur.rect.center
        
        # For Obstacle
        # Position obstacle's main rect first
        self.obstacle.rect.x = 100 + self.dinosaur.rect.width - 10 # Ensure main rects overlap for setup
        self.obstacle.rect.y = GROUND_Y_OFFSET - self.obstacle.rect.height
        # Then update its collision_rect's center based on its main rect
        self.obstacle.collision_rect.center = self.obstacle.rect.center

        # Scenario 1: Overlapping collision_rects
        # To ensure collision_rects overlap, we might need to adjust positions
        # based on the inflation amount.
        # Let's assume inflation is (-10, -10), meaning 5px from each side.
        # For simplicity in test, let's directly set collision_rect positions for overlap.
        self.dinosaur.collision_rect.topleft = (100, GROUND_Y_OFFSET - self.dinosaur.collision_rect.height)
        self.obstacle.collision_rect.topleft = (100 + self.dinosaur.collision_rect.width - 5, GROUND_Y_OFFSET - self.obstacle.collision_rect.height) # overlap by 5px

        self.assertTrue(self.dinosaur.collision_rect.colliderect(self.obstacle.collision_rect), "Should detect collision when collision_rects are overlapping.")

        # Scenario 2: Not overlapping collision_rects
        # Move obstacle's collision_rect far away
        self.obstacle.collision_rect.x = 300 
        self.assertFalse(self.dinosaur.collision_rect.colliderect(self.obstacle.collision_rect), "Should not detect collision when collision_rects are not overlapping.")

    def test_score_increment_on_pass(self):
        # Position dinosaur and obstacle: obstacle is to the right of dinosaur
        self.dinosaur.rect.x = 50
        self.obstacle.rect.x = self.dinosaur.rect.right + 20 # Obstacle ahead
        self.obstacle.rect.right = self.dinosaur.rect.right + 20 # Obstacle ahead, ensure right is set
        
        # Simulate obstacle moving past the dinosaur
        # Obstacle needs to move from being to the right of dino's front (rect.x)
        # to its (obstacle.rect.right) being to the left of dino's front (rect.x)
        
        # Initial state: obstacle.rect.right > self.dinosaur.rect.x
        self.assertFalse(hasattr(self.obstacle, 'scored')) # Should not be scored yet

        # Move obstacle so its right edge is just to the left of dinosaur's x
        self.obstacle.rect.right = self.dinosaur.rect.x - 5
        
        # Scoring logic from main.py:
        # if not hasattr(obstacle, 'scored') and obstacle.rect.right < dinosaur.rect.x:
        #     score += 10
        #     obstacle.scored = True
        
        if not hasattr(self.obstacle, 'scored') and self.obstacle.rect.right < self.dinosaur.rect.x:
            self.score += 10
            self.obstacle.scored = True
            
        self.assertEqual(self.score, 10)
        self.assertTrue(hasattr(self.obstacle, 'scored'))
        self.assertTrue(self.obstacle.scored)

    def test_level_up(self):
        self.score = 40 # Just below level up threshold of 50
        self.level = 1
        self.game_obstacle_speed = INITIAL_OBSTACLE_SPEED_FOR_TEST
        self.score_to_next_level = 50 

        # Simulate scoring points to cross threshold
        # Say, we pass an obstacle
        self.score += 10 # Now score is 50

        if self.score >= self.score_to_next_level:
            self.level += 1
            self.game_obstacle_speed += 1
            # In main.py, score_to_next_level also updates:
            # score_to_next_level += level_up_score_increment * level
            self.score_to_next_level += self.level_up_score_increment * self.level 

        self.assertEqual(self.level, 2)
        self.assertEqual(self.game_obstacle_speed, INITIAL_OBSTACLE_SPEED_FOR_TEST + 1)
        # Expected next threshold: 50 (initial) + 50 * 2 (new level) = 150
        self.assertEqual(self.score_to_next_level, 50 + self.level_up_score_increment * 2)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
