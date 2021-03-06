"""
Initialize the game and basic settings
"""


import pygame
from pygame.locals import *

import ctypes
ctypes.windll.user32.SetProcessDPIAware()

# Start game and initial setting
pygame.init()

# Constants to indicate which kind of input
LCLICK = 1      # Left click (bool)
MCLICK = 2      # Middle click (bool)
RCLICK = 3      # Right click (bool)
SCRLUP = 4      # Scroll up (bool)
SCRLDN = 5      # Scroll down (bool)
CURPOS = 6      # Cursor position (tuple (x, y))

# Defining colors
BLACK = (0, 0, 0)
WHITE1 = (255, 255, 255)
WHITE2 = (127, 127, 127)
WHITE3 = (63, 63, 63)
RED1 = (255, 63, 63)
RED2 = (127, 31, 31)
RED3 = (63, 15, 15)
GREEN1 = (0, 255, 0)
GREEN2 = (0, 127, 0)
GREEN3 = (0, 63, 0)
BLUE1 = (63, 191, 255)
BLUE2 = (31, 95, 127)
BLUE3 = (15, 47, 63)
CYAN1 = (0, 255, 255)
CYAN2 = (0, 127, 127)
CYAN3 = (0, 63, 63)
MAGENTA1 = (255, 0, 255)
MAGENTA2 = (127, 0, 127)
MAGENTA3 = (63, 0, 63)
YELLOW1 = (255, 255, 0)
YELLOW2 = (127, 127, 0)
YELLOW3 = (63, 63, 0)
ORANGE1 = (255, 102, 0)
ORANGE2 = (127, 51, 0)
ORANGE3 = (63, 25, 0)
PURPLE1 = (191, 95, 255)
PURPLE2 = (95, 47, 127)
PURPLE3 = (47, 23, 63)

# Set game title
pygame.display.set_caption("Arc Tracker")

# Create the screen
screen_width, screen_height = 1920, 1080
flags = FULLSCREEN | DOUBLEBUF
screen = pygame.display.set_mode((screen_width, screen_height), flags, 16)

# Frame control
FPS = 60
fps_clock = pygame.time.Clock()
DELTA_TIME = 0

# Mouse control event dict
mouse = {LCLICK: False, MCLICK: False, RCLICK: False, SCRLUP: False, SCRLDN: False, CURPOS: (0, 0)}

# Indicates whether continue game
running = True


# Loading images
arc_tracker_img1 = pygame.image.load("img/character/arc_tracker_1.png").convert()   # Image of Arc tracker (green)
arc_tracker_img1.set_colorkey(BLACK)                                                # Remove black region of the image
arc_tracker_img2 = pygame.image.load("img/character/arc_tracker_2.png").convert()   # Image of Arc tracker (blue)
arc_tracker_img2.set_colorkey(BLACK)                                                # Remove black region of the image
arc_tracker_img3 = pygame.image.load("img/character/arc_tracker_3.png").convert()   # Image of Arc tracker (red)
arc_tracker_img3.set_colorkey(BLACK)                                                # Remove black region of the image
arc_tracker_img_list = [arc_tracker_img1, arc_tracker_img2, arc_tracker_img3]       # List of all ArcTracker images

arc_tracker_clone_img1 = pygame.image.load("img/character/arc_tracker_1_clone.png").convert()           # Image of Arc tracker clone (green)
arc_tracker_clone_img1.set_colorkey(BLACK)                                                              # Remove black region of the image
arc_tracker_clone_img2 = pygame.image.load("img/character/arc_tracker_2_clone.png").convert()           # Image of Arc tracker clone (blue)
arc_tracker_clone_img2.set_colorkey(BLACK)                                                              # Remove black region of the image
arc_tracker_clone_img3 = pygame.image.load("img/character/arc_tracker_3_clone.png").convert()           # Image of Arc tracker clone (red)
arc_tracker_clone_img3.set_colorkey(BLACK)                                                              # Remove black region of the image
arc_tracker_clone_img_list = [arc_tracker_clone_img1, arc_tracker_clone_img2, arc_tracker_clone_img3]   # List of all ArcTrackerClone images

arc_tracker_counter_clone_img1 = pygame.image.load("img/character/arc_tracker_1_counter_clone.png").convert()                           # Image of Arc tracker_counter clone (green)
arc_tracker_counter_clone_img1.set_colorkey(BLACK)                                                                                      # Remove black region of the image
arc_tracker_counter_clone_img2 = pygame.image.load("img/character/arc_tracker_2_counter_clone.png").convert()                           # Image of Arc tracker_counter clone (blue)
arc_tracker_counter_clone_img2.set_colorkey(BLACK)                                                                                      # Remove black region of the image
arc_tracker_counter_clone_img3 = pygame.image.load("img/character/arc_tracker_3_counter_clone.png").convert()                           # Image of Arc tracker_counter clone (red)
arc_tracker_counter_clone_img3.set_colorkey(BLACK)                                                                                      # Remove black region of the image
arc_tracker_counter_clone_img_list = [arc_tracker_counter_clone_img1, arc_tracker_counter_clone_img2, arc_tracker_counter_clone_img3]   # List of all ArcTrackerClone images

axis_marker_O_img = pygame.image.load("img/character/axis_marker_O.png").convert()  # O-shaped image of axis marker
axis_marker_O_img.set_colorkey(BLACK)
axis_marker_X_img = pygame.image.load("img/character/axis_marker_X.png").convert()  # O-shaped image of axis marker
axis_marker_X_img.set_colorkey(BLACK)

goal_point_img_list = []        # List of frame for animating GoalPoint
for i in range(60):             # Load and append all frames to the list
    img_frame = pygame.image.load(f"img/character/goal_point_anim/goal_point_{i}.png").convert()
    img_frame.set_colorkey(BLACK)
    goal_point_img_list.append(img_frame)

example_game_img1 = pygame.image.load("img/example_play_capture/example_1.png").convert()
example_game_img1.set_colorkey(BLACK)
example_game_img2 = pygame.image.load("img/example_play_capture/example_2.png").convert()
example_game_img2.set_colorkey(BLACK)
example_game_img3 = pygame.image.load("img/example_play_capture/example_3.png").convert()
example_game_img3.set_colorkey(BLACK)
example_game_img4 = pygame.image.load("img/example_play_capture/example_4.png").convert()
example_game_img4.set_colorkey(BLACK)

# Load all obstacle images
test_img_1 = pygame.image.load("img/obstacles/test/10-1.png").convert()       # Image for newly testing obstacle
