from generals.save_load import LoadBasic, SaveBasic
from result.helper import DataViewHelper


def cal_sequence_combination(cur_i, cur_len, select_len, cur_sequence, sequences, result):
    if cur_i > len(sequences) - 1:
        return
    if cur_len == select_len and cur_i == len(cur_sequence) - 1:
        result.append(cur_sequence)
        return

    candi_len = sequences[cur_i]
    for i in candi_len:
        cur_sequence.append(i)
        print(cur_sequence)
        cal_sequence_combination(cur_i + 1, cur_len + i, select_len, cur_sequence, sequences, result)
        del cur_sequence[-1]


def cal_sequence_combination_2(cur_i, cur_len, select_len, left_max, cur_sequence, sequences, result):
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
        left_max = sum([max_len[-1] for max_len in sequences[cur_i+1:]])
        cal_sequence_combination_2(cur_i + 1, cur_len + i, select_len, left_max, cur_sequence, sequences, result)
        del cur_sequence[-1]
    return


def select_len_optimization(seq_all):
    result = []
    # cal_sequence_combination(0, 0, 40, [], seq_all, result)
    for i in seq_all[0]:
        left_max = sum([max_len[-1] for max_len in seq_all[0:]])
        cal_sequence_combination_2(0, i, 62, left_max, [i], seq_all, result)

    SaveBasic.save_basic(result, 'all_possible_sequence_{}_combination'.format(58), 'temp')
    return result


def get_sequence_length(data):
    seq_all_len = []
    for i in range(len(data.keys())):
        seq_single = []
        for j in range(len(data[i].keys())):
            seq_single.append(j)
        seq_all_len.append(seq_single)
    return seq_all_len


def get_cost(path, data):
    # n.index(min(n))
    min_cost = 0
    full_path = []
    for i, p in enumerate(path):
        if p == 0:
            min_cost += 0
        else:
            print(i, p)
            seq_data = data[i][p]
            left_min_index = seq_data['left'][1].index(min(seq_data['left'][1]))
            right_min_index = seq_data['right'][1].index(min(seq_data['right'][1]))
            left_min_cost = seq_data['left'][1][left_min_index]
            right_min_cost = seq_data['right'][1][right_min_index]

            select_partial_path = None
            if left_min_cost < right_min_cost:
                print(left_min_cost)
                select_partial_path = seq_data['left'][0][left_min_index]
                min_cost += left_min_cost
            else:
                print(right_min_cost)
                select_partial_path = seq_data['right'][0][right_min_index]
                min_cost += right_min_cost

        for partial_p in select_partial_path:
            if partial_p not in full_path:
                full_path.append(partial_p)

    return min_cost, full_path


def path_translation(path):
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


def main(sel_len):
    data = LoadBasic.load_basic("general_opt.result", 'temp')

    DataViewHelper.get_min_cost_path(data, 0, 8)

    seq_all = get_sequence_length(data)
    select_len_optimization(seq_all)
    all_comb = LoadBasic.load_basic('all_possible_sequence_{}_combination'.format(58), 'temp')

    min_cost = 999
    select_path = None
    for path in all_comb:
        cur_path_cost, cur_path = get_cost(path, data)
        if min_cost > cur_path_cost:
            min_cost = cur_path_cost
            select_path = cur_path
    print(select_path)

    # path translation
    tran_path = path_translation(select_path)

    print(tran_path)
    return select_path


if __name__ == "__main__":
    main(30)