class Configure:
    def __init__(self, setting):
        p_id = setting['p_id']

    @staticmethod
    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1")