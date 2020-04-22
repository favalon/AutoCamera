import numpy as np
import sys

from generals.save_load import LoadBasic, SaveBasic
from optimization.cost_functions import utils
from optimization.cost_functions.utils import StaticCostCalculation
from optimization.cost_functions.utils import EdgeCostCalculation
from optimization.cost_functions import static_cost
from optimization.cost_functions import edge_cost


def get_static_cost_wo_obj(node, project_data, activate_char, cost_weight, debug_flag=True):

    timestamp = node[0]
    camera_index = node[1]

    timestamp_data = project_data.timestamp_data[node[0]]
    camera_data = project_data.default_cams[node[1]]

    # # get sequence_index
    # sequence_index = utils.get_sequence_index(node[0], project_data.data_basic_info)
    # # get action_list
    # action_list = project_data.sequence_data[sequence_index].characters_action

    # calculate visual cost
    vis_cost, sub_vis_list, obj_vis_list = \
        StaticCostCalculation.visual_cost(timestamp_data, timestamp, camera_index, activate_char, debug_flag=debug_flag)

    # calculate hitchcock cost
    hitch_cost = 0
    #static_cost.getHitchCockCost(actions_list, subVis_list, objVis_list)

    # calculate look-room cost
    lr_cost = StaticCostCalculation.lookroom_cost(timestamp_data, timestamp, camera_index, activate_char, debug_flag=debug_flag)

    # calculate head-room cost
    hr_cost = StaticCostCalculation.headroom_cost(timestamp_data, timestamp, camera_index, activate_char, debug_flag=debug_flag)

    # calculate pov cost
    pov_cost = 0

    # calculate shot order cost
    totoal_timestamp = len(project_data.timestamp_data.keys())
    so_cost = StaticCostCalculation.shot_order_cost(totoal_timestamp, camera_data, timestamp, camera_index, debug_flag=debug_flag)

    # calculate camera Y(yaw) P(pitch) R(roll) cost:
    ca_cost = StaticCostCalculation.camera_YPR_cost(camera_data, timestamp, camera_index, debug_flag=True)

    # calculate character talking cost:
    tk_cost = 0
    # tk_cost = StaticCostCalculation.talking_cost()

    # cost summation
    node_static_cost = StaticCostCalculation.cost_sum(timestamp, camera_index, cost_weight,
                                                      vis_cost, hitch_cost,
                                                      lr_cost, hr_cost, pov_cost,
                                                      so_cost, ca_cost, tk_cost)

    return node_static_cost


def prepare_static_cost_map(cost_map, project_data, cost_weight, obj=None, obj_vis=None):
    # obj: we have key object to consider in the scene or not
    # obj_vis : key object visibility

    char_activate_map = utils.get_characters_activate_map(project_data)

    if obj:
        pass
    else:
        for t_i in range(cost_map.shape[0]):
            for cam_i in range(cost_map.shape[1]):
                node_static_cost = get_static_cost_wo_obj([t_i, cam_i], project_data, char_activate_map[t_i], cost_weight)
                cost_map[t_i][cam_i] = node_static_cost


def initial_static_cost_map(project_data, cost_weight):
    static_cost_map = np.full((len(project_data.timestamp_data.keys()), len(project_data.default_cams.keys())), 999.0)

    prepare_static_cost_map(static_cost_map, project_data, cost_weight=cost_weight)

    return static_cost_map


def dynamic_cost(project_data, char_activate_map, node1, node2, config=None, debug_flag=False):
    # calculate transfer pos cost
    pos_cost = EdgeCostCalculation.pos_cost(project_data, char_activate_map, node1, node2, debug_flag=debug_flag)

    # calculate transfer gaze continuity cost
    gaze_cost = EdgeCostCalculation.gaze_cost()

    # calculate moving continuity cost
    mc_cost = EdgeCostCalculation.moving_cost()

    # calculate transfer left right cost
    lf_cost = EdgeCostCalculation.left_right_cost(project_data, node1, node2, debug_flag=debug_flag)

    tr_cost = EdgeCostCalculation.transfer_cost_sum(node1, node2, pos_cost, gaze_cost, mc_cost, lf_cost,
                                                    config=config, debug_flag=debug_flag)

    # dr_cost = EdgeCostCalculation.duration_cost(node1, node2)

    return tr_cost


if __name__ == "__main__":
    p_id = 81
    # load
    project_data = LoadBasic.load_basic('project_data_{}'.format(p_id), '../../data')

    static_cost_map = initial_static_cost_map(project_data)
    node1 = [10, 21]
    node2 = [11, 22]
    char_activate_map = utils.get_characters_activate_map(project_data)
    dynamic_cost(project_data, char_activate_map, node1, node2)
