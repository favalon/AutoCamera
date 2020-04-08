class Sequence:
    def __init__(self, index: int, sequence_index: int, correlation: int, climax: int, event_index: int, action: list,
                 start_time: list, duration: list, characters: dict, objects: list):
        self.index = index  # sequence index in this project
        self.sequence_index = sequence_index  # sequence index in original data
        self.correlation = correlation
        self.climax = climax
        self.event_index = event_index
        self.start_time = start_time
        self.duration = duration
        self.sequence_start = min(start_time)
        self.sequence_dur = max(duration)
        self.sequence_end = self.sequence_start + self.sequence_dur - 1
        self.characters = characters
        self.characters_action = action
        self.objects = objects

    def print_obj(self, format_data=""):
        from generals.printobject import PrintBasic
        PrintBasic.print_basic(self.sequence_index, format_data + "Sequence Index")
        PrintBasic.print_basic(self.correlation, format_data + "Correlation")
        PrintBasic.print_basic(self.climax, format_data + "Climax")
        from generals.printobject import PrintList
        print("Character in the Sequences")
        PrintList.print_list_data(self.characters)
        print("Character action Start Time")
        PrintList.print_list_data(self.start_time)
        print("Character action Duration")
        PrintList.print_list_data(self.duration)

