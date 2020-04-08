from generals.save_load import LoadBasic, SaveBasic
from process.init_data import Data, DataBasicInfo
from obj_class.sequence import Sequence


def color_code2char_parts(project_data):
    cc2cp = {}
    for char_i in project_data.characters.keys():
        char_color_code = project_data.characters[char_i].char_color_code
        char_name = project_data.characters[char_i].character_name
        for parts_key in char_color_code.keys():
            val = char_color_code[parts_key]['val']
            val = [str(int(v)) for v in val]
            val_str = '[{}]'.format(', '.join(val))
            full_parts_key = char_name + '_' + parts_key
            cc2cp[val_str] = full_parts_key

    return cc2cp


def check_replaced_image(cc2cp, project_data, select_cam=0):
    for i in range(len(project_data.timestamp_data.keys())):
        color_abs_coverage = project_data.timestamp_data[i].color_abs_coverage
        color_diff_coverage = project_data.timestamp_data[i].color_diff_coverage
        for cam_i in range(len(color_abs_coverage)):
            abs_coverage = color_abs_coverage[cam_i]
            diff_coverage = color_diff_coverage[cam_i]
            new_abs_coverage = {}
            new_diff_coverage = {}
            for parts_key in abs_coverage.keys():
                cp_key = cc2cp[parts_key]
                new_abs_coverage [cp_key] = abs_coverage[parts_key]
                new_diff_coverage[cp_key] = diff_coverage[parts_key]
            if cam_i == select_cam:
                print('============= timestamp {} ============ camera {} ==========='.format(i, cam_i))
                print(new_abs_coverage)
                print(new_diff_coverage)



def main():
    p_id = 81
    project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../../data')
    cc2cp = color_code2char_parts(project_data)
    check_replaced_image(cc2cp, project_data)
    pass

if __name__ == "__main__":
    main()