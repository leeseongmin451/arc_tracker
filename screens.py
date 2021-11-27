"""
Defines all scenes(screens) of the game
"""
import pygame.sprite

from sprites_and_functions import *
from levels import level_dict


class ImageView(pygame.sprite.Sprite):
    """
    A rectanguler object to display an image
    """

    def __init__(self, image: pygame.Surface, size: (int, int), pos: (int, int), fixpoint="topleft"):
        """

        :param image: image surface object to display
        :param size: size of the image
        :param pos: position of the image
        :param fixpoint: fixpoint of the image
        """

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(image, size)
        self.rect = self.image.get_rect()
        self.pos = pos
        self.fixpoint = fixpoint
        self.fix_position()

    def fix_position(self) -> None:
        """
        Determine exact position of text using fixpoint
        :return: None
        """

        if self.fixpoint == "topleft":
            self.rect.topleft = self.pos
        elif self.fixpoint == "midtop":
            self.rect.midtop = self.pos
        elif self.fixpoint == "topright":
            self.rect.topright = self.pos
        elif self.fixpoint == "midleft":
            self.rect.midleft = self.pos
        elif self.fixpoint == "center":
            self.rect.center = self.pos
        elif self.fixpoint == "midright":
            self.rect.midright = self.pos
        elif self.fixpoint == "bottomleft":
            self.rect.bottomleft = self.pos
        elif self.fixpoint == "midbottom":
            self.rect.midbottom = self.pos
        elif self.fixpoint == "bottomright":
            self.rect.bottomright = self.pos

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw this image on given surface
        :param surface: surface to draw on
        :return: None
        """

        surface.blit(self.image, self.rect)


class Button(pygame.sprite.Sprite):
    """
    A rectangular button class
    """

    group = pygame.sprite.Group()       # Button's own sprite group

    def __init__(self, rect: List[int, int, int, int], text: str, text_font: str, text_font_size: int, color: Tuple[int, int, int], default_back_color=(0, 0, 0)):
        """
        Initialize and apply basic settings to button
        :param rect: position and rectangular size of button
        :param text: text located at the center of button
        :param text_font: font of text
        :param text_font_size: font size of text in pixels
        :param color: color of button boundary and text
        :param default_back_color: color of background of button, default value is black(0, 0, 0)
        """

        pygame.sprite.Sprite.__init__(self)

        # Rect attribute
        self.rect = pygame.Rect(rect)

        # Text & font attribute
        self.text = text
        self.text_font = text_font
        self.text_font_size = text_font_size

        # Color attrubutes
        self.active_color = color
        self.font = pygame.font.SysFont(self.text_font, self.text_font_size)
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)

        # Background color attributes
        # Default color is the darkest color
        self.default_back_color = default_back_color
        # Hovered color displayed when cursor is in rect has half brightness of active color
        self.hovered_back_color = ((self.active_color[0] + self.default_back_color[0]) // 2,
                                   (self.active_color[1] + self.default_back_color[1]) // 2,
                                   (self.active_color[2] + self.default_back_color[2]) // 2)
        # Clicked color displayed when the button is pressed has half brightness of hovered color
        self.clicked_back_color = ((self.hovered_back_color[0] + self.default_back_color[0]) // 2,
                                   (self.hovered_back_color[1] + self.default_back_color[1]) // 2,
                                   (self.hovered_back_color[2] + self.default_back_color[2]) // 2)
        # Set initial color of button
        self.current_color = self.active_color
        self.current_back_color = self.default_back_color
        self.inactive_color = self.hovered_back_color

        # Boolean values for button control
        self.active = True
        self.cursor_in_rect = False
        self.is_clicked = False

        # Add self to button group
        self.group.add(self)

    def activate(self) -> None:
        """
        Make button active(clickable)
        :return: None
        """

        self.current_color = self.active_color
        # Rerender text surface with newly set color
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)
        self.active = True      # Update method will be executed

    def deactivate(self) -> None:
        """
        Make button inactive(not clickable)
        :return:
        """

        self.current_color = self.inactive_color
        # Rerender text surface with newly set color
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)
        self.active = False     # Update method will be passed
        self.current_back_color = self.default_back_color

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        Check whether cursor is in button or clicked the button when button is active(clickable).
        Only if click-and-release the button, operate() method will be executed.

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        # Check whether cursor is in button boundary and change background color
        if self.active and self.rect.collidepoint(mouse_state[CURPOS]):
            self.cursor_in_rect = True
            self.current_back_color = self.hovered_back_color       # Change background status
        else:
            self.cursor_in_rect = False
            self.current_back_color = self.default_back_color       # Change background status

        # Check mouse click event when the cursor is in button
        if self.cursor_in_rect and mouse_state[LCLICK]:
            self.is_clicked = True
            self.current_back_color = self.clicked_back_color       # Change background status
        # Check mouse release event when clicked
        if self.is_clicked and not mouse_state[LCLICK]:
            self.operate()                                          # Operate the button
            self.is_clicked = False
            self.current_back_color = self.hovered_back_color       # Change background status

    def operate(self) -> None:
        """
        Button's specific function will be defined here.
        Child button classes will have specific functions by overriding this method
        :return: None
        """

        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw button on screen
        :param surface: surface on which draw button
        :return: None
        """

        pygame.draw.rect(surface, self.current_back_color, self.rect)   # Draw background first
        pygame.draw.rect(surface, self.current_color, self.rect, 3)     # Draw boundary of button
        surface.blit(self.text_surface, self.text_surface_rect)         # Draw text in button


class LevelSelectButton(Button):
    """
    A Button class for transition to LevelSelectScreen
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 200, screen_height - 440, 400, 100], "SELECT LEVEL", "verdana", 50, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        LevelSelectButton's own operation

        :return: None
        """

        self.on_screen.hide()
        level_select_screen.show()


class HowToPlayButton(Button):
    """
    A Button class for transition to HowToPlayScreen
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 200, screen_height - 320, 400, 100], "HOW TO PLAY", "verdana", 50, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        HowToPlayButton's own operation

        :return: None
        """

        self.on_screen.hide()
        how_to_play_screen.show()


class SettingsButton(Button):
    """
    A Button class for transition to SettingsScreen
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 200, screen_height - 200, 400, 100], "SETTINGS", "verdana", 50, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        SettingsButton's own operation

        :return: None
        """

        self.on_screen.hide()
        settings_screen.show()


class QuitButton(Button):
    """
    A Button class for quitting game
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width - 400, screen_height - 150, 250, 70], "QUIT GAME", "verdana", 30, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        QuitButton's own operation

        :return: None
        """

        init.running = False        # Stop the game loop and quit the game


class MainMenuButton(Button):
    """
    A Button class for returning to main menu screen
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width - 400, screen_height - 150, 250, 70], "MAIN MENU", "verdana", 30, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        MainMenuButton's own operation

        :return: None
        """

        self.on_screen.hide()
        mainmenu_screen.show()


class LevelButton(Button):
    """
    A Button class for playing a specific level

    Each LevelButton instance has its own level attribute to connect to.
    """

    def __init__(self, level: int, rect: List[int, int, int, int], on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        # Number of level to connect
        self.levelnum = level

        # Set button's position according to levelnum
        Button.__init__(self, rect, str(self.levelnum), "verdana", 25, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        LevelButton's own operation

        :return: None
        """

        if self.levelnum <= len(level_dict):
            self.on_screen.hide()
            gameplay_screen.intialize_level(self.levelnum)
            gameplay_screen.show()


class NextLevelButton(Button):
    """
    A Button class for transition to next level
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 150, screen_height // 2 + 100, 300, 70], "NEXT LEVEL", "verdana", 30, WHITE1, WHITE3)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        NextLevelButton's own operation

        :return: None
        """

        self.on_screen.intialize_level(self.on_screen.current_levelnum + 1)


class RetryButton(Button):
    """
    A Button class for replaying current level after clearing it
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 150, screen_height // 2 + 200, 300, 70], "RETRY", "verdana", 30, WHITE1, WHITE3)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        RetryButton's own operation

        :return: None
        """

        self.on_screen.intialize_level(self.on_screen.current_levelnum)


class BackToLevelSelectButton(Button):
    """
    A Button class for transition to next level
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 150, screen_height // 2 + 300, 300, 70], "LEVEL SELECT", "verdana", 30, WHITE1, WHITE3)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self) -> None:
        """
        BackToLevelSelectButton's own operation

        :return: None
        """

        self.on_screen.hide()
        level_select_screen.show()


class Text:
    """
    A text surface class to display all texts appearing in this game
    """

    def __init__(self, text: str, font: str, font_size: int, pos: (int, int), fixpoint="topleft", color=WHITE1):
        self.text = text                                                    # Content to display
        self.font_size = font_size                                          # Size of this text
        self.font = pygame.font.SysFont(font, self.font_size)               # Create font
        self.color = color                                                  # Color of this text
        self.text_surface = self.font.render(self.text, True, self.color)   # Create text surface
        self.rect = self.text_surface.get_rect()                            # Surface rect

        # Position attributes
        self.pos = pos              # Position on screen to display
        self.fixpoint = fixpoint    # Position to fix the text
        self.fix_position()

    def fix_position(self) -> None:
        """
        Determine exact position of text using fixpoint
        :return: None
        """

        if self.fixpoint == "topleft":
            self.rect.topleft = self.pos
        elif self.fixpoint == "midtop":
            self.rect.midtop = self.pos
        elif self.fixpoint == "topright":
            self.rect.topright = self.pos
        elif self.fixpoint == "midleft":
            self.rect.midleft = self.pos
        elif self.fixpoint == "center":
            self.rect.center = self.pos
        elif self.fixpoint == "midright":
            self.rect.midright = self.pos
        elif self.fixpoint == "bottomleft":
            self.rect.bottomleft = self.pos
        elif self.fixpoint == "midbottom":
            self.rect.midbottom = self.pos
        elif self.fixpoint == "bottomright":
            self.rect.bottomright = self.pos

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        pass

    def update_text(self, new_text: str) -> None:
        """
        Change text
        :param new_text: new text to replace
        :return: None
        """

        # Render the new text and create new text surface and rect
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.color)
        self.rect = self.text_surface.get_rect()

        # Fix position again
        self.fix_position()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw text on a given surface
        :param surface: surface to draw on
        :return: None
        """

        surface.blit(self.text_surface, self.rect)


class TextGroupBox(pygame.sprite.Sprite):
    """
    An invisible box which contains multiple line of texts
    """

    def __init__(self, text_list: List[str], font: str, font_size: int, pos: (int, int), color=WHITE1, margin=10, line_space=10):
        """
        Initializing method

        :param text_list: list of text string to display
        :param font: font of text
        :param font_size: size of text
        :param pos: position of topleft of box
        :param color: color of text
        :param margin: margin between text and box boundary (in px)
        :param line_space: space between texts (in px)
        """

        pygame.sprite.Sprite.__init__(self)

        # Font, size, and color of text
        self.font_size = font_size
        self.font = pygame.font.SysFont(font, self.font_size)
        self.color = color

        # Text surfaces and rects list
        self.text_surface_list = []
        self.text_rect_list = []

        # Fill in all lists
        for text in text_list:
            text_surface = self.font.render(text, True, self.color)
            text_rect = text_surface.get_rect()

            self.text_surface_list.append(text_surface)
            self.text_rect_list.append(text_rect)

        # Calculate box size using width of texts, height of texts, number of texts, margin, and line space
        lines_cnt = len(text_list)
        self.box_height = 2 * margin + lines_cnt * self.font_size + (lines_cnt - 1) * line_space
        self.box_width = 2 * margin + max([r.w for r in self.text_rect_list])

        # Create box surface and rect
        self.image = pygame.Surface((self.box_width, self.box_height))
        self.rect = self.image.get_rect(topleft=pos)

        # Draw all texts in the box
        current_text_pos_y = margin
        for surf, rect in zip(self.text_surface_list, self.text_rect_list):
            rect.topleft = (margin, current_text_pos_y)
            self.image.blit(surf, rect)
            current_text_pos_y += self.font_size + line_space

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method needed for all sprite class

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw this box in given surface

        :param surface: Surface to draw on
        :return: None
        """

        surface.blit(self.image, self.rect)


class PopupTextBox(pygame.sprite.Sprite):
    """
    A text box which pops up during gameplay
    """

    group = pygame.sprite.Group()  # PopupTextBox' own sprite group

    def __init__(self, text: str):
        """
        Initializing method

        Size and displaying time of box will be automatically set.

        :param text: text to display
        """

        pygame.sprite.Sprite.__init__(self)

        # Create text surface object
        self.font = pygame.font.SysFont("verdana", 20)              # Font and size of text
        self.text_surface = self.font.render(text, True, WHITE1)    # Contents of text
        self.text_rect = self.text_surface.get_rect()               # A virtual rectangle enclosing text surface

        # Create box surface object
        self.box_w = self.text_rect.w + 100                     # Width of box (slightly longer than text)
        self.box_h = self.text_rect.h + 30                      # Height of box (slightly longer than text)
        self.image = pygame.Surface((self.box_w, self.box_h))   # Create box surface
        self.image.set_colorkey(BLACK)                          # Make black background fully transparent
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height + 100))    # A virtual rectangle enclosing box surface
        pygame.draw.rect(self.image, WHITE3, [0, 0, self.box_w, self.box_h], 0, 10)         # Draw dark gray background in box surface
        pygame.draw.rect(self.image, WHITE2, [0, 0, self.box_w, self.box_h], 4, 10)         # Draw light gray borderline in box surface

        # Determine position of text surface and draw it in box surface
        self.text_rect.centerx = self.box_w // 2
        self.text_rect.centery = self.box_h // 2
        self.image.blit(self.text_surface, self.text_rect)  # Draw text

        # Set displaying time
        self.display_time = self.text_rect.w * 0.005                # In seconds (determined by the length of text)
        self.display_frame_cnt = round(self.display_time * FPS)     # In frame counts
        self.current_frame_cnt = 0

        # Speed and acceleration for popping
        self.popup_speed = 800
        self.popup_acc = 1500

        # Text box is currently going up or down
        self.moving_up = True
        self.moving_down = False

        # Add this sprite to sprite groups
        self.group.add(self)

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Updating method

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        # While moving up
        if self.moving_up:
            # Update current speed and acceleration
            self.popup_speed -= self.popup_acc / FPS
            self.rect.y -= self.popup_speed / FPS
            # Stop moving and start displaying when speed goes to 0
            if self.popup_speed <= 0:
                self.moving_up = False

        # While moving down
        elif self.moving_down:
            # Update current speed and acceleration
            self.popup_speed -= self.popup_acc / FPS
            self.rect.y -= self.popup_speed / FPS
            # Kill this textbox when if it is completely out of the screen
            if self.rect.y > screen_height + 200:
                self.kill()

        # While displaying time
        else:
            self.current_frame_cnt += 1     # Increase frame count
            # Start moving down when frame is fully counted
            if self.current_frame_cnt >= self.display_frame_cnt:
                self.moving_down = True

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw box and text

        :param surface: Surface to draw on
        :return: None
        """

        surface.blit(self.image, self.rect)


class LevelClearedWindow:
    """
    Temporarily appears after clearing a level

    Consists of level-clear message, next-level button, back-to-level-select button.
    """

    def __init__(self, on_screen):
        """
        Initializing method
        """

        self.image = pygame.Surface((screen_width, screen_height))
        self.image.set_alpha(128)
        self.image.fill(WHITE1)
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.cleared_msg = Text("LEVEL CLEARED!!", "verdana", 50, (screen_width // 2, screen_height // 2 - 100), "center", BLACK)
        self.next_level_button = NextLevelButton(on_screen)
        self.retry_button = RetryButton(on_screen)
        self.level_select_button = BackToLevelSelectButton(on_screen)

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Update all texts/buttons on this window

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        self.next_level_button.update(mouse_state, key_state)
        self.retry_button.update(mouse_state, key_state)
        self.level_select_button.update(mouse_state, key_state)

    def draw(self, surface: pygame.Surface):
        """
        Draw all texts/buttons on this window

        :param surface: Surface to draw on
        :return: None
        """

        surface.blit(self.image, self.rect)
        self.cleared_msg.draw(surface)
        self.next_level_button.draw(surface)
        self.retry_button.draw(surface)
        self.level_select_button.draw(surface)


class Screen:
    """
    A screen class to display each scene at desired time

    MainMenuScreen, LevelSelectScreen, SettingsScreen, and each LevelScreen will
    inherit this class.
    """

    def __init__(self):
        """
        Initializing method

        Screen class has a "manage_list" attribute, which contains all texts and buttons
        appeared in screen for updating and drawing. Sprites for gameplay
        (such as ArcTracker, Obstacles, etc...) will not be included,
        because they already have their own sprite group, update and draw method.
        """

        self.manage_list = []
        self.now_display = False        # Whether show this screen now or not

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Update all texts/buttons on this screen

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        for t in self.manage_list:
            t.update(mouse_state, key_state)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all texts/buttons on this screen

        :param surface: Surface to draw on
        :return: None
        """

        screen.fill(BLACK)

        for t in self.manage_list:
            t.draw(surface)

    def show(self) -> None:
        """
        Display this screen

        :return: None
        """

        self.now_display = True

    def hide(self) -> None:
        """
        Hide this screen to show other screen

        :return: None
        """

        self.now_display = False


class MainMenuScreen(Screen):
    """
    Game-starting screen which appears first

    It has game title text, game icon, level select button, settings button, and quit button.
    """

    def __init__(self):
        """
        Initializing method
        """

        Screen.__init__(self)

        self.title_text = Text("ARC TRACKER", "verdana", 80, (screen_width // 2, screen_height // 6), "center")     # Text object
        self.manage_list.append(self.title_text)            # Append this text to manage_list

        self.level_select_button = LevelSelectButton(self)  # Button for level selection
        self.how_to_play_button = HowToPlayButton(self)     # Button for how to play
        self.settings_button = SettingsButton(self)         # Button for settings
        self.quit_button = QuitButton(self)                 # Button for quitting game


class LevelSelectScreen(Screen):
    """
    Screen for level selecting

    Has title, buttons for each level, and main menu button
    """

    def __init__(self):
        """
        Initializing method
        """

        Screen.__init__(self)

        self.title_text = Text("SELECT LEVEL", "verdana", 70, (screen_width // 2, screen_height // 6), "center")     # Text object
        self.manage_list.append(self.title_text)            # Append this text to manage_list

        # Generate 5x10 button array
        self.all_level_buttons = pygame.sprite.Group()      # Group of all buttons connected to each level
        # Width and height of the entire button array
        btn_group_width = 1600
        btn_group_height = 550
        # Width and height of each button
        btn_width = 100
        btn_height = 80
        # Distance of two adjacent buttons
        horizontal_gap = (btn_group_width - btn_width) / 9
        vertical_gap = (btn_group_height - btn_height) / 4
        # Position of top-left button
        first_btn_pos_x = (screen_width - btn_group_width) // 2
        first_btn_pos_y = 300
        for n in range(50):
            self.all_level_buttons.add(LevelButton(n + 1, [first_btn_pos_x + round(horizontal_gap * (n % 10)),
                                                           first_btn_pos_y + round(vertical_gap * (n // 10)),
                                                           btn_width, btn_height], self))

        self.mainmenu_button = MainMenuButton(self)         # Button for going back to the main menu screen


class HowToPlayScreen(Screen):
    """
    Screen for introducing how to play ArcTracker game

    Has title, images, description, and main menu button
    """

    def __init__(self):
        """
        Initializing method
        """

        Screen.__init__(self)

        self.title_text = Text("HOW TO PLAY", "verdana", 70, (screen_width // 2, screen_height // 6), "center")     # Text object
        self.manage_list.append(self.title_text)            # Append this text to manage_list

        # Example images for explaining how to play
        img_size = (369, 235)
        self.exp1_img = ImageView(example_game_img1, img_size, (150, 200))
        self.exp2_img = ImageView(example_game_img2, img_size, (150, 400))
        self.exp3_img = ImageView(example_game_img3, img_size, (150, 600))
        self.exp4_img = ImageView(example_game_img4, img_size, (150, 800))
        self.manage_list.append(self.exp1_img)
        self.manage_list.append(self.exp2_img)
        self.manage_list.append(self.exp3_img)
        self.manage_list.append(self.exp4_img)

        # Description text box
        self.desc_textbox1 = TextGroupBox(text_list=["Welcome to Arc Tracker!!",
                                                     "Just move your 'Arc Tracker (AT)' to get to the goal!! (yellow circle)"],
                                          font="verdana",
                                          font_size=15,
                                          pos=(550, 270))
        self.desc_textbox2 = TextGroupBox(text_list=["You can create a circular 'Orbit' passing through your AT",
                                                     "by setting the center using left mouse button.",
                                                     "First, hold the left mouse button. Then an orbit centered at the",
                                                     "mouse cursor (gray circle line) will appear. You can drag mouse",
                                                     "cursor to modulate radius and center position of the orbit.",
                                                     "If you release the mouse button, the orbit will be fixed.",
                                                     "You can also cancel the orbit by pressing C or ESC key."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(550, 420))
        self.desc_textbox3 = TextGroupBox(text_list=["The red circle line surrounding your AT indicates the minimum",
                                                     "radius of the orbit you can create. You cannot create an orbit",
                                                     "with radius shorter than that of the red circle line.",
                                                     "If you release mouse button in the red circle line, the orbit",
                                                     "will be automatically canceled and disappear."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(550, 660))
        self.desc_textbox4 = TextGroupBox(text_list=["After setting the orbit, click the mouse button to move your AT.",
                                                     "The AT will orbit counterclockwise if you click left mouse button,",
                                                     "and will orbit clockwise if you click right mouse button.",
                                                     "Click left mouse button again to stop moving AT."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(550, 860))
        self.desc_textbox5 = TextGroupBox(text_list=["There are many kind of obstacles. If your AT touches any of them,",
                                                     "you'll fail the level and AT will return to the intial position.",
                                                     "You'll also fail the level when AT gets out of the screen."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(1200, 270))
        self.desc_textbox6 = TextGroupBox(text_list=["There may be some coins (yellow dots) that you should collect",
                                                     "using AT. You must collect all coins in the level before moving AT",
                                                     "to the goal."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(1200, 400))
        self.desc_textbox7 = TextGroupBox(text_list=["Each level has 'PAR' value, the minimum possible move counts.",
                                                     "Try to clear levels using as few movements as you can! Maybe you",
                                                     "can clear some levels even in fewer movements than PAR value..."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(1200, 530))
        self.desc_textbox8 = TextGroupBox(text_list=["If you want to quit a level while playing, press Q key."],
                                          font="verdana",
                                          font_size=15,
                                          pos=(1200, 650))
        self.desc_textbox9 = TextGroupBox(text_list=["ENJOY THE GAME! :)"],
                                          font="verdana",
                                          font_size=40,
                                          pos=(1200, 720))
        self.manage_list.append(self.desc_textbox1)
        self.manage_list.append(self.desc_textbox2)
        self.manage_list.append(self.desc_textbox3)
        self.manage_list.append(self.desc_textbox4)
        self.manage_list.append(self.desc_textbox5)
        self.manage_list.append(self.desc_textbox6)
        self.manage_list.append(self.desc_textbox7)
        self.manage_list.append(self.desc_textbox8)
        self.manage_list.append(self.desc_textbox9)

        self.mainmenu_button = MainMenuButton(self)         # Button for going back to the main menu screen

    def draw(self, surface: pygame.Surface) -> None:
        """
        Overrides draw method from Screen class to draw an additional line

        :param surface: Surface to draw on
        :return: None
        """

        Screen.draw(self, surface)

        # Draw a vertical line to separate description texts
        pygame.draw.line(surface, WHITE1, (1130, 270), (1130, 1000), 2)


class SettingsScreen(Screen):
    """
    Screen for settings

    Has title, texts and buttons for setting, and main menu button
    """

    def __init__(self):
        """
        Initializing method
        """

        Screen.__init__(self)

        self.title_text = Text("SETTINGS", "verdana", 70, (screen_width // 2, screen_height // 6), "center")     # Text object
        self.manage_list.append(self.title_text)            # Append this text to manage_list

        self.mainmenu_button = MainMenuButton(self)         # Button for going back to the main menu screen


class GamePlayScreen(Screen):
    """
    Screen for gameplay

    Display ArcTracker, obstacles, and goal point in a specified level
    When user clicks a level button, then GamePlayScreen initializes its sprite components to
    the corresponding number of level of that button.

    It has a large, transparent number string at the center of the screen, displaying current level number.
    """

    def __init__(self):
        """
        Initializing method
        """

        Screen.__init__(self)

        self.current_levelnum_text = None
        self.current_level = None
        self.current_levelnum = 0

        self.popup_text_box = None

        self.cleared_window = LevelClearedWindow(self)

    def intialize_level(self, levelnum: int) -> None:
        """
        Change and Initialize level to input levelnum parameter.

        :param levelnum: Number of level to initialize
        :return: None
        """

        self.manage_list.clear()

        self.current_levelnum = levelnum
        self.current_levelnum_text = Text(str(self.current_levelnum), "verdana", 400, (screen_width // 2, screen_height // 2), "center", WHITE3)
        self.current_level = level_dict[self.current_levelnum]
        self.current_level.initialize()
        self.manage_list.append(self.current_levelnum_text)
        self.manage_list.append(self.current_level)

    def update(self, mouse_state: Dict[int, Union[bool, Tuple[int, int]]], key_state: Sequence[bool]) -> None:
        """
        Overrides update method of Screen class

        User can press "q" key to quit this level and return to LevelSelectScreen.

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        Screen.update(self, mouse_state, key_state)

        if key_state[pygame.K_q]:
            self.current_level.initialize()
            self.hide()
            level_select_screen.show()

        # Generate popup if needed
        if any([a.raise_popup for a in self.current_level.arctracker_group]):
            self.popup_text_box = PopupTextBox("Rotation radius is too small!!")
            self.manage_list.append(self.popup_text_box)

            for a in self.current_level.arctracker_group:
                a.reject_path()
                a.raise_popup = False

        # Delete popup object from manage list if it is killed
        if self.popup_text_box and not self.popup_text_box.alive():
            del self.manage_list[-1]
            self.popup_text_box = None

        # If current level is cleared
        if self.current_level.cleared:
            self.cleared_window.update(mouse_state, key_state)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all texts/buttons on this screen

        :param surface: Surface to draw on
        :return: None
        """

        Screen.draw(self, surface)

        # Draw cleared window if current level is cleared
        if self.current_level.cleared:
            self.cleared_window.draw(surface)


mainmenu_screen = MainMenuScreen()          # Generate MainMenuScreen class instance
level_select_screen = LevelSelectScreen()   # Generate LevelSelectScreen class instance
how_to_play_screen = HowToPlayScreen()      # Generate HowToPlayScreen class instance
settings_screen = SettingsScreen()          # Generate SettingsScreen class instance
gameplay_screen = GamePlayScreen()          # Generate GamePlayScreen class instance
