import numpy as np


class DataViewHelper:
    @staticmethod
    def get_min_cost_path(data, sequence, time_len):
        cost = 0
        path = None
        cur_seq = data[sequence]
        select_comb = cur_seq[time_len]
        left_path = np.array(select_comb['left'][0])
        left_cost = np.array(select_comb['left'][1])
        left_min_i = np.where(left_cost == np.amin(left_cost))
        left_best_path = left_path[left_min_i]

        right_path = np.array(select_comb['right'][0])
        right_cost = np.array(select_comb['right'][1])
        right_min_i = np.where(right_cost == np.amin(right_cost))
        right_best_path = left_path[right_min_i]

        print(left_best_path[0])
        print(right_best_path[0])

        return cost, path