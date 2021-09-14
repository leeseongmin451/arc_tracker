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

    all_sprites.update(mouse, keys)     # Call "update" method of every sprite

    if mainmenu_screen.now_display:
        mainmenu_screen.update(mouse, keys)
        mainmenu_screen.draw(screen)

    pygame.display.flip()               # Update all display changes and show them
    fps_clock.tick(FPS)                 # Make program never run at more than "FPS" frames per second
