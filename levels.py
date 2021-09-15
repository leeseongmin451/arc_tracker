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

    def __init__(self, arctracker_list: list, obstacle_list: list, goal_list: list, minimum_moves: int):
        """
        Initializing method

        :param arctracker_list: list of all arctrackers
        :param obstacle_list: list of obstacles in this level
        :param goal_list: list of all goal points
        :param minimum_moves: minimum possible movements to clear this level
        """

        # Generate and fill ArcTracker group
        self.arctracker_group = pygame.sprite.Group()
        for a in arctracker_list:
            self.arctracker_group.add(a)

        # Generate and fill obstacle group
        self.obstacle_group = pygame.sprite.Group()
        for o in obstacle_list:
            self.obstacle_group.add(o)

        # Generate and fill goal group
        self.goal_group = pygame.sprite.Group()
        for g in goal_list:
            self.goal_group.add(g)

        self.minimum_moves = minimum_moves      # Minimum possible movements to clear this level
        self.play_framecount = 0                # Level playtime counted in frames
        self.level_playtime = 0                 # Level playtime counted in seconds

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

    def draw(self, surface):
        """
        Draw all sprites and texts in this level

        :param surface: Surface to draw on
        :return: None
        """

        # Draw all sprites in this level
        self.arctracker_group.draw(surface)
        self.obstacle_group.draw(surface)
        self.goal_group.draw(surface)


# Generate all levels (keys: level number, values: level class instance)
level_dict = {1: Level()}
