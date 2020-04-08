from generals.save_load import LoadBasic, SaveBasic

from process.init_data import Data, DataBasicInfo
from process.init_data import process as init_data_process
from process.init_optimization import process as init_optimization
from optimization.cost_functions.cost_main import initial_static_cost_map


def main(produce_new=False):
    p_id = 81
    if produce_new:
        local_data_path = "../local_data"
        project_data = init_data_process(p_id, local_data_path, use_local=True)
        SaveBasic.save_obj(project_data, '../data', 'project_data_{}'.format(p_id))
    # load
    project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../data')

    # initial static cost map
    static_cost_map = initial_static_cost_map(project_data)

    #
    # optimize_matrix = init_optimization(p_id, project_data.data_basic_info)
    return 0

if __name__ == "__main__":
    main(produce_new=False)
    pass
