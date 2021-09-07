"""
Actually running game loop
"""


from sprites_and_functions import *


# Main game loop
while True:
    # Get all kind of events generated from mouse
    pygame.event.get()
    mouse[LCLICK], mouse[MCLICK], mouse[RCLICK], mouse[SCRLUP], mouse[SCRLDN] = pygame.mouse.get_pressed(5)
    mouse[CURPOS] = pygame.mouse.get_pos()        # Get cursor position on the screen

    # Get all kind of events generated from keyboard
    keys = pygame.key.get_pressed()

    # Quit game when clicking mouse wheel (needs to be modified)
    if mouse[MCLICK]:
        break

    all_sprites.update(mouse, keys)     # Call "update" method of every sprite

    screen.fill(BLACK)                  # Fill screen with black
    ArcTrackerPath.group.draw(screen)   # Draw all ArcTrackerPaths
    ArcTracker.group.draw(screen)       # Draw all ArcTrackers

    pygame.display.flip()               # Update all display changes and show them
    fps_clock.tick(FPS)                 # Make program never run at more than "FPS" frames per second
