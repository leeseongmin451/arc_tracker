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

    def __init__(self,
                 arctracker_pos_list: List[Tuple[int, int]],
                 obstacle_list: List[Obstacle],
                 coin_pos_list: List[Tuple[int, int]],
                 goal_pos_list: List[Tuple[int, int]],
                 par: int,
                 arctracker_clone_list: List[Tuple[Tuple[int, int], int, bool]],
                 min_orbit_radius=150):
        """
        Initializing method

        :param arctracker_pos_list: list of all arctrackers positions
        :param obstacle_list: list of obstacles in this level
        :param coin_pos_list: list of all coin positions
        :param goal_pos_list: list of all goal point positions
        :param par: minimum possible movements to clear this level
        :param arctracker_clone_list: info of ArcTrackerClones as a list of tuple(position, id, move_opposite(bool))
        :param min_orbit_radius: minimum radius of the generatable orbit
        """

        # Generate and fill ArcTracker group
        self.arctracker_group = pygame.sprite.Group()
        self.arctracker_list = []
        id_num = 1
        for a in arctracker_pos_list:
            new_arctracker = ArcTracker(a, id_num, min_orbit_radius)
            self.arctracker_group.add(new_arctracker)
            self.arctracker_list.append(new_arctracker)

            # Add ArcTrackerClone if exists
            for a_clone in arctracker_clone_list:
                if a_clone[1] == id_num:
                    new_arctracker_clone = ArcTrackerClone(a_clone[0], a_clone[1], min_orbit_radius, new_arctracker, a_clone[2])
                    self.arctracker_group.add(new_arctracker_clone)
            id_num += 1

        # Generate and fill obstacle group
        self.obstacle_group = pygame.sprite.Group()
        for o in obstacle_list:
            self.obstacle_group.add(o)

            # Assign ArcTracker if there is a AngleFollower-kind of obstacle
            if isinstance(o, AngleFollowerImageObstacle):
                o.assign_arctracker(self.arctracker_list[o.at_index])

        # Generate and fill coin group
        self.coin_group = pygame.sprite.Group()
        self.coin_pos_list = coin_pos_list

        # Generate and fill goal group
        self.goal_group = pygame.sprite.Group()
        for g in goal_pos_list:
            self.goal_group.add(GoalPoint(g))

        self.minimum_moves = par      # Minimum possible movements to clear this level
        self.play_framecount = 0                # Level playtime counted in frames
        self.level_playtime = 0                 # Level playtime counted in seconds

        self.cleared = False                    # Cleared status

    def initialize(self) -> None:
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

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
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

        # Check whether ArcTracker's position gets out of the screen
        for a in self.arctracker_group:
            if a.rect.centerx < -a.rect.w // 2 or a.rect.centerx > screen_width + a.rect.w // 2 or \
               a.rect.centery < -a.rect.h // 2 or a.rect.centery > screen_height + a.rect.h // 2:
                self.initialize()
                break

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

    def draw(self, surface: pygame.Surface) -> None:
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

        # Draw all markers of ArcTrackers
        for a in self.arctracker_group:
            if a.axis_marker:
                surface.blit(a.axis_marker.image, a.axis_marker.rect)

        # Draw all ArcTrackers and GoalPoints in this level
        self.goal_group.draw(surface)
        self.arctracker_group.draw(surface)


# Generate all levels (keys: level number, values: level class instance)
level_dict = {
    1: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
             ],
             coin_pos_list=[],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             par=1,
             arctracker_clone_list=[]),

    2: Level(arctracker_pos_list=[(screen_width - 150, 150)],
             obstacle_list=[
                 StaticRectangularObstacle(760, 0, 400, 600),
                 StaticRectangularObstacle(760, screen_height - 200, 400, 200)
             ],
             coin_pos_list=[],
             goal_pos_list=[(150, 150)],
             par=1,
             arctracker_clone_list=[]),

    3: Level(arctracker_pos_list=[(150, 150)],
             obstacle_list=[
                 StaticCircularObstacle(300, screen_height - 100, 700),
                 StaticCircularObstacle(screen_width - 300, 100, 700)
             ],
             coin_pos_list=[],
             goal_pos_list=[(screen_width - 150, screen_height - 150)],
             par=2,
             arctracker_clone_list=[]),

    4: Level(arctracker_pos_list=[(450, screen_height // 2 - 100)],
             obstacle_list=[
                 StaticRectangularObstacle(0, screen_height // 2 - 20, 550, 40),
                 StaticInnerCurvedObstacle(StaticCircularObstacle, (screen_width // 2, screen_height // 2, 450),
                                           (screen_width // 2, screen_height // 2), 400)
             ],
             coin_pos_list=[],
             goal_pos_list=[(450, screen_height // 2 + 100)],
             par=1,
             arctracker_clone_list=[]),

    5: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
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
             par=4,
             arctracker_clone_list=[]),

    6: Level(arctracker_pos_list=[(350, screen_height // 2)],
             obstacle_list=[
                 StaticRectangularObstacle(0, 0, screen_width, 450),
                 StaticRectangularObstacle(0, 0, 300, screen_height),
                 StaticRectangularObstacle(0, screen_height - 450, screen_width, 450),
                 StaticRectangularObstacle(screen_width - 300, 0, 300, screen_height)
             ],
             coin_pos_list=[],
             goal_pos_list=[(screen_width - 350, screen_height // 2)],
             par=2,
             arctracker_clone_list=[]),

    7: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
             ],
             coin_pos_list=[(1706, 454), (1586, 334), (1450, 237), (1293, 165), (1129, 121), (960, 107),
                            (791, 121), (627, 165), (473, 237), (334, 334), (214, 454)],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             par=1,
             arctracker_clone_list=[]),

    8: Level(arctracker_pos_list=[(150, screen_height // 2)],
             obstacle_list=[
             ],
             coin_pos_list=[(960, 200), (960, 540), (960, 880)],
             goal_pos_list=[(screen_width - 150, screen_height // 2)],
             par=2,
             arctracker_clone_list=[]),

    9: Level(arctracker_pos_list=[(960, 500)],
             obstacle_list=[
             ],
             coin_pos_list=[(900, 540)],
             goal_pos_list=[(960, 580)],
             par=2,
             arctracker_clone_list=[]),

    10: Level(arctracker_pos_list=[(150, 300)],
              obstacle_list=[
                  StaticCircularObstacle(300, 100, 50),
                  StaticCircularObstacle(140, 800, 300),
                  StaticCircularObstacle(1200, 1000, 100),
                  StaticCircularObstacle(980, 500, 75),
                  StaticCircularObstacle(400, 400, 120),
                  StaticCircularObstacle(700, 100, 140),
                  StaticCircularObstacle(800, 350, 60),
                  StaticCircularObstacle(1500, 700, 200),
                  StaticCircularObstacle(1150, 650, 100),
                  StaticCircularObstacle(700, 700, 150),
                  StaticCircularObstacle(1000, 900, 50),
                  StaticCircularObstacle(1820, 80, 120),
                  StaticCircularObstacle(1600, 350, 80),
                  StaticCircularObstacle(1300, 200, 130),
                  StaticCircularObstacle(1300, 400, 30),
                  StaticCircularObstacle(1100, 300, 50),
                  StaticCircularObstacle(900, 100, 70),
              ],
              coin_pos_list=[],
              goal_pos_list=[(screen_width - 150, 800)],
              par=2,
              arctracker_clone_list=[]),

    11: Level(arctracker_pos_list=[(screen_width - 150, 800)],
              obstacle_list=[
                  StaticCircularObstacle(300, 100, 50),
                  StaticCircularObstacle(140, 800, 300),
                  StaticCircularObstacle(1200, 1000, 100),
                  StaticCircularObstacle(980, 500, 75),
                  StaticCircularObstacle(400, 400, 120),
                  StaticCircularObstacle(700, 100, 140),
                  StaticCircularObstacle(800, 350, 60),
                  StaticCircularObstacle(1500, 700, 200),
                  StaticCircularObstacle(1150, 650, 100),
                  StaticCircularObstacle(700, 700, 150),
                  StaticCircularObstacle(1000, 900, 50),
                  StaticCircularObstacle(1820, 80, 120),
                  StaticCircularObstacle(1600, 350, 80),
                  StaticCircularObstacle(1300, 200, 130),
                  StaticCircularObstacle(1300, 400, 30),
                  StaticCircularObstacle(1100, 300, 50),
                  StaticCircularObstacle(900, 100, 70),
              ],
              coin_pos_list=[(1500, 473), (1275, 670), (1150, 773), (950, 850), (535, 750),
                             (540, 440), (760, 260), (830, 440), (300, 170)],
              goal_pos_list=[(150, 300)],
              par=5,
              arctracker_clone_list=[])
}
