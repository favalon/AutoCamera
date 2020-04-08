class TimeStamp:
    def __init__(self, timestamp: int, existence, char_visibility, head_room_ts, left2right_order, eye_pos, char_move_cam_angle,
                 char_cam_dist, char_pro_velocity, char_user_cam_data, color_abs_coverage, color_diff_coverage):
        self.timestamp = timestamp
        self.existence = existence
        self.char_cam_dist = char_cam_dist
        self.char_visibility = char_visibility
        self.head_room = head_room_ts
        self.left2right_order = left2right_order
        self.eye_pos = eye_pos
        self.char_move_cam_angle = char_move_cam_angle
        self.char_pro_velocity = char_pro_velocity
        self.char_user_cam_data = char_user_cam_data
        self.color_abs_coverage = color_abs_coverage
        self.color_diff_coverage = color_diff_coverage


