from obj_class.character import Character
from obj_class.camera import Camera
from obj_class.sequence import Sequence
from obj_class.timestamp import TimeStamp
from generals.save_load import LoadBasic, SaveBasic
from generals.printobject import PrintBasic
from process.support.animaiton_cost import generate_animation_score


class Data:
    require_files_list = ["animation_dict", "characters", "defaultCams", "existence", "charVisibility", "headroom", "leftToRightOrder",
                          "eyePos", "charMoveCamAngle", "charCamDist", "script", "charProVelocity", "userCamData",
                          "color_code", "color_abs_coverage", "color_diff_coverage"]

    def __init__(self, p_id, path=None, use_local=True):
        self.project_id = p_id
        self.animation_score = None
        self.default_cams = None
        self.characters = None
        self.sequence_data = None
        self.sequence_length = 0
        self.timestamp_data = None
        self.data_basic_info = None

        if use_local and path:
            self.init_by_local(path)
            self.basic_data_info()
        else:
            self.init_by_database()

    def init_by_local(self, path):
        fun_name = "Data(obj)/init_by_local"
        from generals.check import check_files_integrity
        check_files_integrity(path, self.require_files_list, suffix="data")

        animation_dict = LoadBasic.load_basic('animation_dict.data', path, 'json', called=fun_name + "animation_dict")

        default_cams = LoadBasic.load_basic("defaultCams.data", path=path, file_type='json',
                                            called=fun_name + "defalutCams")
        characters = LoadBasic.load_basic("characters.data", path=path, file_type='json',
                                          called=fun_name + "characters")
        color_code = LoadBasic.load_basic("color_code.data", path=path, file_type="json",
                                          called=fun_name + " character_color_code")
        script = LoadBasic.load_basic("script.data", path=path, file_type='json', called=fun_name + "script")
        existence = LoadBasic.load_basic("existence.data", path=path, file_type='json', called=fun_name + "existence")
        char_visibility = LoadBasic.load_basic("charVisibility.data", path=path, file_type='json',
                                               called=fun_name + "char_visibility")
        head_room = LoadBasic.load_basic("headroom.data", path=path, file_type='json', called=fun_name + "head_room")
        left2right_order = LoadBasic.load_basic("leftToRightOrder.data", path=path, file_type='json',
                                                called=fun_name + "left2right_order")
        eye_pos = LoadBasic.load_basic("eyePos.data", path=path, file_type='json', called=fun_name + "eye_pos")
        char_move_cam_angle = LoadBasic.load_basic("charMoveCamAngle.data", path=path, file_type='json',
                                                   called=fun_name + "char_move_cam_angle")
        char_cam_dist = LoadBasic.load_basic("charCamDist.data", path=path, file_type='json',
                                             called=fun_name + "char_cam_dist")
        char_pro_velocity = LoadBasic.load_basic("charProVelocity.data", path=path, file_type='json',
                                                 called=fun_name + "char_pro_velocity")
        char_user_cam_data = LoadBasic.load_basic("userCamData.data", path=path, file_type='json',
                                                  called=fun_name + "char_user_cam_data")
        color_abs_coverage = LoadBasic.load_basic("color_abs_coverage.data", path=path, file_type='json',
                                                  called=fun_name + "color_abs_coverage")
        color_diff_coverage = LoadBasic.load_basic("color_diff_coverage.data", path=path, file_type='json',
                                                   called=fun_name + "char_diff_coverage")
        # obj_visibility = LoadBasic.load_basic("objVisibility.data", path=path, file_type='json',
        #                                       called=fun_name + "obj_visibility")

        self.animation_score = generate_animation_score(animation_dict)
        self.default_cams = DataReconstruction.camera_reconstruction(default_cams['defaultCams'])
        self.characters = DataReconstruction.character_reconstruction(characters["characters"], self.default_cams, color_code)
        self.sequence_data = DataReconstruction.script_reconstruction(script['actions'], self.characters)
        self.sequence_length = len(script['actions'])
        self.timestamp_data = DataReconstruction.timestamp_data_reconstruction(existence, char_visibility, head_room,
                                                                               left2right_order, eye_pos,
                                                                               char_move_cam_angle, char_cam_dist,
                                                                               char_pro_velocity, char_user_cam_data,
                                                                               color_abs_coverage, color_diff_coverage)

        # temp disable
        # self.obj_visibility = obj_visibility
        pass

    def init_by_database(self):
        pass

    def basic_data_info(self):
        p_id = self.project_id
        seq_num = self.sequence_length
        ts_len = len(self.timestamp_data.keys())
        char_num = len(self.characters.keys())
        camera_num = len(self.default_cams.keys())
        seq_start = [self.sequence_data[seq].sequence_start for seq in self.sequence_data]
        seq_dur = [self.sequence_data[seq].sequence_dur for seq in self.sequence_data]
        seq_end = [self.sequence_data[seq].sequence_end for seq in self.sequence_data]
        self.data_basic_info = DataBasicInfo(p_id, seq_num, ts_len, char_num, camera_num, seq_start, seq_dur, seq_end)


class DataBasicInfo:
    def __init__(self, p_id, seq_num, ts_len, char_num, camera_num, seq_start, seqs_dur, seq_ed):
        self.project_id = p_id
        self.sequence_num = seq_num
        self.timestamp_length = ts_len
        self.character_num = char_num
        self.camera_num = camera_num
        self.sequences_start = seq_start
        self.sequences_duration = seqs_dur
        self.sequences_end = seq_ed

    def print_obj(self, format_data=""):
        from generals.printobject import PrintBasic
        PrintBasic.print_basic(self.project_id, format_data + "Project ID")
        PrintBasic.print_basic(self.sequence_num, format_data + "Number of Sequence")
        PrintBasic.print_basic(self.timestamp_length, format_data + "Number of Timestamp")
        PrintBasic.print_basic(self.camera_num, format_data + "Number of Camera")
        PrintBasic.print_basic(self.sequences_duration, format_data + "Timestamp's Duration of each Sequence")


class DataReconstruction:

    @staticmethod
    def camera_reconstruction(data):
        camera_dict = {}
        for i, cam in enumerate(data):
            cam_index = cam['camIndex']
            char_index = cam['charIndex']
            object_index = cam['objectIndex']
            distance2char = cam['distance']
            angle = cam['angle']
            rot_angle = cam['rotAngle']
            pov = {0: False, 1: True}[cam["POV"]]
            camera = Camera(cam_index, char_index, angle, rot_angle, distance2char, pov, obj_index=object_index)
            camera_dict[cam_index] = camera
        return camera_dict

    @staticmethod
    def character_reconstruction(data, cam_data, char_color_code):
        character_dict = {}
        for i, char in enumerate(data.keys()):
            char_name = char
            char_index = data[char]
            char_cam_list = []
            for cam_key in cam_data.keys():
                if cam_data[cam_key].character_index == char_index:
                    char_cam_list.append(cam_data[cam_key])
            character = Character(char_index, char_name, char_cam_list, char_color_code[char])
            character_dict[char_index] = character
        return character_dict

    @staticmethod
    def script_reconstruction(data, character_data):
        script = {}
        index = 0
        for seq in data:
            seq_index = seq["sequenceIndex"]
            correlation = seq["correlation"]
            climax = seq["climax"]
            event_index = seq["eventIndex"]
            action = seq["action"]
            ac_start_time = seq["startTime"]
            ac_duration = seq["duration"]
            objects = seq["objects"]
            ori_characters = seq["subjects"]
            characters = {}
            if max(ac_duration) == 0:
                continue
            for char_name in ori_characters:
                for c_k in character_data.keys():
                    if char_name[0] == character_data[c_k].character_name:
                        characters[character_data[c_k].character_index] = character_data[c_k]

            sequence = Sequence(index, seq_index, correlation, climax, event_index, action, ac_start_time, ac_duration,
                                characters, objects)
            script[index] = sequence
            index += 1
        return script

    @staticmethod
    def timestamp_data_reconstruction(existence, char_visibility, head_room, left2right_order, eye_pos, char_move_cam_angle, char_cam_dist,
                                      char_pro_velocity, char_user_cam_data, color_abs_coverage, color_diff_coverage):
        if char_visibility is None or len(char_visibility) == 0:
            PrintBasic.print_message("require data missing", "timestamp_data_reconstruction")
            return
        else:
            pass

        length = len(char_visibility)
        timestamp = {}

        for ts in range(length):
            char_vis_ts = char_visibility[ts]
            if len(head_room) == length:
                head_room_ts = head_room[ts]
            else:
                head_room_ts = None
                if ts == 0:
                    PrintBasic.print_message("l2r_order data has error", "timestamp_data_reconstruction")
            if len(existence) == length:
                existence_ts = existence[ts]
            else:
                existence_ts = None
                if ts == 0:
                    PrintBasic.print_message("l2r_order data has error", "timestamp_data_reconstruction")
            if len(left2right_order) == length:
                l2r_order_ts = left2right_order[ts]
            else:
                l2r_order_ts = None
                if ts == 0:
                    PrintBasic.print_message("l2r_order data has error", "timestamp_data_reconstruction")
            if len(left2right_order) == length:
                eye_pos_ts = eye_pos[ts]
            else:
                eye_pos_ts = None
                if ts == 0:
                    PrintBasic.print_message("eye_pos data has error", "timestamp_data_reconstruction")
            if len(char_move_cam_angle) == length:
                char_move_cam_angle_ts = char_move_cam_angle[ts]
            else:
                char_move_cam_angle_ts = None
                if ts == 0:
                    PrintBasic.print_message("char_move_cam_angle_ts data has error", "timestamp_data_reconstruction")
            if len(char_cam_dist) == length:
                char_cam_dist_ts = char_cam_dist[ts]
            else:
                char_cam_dist_ts = None
                if ts == 0:
                    PrintBasic.print_message("char_cam_dist_ts data has error", "timestamp_data_reconstruction")
            if len(char_pro_velocity) == length:
                char_pro_velocity_ts = char_pro_velocity[ts]
            else:
                char_pro_velocity_ts = None
                if ts == 0:
                    PrintBasic.print_message("char_pro_velocity data has error", "timestamp_data_reconstruction")
            if char_user_cam_data is not None and len(char_user_cam_data) == length:
                char_user_cam_data_ts = char_user_cam_data[ts]
            else:
                char_user_cam_data_ts = None
                if ts == 0:
                    PrintBasic.print_message("char_user_cam_data data has error", "timestamp_data_reconstruction")
            if len(color_abs_coverage) == length:
                color_abs_coverage_ts = color_abs_coverage[ts]
            else:
                color_abs_coverage_ts = None
                if ts == 0:
                    PrintBasic.print_message("color_abs_coverage data has error", "timestamp_data_reconstruction")
            if len(color_diff_coverage) == length:
                color_diff_coverage_ts = color_diff_coverage[ts]
            else:
                color_diff_coverage_ts = None
                if ts == 0:
                    PrintBasic.print_message("color_diff_coverage data has error", "timestamp_data_reconstruction")

            timestamp_data = TimeStamp(ts, existence_ts, char_vis_ts, head_room_ts, l2r_order_ts, eye_pos_ts, char_move_cam_angle_ts,
                                       char_cam_dist_ts, char_pro_velocity_ts, char_user_cam_data_ts,
                                       color_abs_coverage_ts, color_diff_coverage_ts)

            timestamp[ts] = timestamp_data

        return timestamp


def process(p_id, path="../local_data", use_local=False):
    project_data = Data(p_id, path=path, use_local=use_local)
    return project_data


if __name__ == "__main__":
    p_id = 81
    local_data_path = "../local_data"
    project_data = Data(p_id, path=local_data_path, use_local=True)
    SaveBasic.save_obj(project_data, '../data', 'project_data_{}'.format(p_id))
    pass
