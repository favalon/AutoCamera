import numpy as np
from optimization.cost_functions import static_cost
from optimization.cost_functions import edge_cost


def getDefaultEyePos(char, t, cam, eyePosData):
    """
    :param char: character
    :param t: time
    :param cam: camera index
    :param eyePosData: eye position data
    :return: character eye position for node [t, cam]
    """
    eyePos = eyePosData[t][cam][char]
    if eyePos == ["NA", "NA"]:
        return eyePos
    else:
        return [int(x) for x in eyePos]


def get_sequence_index(time, basic_info):

    for i, sq_start in enumerate(basic_info.sequences_start):
        if sq_start <= time <= basic_info.sequences_end[i]:
            return i
    return -1


def get_characters_activate_map(project_data):
    basic_info = project_data.data_basic_info
    char_activate_map = np.full((basic_info.timestamp_length,
                                 basic_info.character_num), 0)

    for i in range(basic_info.sequence_num):
        for c_i in range(basic_info.character_num):
            t_start = project_data.sequence_data[i].start_time[c_i]
            t_dur = project_data.sequence_data[i].duration[c_i]
            for t in range(t_start, t_start+t_dur):
                char_activate_map[t][c_i] = 1

    return char_activate_map


class StaticCostCalculation:

    @staticmethod
    def visual_cost(timestamp_data, timestamp, camera_index, activate_char, debug_flag=True):
        sub_vis_list = []
        obj_vis_list = []
        vis_cost = []

        for i, char_act in enumerate(activate_char.tolist()):
            sub_vis = []
            obj_vis = []
            if activate_char[i] == 1:
                sub_vis.append(timestamp_data.char_visibility[camera_index][i])
                sub_vis_list.append(sub_vis)
                obj_vis = []
                obj_vis_list.append(obj_vis)
            if sub_vis:
                vis_cost.append(static_cost.getVisibilityCost(sub_vis, obj_vis))
            else:
                vis_cost.append(0)

        vis_cost = sum(vis_cost) / len(vis_cost)

        if debug_flag:
            StaticCostCalculation.cost_print(timestamp, camera_index, 'visual', vis_cost)

        return vis_cost, sub_vis_list, obj_vis_list

    @staticmethod
    def lookroom_cost(timestamp_data, timestamp, camera_index, activate_char, debug_flag=True):
        look_room_cost = []
        for i, char_act in enumerate(activate_char.tolist()):
            eye_pos = []
            eye_pos_si = []
            for x in timestamp_data.eye_pos[camera_index][i]:
                if x != 'NA':
                    eye_pos_si.append(int(x))
                else:
                    eye_pos_si.append(x)
            eye_pos.append(eye_pos_si)
            eye_thetas = [0] * len(eye_pos)
            look_room_cost.append(static_cost.get_look_room_cost(eye_pos, eye_thetas))
        look_room_cost = sum(look_room_cost) / len(look_room_cost)

        if debug_flag:
            StaticCostCalculation.cost_print(timestamp, camera_index, 'look room', look_room_cost)

        return look_room_cost

    @staticmethod
    def headroom_cost(timestamp_data, timestamp, camera_index, activate_char, debug_flag=True):
        head_room_cost = []
        for i, char_act in enumerate(activate_char.tolist()):
            x = timestamp_data.head_room[camera_index][i]
            head_room = []
            if x != 'NA':
                head_room.append(int(x))
            else:
                head_room.append(x)
            if head_room:
                head_room_cost.append(static_cost.getHeadRoomCost(head_room))
        head_room_cost = sum(head_room_cost) / len(head_room_cost)

        if debug_flag:
            StaticCostCalculation.cost_print(timestamp, camera_index, ' head room', head_room_cost)

        return head_room_cost

    @staticmethod
    def shot_order_cost(totoal_timestamp, camera_data, timestamp, camera_index, debug_flag=True):
        shot_order_cost = 1
        distMap = {"CU": 0.7, "MS": 1.0, "LS": 3.0}
        if timestamp < totoal_timestamp * .1:
            # if time is in the first 10%
            dist = camera_data.distance2char
            if dist != "NA":
                dist = distMap[dist]
                shot_order_cost = static_cost.getShotOrderCost(dist)
            else:
                # no POV camera at the beginning of video to avoid confusion
                shot_order_cost = 1
        if debug_flag:
            StaticCostCalculation.cost_print(timestamp, camera_index, ' shot order', shot_order_cost)

        return shot_order_cost

    @staticmethod
    def camera_YPR_cost(camera_data, timestamp, camera_index, debug_flag=True):
        YAW_WEIGHT = {0.0: 1, -90.0: 0.25, -45.0: 0, 45.0: 0, 90.0: 0.25, 180.0: 0.5, -180.0: 0.5}
        PITCH_WEIGHT = {0.0: 0, -22.5: 0.5, 22.5: 0.25}

        yaw_cost = YAW_WEIGHT[camera_data.angel]
        pitch_cost = PITCH_WEIGHT[camera_data.rotation]

        ypr_cost = (yaw_cost + pitch_cost) / 2

        return ypr_cost

    @staticmethod
    # def cost_sum(timestamp, camera_index, vis_cost, hitch_cost, lr_cost, hr_cost, pov_cost, so_cost, ca_cost, debug_flag=True):
    def cost_sum(*args, debug_flag=True):
        QUALITY_WEIGHTS = [0.4, 0.5, 0.2, 0.1, 2, 0.2, 0.4, 0.4]

        if len(args) - 2 != len(QUALITY_WEIGHTS):
            print("cost sum args number wrong, please check weight or input cost number")

        qualityCost = 0
        for i in range(2, len(args)):
            qualityCost += args[i] * QUALITY_WEIGHTS[i-2]

        if debug_flag:
            StaticCostCalculation.cost_print(args[0], args[1], 'total node static cost', qualityCost)

        return qualityCost

    @staticmethod
    def cost_print(timestamp, camera, cost_type, value):
        print("time {} -- camera {} -- {} cost : {}".format(timestamp, camera, cost_type, value))


class EdgeCostCalculation:

    @staticmethod
    def pos_cost(project_data, char_activate_map, node1, node2, debug_flag=True):
        FRAMEX = 1024
        FRAMEY = 768
        ts_1 = node1[0]
        ts_2 = node2[0]
        cam_1 = node1[1]
        cam_2 = node2[1]

        pos_cost = 0
        pos_count = 0
        for c_i in range(len(char_activate_map[0])):
            if char_activate_map[ts_1][c_i] == char_activate_map[ts_2][c_i] == 1:
                pos_count += 1
                eye_pos_1 = project_data.timestamp_data[ts_1].eye_pos[cam_1][c_i]
                eye_pos_2 = project_data.timestamp_data[ts_2].eye_pos[cam_2][c_i]
                if eye_pos_1 != ['NA', 'NA'] and eye_pos_2 != ['NA', 'NA']:
                    eye_pos_1 = [int(eye_pos_1[0]) / FRAMEX, int(eye_pos_1[1]) / FRAMEY]
                    eye_pos_2 = [int(eye_pos_2[0]) / FRAMEX, int(eye_pos_2[1]) / FRAMEY]
                    pos_cost += edge_cost.pos_continuity_cost(eye_pos_1, eye_pos_2)

        if pos_count != 0:
            pos_cost = pos_cost / pos_count

        if debug_flag:
            EdgeCostCalculation.cost_print(node1, node2, 'pos cost', pos_cost)

        return pos_cost

    @staticmethod
    def gaze_cost():
        return 0

    @staticmethod
    def moving_cost():
        return 0

    @staticmethod
    def left_right_cost(project_data, node1, node2, debug_flag=True):
        ts_1 = node1[0]
        ts_2 = node2[0]
        cam_1 = node1[1]
        cam_2 = node2[1]

        lr_1 = project_data.timestamp_data[ts_1].left2right_order[cam_1]
        lr_2 = project_data.timestamp_data[ts_2].left2right_order[cam_2]

        lr_cost = edge_cost.get_left_right_continuity_cost(lr_1, lr_2)

        if debug_flag:
            EdgeCostCalculation.cost_print(node1, node2, 'left right order', lr_cost)

        return lr_cost

    @staticmethod
    def transfer_cost_sum(*args, debug_flag=True):
        TRANSFER_WEIGHTS = [0.2, 0.2, 0.3, 0.3]

        if len(args) - 2 != len(TRANSFER_WEIGHTS):
            print("cost sum args number wrong, please check weight or input cost number")

        transfer_cost = 0
        for i in range(2, len(args)):
            transfer_cost += args[i] * TRANSFER_WEIGHTS[i-2]

        if debug_flag:
            EdgeCostCalculation.cost_print(args[0], args[1], 'sum transfer', transfer_cost)

        return transfer_cost

    @staticmethod
    def duration_cost_old(node1, node2):
        duration = abs(node2[0] - node1[0])
        duration_cost = edge_cost.getDurationCost(node1, node2, duration)
        return duration_cost

    @staticmethod
    def duration_cost(d):
        from optimization.cost_functions import cost_curve
        return cost_curve.durationCurve(d)

    @staticmethod
    def cost_print(node1, node2, cost_type, value):
        n1 = ', '.join([str(n) for n in node1])
        n2 = ', '.join([str(n) for n in node2])
        print("node 1: [{}] -- node 2: [{}] -- {} cost : {}".format(n1, n2, cost_type, value))