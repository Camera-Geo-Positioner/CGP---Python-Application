from unittest.mock import Mock, patch, mock_open, MagicMock
from Calibrator.ImageReceiver.CycloMedia import CycloMedia
import numpy as np


class TestCycloMedia:

    rendering = 'Windowing.Rendering.Rendering'
    cycloMedia = 'Calibrator.ImageReceiver.CycloMedia.CycloMedia'
    selectMock = cycloMedia + '._SelectImageFile'
    metaMock = cycloMedia + '._GetMetaFileLines'
    getZoomMock = cycloMedia + '.GetZoomedInImage'

    @patch(selectMock, MagicMock(return_value='somePath.extension'))
    @patch(metaMock, MagicMock(return_value=(0.1, 123456, 456789)))
    @patch('cv2.imread', MagicMock(return_value=[[[255, 0, 0]]]))
    @patch('os.path.exists', MagicMock(return_value=True))
    @patch(getZoomMock, MagicMock(return_value=([[[255, 0, 0]]], (123456, 456789))))
    def test_CreateSmartImage(self):

        cycloMedia = CycloMedia()
        (smartImage, data) = cycloMedia.CreateGeoSmartImage(MagicMock())

        assert smartImage.GetImage() == [[[255, 0, 0]]]
        assert data.anchorPixelPosition == (0, 0)
        assert data.anchorGeoPosition.longitude - 4.92685 < 0.000005
        assert data.anchorGeoPosition.latitude - 52.09845 < 0.000005
        assert data.pixelScale == 0.1

    @patch(selectMock, MagicMock(return_value='somePath.extension'))
    @patch('cv2.imread', MagicMock(return_value=[[[255, 0, 0]]]))
    @patch('os.path.exists', MagicMock(return_value=False))
    def test_CreateSmartImageNoMetaData(self):

        cycloMedia = CycloMedia()
        result = cycloMedia.CreateGeoSmartImage(MagicMock())

        assert result is None

    @patch(selectMock, MagicMock(return_value=''))
    def test_CreateSmartImageCancelled(self):

        cycloMedia = CycloMedia()
        result = cycloMedia.CreateGeoSmartImage(MagicMock())

        assert result is None

    def test_CreateSmartImageNoMasterWindow(self):

        cycloMedia = CycloMedia()
        result = cycloMedia.CreateGeoSmartImage()

        assert result is None

    @patch(selectMock, MagicMock(return_value='somePath.extension'))
    @patch(metaMock, MagicMock(return_value=(0.1, 123456, 456789)))
    @patch('cv2.imread', MagicMock(return_value=[[[255, 0, 0]]]))
    @patch('os.path.exists', MagicMock(return_value=True))
    @patch(getZoomMock, MagicMock(return_value=None))
    def test_CreateSmartImageZoomWasCanceled(self):
        cycloMedia = CycloMedia()
        result = cycloMedia.CreateGeoSmartImage(MagicMock())

        assert result is None

    @patch('tkinter.filedialog.askopenfilename', MagicMock(return_value='somePath.extension'))
    @patch('tkinter.Tk', MagicMock())
    def test_SelectImageFile(self):
        assert CycloMedia._SelectImageFile() == 'somePath.extension'

    @patch('builtins.open', mock_open(read_data="0.1\n0\n0\n-0.1\n139000\n456000"))
    def test_GetMetaFileLines(self):
        result = CycloMedia._GetMetaFileLines("someMetaDataPath.tfw")
        assert result == (0.1, 139000, 456000)

    @patch(cycloMedia + '.GetZoomSquareFromUser', MagicMock(return_value=[(0, 0), (1, 1)]))
    @patch('cv2.imread', MagicMock(return_value=np.array([[[255, 0, 0]]])))
    @patch(rendering + '.ConvertOpenCVImageToPyGameImage', MagicMock(return_value=MagicMock()))
    @patch(rendering + '.ConvertSurfaceToOpenCV', MagicMock(return_value=[[[255, 0, 0]]]))
    def test_GetZoomedInImage(self):
        (image, newAnchor) = CycloMedia.GetZoomedInImage("somePath", (0.1, 1000, 2000), MagicMock())
        assert image == [[[255, 0, 0]]]
        assert newAnchor == (1000, 2000)

    @patch(cycloMedia + '.GetZoomSquareFromUser', MagicMock(return_value=None))
    @patch('cv2.imread', MagicMock(return_value=np.array([[[255, 0, 0]]])))
    def test_GetZoomedInImageNoRect(self):
        result = CycloMedia.GetZoomedInImage("somePath", (0.1, 1000, 2000), MagicMock())
        assert result is None
