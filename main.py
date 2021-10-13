"""
Actually running game loop
"""


from screens import *


mainmenu_screen.show()


# Main game loop
while init.running:

    # Get all kind of events generated from mouse
    pygame.event.get()
    mouse[LCLICK], mouse[MCLICK], mouse[RCLICK], mouse[SCRLUP], mouse[SCRLDN] = pygame.mouse.get_pressed(5)
    mouse[CURPOS] = pygame.mouse.get_pos()        # Get cursor position on the screen

    # Get all kind of events generated from keyboard
    keys = pygame.key.get_pressed()

    if mainmenu_screen.now_display:
        mainmenu_screen.update(mouse, keys)
        mainmenu_screen.draw(screen)

    elif level_select_screen.now_display:
        level_select_screen.update(mouse, keys)
        level_select_screen.draw(screen)

    elif how_to_play_screen.now_display:
        how_to_play_screen.update(mouse, keys)
        how_to_play_screen.draw(screen)

    elif settings_screen.now_display:
        settings_screen.update(mouse, keys)
        settings_screen.draw(screen)

    elif gameplay_screen.now_display:
        gameplay_screen.update(mouse, keys)
        gameplay_screen.draw(screen)

    pygame.display.flip()               # Update all display changes and show them
    fps_clock.tick(FPS)                 # Make program never run at more than "FPS" frames per second
