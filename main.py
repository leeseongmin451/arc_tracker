import pygame
from pygame.locals import *
import math

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


def distance(pos1, pos2) -> float:
    """
    Returns distance of two positions with x, y coordinates
    :param pos1: position 1
    :param pos2: position 2
    :return: distance of the two positions
    """

    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def collide_with_rect(sprite: pygame.sprite.Sprite, rectgroup: pygame.sprite.Group) -> bool:
    """
    Detects if circular sprite collides with any of rectangular sprite in group

    :param sprite: circular sprite
    :param rectgroup: sprite group consists of only rectangular sprites
    :return: bool
    """

    # Return False if no sprite in the group
    if not rectgroup:
        return False

    # Get sprite's position & size
    sprite_centerx = sprite.rect.centerx
    sprite_centery = sprite.rect.centery
    sprite_radius = sprite.rect.w // 2

    # Repeat for every rect sprite in group
    def collided(spr):
        rect = spr.rect
        if abs(sprite_centerx - rect.centerx) > rect.w // 2 + sprite_radius or \
                abs(sprite_centery - rect.centery) > rect.h // 2 + sprite_radius:
            return False

        # Dealing with corner case (circle is nearby rentangle's corner)
        elif rect.w // 2 < abs(sprite_centerx - rect.centerx) <= rect.w // 2 + sprite_radius:
            if rect.h // 2 < abs(sprite_centery - rect.centery) <= rect.h // 2 + sprite_radius:
                return distance(sprite.rect.center, rect.center) <= sprite_radius
            else:
                return True

        else:
            return True

    # Repeat for every rect sprite in group
    return any(map(collided, rectgroup))


def collide_with_circle(sprite: pygame.sprite.Sprite, circgroup: pygame.sprite.Group) -> bool:
    """
    Detects if circular sprite collides with any of circular sprite in group

    :param sprite: circular sprite
    :param circgroup: sprite group consists of only circular sprites
    :return: bool
    """

    # Return False if no sprite in the group
    if not circgroup:
        return False

    # Get sprite's position & size
    sprite_center = sprite.rect.center
    sprite_radius = sprite.rect.w // 2

    # Repeat for every rect sprite in group
    def collided(spr):
        rect = spr.rect
        return distance(sprite_center, rect.center) < spr.radius + sprite_radius

    # Repeat for every rect sprite in group
    return any(map(collided, circgroup))


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
        self.initial_pos = pos          # Memorize stating position
        self.x_pos, self.y_pos = pos    # Position on screen

        self.size = (30, 30)                                                    # Size of ArcTracker
        self.image = pygame.transform.scale(arc_tracker_img, self.size)         # Image of ArcTracker
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))        # A virtual rectangle which encloses ArcTracker

        self.rotation_axis = (0, 0)         # Position of axis ArcTracker rotate around
        self.rotation_radius = 0            # Distance between ArcTracker's position and rotation axis
        self.rotation_speed = 240           # px/sec (NOT an angular speed)
        self.rotation_angular_speed = 0     # rad/sec
        # Relative angular position of ArcTracker with respect to rotation axis measured from horizontal x axis
        self.relative_angle = 0
        self.direction_factor = 1           # 1 for counterclockwise, -1 for clockwise

        # ArcTrackerPath class instance will be allocated if needed
        self.path = None

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
                self.path = ArcTrackerPath(mouse_state[CURPOS], self.rect.center)   # Generate ArcTrackerPath

            # Set the position of rotation axis to current cursor position until mouse button is released
            if self.mouse_pressed:
                self.rotation_axis = mouse_state[CURPOS]

                # Change to Ready state and fix the rotation axis when releasing mouse left button
                if not mouse_state[LCLICK]:
                    all_sprites.remove(self.path)
                    self.mouse_pressed = False
                    self.state = "ready"

        # At Ready state
        elif self.state == "ready":
            # Accepts only one input between left and right click
            if not self.mouse_pressed and (mouse_state[LCLICK] ^ mouse_state[RCLICK]):
                self.mouse_pressed = True

                # Calculate all variables needed for rotation
                self.rotation_radius = distance((self.x_pos, self.y_pos), self.rotation_axis)
                self.rotation_angular_speed = self.rotation_speed / self.rotation_radius
                self.relative_angle = math.atan2(self.y_pos - self.rotation_axis[1], self.x_pos - self.rotation_axis[0])
                self.direction_factor = -1 if mouse_state[LCLICK] else 1    # Set rotation direction

            # Change to Moving state when releasing mouse button
            if self.mouse_pressed and not (mouse_state[LCLICK] or mouse_state[RCLICK]):
                self.mouse_pressed = False
                self.state = "Moving"

            if (key_state[pygame.K_ESCAPE] or key_state[pygame.K_c]) and not (mouse_state[LCLICK] or mouse_state[RCLICK]):
                self.path.kill()
                self.path = None
                self.state = "idle"

        # At Moving state
        else:
            # Move ArcTracker
            self.relative_angle += self.direction_factor * self.rotation_angular_speed / FPS
            self.x_pos = self.rotation_axis[0] + self.rotation_radius * math.cos(self.relative_angle)
            self.y_pos = self.rotation_axis[1] + self.rotation_radius * math.sin(self.relative_angle)

            # If ArcTracker touches any kind of obstacles, it will be taken back to the initial position
            collided = False

            # Check collision with StaticRectangularObstacle
            if collide_with_rect(self, StaticRectangularObstacle.group):
                collided = True

            # Check collision with StaticCircularObstacle
            elif collide_with_circle(self, StaticCircularObstacle.group):
                collided = True

            if collided:
                self.path.kill()
                self.path = None
                self.x_pos, self.y_pos = self.initial_pos
                self.rect.center = self.initial_pos
                self.state = "idle"

            else:
                # Delete its path if left mouse button pressed when moving
                if not self.mouse_pressed and mouse_state[LCLICK]:
                    self.mouse_pressed = True
                    self.path.kill()
                    self.path = None

                # Return to Idle state if left mouse button released
                if self.mouse_pressed and not mouse_state[LCLICK]:
                    self.mouse_pressed = False
                    self.state = "idle"

        # Update position of ArcTracker
        self.rect.centerx = round(self.x_pos)
        self.rect.centery = round(self.y_pos)


class ArcTrackerPath(pygame.sprite.Sprite):
    """
    A virtual circular guideline where ArcTracker passes through

    Appears from first clicked time until complete moving. Invisible at Idle state of ArcTracker.
    """

    group = pygame.sprite.Group()  # ArcTrackerPath' own sprite group

    def __init__(self, cursor_pos, arc_tracker_pos):
        """
        Initializing method

        :param cursor_pos: Initial center position of circular path
        :param arc_tracker_pos: ArcTrackerPath will always pass this position
        """

        pygame.sprite.Sprite.__init__(self)

        self.x_pos, self.y_pos = cursor_pos                         # Center position of circular path
        self.arc_tracker_pos = arc_tracker_pos                      # Position of ArcTracker which will follow this path
        self.radius = distance(cursor_pos, self.arc_tracker_pos)    # Radius of circular path

        self.image = pygame.Surface((2 * self.radius, 2 * self.radius))     # Create a new surface object to draw circle on
        self.image.set_colorkey(BLACK)                                      # Initially make it fully transparent
        self.rect = self.image.get_rect(center=cursor_pos)                  # A virtual rectangle which encloses ArcTrackerPath
        # Draw a circle path on this surface
        pygame.draw.circle(self.image, WHITE2, (self.radius, self.radius), self.radius, 2)

        # Add this sprite to sprite groups
        all_sprites.add(self)
        self.group.add(self)

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.x_pos, self.y_pos = mouse_state[CURPOS]                        # Update center position of circular path
        self.radius = distance(mouse_state[CURPOS], self.arc_tracker_pos)   # Update radius of circular path

        # Redefine surface using updated position and radius
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius))     # Create a new surface object to draw circle on
        self.image.set_colorkey(BLACK)                                      # Initially make it fully transparent
        self.rect = self.image.get_rect(center=mouse_state[CURPOS])         # A virtual rectangle which encloses ArcTrackerPath
        # Draw a circle path on this surface
        pygame.draw.circle(self.image, WHITE2, (self.radius, self.radius), self.radius, 2)


class StaticRectangularObstacle(pygame.sprite.Sprite):
    """
    A normal, non-moving rectangular obstacle
    """

    group = pygame.sprite.Group()  # StaticRectangularObstacle' own sprite group

    def __init__(self, x, y, w, h):
        """
        Initializing method

        :param x: x position
        :param y: y position
        :param w: width
        :param h: height
        """

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((w, h))                 # Create a new rectangular surface object
        self.image.fill(WHITE1)                             # Fill in this surface with white
        self.rect = self.image.get_rect(topleft=(x, y))     # A virtual rectangle which encloses StaticRectangularObstacle

        # Add this sprite to sprite groups
        all_sprites.add(self)
        all_obstacles.add(self)
        self.group.add(self)

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """


class StaticCircularObstacle(pygame.sprite.Sprite):
    """
    A normal, non-moving circular obstacle
    """

    group = pygame.sprite.Group()  # StaticCircularObstacle' own sprite group

    def __init__(self, x, y, r):
        """
        Initializing method

        :param x: x position
        :param y: y position
        :param r: radius
        """

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((2 * r, 2 * r))         # Create a new rectangular surface object
        pygame.draw.circle(self.image, WHITE1, (r, r), r)   # Draw a circle in this surface
        self.rect = self.image.get_rect(center=(x, y))      # A virtual rectangle which encloses StaticCircularObstacle
        self.radius = r                                     # Used for collision detection

        # Add this sprite to sprite groups
        all_sprites.add(self)
        all_obstacles.add(self)
        self.group.add(self)

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """


all_sprites = pygame.sprite.Group()     # Sprite group for update method
all_obstacles = pygame.sprite.Group()     # Sprite group for all obstacles
arc_tracker = ArcTracker((960, 540))
test_obstacle = StaticCircularObstacle(200, 200, 100)


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
    all_obstacles.draw(screen)          # Draw all obstacle objects
    ArcTrackerPath.group.draw(screen)   # Draw all ArcTrackerPaths
    ArcTracker.group.draw(screen)       # Draw all ArcTrackers

    pygame.display.flip()               # Update all display changes and show them
    fps_clock.tick(FPS)                 # Make program never run at more than "FPS" frames per second
