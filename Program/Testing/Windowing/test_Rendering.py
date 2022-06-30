# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)

import pygame
from IO import Pathing
from Windowing.Rendering import Rendering


def test_Convert():
    testImage = pygame.image.load(str(Pathing.AssureAbsolutePath('Windowing/Assets/WatchfulEye_Small.png')))

    cvTestImage = Rendering.ConvertSurfaceToOpenCV(testImage)
    Rendering.ConvertOpenCVImageToPyGameImage(cvTestImage)
