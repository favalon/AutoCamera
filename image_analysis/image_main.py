import pathlib
import cv2
from generals.save_load import LoadBasic
from process.init_data import Data, DataBasicInfo


def prepare_basic(dp):
    p_dp = pathlib.Path(dp)
    if not p_dp.exists():
        raise NotADirectoryError
    project_data = LoadBasic.load_basic('project_data', dp, called='image_analysis/prepare_basic')
    return project_data.characters


def main():
    data_path = 'data'
    image_path = ''
    # 1. load basic information, characters' color code and camera index
    characters_info = prepare_basic(data_path)
    pass


if __name__ == "__main__":
    main()