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
        self.min_path_radius = 150

        # MinimumRadiusBorderLine class instance will be allocated if needed
        self.borderline = None

        # To indicate whether mouse button is pressed
        self.mouse_pressed = False

        # A reference to determine raise popup
        self.raise_popup = False

        # Whether ArcTracker reached to GoalPoint
        self.level_complete = False

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
        if self.borderline:
            self.borderline.kill()
            self.borderline = None
        self.state = "idle"
        self.x_pos, self.y_pos = self.initial_pos

        # Initializing all boolean variables
        self.mouse_pressed = False
        self.raise_popup = False
        self.level_complete = False

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

        # All operations of ArcTracker are available only before reaching goal point
        if not self.level_complete:
            # At Idle state
            if self.state == "idle":
                # Enters to axis setting mode when holding mouse left button
                if not self.mouse_pressed and mouse_state[LCLICK]:
                    self.mouse_pressed = True
                    self.path = ArcTrackerPath(mouse_state[CURPOS], self.rect.center)                   # Generate ArcTrackerPath
                    self.borderline = MinimumRadiusBorderLine(self.rect.center, self.min_path_radius)   # Generate MinimumRadiusBorderLine

                # Set the position of rotation axis to current cursor position until mouse button is released
                if self.mouse_pressed:
                    self.rotation_axis = mouse_state[CURPOS]

                    # When releasing mouse left button
                    # And delete MinimumRadiusBorderLine
                    if not mouse_state[LCLICK]:
                        self.borderline.kill()
                        self.borderline = None
                        self.mouse_pressed = False

                        # Calculate rotation radius
                        self.rotation_radius = distance((self.x_pos, self.y_pos), self.rotation_axis)

                        # Change to Ready state and fix the rotation axis if radius of orbit is valid
                        if self.rotation_radius >= self.min_path_radius:
                            self.state = "ready"
                        # Stay in Idle state and delete orbit if radius is invalid
                        else:
                            self.raise_popup = True
                            self.reject_path()

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

    def reject_path(self) -> None:
        """
        Delete path

        :return: None
        """

        if self.path:
            self.path.kill()
            self.path = None
        self.state = "idle"


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


class MinimumRadiusBorderLine(pygame.sprite.Sprite):
    """
    A border line class which encloses around ArcTracker

    It informs that player cannot generate orbit whose radius is smaller than the radius of it.
    It has red circular shape.
    It is generated during Idle state of ArcTracker when dragging mouse to set an orbit.
    """

    group = pygame.sprite.Group()  # MinimumRadiusBorderLine' own sprite group

    def __init__(self, center, radius):
        """
        Initializing method

        :param center: center of MinimumRadiusBorderLine
        :param radius: radius of MinimumRadiusBorderLine
        """

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((2 * radius, 2 * radius))   # Create a new surface object to draw circle on
        self.image.set_colorkey(BLACK)                          # Initially make it fully transparent
        self.rect = self.image.get_rect(center=center)          # A virtual rectangle which encloses MinimumRadiusBorderLine
        # Draw a circle border line on this surface
        pygame.draw.circle(self.image, RED1, (radius, radius), radius, 2)

        # Add this sprite to sprite groups
        self.group.add(self)

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """


class Coin(pygame.sprite.Sprite):
    """
    A coin class which ArcTracker should collect

    Coin has a tiny round shape, and wellow color. ArcTracker must collect all coins
    before reaching goal to complete a level.
    """

    group = pygame.sprite.Group()

    def __init__(self, pos):
        """
        Initializing method

        :param pos: center position of coin
        """

        pygame.sprite.Sprite.__init__(self)

        self.size = (10, 10)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, YELLOW1, (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)

    def initialize(self):
        """
        Initialize this coin

        :return: None
        """

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """


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

        # Whether ArcTracker reached to GoalPoint
        self.arctracker_matched = False

    def initialize(self):
        """
        Initialize this goal point

        :return: None
        """

        self.arctracker_matched = False

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

        # Add this sprite to sprite groups
        self.group.add(self)


class StaticInnerCurvedObstacle(Obstacle):
    """
    A normal, non-moving, obstacle

    It is similar to regular static obstacles, but is cut off in arc shape using transparent circle
    """

    group = pygame.sprite.Group()  # StaticInnerCurvedObstacle's own sprite group

    def __init__(self, original_obstacle_class, params: tuple, inner_curve_center: (int, int), inner_curve_radius: float):
        """
        Initializing method

        :param original_obstacle_class: original obstacle class
        :param params: parameters needed for creating obstacle class instance
        :param inner_curve_center: center of transparent circle
        :param inner_curve_radius: radius of transparent circle
        """

        # Create original obstacle
        original_obstacle_class.__init__(self, *params)

        # Cut off this obstacle in arc shape by drawing transparent circle
        relative_centerx = inner_curve_center[0] - self.rect.x
        relative_centery = inner_curve_center[1] - self.rect.y
        pygame.draw.circle(self.image, BLACK, (relative_centerx, relative_centery), inner_curve_radius)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection

        # Add this sprite to sprite groups
        self.group.add(self)


class StaticImageObstacle(Obstacle):
    """
    A normal, non-moving obstacle class which uses a black-and-white image

    Black will be considered as background, and white will be the obstacle
    """

    group = pygame.sprite.Group()   # StaticInnerCurvedObstacle's own sprite group

    def __init__(self, image: pygame.Surface, rect: list):
        """
        Initializing method

        :param image: A black-and-white image
        :param rect: Position and size of this obstacle
        """

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(image, rect[2:])    # Create a new rectangular surface object
        self.image.set_colorkey(BLACK)                          # Make the black bakground fully transparent
        self.mask = pygame.mask.from_surface(self.image)        # Create a mask object for collision detection
        self.rect = self.image.get_rect(topleft=rect[:2])       # A virtual rectangle which encloses StaticImageObstacle

        # Add this sprite to sprite groups
        self.group.add(self)


class ObstaclePath:
    """
    A path needed for moving obstacles

    It is represented by a combination of multiple segments
    """

    def __init__(self):
        pass


class ObstaclePathSegment:
    """
    A segment as a part of the ObstaclePath
    """

    def __init__(self):
        pass


class LinearMovingRectangularObstacle(Obstacle):
    """
    A rectangular obstacle which moves through straight line in a given period
    """

    def __init__(self):
        pass


class LinearMovingCircularObstacle(Obstacle):
    """
    A circular obstacle which moves through straight line in a given period
    """

    def __init__(self):
        pass


class LinearMovingImageObstacle(Obstacle):
    """
    An obstacle which moves through straight line in a given period

    Its shape will be determined by masking the given image
    """

    def __init__(self):
        pass


class OrbittingRectangularObstacle(Obstacle):
    """
    A rectangular obstacle which orbits around a given point in a given period
    """

    def __init__(self):
        pass


class OrbittingCircularObstacle(Obstacle):
    """
    A circular obstacle which orbits around a given point in a given period
    """

    def __init__(self):
        pass


class OrbittingImageObstacle(Obstacle):
    """
    An obstacle which orbits around a given point in a given period

    Its shape will be determined by masking the given image
    """

    def __init__(self):
        pass


class OpenedGeneralPathRectangularObstacle(Obstacle):
    """
    A rectangular obstacle which moves through opened path in a given period
    """

    def __init__(self):
        pass


class OpenedGeneralPathCircularObstacle(Obstacle):
    """
    A circular obstacle which moves through opened path in a given period
    """

    def __init__(self):
        pass


class OpenedGeneralPathImageObstacle(Obstacle):
    """
    An obstacle which moves through opened path in a given period

    Its shape will be determined by masking the given image
    """

    def __init__(self):
        pass


class ClosedGeneralPathRectangularObstacle(Obstacle):
    """
    A rectangular obstacle which moves through closed path in a given period
    """

    def __init__(self):
        pass


class ClosedGeneralPathCircularObstacle(Obstacle):
    """
    A circular obstacle which moves through closed path in a given period
    """

    def __init__(self):
        pass


class ClosedGeneralPathImageObstacle(Obstacle):
    """
    An obstacle which moves through closed path in a given period

    Its shape will be determined by masking the given image
    """

    def __init__(self):
        pass


class RotatingRectangularObstacle(Obstacle):
    """
    A rotating rectangular obstacle using its own axis
    """

    def __init__(self):
        pass


class RotatingImageObstacle(Obstacle):
    """
    A rotating obstacle using its own axis
    """

    group = pygame.sprite.Group()   # RotatingImageObstacle' own sprite group

    def __init__(self, image: pygame.Surface, axis_pos: (int, int), rotation_speed: float):
        """
        Initializing method

        :param image: A black-and-white image
        :param axis_pos: Position of rotation axis
        :param rotation_speed: Rotationg speed (degrees/sec)
        """

        pygame.sprite.Sprite.__init__(self)

        self.image = image                                  # Create a new rectangular surface object
        self.image_orig = image                             # Used for rotating
        self.image.set_colorkey(BLACK)                      # Make the black bakground fully transparent
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection
        self.rect = self.image.get_rect(center=axis_pos)    # A virtual rectangle which encloses RotatingImageObstacle
        self.center_orig = axis_pos                         # For preserving rotation axis

        self.rotation_speed = rotation_speed    # Angular speed of rotation in degrees/sec
        self.current_angle = 0

        # Add this sprite to sprite groups
        self.group.add(self)

    def initialize(self):
        """
        Initializing method during gameplay

        :return: None
        """

        self.current_angle = 0      # Reset angle to 0

    def update(self, mouse_state, key_state) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.current_angle += self.rotation_speed / FPS   # Update angle
        self.image = pygame.transform.rotate(self.image_orig, self.current_angle)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.center_orig)


class AngleFollowerRectangularObstacle(Obstacle):
    """
    A rectangular obstacle whose rotation exactly follows ArcTracker's angular motion
    """

    def __init__(self):
        pass


class AngleFollowerImageObstacle(Obstacle):
    """
    An obstacle whose rotation exactly follows ArcTracker's angular motion

    Its shape will be determined by masking the given image
    """

    def __init__(self):
        pass
