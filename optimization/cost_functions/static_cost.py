import math
from optimization.cost_functions import cost_curve

FRAMEX = 1024
FRAMEY = 768
FRAMESIZE = FRAMEX*FRAMEY
FRAME_DIAGONAL = math.sqrt(FRAMEX ** 2 + FRAMEY ** 2)
QUALITY_WEIGHTS = [0.4, 0.5, 0.2, 0.1, 2, 0.2]
TRANSFER_WEIGHTS = [0.2, 0.2, 0.3, 0.3]


def getVisibilityCost(subVis, objVis):
    """
    :param subVis: subject visibilities
    :param objVis: object visibilities
    :return: visibility proximity cost
    description:
    visibility cost is one of the node cost
    subject: action subject, object: action object
    subVis: onscreen visibility of all subjects for this node
    objVis: onscreen visibility of all objects for this node
    FRAMESIZE: actual frame size after rendering
    1 - (subject visibility + object visibility)/FRAMESIZE is the normalized cost for how much of the current action
    can be seen after rendering for this node
    """
    # TODO: Should it consider object or character actual size?
    cost = 1 - (sum(map(sum, subVis)) + sum(map(sum, objVis))) / FRAMESIZE
    return cost


def get_look_room_cost(eyepos, eyeThetas):
    """
    :param eyepos: human on screen eye position
    :param eyeThetas: human on screen eye direction
    :return: lookroom cost
    description:
    look room is the distance from left boundary to character eye's onscreen position and the eye's onscreen position's distance to right boundary
    if the character is looking to right, then the lookroom to right boundary should be larger
    if the character is looking to left, then the lookroom to left boundary should be larger
    curve is the weight function curve, a combination of two sigmoid function.
    But here because the character's eye orientation is not concerned in animation, we assume all eyes are looking perpendicular to viewers
    """
    cost = 0
    # print(eyepos)
    for i, pos in enumerate(eyepos):
        if pos != ["NA", "NA"]:
            # not using eye direction now, character models are not considering eye orientations
            theta = eyeThetas[i]
            [x, y] = eyepos[i]
            leftRoom = x
            rightRoom = FRAMESIZE - x
            cost += cost_curve.lookRoomCostCurve(leftRoom / FRAMEX, 0)
            # TODO: lookroom cost should consider eye thetas, but our model has limited gaze orientation, ignore for now
            # use right-hand coordinate system
            # if theta <= 0:
            #     # face facing left in 2D
            #     cost += lookRoomCostCurve(leftRoom / FRAMEX, theta)
            # else:
            #     # face facing right in 2D
            #     cost += lookRoomCostCurve(rightRoom / FRAMEX, theta)
        else:
            cost += 1
    return cost / len(eyepos)

def getHeadRoom(cam, char, headroomData):
    """
    :param t: time
    :param cam: camera index
    :param char: character
    :param headroomData: head room data
    :return: character headroom for node [t, cam]
    """
    headroom = headroomData[cam][char]
    if headroom == "NA":
        return headroom
    else:
        return int(headroom)


def getHeadRoomCost(headTop):
    """
    :param headTop: character on screen headroom
    :return: headroom cost
    description:
    characters' heads should not be too close or too far from the top boundary of frame
    """
    cost = 0
    for top in headTop:
        if top != "NA":
            cost += cost_curve.headRoomCostCurve(top)
    # normalize
    return cost / len(headTop)


def getShotOrderCost(dist):
    """
    :param dist:
    :return: shot order cost
    description:
    expose background information at the beginning of a scene
    cameras with higher shot size should have higher probability to show at the beginning
    """
    return cost_curve.shotOrderCurve(dist)
# def getHitchCockCost(actions_list, subVis_list, objVis_list):
#     """
#     :param actions_list: action list
#     :param subVis_list: subject visibility list
#     :param objVis_list: object visibility list
#     :return: hitchcock cost
#     description:
#     Hitchcock mentioned "the size of an object in the frame should be equal to its importance in the story at that momentum"
#     hitchcock cost is measuring whether the character/item onscreen visibility is proportional to its importance in the action
#     For visibility of characters, it is divided into 6 parts: [front head, back head, front upper body, back upper body, front lower body, back lower body]
#     For visibility of items, it is divided into 2 parts: [front, back]
#     for a single action, the importance between subject and object are different
#     for a single action, the importance of body parts are different
#     In order to calculate hitchcock cost, first find the action, then get the action SO (subject object importance distribution), then get the body (different body part importance distribution)
#     The main purpose is to see whether different part of different characters/items visibility is proportional to its importance
#     """
#     hcCosts = []
#     for i in range(len(actions_list)):
#         objVis = objVis_list[i]
#         subVis = subVis_list[i]
#         action = actions_list[i]
#         if not objVis:
#             cost = 0
#             # subVis can include character vis and object vis
#             totalVis = sum(map(sum, subVis))
#             if totalVis == 0:
#                 hcCosts.append(1)
#             else:
#                 # subjects can be characters or items
#                 for i in range(len(subVis)):
#                     if len(subVis[i]) == 6:
#                         for j in range(6):
#                             cost += abs(
#                                 (utils.getSOImportance(action)[0] / len(subVis)) * utils.getBodyImportance(action)[j] - subVis[i][j] / totalVis)
#
#                     if len(subVis[i]) == 2:
#                         for j in range(2):
#                             cost += abs(
#                                 (utils.getSOImportance(action)[0] / len(subVis)) * utils.getObjectImportance()[j] - subVis[i][j] / totalVis)
#                 hcCosts.append(cost / len(subVis))
#
#         # if this action has objects
#         else:
#             cost = 0
#             totalVis = sum(map(sum, subVis)) + sum(map(sum, objVis))
#             if totalVis == 0:
#                 hcCosts.append(1)
#             else:
#                 subjectImportance = utils.getSOImportance(action)[0] / len(subVis)
#                 objectImportance = utils.getSOImportance(action)[1] / len(objVis)
#                 bodyImportance = utils.getBodyImportance(action)
#                 itemImportance = utils.getObjectImportance()
#                 for i in range(len(subVis)):
#                     if len(subVis[i]) == 6:
#                         # this subject is a character subject
#                         for j in range(6):
#                             cost += abs(subjectImportance * bodyImportance[j] - subVis[i][j] / totalVis)
#
#                     if len(subVis[i]) == 2:
#                         # this subject is a item subject
#                         for j in range(2):
#                             cost += abs(subjectImportance * bodyImportance[j] - subVis[i][j] / totalVis)
#
#
#                 for i in range(len(objVis)):
#                     if len(objVis[i]) == 6:
#                         for j in range(6):
#                             cost += abs(objectImportance * bodyImportance[j] - objVis[i][j] / totalVis)
#
#                     if len(objVis[i]) == 2:
#                         for j in range(2):
#                             cost += abs(objectImportance * bodyImportance[j] - objVis[i][j] / totalVis)
#
#                 hcCosts.append(cost / (len(subVis) + len(objVis)))
#     return sum(hcCosts) / len(hcCosts)