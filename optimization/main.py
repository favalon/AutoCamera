from generals.save_load import LoadBasic, SaveBasic
from optimization.cost_functions.cost_main import initial_static_cost_map
from process.support.lrtree_method_test import recursion_cost
from optimization.cost_functions import utils


class Optimization:
    def __init__(self, project_data, set_time_len):
        self.project_data = project_data
        self.seq_dur = OptimizationHelper.get_sequence_duration(project_data.sequence_data)
        self.seq_ts_group = OptimizationHelper.get_sequence_timestamp_group(self.seq_dur)
        self.all_seq_comb = OptimizationHelper.get_all_sequence_combination(self.seq_ts_group)
        self.static_cost = initial_static_cost_map(project_data)
        self.char_activate_map = utils.get_characters_activate_map(project_data)
        self.run_optimization(set_time_len)

    def run_optimization(self, set_time_len):
        general_result = self.run_general_optimization()
        pass

    def run_general_optimization(self):

        general_result = {}
        for seq_i in self.all_seq_comb.keys():
            seq_comb = self.all_seq_comb[seq_i]
            cur_sequence_result = {}
            for len_i in seq_comb.keys():
                len_seq_comb = seq_comb[len_i]

                cur_len_result = {}
                for i, choice_comb in enumerate(len_seq_comb):
                    n = choice_comb
                    # cost_update
                    l_path, r_path, l_cost, r_cost = recursion_cost(choice_comb, self.static_cost,
                                                                    self.project_data, self.char_activate_map)
                    l_leaf, r_leaf = [l_path, l_cost], [r_path, r_cost]
                    if i == 0:
                        cur_len_result['left'] = l_leaf
                        cur_len_result['right'] = r_leaf
                    else:
                        OptimizationHelper.cal_cost_comparator(l_leaf, r_leaf, cur_len_result)

                    print("{}-{}-{}".format(seq_i, len_i, i))
                cur_sequence_result[len_i] = cur_len_result
            general_result[seq_i] = cur_sequence_result

            SaveBasic.save_basic(cur_sequence_result, 'sequence_{}.result'.format(seq_i), path='../result/temp',
                                 called='fun: general_optimization')

        SaveBasic.save_basic(general_result, 'general_opt.result', path='../result/temp',
                             called='fun: general_optimization')

        return general_result

    def select_length_optimization(self, sel_len):
        return 0


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

        pass


def main():
    p_id = 81
    project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../data')
    opt_project = Optimization(project_data, 100)


if __name__ == "__main__":
    main()