import pygame
from pygame.locals import *

import ctypes
ctypes.windll.user32.SetProcessDPIAware()

# START GAME AND INITIAL SETTING#
pygame.init()

# DEFINING COLORS
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

# frame control
FPS = 60
fps_clock = pygame.time.Clock()


class ArcTracker(pygame.sprite.Sprite):
    """
    A sprite controlled by player

    This moves only through "arc track" indicated by user input.

    Arc tracks have rotation axis, rotation angle and direction(either clockwise or counterclockwise).

    Arctracker has 3 states: Idle, Ready, and Moving.

    Idle: Does nothing. When a left-click event occurs, it changes to Ready state.

    Ready: In this state, rotation axis had been set and user can modulate rotation angle and direction
    by moving mouse cursor around ArcTracker. When left-click event occurs again, it changes to Moving state.
    If user presses "c" or ESC key, it'll move back to the Idle state and arc track setting process is canceled.

    Moving: ArcTracker actually moves along the arc trail.
    After moving, it returns back to the Idle state automatically.
    """

    def __init__(self):
        """
        Initializing method
        """

        pygame.sprite.Sprite.__init__(self)

    def update(self) -> None:
        """
        Updating method needed for all sprite class
        :return: None
        """

        pass


# MAIN GAME LOOP #

while True:
    # Get all kind of events generated from mouse
    pygame.event.get()
    left_click, middle_click, right_click, scroll_up, scroll_down = pygame.mouse.get_pressed(5)

    # Quit game when clicking mouse wheel (needs to be modified)
    if middle_click:
        break

    curspos = pygame.mouse.get_pos()    # Get cursor position on the screen


    screen.fill(BLACK)                  # Fill screen with black

    pygame.display.flip()               # Update all display changes and show them
    fps_clock.tick(FPS)                 # Make program never run at more than "FPS" frames per second
