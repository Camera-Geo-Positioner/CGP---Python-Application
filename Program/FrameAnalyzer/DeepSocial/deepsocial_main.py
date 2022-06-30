# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software Project course.
# © Copyright Utrecht University (Department of Information and Computing Sciences)


# import dependencies
# from IPython.display import display, Javascript, Image
# from js2py import eval_js
# from google.colab.patches import cv2_imshow
# from base64 import b64decode, b64encode
import os
import time

import cv2
import numpy as np
import torch

from CameraReader import CameraVideoReader
from FrameAnalyzer.DeepSocial import deepsocial
from FrameAnalyzer.DeepSocial.darknet import darknet
from FrameAnalyzer.DeepSocial.darknet import sort as sort

# os.chdir('darknet')
# print currect directory
print(os.getcwd())
# %%
# import darknet functions to perform object detections -- done above
if __name__ == '__main__':
    # load in our YOLOv4 architecture network
    network, class_names, class_colors = darknet.load_network("FrameAnalyzer/DeepSocial/darknet/cfg/yolov4.cfg",
                                                              "FrameAnalyzer/DeepSocial/darknet/cfg/coco.data",
                                                              "FrameAnalyzer/DeepSocial/DeepSocial.weights")
    # network, class_names, class_colors = darknet.load_network("cfg/yolov4-tiny.cfg", "cfg/coco.data", "../yolov4-tiny.weights")
    class_names = ['person', 'bicycle', 'car', 'motorbike', 'bus', 'truck']
    # class_names = ['person']

    width = darknet.network_width(network)
    height = darknet.network_height(network)


# darknet helper function to run detection on image
def darknet_helper(img, width, height, network, class_names, threshold=0.5):
    darknet_image = darknet.make_image(width, height, 3)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (width, height), interpolation=cv2.INTER_LINEAR)

    # get image ratios to convert bounding boxes to proper size
    img_height, img_width, _ = img.shape
    width_ratio = img_width / width
    height_ratio = img_height / height

    # run model on darknet style image to get detections
    darknet.copy_image_from_bytes(darknet_image, img_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=threshold)
    darknet.free_image(darknet_image)
    return detections, width_ratio, height_ratio

if __name__ == '__main__':
    mot_tracker = sort.Sort(max_age=25, min_hits=4, iou_threshold=0.3)

    Input = "Program/FrameAnalyzer/DeepSocial/OxfordTownCentreDataset.mp4"
    # Input = "rtsp://user1:2D3Dproject@192.168.0.200:554/profile3/media.smp"
    ReductionFactor = 1
    calibration = [[180, 162], [618, 0], [552, 540], [682, 464]]  # standard calibration for Oxford dataset
    # calibration = [[0, 0], [960, 0], [302, 540], [482, 540]]  # self-added configuration for view outside the window
    UseModifiedBirdEye = False
    rectSrc = np.float32([[434, 66], [500, 56], [503, 372], [735, 357]])
    dx = 350
    dy = 50
    destSrc = np.float32([[dx, dy], [960-dx, dy], [dx, 540-dy], [960-dx, 540-dy]])


    ######################## Frame number
    StartFrom = 0
    EndAt = 5000  # 500                       #-1 for the end of the video
    ######################## (0:OFF/ 1:ON) Outputs
    CouplesDetection = 0  # Enable Couple Detection
    DTC = 1  # Detection, Tracking and Couples
    SocialDistance = 1
    CrowdMap = 0
    MoveMap = 0
    ViolationMap = 0
    RiskMap = 0
    ######################## Units are Pixel
    ViolationDistForIndivisuals = 28
    ViolationDistForCouples = 31
    ####
    CircleradiusForIndivsual = 10
    CircleradiusForCouples = 12
    ########################
    MembershipDistForCouples = (16, 10)  # (Forward, Behind) per Pixel
    MembershipTimeForCouples = 35  # Time for considering as a couple (per Frame)
    ######################## (0:OFF/ 1:ON)
    CorrectionShift = 1  # Ignore people in the margins of the video
    # HumanHeightLimit = 200  # Ignore people with unusual heights
    HumanHeightLimit = 900  # Ignore people with unusual heights
    ########################
    Transparency = 0.7
    ######################## Output Video's path
    Path_For_DTC = os.getcwd() + "Program/FrameAnalyzer/DeepSocial/DeepSOCIAL DTC.avi"
    Path_For_SocialDistance = os.getcwd() + "Program/FrameAnalyzer/DeepSocial/DeepSOCIAL Social Distancing.avi"
    Path_For_CrowdMap = os.getcwd() + "Program/FrameAnalyzer/DeepSocial/DeepSOCIAL Crowd Map.avi"


# %%
def extract_humans(detections):
    detetcted = []
    if len(detections) > 0:  # At least 1 detection in the image and check detection presence in a frame
        idList = []
        id = 0
        for label, confidence, bbox in detections:
            # if label in ['person', 'bicycle', 'car', 'motorbike', 'bus', 'truck', 'cat', 'dog']:
            if label == 'person':
                xmin, ymin, xmax, ymax = darknet.bbox2points(bbox)
                id += 1
                if id not in idList: idList.append(id)
                detetcted.append([int(xmin), int(ymin), int(xmax), int(ymax), idList[-1]])
    return np.array(detetcted)


def centroid(detections, image, calibration, _centroid_dict, CorrectionShift, HumanHeightLimit):
    e = deepsocial.birds_eye(image.copy(), calibration, False, 0, 0) #np.float32(rectSrc), np.float32(destSrc))
    centroid_dict = dict()
    now_present = list()
    if len(detections) > 0:
        for d in detections:
            p = int(d[4])
            now_present.append(p)
            xmin, ymin, xmax, ymax = d[0], d[1], d[2], d[3]
            w = xmax - xmin
            h = ymax - ymin
            x = xmin + w / 2
            y = ymax - h / 2
            if h < HumanHeightLimit:
                overley = e.image
                bird_x, bird_y = e.projection_on_bird((x, ymax))
                if CorrectionShift:
                    if deepsocial.checkupArea(overley, 1, 0.25, (x, ymin)):
                        continue
                e.setImage(overley)
                center_bird_x, center_bird_y = e.projection_on_bird((x, ymin))
                centroid_dict[p] = (
                    int(bird_x), int(bird_y),
                    int(x), int(ymax),
                    int(xmin), int(ymin), int(xmax), int(ymax),
                    int(center_bird_x), int(center_bird_y))

                _centroid_dict[p] = centroid_dict[p]
    return _centroid_dict, centroid_dict, e.image


def ColorGenerator(seed=1, size=10):
    np.random.seed = seed
    color = dict()
    for i in range(size):
        h = int(np.random.uniform() * 255)
        color[i] = h
    return color


def VisualiseResult(_Map, e):
    Map = np.uint8(_Map)
    histMap = e.convrt2Image(Map)
    visualBird = cv2.applyColorMap(np.uint8(_Map), cv2.COLORMAP_JET)
    visualMap = e.convrt2Image(visualBird)
    visualShow = cv2.addWeighted(e.original, 0.7, visualMap, 1 - 0.7, 0)
    return visualShow, visualBird, histMap


# %%
if __name__ == '__main__':

    # cap = cv2.VideoCapture(Input)
    cap = CameraVideoReader.VideoCapture(Input, False)
    frame_width = int(cap.GetWidth())
    frame_height = int(cap.GetHeigth())
    height, width = frame_height // ReductionFactor, frame_width // ReductionFactor
    # height, width = 540, 960
    print("Video Reolution: ", (width, height))

    if DTC: DTCVid = cv2.VideoWriter(Path_For_DTC, cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (width, height))
    if SocialDistance: SDimageVid = cv2.VideoWriter(Path_For_SocialDistance, cv2.VideoWriter_fourcc(*"MJPG"), 30.0,
                                                    (width, height))
    if CrowdMap: CrowdVid = cv2.VideoWriter(Path_For_CrowdMap, cv2.VideoWriter_fourcc(*"XVID"), 30.0, (width, height))

    colorPool = ColorGenerator(size=3000)
    _centroid_dict = dict()
    _numberOFpeople = list()
    _greenZone = list()
    _redZone = list()
    _yellowZone = list()
    _final_redZone = list()
    _relation = dict()
    _couples = dict()
    _trackMap = np.zeros((height, width, 3), dtype=np.uint8)
    _crowdMap = np.zeros((height, width), dtype=int)
    _allPeople = 0
    _counter = 1
    frame = 0
    keepRunning = True

    while keepRunning:
        print('-- Frame : {}'.format(frame))
        prev_time = time.time()
        ret, frame_read = cap.read()
        # frame_resized = cv2.resize(frame_read, (width, height), interpolation=cv2.INTER_LINEAR)
        # image = frame_resized
        # cv2.imshow('Frames', image.copy())
        # continue
        if not ret: break

        frame += 1
        if frame <= StartFrom: continue
        if frame != -1:
            if frame > EndAt: break

        frame_resized = cv2.resize(frame_read, (width, height), interpolation=cv2.INTER_LINEAR)
        image = frame_resized
        e = deepsocial.birds_eye(image, calibration, UseModifiedBirdEye, rectSrc, destSrc)
        detections, width_ratio, height_ratio = darknet_helper(image, width, height)
        humans = extract_humans(detections)
        track_bbs_ids = mot_tracker.update(humans) if len(humans) != 0 else humans

        _centroid_dict, centroid_dict, partImage = centroid(track_bbs_ids, image, calibration, _centroid_dict,
                                                            CorrectionShift, HumanHeightLimit)
        redZone, greenZone = deepsocial.find_zone(centroid_dict, _greenZone, _redZone, criteria=ViolationDistForIndivisuals)

        if CouplesDetection:
            _relation, relation = deepsocial.find_relation(e, centroid_dict, MembershipDistForCouples, redZone, _couples,
                                                           _relation)
            _couples, couples, coupleZone = deepsocial.find_couples(image, _centroid_dict, relation,
                                                                    MembershipTimeForCouples,
                                                                    _couples)
            yellowZone, final_redZone, redGroups = deepsocial.find_redGroups(image, centroid_dict, calibration,
                                                                             ViolationDistForCouples, redZone, coupleZone,
                                                                             couples,
                                                                             _yellowZone, _final_redZone)
        else:
            couples = []
            coupleZone = []
            yellowZone = []
            redGroups = redZone
            final_redZone = redZone

        if DTC:
            DTC_image = image.copy()
            _trackMap = deepsocial.Apply_trackmap(centroid_dict, _trackMap, colorPool, 3)
            DTC_image = cv2.add(e.convrt2Image(_trackMap), image)
            DTCShow = DTC_image
            for id, box in centroid_dict.items():
                center_bird = box[0], box[1]
                if not id in coupleZone:
                    cv2.rectangle(DTCShow, (box[4], box[5]), (box[6], box[7]), (0, 255, 0), 2)
                    cv2.rectangle(DTCShow, (box[4], box[5] - 13), (box[4] + len(str(id)) * 10, box[5]), (0, 200, 255), -1)
                    cv2.putText(DTCShow, str(id), (box[4] + 2, box[5] - 2), cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 0, 0), 1,
                                cv2.LINE_AA)
            if CouplesDetection:
                for coupled in couples:
                    p1, p2 = coupled
                    couplesID = couples[coupled]['id']
                    couplesBox = couples[coupled]['box']
                    cv2.rectangle(DTCShow, couplesBox[2:4], couplesBox[4:], (0, 150, 255), 4)
                    loc = couplesBox[0], couplesBox[3]
                    offset = len(str(couplesID) * 5)
                    captionBox = (loc[0] - offset, loc[1] - 13), (loc[0] + offset, loc[1])
                    cv2.rectangle(DTCShow, captionBox[0], captionBox[1], (0, 200, 255), -1)
                    wc = captionBox[1][0] - captionBox[0][0]
                    hc = captionBox[1][1] - captionBox[0][1]
                    cx = captionBox[0][0] + wc // 2
                    cy = captionBox[0][1] + hc // 2
                    textLoc = (cx - offset, cy + 4)
                    cv2.putText(DTCShow, str(couplesID), (textLoc), cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 0, 0), 1, cv2.LINE_AA)
            # DTCVid.write(DTCShow)
            cv2.imshow('Frames', DTCShow)
            # key = cv2.waitKey(1)
            # if key == 27:  # exit on ESC
            #     print(cap.lasttime - cap.starttime)
            #
            #     break

        if SocialDistance:
            SDimage, birdSDimage = deepsocial.Apply_ellipticBound(centroid_dict, image, calibration, redZone, greenZone,
                                                                  yellowZone,
                                                                  final_redZone, coupleZone, couples,
                                                                  CircleradiusForIndivsual,
                                                                  CircleradiusForCouples,
                                                                  UseModifiedBirdEye, rectSrc, destSrc)
            # SDimageVid.write(SDimage)
            cv2.imshow('birdSDimage', birdSDimage)
            cv2.imshow('SDimage', SDimage)

        if CrowdMap:
            _crowdMap, crowdMap = deepsocial.Apply_crowdMap(centroid_dict, image, _crowdMap)
            crowd = (crowdMap - crowdMap.min()) / (crowdMap.max() - crowdMap.min()) * 255
            crowd_visualShow, crowd_visualBird, crowd_histMap = VisualiseResult(crowd, e)
            # CrowdVid.write(crowd_visualShow)

        cv2.waitKey(1)
        # key = cv2.waitKey(5)
        # if key == 27:  # exit on ESC
        #     keepRunning = False
        #     cap.stopDeamon()
        #     break
    print('::: Analysis Completed')

    cap.release()
    # cv2.destroyWindow("Frames")
    cap.stopDeamon()

    if DTC: DTCVid.release(); print("::: Video Write Completed : ", Path_For_DTC)
    if SocialDistance: SDimageVid.release(); print("::: Video Write Completed : ", Path_For_SocialDistance)
    if CrowdMap: CrowdVid.release(); print("::: Video Write Completed : ", Path_For_CrowdMap)
    # os.chdir('..')
    torch.cuda.empty_cache()