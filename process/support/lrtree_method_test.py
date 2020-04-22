import numpy as np
from optimization.cost_functions.cost_main import dynamic_cost
from optimization.cost_functions import cost_curve

class ACTree:
    l_ts = []  # left timestamp
    r_ts = []  # right timestamp
    l_actree = {}
    r_actree = {}
    full_actree = []

    def __init__(self, se_dur, to_dur):
        """
        :param se_dur: selected duration
        :param to_dur: total duration
        """
        self.se_dur = se_dur
        self.to_dur = to_dur

        self.l_max = int(to_dur/2)
        self.r_max = self.to_dur - self.l_max

        self.generate_acleaf()

    def generate_acleaf(self):
        for i in range(self.se_dur + 1):
            l_dur = i
            r_dur = self.se_dur - i
            if l_dur > self.l_max or r_dur > self.r_max:
                continue
            pair_dur = [l_dur, r_dur]
            if pair_dur in self.full_actree:
                continue
            else:
                self.l_actree[i] = l_dur
                self.r_actree[i] = r_dur
                self.full_actree.append(pair_dur)


def calculate_pair_list(s_n, l_n, r_n):
    '''
    :param s_n: selected cut
    :param l_n: left total cut
    :param r_n: right total cut
    :return: able to find pair, cut pair combinations
    '''
    cut_pairs = []
    p_flag = False
    if s_n > l_n + r_n:
        return p_flag, cut_pairs
    for l_i in range(s_n+1):
        r_i = s_n - l_i
        if l_i <= l_n and r_i <= r_n:
            pair = [l_i, r_i]
            cut_pairs.append(pair)
    if len(cut_pairs) > 0:
        p_flag = True
    return p_flag, cut_pairs


def cal_cost(project_data, char_activate_map, cost_map, path, config=None, debug_flag=False):
    DURATION_COST_WEIGHT = 1.0
    # calculate cost by given path

    if len(path) == 0:
        return 0
    if len(path) == 1:
        return dynamic_cost(project_data, char_activate_map, path[0], path[0], config=config, debug_flag=config['debug'])
    if len(path) == 2:
        return dynamic_cost(project_data, char_activate_map, path[0], path[1], config=config, debug_flag=config['debug'])

    t_cost = 0

    # static cost
    for p in path:
        t_cost += cost_map[p[0]][p[1]]

    # dynamic cost
    for i in range(len(path)-1):
        node1 = path[i]
        node2 = path[i+1]
        t_cost += dynamic_cost(project_data, char_activate_map, node1, node2, config=config, debug_flag=config['debug'])

    # duration cost
    pre_ts = 0
    pre_cam = 0
    change_cam = 0
    sta_len = 0
    t_dur_cost = 0
    duration_center = config['duration_center']
    for i, p in enumerate(path):
        if i == 0:
            pre_cam = p[1]
            pre_ts = p[0]
            sta_len = 1
            change_cam = 1
        elif i == len(path) - 1 and p[1] == pre_cam:
            sta_len += 1
            t_dur_cost += cost_curve.durationCurve(sta_len, center=duration_center)
        elif i == len(path) - 1 and p[1] != pre_cam:
            t_dur_cost += cost_curve.durationCurve(sta_len, center=duration_center)
            change_cam += 1
            sta_len = 1
            t_dur_cost += cost_curve.durationCurve(sta_len, center=duration_center)
        else:
            if p[0] == pre_ts:
                sta_len -= 1
            if p[1] != pre_cam:
                change_cam += 1
                t_dur_cost += cost_curve.durationCurve(sta_len, center=duration_center)
                sta_len = 1
            else:
                sta_len += 1
    dur_cost = t_dur_cost/change_cam

    t_cost += dur_cost * config['duration_cost_weight']

    return t_cost


def cal_single_cost(c_n, cost_map):
    path = [[[c_n, i], [c_n, i]] for i in range(len(cost_map[0]))]
    cost = [0 for i in range(len(cost_map[0]))]
    return path, path, cost, cost


def cal_pair_cost(project_data, char_activate_map, l_c_n, r_c_n, cost_map, config=None):
    l_path = []
    r_path = []
    l_cost = []
    r_cost = []
    for cam_l_i in range(len(cost_map[l_c_n])):
        min_cost = float('inf')
        path = [None, None]
        for cam_r_i in range(len(cost_map[r_c_n])):
            cur_cost \
                = cal_cost(project_data, char_activate_map, cost_map, [[l_c_n, cam_l_i], [r_c_n, cam_r_i]], config=config)
            if cur_cost < min_cost:
                min_cost = cur_cost
                path = [[l_c_n, cam_l_i], [r_c_n, cam_r_i]]
        l_cost.append(min_cost)
        l_path.append(path)

    for cam_r_i in range(len(cost_map[r_c_n])):
        min_cost = float('inf')
        for cam_l_i in range(len(cost_map[l_c_n])):
            cur_cost\
                = cal_cost(project_data, char_activate_map, cost_map, [[l_c_n, cam_l_i], [r_c_n, cam_r_i]], config=config)
            if cur_cost < min_cost:
                min_cost = cur_cost
                path = [[l_c_n, cam_l_i], [r_c_n, cam_r_i]]
        r_cost.append(min_cost)
        r_path.append(path)

    return l_path, r_path, l_cost, r_cost


def cal_multi_cost(project_data, char_activate_map, path_l, path_r, cost_map, left=False, config=None):
    path = []
    cost = []
    if left:
        for lp in path_l:
            min_cost = float('inf')
            selected_path = None
            for rp in path_r:
                cur_path = lp + rp
                cur_cost = cal_cost(project_data, char_activate_map, cost_map, cur_path, config=config)
                if min_cost > cur_cost:
                    min_cost = cur_cost
                    selected_path = cur_path

            path.append(selected_path)
            cost.append(min_cost)
    else:
        for rp in path_r:
            min_cost = float('inf')
            selected_path = None
            for lp in path_l:
                cur_path = lp + rp
                cur_cost = cal_cost(project_data, char_activate_map, cost_map, cur_path, config=config)
                if min_cost > cur_cost:
                    min_cost = cur_cost
                    selected_path = cur_path
            path.append(selected_path)
            cost.append(min_cost)

    return path, cost


def path_selection(path_l, path_r, cost_l, cost_r, left_primary=True):
    # selected path from path_ori (primary) and path_in (check insert)

    if left_primary:
        path = path_l
        cost_path = cost_l
        for i, p_r in enumerate(path_r):
            start_cam = p_r[0][1]
            r_cost = cost_r[i]
            l_cost = cost_path[start_cam]
            if r_cost < l_cost:
                path[start_cam] = p_r
                cost_path[start_cam] = r_cost

    else:
        path = path_r
        cost_path = cost_r
        for i, p_l in enumerate(path_l):
            start_cam = p_l[0][1]
            l_cost = cost_l[i]
            r_cost = cost_path[start_cam]
            if l_cost < r_cost:
                path[start_cam] = p_l
                cost_path[start_cam] = l_cost

    return path, cost_path


def recursion_cost(c_n, cost_map, project_data, char_activate_map, config=None):
    if not c_n:
        # return np.array([]), np.array([]), np.array([]), np.array([])
        return [], [], [], []
    n = len(c_n)
    if n == 0:
        return 0
    if n == 1:
        return cal_single_cost(c_n[0], cost_map)
    elif n == 2:
        return cal_pair_cost(project_data, char_activate_map, c_n[0], c_n[1], cost_map, config=config)
    else:
        l_n = int(n/2)
        r_n = n - l_n
        l_c_n = c_n[:l_n]
        r_c_n = c_n[l_n:]
        l_l_path, l_r_path, l_l_cost, l_r_cost \
            = recursion_cost(l_c_n, cost_map, project_data, char_activate_map, config=config)
        r_l_path, r_r_path, r_l_cost, r_r_cost \
            = recursion_cost(r_c_n, cost_map, project_data, char_activate_map, config=config)

        path_1, cost_1 \
            = cal_multi_cost(project_data, char_activate_map, l_l_path, r_l_path, cost_map, left=True, config=config)
        path_2, cost_2 \
            = cal_multi_cost(project_data, char_activate_map, l_r_path, r_l_path, cost_map, left=True, config=config)
        # l start best path selection
        l_path, l_cost = path_selection(path_1, path_2, cost_1, cost_2, left_primary=True)

        path_3, cost_3 \
            = cal_multi_cost(project_data, char_activate_map, l_l_path, r_r_path, cost_map, left=False, config=config)
        path_4, cost_4 \
            = cal_multi_cost(project_data, char_activate_map, l_r_path, r_r_path, cost_map, left=False, config=config)
        # r end best path selection
        r_path, r_cost = path_selection(path_3, path_4, cost_3, cost_4, left_primary=False)
    return l_path, r_path, l_cost, r_cost


def recur_test_main():
    total_cut = 30
    cams_n = 40
    fake_cost_map = np.random.rand(total_cut, cams_n)

    l, r = recursion_cost(np.array([0]), fake_cost_map)
    print(l)
    print(r)
    return 0


def get_combination(sequence, cur_index, sel_len, sel_seq, result):
    cana_len = len(sequence) - cur_index - 1
    # if sel_seq already sel_len
    if len(sel_seq) == sel_len:
        seq = sel_seq[:]
        result.append(seq)
        return

    # if no enough element for develop a new seq
    if len(sel_seq) + cana_len > len(sequence):
        return

    # recursion
    for i in range(cur_index, len(sequence)):
        cur_seq = sel_seq[:]
        cur_seq.append(sequence[i])
        get_combination(sequence, i + 1, sel_len, cur_seq, result)
        del cur_seq[-1]


def main():
    # 1. pair calculating
    # print(calculate_pair_list(4, 5, 2))

    # 2 recursion
    recur_test_main()

    # basic info
    # sequence = [8, 6, 5, 4, 7, 8, 9, 6, 8]
    # seq_ts_group = []
    # ts = 0
    # for seq in sequence:
    #     seq_ts = []
    #     for x in range(seq):
    #         seq_ts.append(ts)
    #         ts += 1
    #     seq_ts_group.append(seq_ts)
    #
    # seq_num = len(sequence)
    #
    # sel_comb_dict = {}
    # for i in range(len(seq_ts_group[0])+1):
    #     sel_seq, result = [], []
    #     get_combination(seq_ts_group[0], 0, i, sel_seq, result)
    #     sel_comb_dict[i] = result



    pass


if __name__ == "__main__":
    main()