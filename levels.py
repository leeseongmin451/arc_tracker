"""
A collection of all levels in the game
"""


# Import all sprites defined in sprites_and_functions
import pygame.sprite
from sprites_and_functions import *


class Level:
    """
    A single level class which ArcTracker should clear

    It consists of starting position of ArcTracker and goal points,
    various kinds of obstacles, and several numerical informations
    such as level number, minimum moves to clear, playtime, etc..
    """

    def __init__(self, arctracker_pos_list: list, obstacle_list: list, goal_pos_list: list, minimum_moves: int):
        """
        Initializing method

        :param arctracker_pos_list: list of all arctrackers positions
        :param obstacle_list: list of obstacles in this level
        :param goal_pos_list: list of all goal point positions
        :param minimum_moves: minimum possible movements to clear this level
        """

        # Generate and fill ArcTracker group
        self.arctracker_group = pygame.sprite.Group()
        for a in arctracker_pos_list:
            self.arctracker_group.add(ArcTracker(a))

        # Generate and fill obstacle group
        self.obstacle_group = pygame.sprite.Group()
        for o in obstacle_list:
            self.obstacle_group.add(o)

        # Generate and fill goal group
        self.goal_group = pygame.sprite.Group()
        for g in goal_pos_list:
            self.goal_group.add(GoalPoint(g))

        self.minimum_moves = minimum_moves      # Minimum possible movements to clear this level
        self.play_framecount = 0                # Level playtime counted in frames
        self.level_playtime = 0                 # Level playtime counted in seconds

    def initialize(self):
        """
        Initialize all arc trackers and all obstacles in this level

        :return: None
        """

        # Initialize all arc trackers
        for a in self.arctracker_group:
            a.initialize()

        # Initialize all obstacles
        for o in self.obstacle_group:
            o.initialize()

    def update(self, mouse_state, key_state) -> None:
        """
        Update all sprites(ArcTracker, obstacles, etc.) in this level

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        # Update all sprites in this level
        self.arctracker_group.update(mouse_state, key_state)
        self.obstacle_group.update(mouse_state, key_state)
        self.goal_group.update(mouse_state, key_state)

        # Detect collision between src tracker and obstacles
        for a in self.arctracker_group:
            for o in self.obstacle_group:
                if o.collided(a):
                    self.initialize()
                    break

    def draw(self, surface: pygame.Surface):
        """
        Draw all sprites and texts in this level

        :param surface: Surface to draw on
        :return: None
        """

        # Draw all path of ArcTrackers
        for a in self.arctracker_group:
            if a.path:
                surface.blit(a.path.image, a.path.rect)

        # Draw all sprites in this level
        self.obstacle_group.draw(surface)
        self.goal_group.draw(surface)
        self.arctracker_group.draw(surface)


# Generate all levels (keys: level number, values: level class instance)
level_dict = {
    1: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height)
             ],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             minimum_moves=1),

    2: Level(arctracker_pos_list=[(screen_width - 150, 150)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height),
                 StaticRectangularObstacle(760, 0, 400, 600),
                 StaticRectangularObstacle(760, screen_height - 200, 400, 200)
             ],
             goal_pos_list=[(150, 150)],
             minimum_moves=1),

    3: Level(arctracker_pos_list=[(150, 150)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height),
                 StaticCircularObstacle(300, screen_height - 100, 700),
                 StaticCircularObstacle(screen_width - 300, 100, 700)
             ],
             goal_pos_list=[(screen_width - 150, screen_height - 150)],
             minimum_moves=2),

    4: Level(arctracker_pos_list=[(450, screen_height // 2 - 100)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height // 2 - 20, 600, 40),
                 StaticCircularObstacle(screen_width // 2, screen_height // 2, 450)
             ],
             goal_pos_list=[(450, screen_height // 2 + 100)],
             minimum_moves=2),

    5: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height),
                 StaticRectangularObstacle(270, 0, 300, screen_height // 2),
                 StaticRectangularObstacle(990, 0, 300, screen_height // 2),
                 StaticRectangularObstacle(630, screen_height // 2, 300, screen_height // 2),
                 StaticRectangularObstacle(1350, screen_height // 2, 300, screen_height // 2),
                 StaticCircularObstacle(420, screen_height // 2, 150),
                 StaticCircularObstacle(780, screen_height // 2, 150),
                 StaticCircularObstacle(1140, screen_height // 2, 150),
                 StaticCircularObstacle(1500, screen_height // 2, 150)
             ],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             minimum_moves=2)
}
