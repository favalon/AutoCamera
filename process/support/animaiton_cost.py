from generals.save_load import LoadBasic, SaveBasic

ANIMATION_SCORE = {
    'idle': 0.9,
    'walk': 0.5,
    'run': 0.5,
    'talk': 0.2,
    'spreadouthishands': 0.2,
    'holdhand': 0.4,
    'choose': 0.4,
    'angrylook': 0.4,
    'special': 0.4,
    'say': 0.2


}


def generate_animation_score(ad):
    animation_score = {}
    for action in ad.keys():
        action_key = action.lower()
        animation_score[action_key] = 0.3

        for ac_key in ANIMATION_SCORE.keys():
            if ac_key in action_key:
                animation_score[action_key] = ANIMATION_SCORE[ac_key]

    return animation_score


def main(path):
    animation_dict = LoadBasic.load_basic('animation_dict.data', path, 'json')
    animation_score = generate_animation_score(animation_dict)
    SaveBasic.save_basic(animation_score, 'animation_score.data', "../../local_data", 'json')



if __name__ == "__main__":
    path = "../../local_data"
    main(path)
