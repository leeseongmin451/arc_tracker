"""
Define all sprites and functions needed
"""
import pygame.sprite

import init
from init import *
import math
from typing import Union, Dict, Sequence, Tuple, List
from typing import Callable
import copy


def distance(pos1: (Union[int, float], Union[int, float]),
             pos2: (Union[int, float], Union[int, float])) -> Union[int, float]:
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

    def __init__(self, pos: (int, int), id_num: int, min_orbit_radius: int):
        """
        Initializing method
        :param pos: starting position
        :param id_num: ID number for multiple ArcTrackers, 1 for green, 2 for blue, and 3 for red
        :param min_orbit_radius: minimum radius of the generatable orbit
        """

        pygame.sprite.Sprite.__init__(self)

        # Basic attributes
        self.state = "idle"             # ["idle", "ready", "moving"]
        self.initial_pos = pos          # Initial position
        self.x_pos, self.y_pos = pos    # Position on screen
        self.id_num = id_num            # ID number of ArcTracker

        self.size = (30, 30)                                                                # Size of ArcTracker
        self.image = pygame.transform.scale(arc_tracker_img_list[id_num - 1], self.size)    # Image of ArcTracker
        self.mask = pygame.mask.from_surface(self.image)                                    # Create a mask object for collision detection
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))                    # A virtual rectangle which encloses ArcTracker

        self.rotation_axis = (0, 0)         # Position of axis ArcTracker rotate around
        self.rotation_radius = 0            # Distance between ArcTracker's position and rotation axis
        self.rotation_speed = 360           # px/sec (NOT an angular speed)
        self.rotation_angular_speed = 0     # rad/sec
        # Relative angular position of ArcTracker with respect to rotation axis measured from horizontal x axis
        self.relative_angle = 0
        self.direction_factor = 1           # 1 for counterclockwise, -1 for clockwise
        self.angular_speed_per_frame = 0

        # ArcTrackerPath class instance will be allocated if needed
        self.path = None
        self.min_path_radius = min_orbit_radius

        # MinimumRadiusBorderLine class instance will be allocated if needed
        self.borderline = None

        # RotationAxisMarker class instance will be allocated if needed
        self.axis_marker = None

        # To indicate whether mouse button is pressed
        self.mouse_pressed = False

        # A reference to determine raise popup
        self.raise_popup = False

        # Whether ArcTracker reached to GoalPoint
        self.level_complete = False

        # Add this sprite to sprite groups
        self.group.add(self)

    def initialize(self) -> None:
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
        if self.axis_marker:
            self.axis_marker.kill()
            self.axis_marker = None
        self.state = "idle"
        self.x_pos, self.y_pos = self.initial_pos
        self.rect.center = self.initial_pos

        # Initializing all boolean variables
        self.mouse_pressed = False
        self.raise_popup = False
        self.level_complete = False

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
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
            # Angular speed will be nonzero only at Moving state
            self.angular_speed_per_frame = 0

            # At Idle state
            if self.state == "idle":
                # Enters to axis setting mode when holding mouse left button
                if not self.mouse_pressed and mouse_state[LCLICK]:
                    self.mouse_pressed = True
                    self.path = ArcTrackerPath(mouse_state[CURPOS], self.rect.center)                   # Generate ArcTrackerPath
                    self.borderline = MinimumRadiusBorderLine(self.rect.center, self.min_path_radius)   # Generate MinimumRadiusBorderLine
                    self.axis_marker = RotationAxisMarker(self)                                         # Generate RotationAxisMarker

                # Set the position of rotation axis to current cursor position until mouse button is released
                if self.mouse_pressed:
                    self.rotation_axis = mouse_state[CURPOS]

                    # When releasing mouse left button
                    # And delete MinimumRadiusBorderLine
                    if not mouse_state[LCLICK]:
                        self.borderline.kill()
                        self.borderline = None
                        self.axis_marker.kill()
                        self.axis_marker = None
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
                # Update axis marker of ArcTracker only at Idle state
                if self.axis_marker:
                    self.axis_marker.update(mouse_state, key_state)

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
                self.angular_speed_per_frame = self.direction_factor * self.rotation_angular_speed * init.DELTA_TIME
                self.relative_angle += self.angular_speed_per_frame
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

        else:
            self.angular_speed_per_frame = 0

    def reject_path(self) -> None:
        """
        Delete path

        :return: None
        """

        if self.path:
            self.path.kill()
            self.path = None
        self.state = "idle"


class ArcTrackerClone(pygame.sprite.Sprite):
    """
    Moves in exactly the same pattern with ArcTracker

    When rotation axis of ArcTracker is set, another axis for ArcTrackerClone will be set.

    """
    group = pygame.sprite.Group()       # ArcTrackers' own sprite group

    def __init__(self, pos: (int, int), id_num: int, min_orbit_radius: int, host: ArcTracker, move_opposite_direction=False):
        """
        Initializing method
        :param pos: starting position
        :param id_num: ID number for multiple ArcTrackers, 1 for green, 2 for blue, and 3 for red
        :param min_orbit_radius: minimum radius of the generatable orbit
        :param host: ArcTracker to follow movement
        :param move_opposite_direction: boolean value for moving direction (True for movind opposite direction of its pair ArcTracker)
        """

        pygame.sprite.Sprite.__init__(self)

        # Basic attributes
        self.state = "idle"             # ["idle", "ready", "moving"]
        self.initial_pos = pos          # Initial position
        self.x_pos, self.y_pos = pos    # Position on screen
        self.id_num = id_num            # ID number of ArcTrackerClone
        # Determine whether move to the same or opposite direction to ArcTracker
        self.move_opposite_direction = move_opposite_direction

        self.size = (30, 30)                                                                # Size of ArcTrackerClone
        # Image of ArcTrackerClone
        if not move_opposite_direction:
            self.image = pygame.transform.scale(arc_tracker_clone_img_list[id_num - 1], self.size)
        else:
            self.image = pygame.transform.scale(arc_tracker_counter_clone_img_list[id_num - 1], self.size)
        self.mask = pygame.mask.from_surface(self.image)                                    # Create a mask object for collision detection
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))                    # A virtual rectangle which encloses ArcTrackerClone

        self.rotation_axis = (0, 0)         # Position of axis ArcTrackerClone rotate around
        self.rotation_radius = 0            # Distance between ArcTrackerClone's position and rotation axis
        self.rotation_speed = 360           # px/sec (NOT an angular speed)
        self.rotation_angular_speed = 0     # rad/sec
        # Relative angular position of ArcTrackerClone with respect to rotation axis measured from horizontal x axis
        self.relative_angle = 0
        self.direction_factor = 1           # 1 for counterclockwise, -1 for clockwise
        self.angular_speed_per_frame = 0

        # ArcTrackerPath class instance will be allocated if needed
        self.path = None
        self.min_path_radius = min_orbit_radius

        # MinimumRadiusBorderLine class instance will be allocated if needed
        self.borderline = None

        # RotationAxisMarker class instance will be allocated if needed
        self.axis_marker = None

        # To indicate whether mouse button is pressed
        self.mouse_pressed = False

        # A reference to determine raise popup
        self.raise_popup = False

        # Whether ArcTracker reached to GoalPoint
        self.level_complete = False

        # Add this sprite to sprite groups
        self.group.add(self)

        # ArcTracker to follow movement
        self.host = host

        # Relative x, y, position of rotation axis with respect to ArcTrackerClone
        self.relative_axis_x = 0
        self.relative_axis_y = 0

        # Position of its own rotation axis (determined by cursor position)
        self.new_axis = (0, 0)


    def initialize(self) -> None:
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
        if self.axis_marker:
            self.axis_marker.kill()
            self.axis_marker = None
        self.state = "idle"
        self.x_pos, self.y_pos = self.initial_pos
        self.rect.center = self.initial_pos

        # Initializing all boolean variables
        self.mouse_pressed = False
        self.raise_popup = False
        self.level_complete = False

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        # All operations of ArcTrackerClone are available only before reaching goal point
        if not self.level_complete:
            # Angular speed will be nonzero only at Moving state
            self.angular_speed_per_frame = 0

            # At Idle state
            if self.state == "idle":
                # Enters to axis setting mode when holding mouse left button
                if not self.mouse_pressed and mouse_state[LCLICK]:
                    self.mouse_pressed = True

                    self.relative_axis_x = mouse_state[CURPOS][0] - self.host.rect.centerx
                    self.relative_axis_y = mouse_state[CURPOS][1] - self.host.rect.centery
                    self.new_axis = (self.rect.centerx + self.relative_axis_x,
                                     self.rect.centerx + self.relative_axis_y)

                    self.path = ArcTrackerPath(self.new_axis, self.rect.center)                   # Generate ArcTrackerPath
                    self.borderline = MinimumRadiusBorderLine(self.rect.center, self.min_path_radius)   # Generate MinimumRadiusBorderLine
                    self.axis_marker = RotationAxisMarker(self)                                         # Generate RotationAxisMarker

                # Set the position of rotation axis to current cursor position until mouse button is released
                if self.mouse_pressed:
                    self.rotation_axis = self.new_axis

                    # When releasing mouse left button
                    # And delete MinimumRadiusBorderLine
                    if not mouse_state[LCLICK]:
                        self.borderline.kill()
                        self.borderline = None
                        self.axis_marker.kill()
                        self.axis_marker = None
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

                # Calculate current position of rotation axis of ArcTrackerClone
                new_mouse_state = copy.deepcopy(mouse_state)

                self.relative_axis_x = mouse_state[CURPOS][0] - self.host.rect.centerx
                self.relative_axis_y = mouse_state[CURPOS][1] - self.host.rect.centery
                self.new_axis = (self.rect.centerx + self.relative_axis_x,
                                 self.rect.centery + self.relative_axis_y)
                new_mouse_state[CURPOS] = self.new_axis

                # Update path of ArcTrackerClone only at Idle state
                if self.path:
                    self.path.update(new_mouse_state, key_state)
                # Update axis marker of ArcTrackerClone only at Idle state
                if self.axis_marker:
                    self.axis_marker.update(new_mouse_state, key_state)

            # At Ready state
            elif self.state == "ready":
                # Accepts only one input between left and right click
                if not self.mouse_pressed and (mouse_state[LCLICK] ^ mouse_state[RCLICK]):
                    self.mouse_pressed = True

                    # Calculate all variables needed for rotation
                    self.rotation_radius = distance((self.x_pos, self.y_pos), self.rotation_axis)
                    self.rotation_angular_speed = self.rotation_speed / self.rotation_radius
                    self.relative_angle = math.atan2(self.y_pos - self.rotation_axis[1], self.x_pos - self.rotation_axis[0])

                    # Set rotation direction of ArcTrackerClone
                    if not self.move_opposite_direction:
                        self.direction_factor = -1 if mouse_state[LCLICK] else 1
                    else:
                        self.direction_factor = 1 if mouse_state[LCLICK] else -1

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
                # Move ArcTrackerClone
                self.angular_speed_per_frame = self.direction_factor * self.rotation_angular_speed * init.DELTA_TIME
                self.relative_angle += self.angular_speed_per_frame
                self.x_pos = self.rotation_axis[0] + self.rotation_radius * math.cos(self.relative_angle)
                self.y_pos = self.rotation_axis[1] + self.rotation_radius * math.sin(self.relative_angle)

                # Stop ArcTrackerClone and delete its path if left mouse button pressed when moving
                if not self.mouse_pressed and mouse_state[LCLICK]:
                    self.rotation_angular_speed = 0
                    self.mouse_pressed = True
                    self.path.kill()
                    self.path = None

                # Return to Idle state if left mouse button released
                if self.mouse_pressed and not mouse_state[LCLICK]:
                    self.mouse_pressed = False
                    self.state = "idle"

            # Update position of ArcTrackerClone
            self.rect.centerx = round(self.x_pos)
            self.rect.centery = round(self.y_pos)

        else:
            self.angular_speed_per_frame = 0

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

    def __init__(self, cursor_pos: (int, int), arc_tracker_pos: (int, int)):
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

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
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

    def __init__(self, center: (int, int), radius: int):
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

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """


class RotationAxisMarker(pygame.sprite.Sprite):
    """
    A marker temporarily appears while setting orbit of ArcTracker

    This represents the position of rotation axis.
    If mouse cursor is out of borderline, it will appear as a blueish "O" sign, otherwise a reddish "X" sign.
    """

    group = pygame.sprite.Group()   # RotationAxisMarker' own sprite group

    def __init__(self, arc_tracker: Union[ArcTracker, ArcTrackerClone]):
        """
        Initializing method

        :param arc_tracker: ArcTracker which this marker belongs to
        """

        pygame.sprite.Sprite.__init__(self)

        self.at = arc_tracker       # ArcTracker which this marker belongs to

        # Determine current image according to whether cursor position is out of borderline
        self.image_list = [axis_marker_O_img, axis_marker_X_img]
        if distance(mouse[CURPOS], self.at.rect.center) >= self.at.min_path_radius:
            self.image = self.image_list[0]
        else:
            self.image = self.image_list[1]
        self.rect = self.image.get_rect(center=mouse[CURPOS])

        # Add this sprite to sprite groups
        self.group.add(self)

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.rect.center = mouse_state[CURPOS]      # Update position

        # Update current image according to whether cursor position is out of borderline
        self.image_list = [axis_marker_O_img, axis_marker_X_img]
        if distance(mouse_state[CURPOS], self.at.rect.center) >= self.at.min_path_radius:
            self.image = self.image_list[0]
        else:
            self.image = self.image_list[1]


class Coin(pygame.sprite.Sprite):
    """
    A coin class which ArcTracker should collect

    Coin has a tiny round shape, and wellow color. ArcTracker must collect all coins
    before reaching goal to complete a level.
    """

    group = pygame.sprite.Group()

    def __init__(self, pos: (int, int)):
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

    def initialize(self) -> None:
        """
        Initialize this coin

        :return: None
        """

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
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

    def __init__(self, pos: (int, int)):
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

        self.sec_per_frame = 1 / FPS        # Seconds per frame
        self.animated_time = 0              # Elapsed time from init

    def initialize(self) -> None:
        """
        Initialize this goal point

        :return: None
        """

        self.arctracker_matched = False

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        Switch image at every frame to display animating effect of GoalPoint

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.image = goal_point_img_list[self.frame_num]
        #self.frame_num = (self.frame_num + 1) % 60
        self.animated_time += init.DELTA_TIME
        self.frame_num = int(self.animated_time / self.sec_per_frame) % 60


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

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
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

    def __init__(self, x: int, y: int, w: int, h: int):
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

    def __init__(self, x: int, y: int, r: int):
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

    def __init__(self, *vertices: Tuple[int, int]):
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

    def __init__(self, x: int, y: int, w: int, h: int, del_angle_pos="topleft"):
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

    def __init__(self, image: pygame.Surface, rect: List[int]):
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

    It is represented by a combination of multiple ObstaclePathSegment
    """

    def __init__(self):
        pass


class ObstaclePathSegment:
    """
    A segment as a part of the ObstaclePath
    """

    def __init__(self, x: Callable, y: Callable):
        self.x, self.y = x, y

    def get_pos(self, t: Union[int, float]) -> (Union[int, float], Union[int, float]):
        """
        Returns position on this path segment at time t

        :param t: time
        :return: position at time t
        """

        return self.x(t), self.y(t)


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

    group = pygame.sprite.Group()   # RotatingRectangularObstacle' own sprite group

    def __init__(self, size: (int, int), rotation_axis: (int, int), angular_speed: Union[int, float], initial_angle=0, center_offset=(0, 0)):
        """
        Initializing method

        :param size: size of the rectangle
        :param rotation_axis: axis of rotation
        :param angular_speed: speed of rotation (deg/sec)
        :param initial_angle: angular offset (deg)
        :param center_offset: relative position of center of rectangle with respect to rotation_axis
        """

        Obstacle.__init__(self)

        self.rotation_axis = rotation_axis                      # Axis of rotation
        self.rotation_radius = distance((0, 0), center_offset)  # Radius of rotation
        self.angular_speed = angular_speed                      # Angular speed of rotation
        self.offset_angle = math.atan2(center_offset[1], center_offset[0]) * 180 / math.pi  # Angle by center_offset
        self.initial_angle = initial_angle + self.offset_angle  # Set starting angle (will be used for initializing)
        self.current_angle = initial_angle + self.offset_angle  # Current angle is the same as initial angle

        # Generate rectangle image leaving a thin margin for accurate rotation
        self.rect_image = pygame.Surface((size[0] + 2, size[1] + 2))
        pygame.draw.rect(self.rect_image, WHITE1, (1, 1, size[0], size[1]))

        self.image_orig = self.rect_image                   # Used for rotating
        self.image = pygame.transform.rotate(self.image_orig, initial_angle)    # Make image using initial angle
        self.image.set_colorkey(BLACK)                      # Make black background fully transparent
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection
        # A virtual rectangle which encloses RotatingRectangularObstacle
        self.rect = self.image.get_rect(center=[a + f for a, f in zip(self.rotation_axis, center_offset)])

        # Add this sprite to sprite groups
        self.group.add(self)

    def initialize(self) -> None:
        """
        Initializing method during gameplay

        :return: None
        """

        self.current_angle = self.initial_angle     # Reset angle to initial value

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.current_angle += self.angular_speed * init.DELTA_TIME
        self.image = pygame.transform.rotate(self.image_orig, self.current_angle - self.offset_angle)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(self.rotation_axis[0] + self.rotation_radius * math.cos(self.current_angle * math.pi / 180),
                                                self.rotation_axis[1] - self.rotation_radius * math.sin(self.current_angle * math.pi / 180)))


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

        Obstacle.__init__(self)

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

    def initialize(self) -> None:
        """
        Initializing method during gameplay

        :return: None
        """

        self.current_angle = 0      # Reset angle to 0

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.current_angle += self.rotation_speed * init.DELTA_TIME          # Update angle
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

    group = pygame.sprite.Group()   # AngleFollowerImageObstacle' own sprite group

    def __init__(self, image: pygame.Surface, axis_pos: (int, int), at_index=0):
        """
        Initializing method

        :param image: Image of obstacle
        :param axis_pos: Position of rotation axis
        :param at_index: Index of ArcTracker list in level
        """

        Obstacle.__init__(self)

        self.image = image                                  # Create a new rectangular surface object
        self.image_orig = image                             # Used for rotating
        self.image.set_colorkey(BLACK)                      # Make the black bakground fully transparent
        self.mask = pygame.mask.from_surface(self.image)    # Create a mask object for collision detection
        self.rect = self.image.get_rect(center=axis_pos)    # A virtual rectangle which encloses RotatingImageObstacle
        self.center_orig = axis_pos                         # For preserving rotation axis

        self.current_angle = 0
        self.at_index = at_index
        self.following_at = None                            # ArcTracker to follow rotation angle (will be assigned at level class initialization)

        self.current_at_angle = self.last_at_angle = 0
        self.angle_diff = (self.current_at_angle - self.last_at_angle) * 180 / math.pi

        # Add this sprite to sprite groups
        self.group.add(self)

    def assign_arctracker(self, arctracker: ArcTracker) -> None:
        """

        :param arctracker:
        :return: None
        """

        self.following_at = arctracker
        self.current_at_angle = self.last_at_angle = self.following_at.relative_angle

    def initialize(self) -> None:
        """
        Initializing method during gameplay

        :return: None
        """

        self.current_angle = 0      # Reset angle to 0

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        # Update angle
        self.current_angle -= self.following_at.angular_speed_per_frame * 180 / math.pi
        self.last_at_angle = self.current_at_angle
        self.current_at_angle = self.following_at.relative_angle

        # Update image according to current angle
        self.image = pygame.transform.rotate(self.image_orig, self.current_angle)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.center_orig)
