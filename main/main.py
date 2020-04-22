import configparser
from generals.Configure import Configure
from generals.save_load import LoadBasic, SaveBasic

from process.init_data import Data, DataBasicInfo
from process.init_data import process as init_data_process
from optimization.main import main as optimization_main


def load_configure(file):
    configure = {}
    config = configparser.ConfigParser()
    # config.sections()
    config.read(file)
    config.sections()
    print(config.sections())

    # project setting
    configure['local_data_path'] = config['project']['LocalDataPath']
    configure['use_new_data'] = Configure.str2bool(config['project']['UseNewData'])
    configure['save_opt_temp'] = Configure.str2bool(config['project']['SaveOptimizationTempFile'])
    configure['use_latest_general_result'] = Configure.str2bool(config['project']['UseLatestGeneralResult'])
    configure['use_latest_sequence_combination'] = Configure.str2bool(config['project']['UseLatestSequenceCombination'])
    configure['debug'] = Configure.str2bool(config['project']['Debug'])
    configure['p_id'] = config['project']['ProjectID']
    configure['opt_len'] = int(config['project']['SelectOptimizationLength'])

    # static cost weight
    static_cost_weight = []
    for static_cost in config['cost.weight.static']:
        static_cost_weight.append(float(config['cost.weight.static'][static_cost]))
    configure['static_cost_weight'] = static_cost_weight

    # dynamic cost weight
    dynamic_cost_weight = []
    for dynamic_cost in config['cost.weight.dynamic']:
        dynamic_cost_weight.append(float(config['cost.weight.dynamic'][dynamic_cost]))
    configure['dynamic_cost_weight'] = dynamic_cost_weight

    # duration setting
    configure['duration_cost_weight'] = float(config['cost.weight.duration']['Duration'])
    configure['duration_center'] = int(config['cost.weight.duration']['DurationSoftCenter'])

    return configure


def main(setting_path):

    project_configure = load_configure(setting_path)

    p_id = project_configure['p_id']
    if bool(project_configure['use_new_data']):
        local_data_path = project_configure['local_data_path']
        project_data = init_data_process(p_id, local_data_path, use_local=True)
        SaveBasic.save_obj(project_data, '../data', 'project_data_{}'.format(p_id))
    # load
    project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../data')

    optimization_main(project_data, project_configure)



    return 0


if __name__ == "__main__":
    config_file_path = 'config.ini'

    main(config_file_path)
    pass
