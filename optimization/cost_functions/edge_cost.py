from optimization.cost_functions import cost_curve


def pos_continuity_cost(eye_pos_1, eye_pos_2):
    """
        :param eyepos1: character eye position in first node
        :param eyepos2: character eye position in second node
        :return: character eye position continuity cost
        description:
        character's eye position should be consistent between shots
        """
    cost = cost_curve.positionChangeCurve(eye_pos_1, eye_pos_2)
    return cost

def getDefaultLeftRightOrder(t, cam, leftRightOrder):
    """
    :param t: time
    :param cam: camera index
    :param leftRightOrder: left right order data
    :return: character on screen left to right order for node [t, cam]
    """
    return leftRightOrder[t][cam]


def getDurationCost(node1, node2, d):
    """
    :param node1: first node
    :param node2: second node
    :param d: duration
    :return: duration cost
    description:
    in patent I mentioned shot intensity should be proportional to user sepecified story intensity. Because the director's hint idea is not
    considered in project for now, we use average duration = 3 seconds
    """
    if node1[1] == node2[1]:
        return cost_curve.durationCurve(0)
    return cost_curve.durationCurve(d)


def get_left_right_continuity_cost(lr_1, lr_2):
    cost = 0
    for i in range(len(lr_1)):
        if lr_1[i] != lr_2[i]:
            cost += 1
    cost = cost / len(lr_1)
    return cost