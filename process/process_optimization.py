import numpy as np

from generals.save_load import LoadBasic, SaveBasic
from process.init_data import Data, DataBasicInfo
from obj_class.sequence import Sequence


class Cost:
    weight = [1, 1, 1]  # visual, action, talking

    def __init__(self, time_num, seq_num, char_num, cam_num, weight=None):
        if weight is not None:
            self.weight = weight
        self.time_num = time_num
        self.seq_num = seq_num
        self.char_num = char_num
        self.cam_num = cam_num

        self.default_total_cost = np.full((time_num, cam_num), 0, dtype=float)


class CostCalculate:
    require_files_list = ['animation_score']

    @staticmethod
    def request_files_check(path):
        from generals.check import check_files_integrity
        return check_files_integrity(path, CostCalculate.require_files_list, suffix="data")

    @staticmethod
    def add_camera_cost(cost_basic, project_data, weight, save=True):
        # camera_angle_cost
        CostCalculate.add_camera_angle_cost(cost_basic, project_data, weight)
        CostCalculate.add_camera_view_cost(cost_basic, project_data, weight)

    @staticmethod
    def add_action_cost(cost_basic, project_data, weight, save=True):
        # action_score
        action_cost_dict = LoadBasic.load_basic('animation_score.data', '../local_data', 'json')

        # action_map_phase
        action_map = np.full((cost_basic.time_num, cost_basic.char_num), None)
        for s_i in range(len(project_data.sequence_data.keys())):
            for t_i in range(project_data.data_basic_info.sequences_start[s_i], project_data.data_basic_info.sequences_end[s_i]+1):
                for c_i in range(cost_basic.char_num):
                    char_name = project_data.characters[c_i].character_name
                    action_cost = 0
                    for action in project_data.sequence_data[s_i].characters_action[c_i]:
                        if action == 'NA':
                            cost = 1
                        else:
                            cost_key = '{char_name}_base_{action_name}'.format(char_name=char_name, action_name=action).lower()
                            # temp, animation dict 中的 action 存在描述性错误或者缺少
                            if cost_key in action_cost_dict.keys():
                                cost = action_cost_dict[cost_key] * weight
                            else:
                                print(cost_key)
                                cost = 0.5 * weight
                            # temp end
                        action_cost += cost
                    action_map[t_i][c_i] = project_data.sequence_data[s_i].characters_action[c_i]

                    cam_list = project_data.characters[c_i].camera_list
                    for cam in cam_list:
                        cam_index = cam.camera_index
                        cost_basic.default_total_cost[t_i][cam_index] += action_cost
        if save:
            SaveBasic.save_basic(action_map, 'action_map_ori_name', '../data/middle_data', called='add_action_cost')
            SaveBasic.save_basic(cost_basic, 'cost_basic', '../data/middle_data', called='add_action_cost')

    @staticmethod
    def add_talking_cost(cost_basic, project_data, weight, save=True):
        pass

    @staticmethod
    def add_camera_angle_cost(cost_basic, project_data, weight):
        # 没有加入rotation的考虑，需要在未来制作更加详细的camera_basic_cost dict
        # LoadBasic.load_basic(camera_basic_cost dict)
        camera_basic_cost = {'LS': {-90.0: 1, 0.0: 1.5, 90.0: 1, 180.0: 1.25},
                'MS': {-90.0: 0.5, -45.0: 0.0, 0.0: 1.0, 45.0: 0.0, 90.0: 0.5},
                'CU': {0.0: 1.75},
                'NA': {0.0: 2}}

        for t_i in range(cost_basic.time_num):
            for c_i in range(cost_basic.char_num):
                for cam in project_data.characters[c_i].camera_list:
                    cam_i = cam.camera_index

                    cost = camera_basic_cost[cam.distance2char][cam.angel]
                    cost_basic.default_total_cost[t_i][cam_i] += cost


    @staticmethod
    def add_camera_view_cost(cost_basic, project_data, weight):
        pass


def dynamic_optimization(cost_basic, project_data):
    sequence_start = project_data.data_basic_info.sequences_start
    sequence_duration = project_data.data_basic_info.sequences_duration
    sequence_end = project_data.data_basic_info.sequences_end

    for s_i, start in enumerate(sequence_start):
        timestamp_data = [project_data.timestamp_data[i] for i in range(start, sequence_end[s_i]+1)]
        seq_cost_map = process_one_sequence(project_data.sequence_data[s_i], project_data.timestamp_data,
                                            start, sequence_duration[s_i])

    pass


def process_one_sequence(sequence_data, timestamp_data, seq_start_t, seq_dur):
    selection_duration = [i for i in reversed(range(seq_dur+1))]
    for selected_dur in selection_duration:
        l_s = seq_start_t
        r_s = seq_start_t + int(seq_dur/2)
        selected_duration(sequence_data, timestamp_data, l_s, r_s, selected_dur, seq_dur)
        pass
    return -1


def selected_duration(sequence_data, timestamp_data, l_s, r_s, select_dur, seq_dur):
    if select_dur == 1:
        return 1
    l_max = int(seq_dur/2)
    r_max = seq_dur - l_max
    dur_pair = cal_pair(select_dur, l_max, r_max)

    pass


def cal_pair(dur, l_max, r_max):
    pair_list = []
    for i in range(dur+1):
        l_dur = i
        r_dur = dur - i
        if l_dur > l_max or r_dur > r_max:
            continue
        pair_dur = [l_dur, r_dur]
        if pair_dur in pair_list:
            continue
        else:
            pair_list.append(pair_dur)
    return pair_list


def init_optimization(project_data):
    time_num = project_data.data_basic_info.timestamp_length
    sequence_num = project_data.data_basic_info.sequence_num
    sequence_start = 0
    sequence_end = 0
    char_num = project_data.data_basic_info.character_num
    camera_num = project_data.data_basic_info.camera_num

    cost_basic = Cost(time_num, sequence_num, char_num, camera_num)
    return cost_basic


def main():
    p_id = 81
    project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../data')

    # static cost initialization
    cost_basic = init_optimization(project_data)
    CostCalculate.request_files_check('../local_data')
    # CostCalculate.add_action_cost(cost_basic, project_data, 1)
    CostCalculate.add_camera_cost(cost_basic, project_data, 1)

    # dynamic cost calculation
    dynamic_optimization(cost_basic, project_data)
    pass


if __name__ == "__main__":
    main()