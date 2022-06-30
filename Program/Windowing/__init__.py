# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

# Hide the PyGame welcoming message, to avoid PEP8 errors we put this in an empty file
# in this case the __init__.py file from the Windowing module Without this, when importing
# the PyGame module the program will always print out the welcome message.
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
