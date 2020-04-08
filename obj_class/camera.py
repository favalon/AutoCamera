
class Camera:
    object_index = "NA" # the camera is bind with an object

    def __init__(self, cam_index: int, char_index: int, angel: float, rotation: float, d2c: str, pov: bool, obj_index="NA"):
        self.camera_index = cam_index
        self.character_index = char_index
        self.angel = angel
        self.rotation = rotation
        self.distance2char = d2c
        self.pov = pov  # first person camera 0 (False) 1 (True)
        self.object_index = obj_index

    def print_obj(self, format_data=""):
        from generals.printobject import PrintBasic
        PrintBasic.print_basic(self.camera_index, format_data + "Camera Index")
        PrintBasic.print_basic(self.character_index, format_data + "Binding Character Index")
        PrintBasic.print_basic(self.angel, format_data + "Camera Angel")
        PrintBasic.print_basic(self.rotation, format_data + "Camera Rotation")
        PrintBasic.print_basic(self.distance2char, format_data + "Distance to character")
        PrintBasic.print_basic(self.pov, format_data + "First Person View Camera")
        if self.object_index != "NA":
            PrintBasic.print_basic(self.pov, format_data + "Camera Binds with Obeject")