from Calibrator.ImageReceiver.SmartImage import SmartImage
import cv2
from IO import Pathing
import numpy as np


class Test_SmartImage:
    image = cv2.imread(str(Pathing.AssureAbsolutePath("Testing/Assets/map.jpg")))

    def test_init(self):
        SmartImage(self.image)
        assert True

    def test_GetImage(self):
        smartImage = SmartImage(self.image)
        newImage = smartImage.GetImage()
        assert np.array_equal(newImage, self.image), "images not the same"
