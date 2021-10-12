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

    def __init__(self, arctracker_pos_list: list, obstacle_list: list, coin_pos_list: list, goal_pos_list: list, minimum_moves: int):
        """
        Initializing method

        :param arctracker_pos_list: list of all arctrackers positions
        :param obstacle_list: list of obstacles in this level
        :param coin_pos_list: list of all coin positions
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

        # Generate and fill coin group
        self.coin_group = pygame.sprite.Group()
        self.coin_pos_list = coin_pos_list

        # Generate and fill goal group
        self.goal_group = pygame.sprite.Group()
        for g in goal_pos_list:
            self.goal_group.add(GoalPoint(g))

        self.minimum_moves = minimum_moves      # Minimum possible movements to clear this level
        self.play_framecount = 0                # Level playtime counted in frames
        self.level_playtime = 0                 # Level playtime counted in seconds

        self.cleared = False                    # Cleared status

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

        # Clear and refill coin group
        self.coin_group.empty()
        for c in self.coin_pos_list:
            self.coin_group.add(Coin(c))

        # Initialize all goal points
        for g in self.goal_group:
            g.initialize()

        # Initialize cleard status
        self.cleared = False

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
        self.coin_group.update(mouse_state, key_state)
        self.goal_group.update(mouse_state, key_state)

        # Detect collision between arc tracker and obstacles
        for a in self.arctracker_group:
            for o in self.obstacle_group:
                if o.collided(a):
                    self.initialize()
                    break

        # Detect collision between arc tracker and coins
        for a in self.arctracker_group:
            for c in self.coin_group:
                if distance(a.rect.center, c.rect.center) < 20:
                    c.kill()

        # Determine whether arc tracker reached to goal point
        for a in self.arctracker_group:
            for g in self.goal_group:
                # Lock-on will be available only when there is no coin left
                if distance(a.rect.center, g.rect.center) < 10 and not g.arctracker_matched and len(self.coin_group) == 0:
                    a.level_complete = True
                    a.reject_path()
                    g.arctracker_matched = True
                    a.rect.center = g.rect.center       # Lock the position of ArcTracker to GoalPoint

        # Complete level if all ArcTrackers reached all GoalPoints
        if all([a.level_complete for a in self.arctracker_group]):
            self.cleared = True

    def draw(self, surface: pygame.Surface):
        """
        Draw all sprites and texts in this level

        :param surface: Surface to draw on
        :return: None
        """

        # Draw all coins and obstacles in this level
        self.coin_group.draw(surface)
        self.obstacle_group.draw(surface)

        # Draw all path of ArcTrackers
        for a in self.arctracker_group:
            if a.path:
                surface.blit(a.path.image, a.path.rect)

        # Draw all borderline of ArcTrackers
        for a in self.arctracker_group:
            if a.borderline:
                surface.blit(a.borderline.image, a.borderline.rect)

        # Draw all ArcTrackers and GoalPoints in this level
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
             coin_pos_list=[],
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
             coin_pos_list=[],
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
             coin_pos_list=[],
             goal_pos_list=[(screen_width - 150, screen_height - 150)],
             minimum_moves=2),

    4: Level(arctracker_pos_list=[(450, screen_height // 2 - 100)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height // 2 - 20, 550, 40),
                 StaticInnerCurvedObstacle(StaticCircularObstacle, (screen_width // 2, screen_height // 2, 450), (screen_width // 2, screen_height // 2), 400)
             ],
             coin_pos_list=[],
             goal_pos_list=[(450, screen_height // 2 + 100)],
             minimum_moves=1),

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
             coin_pos_list=[],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             minimum_moves=4),

    6: Level(arctracker_pos_list=[(350, screen_height // 2)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 450),
                 StaticRectangularObstacle(0, 0, 300, screen_height),
                 StaticRectangularObstacle(0, screen_height - 450, screen_width, 450),
                 StaticRectangularObstacle(screen_width - 300, 0, 300, screen_height)
             ],
             coin_pos_list=[],
             goal_pos_list=[(screen_width - 350, screen_height // 2)],
             minimum_moves=2),

    7: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 20),
                 StaticRectangularObstacle(0, 0, 20, screen_height),
                 StaticRectangularObstacle(0, screen_height - 20, screen_width, 20),
                 StaticRectangularObstacle(screen_width - 20, 0, 20, screen_height)
             ],
             coin_pos_list=[(screen_width // 2, screen_height // 2)],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             minimum_moves=4)
}
