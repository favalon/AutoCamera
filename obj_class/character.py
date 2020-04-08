
class Character:
    def __init__(self, char_index: int, char_name: str, cam_list: list, color_code, action_list=None):
        self.character_index = char_index
        self.character_name = char_name
        self.camera_list = cam_list
        self.action_list = action_list
        self.char_color_code = color_code

    def print_obj(self, format_data=""):
        from generals.printobject import PrintBasic
        PrintBasic.print_basic(self.character_index, format_data + "Character Index")
        PrintBasic.print_basic(self.character_name, format_data + "Character Name")
        from generals.printobject import PrintList
        print("Character {} Camera List".format(self.character_index))
        PrintList.print_list_data(self.camera_list)
        print("Character {} action List".format(self.character_index))
        PrintList.print_list_data(self.action_list)