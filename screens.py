"""
Defines all scenes(screens) of the game
"""


import init
from sprites_and_functions import *


class Button(pygame.sprite.Sprite):
    """
    A rectangular button class
    """

    group = pygame.sprite.Group()       # Button's own sprite group

    def __init__(self, rect, text, text_font, text_font_size, color, default_back_color=(0, 0, 0)):
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
        all_sprites.add(self)
        self.group.add(self)

    def activate(self):
        """
        Make button active(clickable)
        :return: None
        """

        self.current_color = self.active_color
        # Rerender text surface with newly set color
        self.text_surface = self.font.render(self.text, True, self.active_color)
        self.text_surface_rect = self.text_surface.get_rect(center=self.rect.center)
        self.active = True      # Update method will be executed

    def deactivate(self):
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

    def update(self, mouse_state, key_state) -> None:
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

    def operate(self):
        """
        Button's specific function will be defined here.
        Child button classes will have specific functions by overriding this method
        :return: None
        """

        pass

    def draw(self, surface):
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

        Button.__init__(self, [screen_width // 2 - 200, screen_height - 400, 400, 150], "SELECT LEVEL", "verdana", 50, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self):
        """
        LevelSelectButton's own operation

        :return: None
        """

        pass        # Will be added after making LevelSelectScreen class


class SettingsButton(Button):
    """
    A Button class for transition to SettingsScreen
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width // 2 - 200, screen_height - 200, 400, 150], "SETTINGS", "verdana", 50, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self):
        """
        SettingsButton's own operation

        :return: None
        """

        pass        # Will be added after making SettingsScreen class


class QuitButton(Button):
    """
    A Button class for quitting game
    """

    def __init__(self, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        Button.__init__(self, [screen_width - 400, screen_height - 150, 300, 100], "QUIT GAME", "verdana", 40, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self):
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

        Button.__init__(self, [screen_width - 400, screen_height - 150, 300, 100], "MAIN MENU", "verdana", 40, WHITE1)

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self):
        """
        MainMenuButton's own operation

        :return: None
        """

        pass


class LevelButton(Button):
    """
    A Button class for playing a specific level

    Each LevelButton instance has its own level attribute to connect to.
    """

    def __init__(self, level, on_screen):
        """
        Initializing method

        Fix all properties of Button class
        """

        # This will be modified in further commits
        Button.__init__(self, [screen_width - 400, screen_height - 150, 300, 100], "QUIT GAME", "verdana", 40, WHITE1)

        # Number of level to connect
        self.levelnum = level

        # Screen class in which this button is included
        self.on_screen = on_screen
        self.on_screen.manage_list.append(self)     # Add this button to this screen

    def operate(self):
        """
        LevelButton's own operation

        :return: None
        """

        pass        # Will be added after making LevelScreen class


class Text:
    """
    A text surface class to display all texts appearing in this game
    """

    def __init__(self, text, font, font_size, pos, fixpoint="topleft", color=WHITE1):
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

    def fix_position(self):
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

    def update(self, mouse_state, key_state):
        """
        Updating method

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        pass

    def update_text(self, new_text):
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

    def draw(self, surface):
        """
        Draw text on a given surface
        :param surface: surface to draw on
        :return: None
        """

        surface.blit(self.text_surface, self.rect)


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

    def update(self, mouse_state, key_state) -> None:
        """
        Update all texts/buttons on this screen

        :param mouse_state: Dictionary of clicking event and position info
        :param key_state: Dictionary of event from pressing keyboard
        :return: None
        """

        for t in self.manage_list:
            t.update(mouse_state, key_state)

    def draw(self, surface):
        """
        Draw all texts/buttons on this screen

        :param surface: Surface to draw on
        :return: None
        """

        screen.fill(BLACK)

        for t in self.manage_list:
            t.draw(surface)

    def show(self):
        """
        Display this screen

        :return: None
        """

        self.now_display = True

    def hide(self):
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

        self.title_text = Text("ARC TRACKER", "verdana", 50, (screen_width // 2, screen_height // 5), "midtop")     # Text object
        self.manage_list.append(self.title_text)            # Append this text to manage_list

        self.level_select_button = LevelSelectButton(self)  # Button for level selection
        self.settings_button = SettingsButton(self)         # Button for settings
        self.quit_button = QuitButton(self)                 # Button for quitting game


mainmenu_screen = MainMenuScreen()      # Generate MainMenuScreen class instance
