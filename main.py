"""
Actually running game loop
"""


from screens import *
import init


mainmenu_screen.show()


# Main game loop
while init.running:

    # Get all kind of events generated from mouse
    pygame.event.get()
    mouse[LCLICK], mouse[MCLICK], mouse[RCLICK], mouse[SCRLUP], mouse[SCRLDN] = pygame.mouse.get_pressed(5)
    mouse[CURPOS] = pygame.mouse.get_pos()        # Get cursor position on the screen

    # Get all kind of events generated from keyboard
    keys = pygame.key.get_pressed()

    # Update and draw main menu screen
    if mainmenu_screen.now_display:
        mainmenu_screen.update(mouse, keys)
        mainmenu_screen.draw(screen)

    # Update and draw level selection screen
    elif level_select_screen.now_display:
        level_select_screen.update(mouse, keys)
        level_select_screen.draw(screen)

    # Update and draw how-to-play screen
    elif how_to_play_screen.now_display:
        how_to_play_screen.update(mouse, keys)
        how_to_play_screen.draw(screen)

    # Update and draw settings screen
    elif settings_screen.now_display:
        settings_screen.update(mouse, keys)
        settings_screen.draw(screen)

    # Update and draw gameplay screen
    elif gameplay_screen.now_display:
        gameplay_screen.update(mouse, keys)
        gameplay_screen.draw(screen)

    pygame.display.flip()                           # Update all display changes and show them
    init.DELTA_TIME = fps_clock.tick(FPS) / 1000    # Get time difference between present and previous game loop in seconds
