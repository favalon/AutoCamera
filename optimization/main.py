from generals.save_load import LoadBasic, SaveBasic
from optimization.cost_functions.cost_main import initial_static_cost_map
from process.support.lrtree_method_test import recursion_cost
from optimization.cost_functions import utils


class Optimization:

    def __init__(self, project_data, config):
        self.project_data = project_data
        self.project_config = config
        self.seq_dur = OptimizationHelper.get_sequence_duration(project_data.sequence_data)
        self.seq_ts_group = OptimizationHelper.get_sequence_timestamp_group(self.seq_dur)
        self.all_seq_comb = OptimizationHelper.get_all_sequence_combination(self.seq_ts_group)
        self.static_cost = initial_static_cost_map(project_data, self.project_config['static_cost_weight'])
        self.char_activate_map = utils.get_characters_activate_map(project_data)
        self.general_result = self.run_optimization_general()
        if config['use_latest_sequence_combination']:
            self.all_comb = LoadBasic.load_basic('all_possible_sequence_{}_combination'.format(config['p_id']), '../result/temp')
        else:
            seq_all = OptimizationHelper.get_sequence_length(self.general_result)
            self.all_comb = OptimizationHelper.select_len_optimization(seq_all)

    def run_optimization_general(self):
        if not self.project_config['use_latest_general_result']:
            general_result = self.run_general_optimization()
        else:
            general_result = LoadBasic.load_basic("general_opt.result", '../result/temp')
        return general_result

    def run_general_optimization(self):

        general_result = {}
        for seq_i in self.all_seq_comb.keys():
            seq_comb = self.all_seq_comb[seq_i]
            cur_sequence_result = {}

            for len_i in seq_comb.keys():
            # for len_i in [self.seq_dur[seq_i]]:
                len_seq_comb = seq_comb[len_i]

                cur_len_result = {}
                for i, choice_comb in enumerate(len_seq_comb):
                    n = choice_comb
                    # cost_update
                    l_path, r_path, l_cost, r_cost = recursion_cost(choice_comb, self.static_cost,
                                                                    self.project_data, self.char_activate_map,
                                                                    config=self.project_config)
                    l_leaf, r_leaf = [l_path, l_cost], [r_path, r_cost]
                    if i == 0:
                        cur_len_result['left'] = l_leaf
                        cur_len_result['right'] = r_leaf
                    else:
                        OptimizationHelper.cal_cost_comparator(l_leaf, r_leaf, cur_len_result, debug=self.project_config['debug'])

                    print("{}-{}-{}".format(seq_i, len_i, i))
                cur_sequence_result[len_i] = cur_len_result
            general_result[seq_i] = cur_sequence_result

            if self.project_config['save_opt_temp']:
                SaveBasic.save_basic(cur_sequence_result, 'sequence_{}.result'.format(seq_i), path='../result/temp',
                                     called='fun: general_optimization')

        SaveBasic.save_basic(general_result, 'general_opt.result', path='../result/temp',
                             called='fun: general_optimization')

        return general_result

    def optimize_select_length(self, sel_len):
        pass

    def optimize_full_length(self):
        min_cost = 999
        select_path = None
        for path in self.all_comb:
            cur_path_cost, cur_path = OptimizationHelper.get_path_cost(path, self.general_result)
            if min_cost > cur_path_cost:
                min_cost = cur_path_cost
                select_path = cur_path
        return select_path


class OptimizationHelper:
    @staticmethod
    def get_sequence_duration(sequence):
        if not sequence:
            print("func - get_sequence_duration, sequence_data wrong")
            return -1
        seq_dur = []
        for i in range(len(sequence.keys())):
            seq_dur.append(sequence[i].sequence_dur)
        return seq_dur

    @staticmethod
    def get_sequence_timestamp_group(seq_dur):
        seq_ts_group = []
        ts = 0
        for seq in seq_dur:
            seq_ts = []
            for x in range(seq):
                seq_ts.append(ts)
                ts += 1
            seq_ts_group.append(seq_ts)

        return seq_ts_group

    @staticmethod
    def get_all_sequence_combination(seq_ts_group):
        if not seq_ts_group:
            print("func - get_all_sequence_combination, seq_ts_group wrong")
            return -1
        all_seq_comb_dict = {}
        for seq_i in range(len(seq_ts_group)):
            sel_comb_dict = {}
            for i in range(len(seq_ts_group[seq_i]) + 1):
                sel_seq, result = [], []
                OptimizationHelper.get_combination(seq_ts_group[seq_i], 0, i, sel_seq, result)
                sel_comb_dict[i] = result
            all_seq_comb_dict[seq_i] = sel_comb_dict
        return all_seq_comb_dict

    @staticmethod
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
            OptimizationHelper.get_combination(sequence, i + 1, sel_len, cur_seq, result)
            del cur_seq[-1]

    @staticmethod
    def cal_cost_comparator(l, r, len_result, debug=False):

        cur_l_path = l[0]
        cur_l_cost = l[1]
        cur_r_path = r[0]
        cur_r_cost = r[1]

        pre_l_path = len_result['left'][0]
        pre_l_cost = len_result['left'][1]
        pre_r_path = len_result['right'][0]
        pre_r_cost = len_result['right'][1]

        for i, s_l_p in enumerate(cur_l_path):
            pre_s_l_p = pre_l_path[i]
            pre_s_l_c = pre_l_cost[i]

            if pre_s_l_c < cur_l_cost[i]:
                if debug:
                    print('left path {} replace'.format(i))
                len_result['left'][0][i] = s_l_p
                len_result['left'][1][i] = cur_l_cost[i]

        for i, s_r_p in enumerate(cur_r_path):
            pre_s_r_p = pre_r_path[i]
            pre_s_r_c = pre_r_cost[i]

            if pre_s_r_c < cur_r_cost[i]:
                if debug:
                    print('right path {} replace'.format(i))
                len_result['right'][0][i] = s_r_p
                len_result['right'][1][i] = cur_r_cost[i]

    @staticmethod
    def get_sequence_length(data):
        seq_all_len = []
        for i in range(len(data.keys())):
            seq_single = []
            for j in range(len(data[i].keys())):
                seq_single.append(j)
            seq_all_len.append(seq_single)
        return seq_all_len

    @staticmethod
    def select_len_optimization(seq_all, config=None):
        result = []
        # cal_sequence_combination(0, 0, 40, [], seq_all, result)
        for i in seq_all[0]:
            left_max = sum([max_len[-1] for max_len in seq_all[0:]])
            OptimizationHelper.cal_sequence_combination(0, i, 62, left_max, [i], seq_all, result)

        SaveBasic.save_basic(result, 'all_possible_sequence_{}_combination'.format(config['p_id']), 'temp')
        return result

    @staticmethod
    def cal_sequence_combination(cur_i, cur_len, select_len, left_max, cur_sequence, sequences, result):
        if cur_i > len(sequences) - 1:
            return
        if cur_len > select_len:
            return
        if cur_len + left_max < select_len:
            return

        # print(cur_i, cur_len, cur_sequence)
        if cur_len == select_len and cur_i == len(sequences) - 1:
            print(cur_i, cur_len, cur_sequence)
            sel_comb = cur_sequence[:]
            result.append(sel_comb)
            return

        if cur_i + 1 > len(sequences) - 1:
            return

        candi_len = sequences[cur_i + 1]
        for i in candi_len:
            cur_sequence.append(i)
            left_max = sum([max_len[-1] for max_len in sequences[cur_i + 1:]])
            OptimizationHelper.cal_sequence_combination(cur_i + 1, cur_len + i, select_len, left_max, cur_sequence, sequences, result)
            del cur_sequence[-1]

    @staticmethod
    def get_path_cost(path, data):
        # n.index(min(n))
        min_cost = 0
        full_path = []
        for i, p in enumerate(path):
            if p == 0:
                min_cost += 0
            else:
                # print(i, p)
                seq_data = data[i][p]
                left_min_index = seq_data['left'][1].index(min(seq_data['left'][1]))
                right_min_index = seq_data['right'][1].index(min(seq_data['right'][1]))
                left_min_cost = seq_data['left'][1][left_min_index]
                right_min_cost = seq_data['right'][1][right_min_index]

                select_partial_path = None
                if left_min_cost < right_min_cost:
                    # print(left_min_cost)
                    select_partial_path = seq_data['left'][0][left_min_index]
                    min_cost += left_min_cost
                else:
                    # print(right_min_cost)
                    select_partial_path = seq_data['right'][0][right_min_index]
                    min_cost += right_min_cost

            for partial_p in select_partial_path:
                if partial_p not in full_path:
                    full_path.append(partial_p)

        return min_cost, full_path

    @staticmethod
    def get_path_cost_2(path, data):
        min_cost = 0
        full_path = []
        return min_cost, full_path


    @staticmethod
    def translate_path(path):
        tran_path = {"cam_sequence": []}
        start_time = 0
        previous_cam = None
        duration = 0
        for i, p in enumerate(path):
            if i == 0:
                start_time = 0
                previous_cam = p[1]
                duration = 1
            elif i != len(path) - 1:
                if p[1] == previous_cam:
                    duration += 1
                else:
                    pattern = {"startTime": start_time, "duration": duration, "camIndex": previous_cam, "tracking": 0}
                    tran_path["cam_sequence"].append(pattern)
                    previous_cam = p[1]
                    start_time += duration
                    duration = 1
            else:
                pattern = {"startTime": start_time, "duration": duration, "camIndex": p[1], "tracking": 0}
                tran_path["cam_sequence"].append(pattern)

        return tran_path


def main(project_data, config):
    # project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../data')
    opt_project = Optimization(project_data, config)
    select_path = opt_project.optimize_full_length()
    tran_select_path = OptimizationHelper.translate_path(select_path)
    print(tran_select_path)


if __name__ == "__main__":
    main()