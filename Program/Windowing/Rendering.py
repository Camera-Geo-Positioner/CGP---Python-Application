# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)
import math
from enum import Enum

import cv2
import numpy as np
import pygame


class Rendering:    # pragma: no cover
    class FontSize(Enum):
        """ Enum for the different font sizes. """
        Mini = 12
        Small = 14
        Medium = 20
        Large = 24

    class TextAlignment(Enum):
        """Enum for the different text alignments. """
        TopLeft = 0
        TopCenter = 1
        TopRight = 2
        MiddleLeft = 3
        MiddleCenter = 4
        MiddleRight = 5

    @staticmethod
    def RenderText(
            surface,
            text,
            x, y,
            fontSize=FontSize.Medium,
            textAlignment=TextAlignment.TopLeft,
            color=(255, 255, 255, 255),
            shadowOffset=2
    ):  # pragma: no cover
        """ Renders a text on a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the text on.
        text : str
            The text to render.
        x : int
            The x coordinate of the text.
        y : int
            The y coordinate of the text.
        fontSize : FontSize
            The font size of the text, default is FontSize.Medium.
        textAlignment : TextAlignment
            The text alignment of the text, default is TextAlignment.TopLeft.
        color : tuple
            The color of the text, default is (255, 255, 255, 255).
        shadowOffset : int
            The offset of the shadow, default is 2.
        """

        # Render shadow, if necessary
        if shadowOffset > 0:
            Rendering._RenderLabel(surface, text, x, y + shadowOffset, fontSize, textAlignment, (0, 0, 0))

        # Render text
        Rendering._RenderLabel(surface, text, x, y, fontSize, textAlignment, color)

    @staticmethod
    def RenderLine(surface, x1, y1, x2, y2, color=(255, 255, 255, 255), width=1):  # pragma: no cover
        """ Renders a line on a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the line on.
        x1 : int
            The x coordinate of the first point.
        y1 : int
            The y coordinate of the first point.
        x2 : int
            The x coordinate of the second point.
        y2 : int
            The y coordinate of the second point.
        color : tuple
            The color of the line, default is (255, 255, 255, 255).
        width : int
            The width of the line, default is 1.
        """

        # Create a new surface
        lineSurface = Rendering._CopyEmptySurface(surface)

        # Parse the color and alpha value
        color, alpha = Rendering._ParseColorAndAlpha(color)

        # Draw the line
        pygame.draw.line(lineSurface, color, (x1, y1), (x2, y2), width)

        # Apply the alpha value
        lineSurface.set_alpha(alpha)

        # Blit the line to the surface
        surface.blit(lineSurface, (0, 0))

    @staticmethod
    def RenderPolygon(surface, points, color=(255, 255, 255, 255), width=1):  # pragma: no cover
        """ Renders a polygon of points on a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the line on.
        points: [(int, int)]
            The list of points to render lines between.
        color : tuple
            The color of the line, default is (255, 255, 255, 255).
        width : int
            The width of the line, default is 1.
        """

        # Create a new surface
        polygonSurface = Rendering._CopyEmptySurface(surface)

        # Parse the color and alpha value
        color, alpha = Rendering._ParseColorAndAlpha(color)

        # Draw the lines, between the points
        for i in range(len(points)):
            pygame.draw.line(polygonSurface, color, points[i], points[(i + 1) % len(points)], width)

        # Apply the alpha value
        polygonSurface.set_alpha(alpha)

        # Blit the line to the surface
        surface.blit(polygonSurface, (0, 0))

    @staticmethod
    def RenderPoint(surface, x, y, color=(255, 255, 255, 255), radius=3):  # pragma: no cover
        """ Renders a point on a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the point on.
        x : int
            The x coordinate of the point.
        y : int
            The y coordinate of the point.
        color : tuple
            The color of the point, default is (255, 255, 255, 255).
        radius : int
            The radius of the point, default is 3.
        """

        # Create a new surface
        pointSurface = Rendering._CopyEmptySurface(surface)

        # Parse the color and alpha value
        color, alpha = Rendering._ParseColorAndAlpha(color)

        # Draw the point
        pygame.draw.circle(pointSurface, color, (x, y), radius)

        # Apply the alpha value
        pointSurface.set_alpha(alpha)

        # Blit the point to the surface
        surface.blit(pointSurface, (0, 0))

    @staticmethod
    def RenderBox(surface, x, y, width, height, color=(25, 25, 25, 125), cornerRadius=4):  # pragma: no cover
        """ Renders a box on a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the box on.
        x : int
            The x coordinate of the box.
        y : int
            The y coordinate of the box.
        width : int
            The width of the box.
        height : int
            The height of the box.
        color : tuple
            The color of the box, default is (25, 25, 25, 125).
        cornerRadius : int
            The radius of the corners, default is 4.
        """

        # Create a new surface
        boxSurface = Rendering._CopyEmptySurface(surface)

        # Parse the color and alpha value
        color, alpha = Rendering._ParseColorAndAlpha(color)

        # Draw the box
        pygame.draw.rect(boxSurface, color, (x, y, width, height), 0, cornerRadius)

        # Apply the alpha value
        boxSurface.set_alpha(alpha)

        # Blit the box to the surface
        surface.blit(boxSurface, (0, 0))

    @staticmethod
    def RenderCrosshair(surface, x, y, color=(255, 0, 0, 180), spacing=4, lengths=12, width=4,
                        centerOutline=True):  # pragma: no cover
        """
        Renders a crosshair on the given surface the surface to render the crosshair on

        Parameters
        ---------
        surface : pygame.Surface
            The surface to render the crosshair onto.
        x : int
            The x coordinate of the position of the CENTER of the crosshair.
        y : int
            The y coordinate of the position of the CENTER of the crosshair.
        color : tuple
            The color of the crosshair in (r, g, b, alpha), default is (255, 0, 0, 180).
        spacing : int
            The distance from center to where crosshair lines start, default is 4.
        lengths : int
            The length of the crosshair lines, default is 12.
        width : int
            The width of the crosshair lines, default is 4.
        centerOutline : bool
            Defines if an outline box should be drawn around the center, default is True.
        """

        # create temporary surface
        crosshairSurface = Rendering._CopyEmptySurface(surface)

        # Parse the color and alpha value
        color, alpha = Rendering._ParseColorAndAlpha(color)

        # draw the four sides of the crosshair:
        # top:
        pygame.draw.rect(crosshairSurface, color, (x - math.ceil(width / 2), y - spacing - lengths, width, lengths))
        # bottom:
        pygame.draw.rect(crosshairSurface, color, (x - math.ceil(width / 2), y + spacing, width, lengths))
        # left:
        pygame.draw.rect(crosshairSurface, color, (x - spacing - lengths, y - math.ceil(width / 2), lengths, width))
        # right:
        pygame.draw.rect(crosshairSurface, color, (x + spacing, y - math.ceil(width / 2), lengths, width))

        # if enabled, also draw center outline
        if centerOutline:
            rectangle = (x - spacing, y - spacing, spacing * 2, spacing * 2)
            pygame.draw.rect(crosshairSurface, color, rectangle, 1)

        # set alpha
        crosshairSurface.set_alpha(alpha)

        # Blit the crosshair to the surface
        surface.blit(crosshairSurface, (0, 0))

    @staticmethod
    def ConvertOpenCVImageToPyGameImage(image: np.ndarray) -> pygame.Surface:
        """ Convert OpenCV images for Pygame.

        Parameters
        ----------
        image : numpy.ndarray
            The OpenCV image.

        Returns
        -------
        pygame.Surface
            The Pygame image.
        """

        # Prevent unnecessary conversion
        if isinstance(image, pygame.Surface):
            return image

        # Convert to pygame image
        imageFormat = 'RGB'
        if image.dtype.name == 'uint16':
            image = (image / 256).astype('uint8')
        size = image.shape[1::-1]
        if len(image.shape) == 2:
            image = np.repeat(image.reshape(size[1], size[0], 1), 3, axis=2)
            imageFormat = 'RGB'
        else:
            imageFormat = 'RGBA' if image.shape[2] == 4 else 'RGB'
            image[:, :, [0, 2]] = image[:, :, [2, 0]]

        # Create surface and internally convert based on image format
        surface = pygame.image.frombuffer(image.flatten(), size, imageFormat)
        if pygame.get_init() and pygame.display.get_init():
            return surface.convert_alpha() if imageFormat == 'RGBA' else surface.convert()
        else:
            return surface

    @staticmethod
    def ConvertSurfaceToOpenCV(surface) -> np.ndarray:
        """
        Convert a Pygame surface to OpenCV.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to convert.

        Returns
        -------
        numpy.ndarray
            The OpenCV image.
        """
        image = pygame.surfarray.array3d(surface)
        image = np.swapaxes(image, 0, 1)
        image = image[:, :, ::-1]
        return image

    @staticmethod
    def _GetFont(fontSize) -> pygame.font.Font:  # pragma: no cover
        """ Returns the font used for rendering.

        Parameters
        ----------
        fontSize : int
            The size of the font.

        Returns
        -------
        pygame.font.Font
            The font used for rendering.
        """

        return pygame.font.SysFont('Arial', fontSize.value)

    @staticmethod
    def _CopyEmptySurface(surface) -> pygame.Surface:  # pragma: no cover
        """ Creates an empty surface from a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to create the empty surface from.

        Returns
        -------
        pygame.Surface
            The empty surface.
        """

        width, height = surface.get_size()
        return pygame.Surface((width, height), pygame.SRCALPHA, 32)

    @staticmethod
    def _ParseColorAndAlpha(color) -> ((int, int, int), int):  # pragma: no cover
        """ Parses a color and alpha value from a given color.

        Parameters
        ----------
        color : tuple
            The color to parse.

        Returns
        -------
        ((int, int, int), int)
            The parsed color and alpha value.
        """

        if len(color) == 3:
            return color, 255
        elif len(color) == 4:
            return (color[0], color[1], color[2]), color[3]

    @staticmethod
    def _RenderLabel(
            surface,
            text,
            x, y,
            fontSize=FontSize.Medium,
            textAlignment=TextAlignment.TopLeft,
            color=(255, 255, 255, 255)
    ):  # pragma: no cover
        """ Renders a label of text on a given surface.

        Parameters
        ----------
        surface : pygame.Surface
            The surface to render the label on.
        text : str
            The text to render.
        x : int
            The x coordinate of the label.
        y : int
            The y coordinate of the label.
        fontSize : FontSize
            The font size of the text, default is FontSize.Medium.
        textAlignment : TextAlignment
            The text alignment of the text, default is TextAlignment.TopLeft.
        color : tuple
            The color of the label, default is (255, 255, 255, 255).
        """

        # Get the font
        font = Rendering._GetFont(fontSize)

        # Parse the color and alpha value
        color, alpha = Rendering._ParseColorAndAlpha(color)

        # Render the text surface
        textSurface = font.render(text, True, color)

        # Apply the alpha value
        textSurface.set_alpha(alpha)

        # Blit the text surface on the given surface,
        # aligned as specified

        textRect = textSurface.get_rect()
        switcher = {
            0: (x, y),  # top-left
            1: (x - textRect.width / 2, y),  # top-center
            2: (x - textRect.width, y),  # top-right

            3: (x, y - textRect.height / 2),  # middle-left
            4: (x - textRect.width / 2, y - textRect.height / 2),  # middle-center
            5: (x - textRect.width, y - textRect.height / 2),  # middle-right
        }
        (ax, ay) = switcher.get(textAlignment.value)

        textRect.left = ax
        textRect.top = ay
        surface.blit(textSurface, textRect)
