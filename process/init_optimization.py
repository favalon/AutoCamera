class Optimization:
    def __init__(self, data_info):
        self.data_info = data_info


class CostMatrix:

    def __init__(self, project_id, action_cost_weight=5, visual_cost_weight=1, talking_cost_weight=15):
        self.project_id = project_id
        self.action_cost_weight = action_cost_weight
        self.visual_cost_weight = visual_cost_weight
        self.talking_cost_weight = talking_cost_weight

        self.sequence_cover = None
        self.action_map = None
        self.visual_cost_map = None
        self.action_cost_map = None
        self.talking_cost = None

        # ======= sum up the cost parts ===========
        self.quality_cost = None

    def init_sequence_cover(self, sequence_cover):
        self.sequence_cover = sequence_cover

    def init_action_map(self, action_map):
        self.action_map = action_map

    def init_visual_cost_map(self, visual_cost_map):
        self.visual_cost_map = visual_cost_map

    def init_action_cost_map(self, action_cost_map):
        self.action_cost_map = action_cost_map

    def normalize_cost(self, matrix):
        pass

    def init_talking_cost(self, talking_cost):
        self.talking_cost = talking_cost

    def init_quality_cost(self, quality_cost):
        self.quality_cost = quality_cost


def process(p_id, weight, data_info):
    cost_matrix = CostMatrix(p_id, action_cost_weight=weight[0], visual_cost_weight=weight[1], talking_cost_weight=weight[2])
    
    return


if __name__ == "__main__":
    process()