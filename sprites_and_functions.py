"""
Define all sprites and functions needed
"""
import pygame.sprite

from init import *
import math


def distance(pos1, pos2):
    """
    Returns distance of two positions with x, y coordinates
    :param pos1: position 1
    :param pos2: position 2
    :return: distance of the two positions
    """

    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def collide_with_line_segment(circular_sprite: pygame.sprite.Sprite, pos1, pos2) -> bool:
    """
    Detects if circular sprite collides with a line segment given by two positions

    :param circular_sprite: circular sprite
    :param pos1: one position of line segment
    :param pos2: other position of line segment
    :return: bool
    """

    # Get sprite's position & size
    sprite_centerx = circular_sprite.rect.centerx
    sprite_centery = circular_sprite.rect.centery
    sprite_radius = circular_sprite.rect.w // 2

    length = distance(pos1, pos2)                   # Length of line segment
    x_diff = pos1[0] - pos2[0]                      # Difference of x coordinates of two positions
    y_diff = pos1[1] - pos2[1]                      # Difference of y coordinates of two positions
    x_mid = (pos1[0] + pos2[0]) / 2                 # x coordinate of midpoint of the segment
    y_mid = (pos1[1] + pos2[1]) / 2                 # y coordinate of midpoint of the segment

    close_to_line = abs(y_diff*sprite_centerx - x_diff*sprite_centery + pos1[0]*pos2[1] - pos1[1]*pos2[0]) / length <= sprite_radius
    within_segment = abs(x_diff*sprite_centerx + y_diff*sprite_centery - x_diff*x_mid - y_diff*y_mid) / length <= length / 2

    return close_to_line and within_segment


def collide_with_rect(circular_sprite: pygame.sprite.Sprite, rectangular_sprite: pygame.sprite.Sprite) -> bool:
    """
    Detects if circular sprite collides with other rectangular sprite

    :param circular_sprite: circular sprite
    :param rectangular_sprite: rectangular sprite
    :return: bool
    """

    # Get sprite's position & size
    sprite_centerx = circular_sprite.rect.centerx
    sprite_centery = circular_sprite.rect.centery
    sprite_radius = circular_sprite.rect.w // 2

    # Detect collision
    rect = rectangular_sprite.rect
    if abs(sprite_centerx - rect.centerx) > rect.w // 2 + sprite_radius or \
            abs(sprite_centery - rect.centery) > rect.h // 2 + sprite_radius:
        return False

    # Dealing with corner case (circle is nearby rentangle's corner)
    elif rect.w // 2 < abs(sprite_centerx - rect.centerx) <= rect.w // 2 + sprite_radius:
        if rect.h // 2 < abs(sprite_centery - rect.centery) <= rect.h // 2 + sprite_radius:
            return distance(circular_sprite.rect.center, rect.center) <= sprite_radius
        else:
            return True

    else:
        return True


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
        self.initial_pos = pos          # Initial position
        self.x_pos, self.y_pos = pos    # Position on screen

        self.size = (30, 30)                                                    # Size of ArcTracker
        self.image = pygame.transform.scale(arc_tracker_img, self.size)         # Image of ArcTracker
        self.mask = pygame.mask.from_surface(self.image)                        # Create a mask object for collision detection
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))        # A virtual rectangle which encloses ArcTracker

        self.rotation_axis = (0, 0)         # Position of axis ArcTracker rotate around
        self.rotation_radius = 0            # Distance between ArcTracker's position and rotation axis
        self.rotation_speed = 360           # px/sec (NOT an angular speed)
        self.rotation_angular_speed = 0     # rad/sec
        # Relative angular position of ArcTracker with respect to rotation axis measured from horizontal x axis
        self.relative_angle = 0
        self.direction_factor = 1           # 1 for counterclockwise, -1 for clockwise

        # ArcTrackerPath class instance will be allocated if needed
        self.path = None

        # To indicate whether mouse button is pressed
        self.mouse_pressed = False

        # Add this sprite to sprite groups
        self.group.add(self)

    def initialize(self):
        """
        Initializing method during gameplay

        :return: None
        """

        if self.path:
            self.path.kill()
            self.path = None
        self.state = "idle"
        self.x_pos, self.y_pos = self.initial_pos
        self.mouse_pressed = False

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
                    self.mouse_pressed = False
                    self.state = "ready"

            # Update path of ArcTracker only at Idle state
            if self.path:
                self.path.update(mouse_state, key_state)

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

            # Stop AcrTrakcer and delete its path if left mouse button pressed when moving
            if not self.mouse_pressed and mouse_state[LCLICK]:
                self.rotation_angular_speed = 0
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


class GoalPoint(pygame.sprite.Sprite):
    """
    A point where ArcTracker should reach in a single level.
    """

    def __init__(self, pos):
        """
        Initializing method

        :param pos: Position of GoalPoint
        """

        pygame.sprite.Sprite.__init__(self)

        self.pos = pos              # Position of GoalPoint
        self.frame_num = 0          # Current frame number of animation list
        self.image = goal_point_img_list[self.frame_num]        # Current image of GoalPoint
        self.rect = self.image.get_rect(center=self.pos)        # A virtual rectangle which encloses GoalPoint


    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        Switch image at every frame to display animating effect of GoalPoint

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.image = goal_point_img_list[self.frame_num]
        self.frame_num = (self.frame_num + 1) % 60


class Obstacle(pygame.sprite.Sprite):
    """
    A normal, non-moving obstacle class
    """

    def __init__(self):
        """
        Initializing method
        """

        pygame.sprite.Sprite.__init__(self)

    def initialize(self):
        """
        Initializing method during gameplay

        :return: None
        """

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

    def collided(self, sprite: pygame.sprite.Sprite) -> bool:
        """
        Check collision with given sprite

        :param sprite: Sprite to check collision
        :return: bool
        """

        return bool(pygame.sprite.collide_mask(self, sprite))


class StaticRectangularObstacle(Obstacle):
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

        Obstacle.__init__(self)

        self.image = pygame.Surface((w, h))                 # Create a new rectangular surface object
        self.image.fill(WHITE1)                             # Fill in this surface with white
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection
        self.rect = self.image.get_rect(topleft=(x, y))     # A virtual rectangle which encloses StaticRectangularObstacle

        # Add this sprite to sprite groups
        self.group.add(self)


class StaticCircularObstacle(Obstacle):
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

        Obstacle.__init__(self)

        self.image = pygame.Surface((2 * r, 2 * r))         # Create a new rectangular surface object
        self.image.set_colorkey(BLACK)                      # Initially make it fully transparent
        pygame.draw.circle(self.image, WHITE1, (r, r), r)   # Draw a circle in this surface
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection
        self.rect = self.image.get_rect(center=(x, y))      # A virtual rectangle which encloses StaticCircularObstacle
        self.radius = r                                     # Used for collision detection

        # Add this sprite to sprite groups
        self.group.add(self)

    def collided(self, sprite: pygame.sprite.Sprite) -> bool:
        """
        Check collision with given sprite

        Since there is more simple collision detecting algorithm using distsnce and redius,
        this method does not use mask object.

        :param sprite: Sprite to check collision
        :return: bool
        """

        return distance(self.rect.center, sprite.rect.center) < self.radius + sprite.rect.w // 2


class StaticPolygonObstacle(Obstacle):
    """
    A normal, non-moving, and any kind of polygon-shaped obstacle
    """

    group = pygame.sprite.Group()  # StaticPolygonObstacle's own sprite group

    def __init__(self, *vertices):
        """
        Initializing method

        :param vertices: sequence of 3 or more coordinates
        """

        Obstacle.__init__(self)

        # Get all given vertices
        self.vertices_list = []
        for v in vertices:
            self.vertices_list.append(v)

        # Get maximum and minimum value of each coordinate
        # (for calculating size and position of virtual rectangle)
        max_x = max([p[0] for p in self.vertices_list])
        min_x = min([p[0] for p in self.vertices_list])
        max_y = max([p[1] for p in self.vertices_list])
        min_y = min([p[1] for p in self.vertices_list])

        w, h = max_x - min_x, max_y - min_y
        self.image = pygame.Surface((w, h))                         # Create a new rectangular surface object
        self.image.set_colorkey(BLACK)                              # Initially make it fully transparent

        # Draw polygon in this surface with given vertices
        relative_vertices_list = [[p[0] - min_x, p[1] - min_y] for p in self.vertices_list]
        pygame.draw.polygon(self.image, WHITE1, relative_vertices_list)

        self.mask = pygame.mask.from_surface(self.image)            # Create a mask object for collision detection
        self.rect = self.image.get_rect(topleft=(min_x, min_y))     # A virtual rectangle which encloses StaticPolygonObstacle

        # Add this sprite to sprite groups
        self.group.add(self)


class StaticRightTriangularObstacle(Obstacle):
    """
    A normal, non-moving, right-triangular obstacle
    """

    group = pygame.sprite.Group()  # StaticRightTriangularObstacle's own sprite group

    def __init__(self, x, y, w, h, del_angle_pos="topleft"):
        """
        Initializing method

        :param x: x position
        :param y: y position
        :param w: width
        :param h: height
        :param del_angle_pos: opposite position of right angle, which is not included in right triangle
                              (can be "topleft", "topright", "bottomleft", "bottomright")
        """

        Obstacle.__init__(self)

        # Select 3 vertices of right triangle
        vertices_dict = {"topleft": (0, 0), "topright": (w, 0), "bottomleft": (0, h), "bottomright": (w, h)}
        del vertices_dict[del_angle_pos]

        self.image = pygame.Surface((w, h))                 # Create a new rectangular surface object
        self.image.set_colorkey(BLACK)                      # Initially make it fully transparent
        # Draw a right triangle in this surface
        pygame.draw.polygon(self.image, WHITE1, list(vertices_dict.values()))
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection
        self.rect = self.image.get_rect(topleft=(x, y))     # A virtual rectangle which encloses StaticRightTriangularObstacle

        # Generate list of vertices to deal with it using the same method as StaticPolygonObstacle
        self.vertices_dict = {"topleft": self.rect.topleft,
                              "topright": self.rect.topright,
                              "bottomleft": self.rect.bottomleft,
                              "bottomright": self.rect.bottomright}
        del self.vertices_dict[del_angle_pos]
        self.vertices_list = list(self.vertices_dict.values())

        # Add this sprite to sprite groups
        self.group.add(self)
