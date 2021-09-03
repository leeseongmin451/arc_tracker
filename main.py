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

# Mouse control event dict
mouse = {LCLICK: False, MCLICK: False, RCLICK: False, SCRLUP: False, SCRLDN: False, CURPOS: (0, 0)}


# Loading images
arc_tracker_img = pygame.image.load("img/character/arc_tracker.png").convert()      # Image of Arc tracker
arc_tracker_img.set_colorkey(BLACK)                                                 # Remove black region of the image


class ArcTracker(pygame.sprite.Sprite):
    """
    A sprite controlled by player

    This moves only through "arc track" indicated by user input.

    Arc tracks have rotation axis, rotation angle and direction(either clockwise or counterclockwise).

    Arctracker has 3 states: Idle, Ready, and Moving.

    Idle: Does nothing. When a left-click event occurs, it changes to Ready state.

    Ready: In this state, rotation axis had been set. When user clicks again, it changes to Moving state.
    It moves clockwise for right-click event, and counterclockwise for left-click event.
    If user presses "c" or ESC key, it'll move back to the Idle state and arc track setting process is canceled.

    Moving: ArcTracker actually moves along the arc trail.
    If a click event occurs, it stops moving and returns back to the Idle state.
    """
    group = pygame.sprite.Group()       # ArcTrackers' own sprite group

    def __init__(self, pos):
        """
        Initializing method
        :param pos: starting position
        """

        pygame.sprite.Sprite.__init__(self)

        # Basic attributes
        self.state = "idle"             # ["idle", "ready", "moving"]
        self.x_pos, self.y_pos = pos    # Position on screen

        self.size = (30, 30)                                                    # Size of ArcTracker
        self.image = pygame.transform.scale(arc_tracker_img, self.size)         # Image of ArcTracker
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))        # A virtual rectangle which encloses ArcTracker

        self.rotation_axis = (0, 0)     # Position of axis ArcTracker rotate around
        self.rotation_angle = 0         # Rotating angle (in radians)
        self.direction_factor = 1       # 1 for counterclockwise, -1 for clockwise

        # To indicate whether mouse button is pressed
        self.mouse_pressed = False

        # Add this sprite to sprite groups
        all_sprites.add(self)
        self.group.add(self)

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        When the left mouse button is initially pressed, a virtual circular guideline appears in order to check
        ArkTracker's path to move around. This guideline's center will be the axis of rotation,
        and it always passes the center of ArcTracker. User can move the axis position until the mouse button is released.
        It is defined as an independent sprite class(ArcTrackerPath),
        and exists until moving process of ArcTracker finishes.

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        # At Idle state
        if self.state == "idle":
            # Enters to axis setting mode when holding mouse left button
            if not self.mouse_pressed and mouse_state[LCLICK]:
                self.mouse_pressed = True
                """ ArcTrackerPath generating code """

            # Set the position of rotation axis to current cursor position until mouse button is released
            if self.mouse_pressed:
                self.rotation_axis = mouse_state[CURPOS]

                # Change to Ready state and fix the rotation axis when releasing mouse left button
                if mouse_state[LCLICK]:
                    self.mouse_pressed = False
                    self.state = "ready"

        # At Ready state
        elif self.state == "ready":
            # Accepts only one input between left and right click
            if not self.mouse_pressed and (mouse_state[LCLICK] ^ mouse_state[RCLICK]):
                self.mouse_pressed = True
                self.direction_factor = 1 if mouse_state[LCLICK] else -1    # Set rotation direction

            # Change to Moving statewhen releasing mouse button
            if self.mouse_pressed and not (mouse_state[LCLICK] or mouse_state[RCLICK]):
                self.mouse_pressed = False
                self.state = "Moving"

        # At Moving state
        else:
            """ ArcTracker moving code """

            # Return to Idle state if left mouse button pressed when moving
            if mouse_state[LCLICK]:
                self.state = "idle"

        # Update position of ArcTracker
        self.rect.x = round(self.x_pos)
        self.rect.y = round(self.y_pos)


class ArcTrackerPath(pygame.sprite.Sprite):
    """
    A virtual circular guideline where ArcTracker passes through


    """

    def __init__(self):
        """
        Initializing method
        """

        pygame.sprite.Sprite.__init__(self)

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        pass




all_sprites = pygame.sprite.Group()     # Sprite group for update method


# Main game loop
while True:
    # Get all kind of events generated from mouse
    pygame.event.get()
    mouse[LCLICK], mouse[MCLICK], mouse[RCLICK], mouse[SCRLUP], mouse[SCRLDN] = pygame.mouse.get_pressed(5)
    mouse[CURPOS] = pygame.mouse.get_pos()        # Get cursor position on the screen

    # Get all kind of events generated from keyboard
    keys = pygame.key.get_pressed()

    # Quit game when clicking mouse wheel (needs to be modified)
    if mouse[MCLICK]:
        break

    all_sprites.update(mouse, keys)     # Call "update" method of every sprite

    screen.fill(BLACK)                  # Fill screen with black
    ArcTracker.group.draw(screen)       # Draw all ArcTrackers

    pygame.display.flip()               # Update all display changes and show them
    fps_clock.tick(FPS)                 # Make program never run at more than "FPS" frames per second
