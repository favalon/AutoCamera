import os
from os import listdir
from os.path import isfile, join
from generals.printobject import PrintBasic


def check_files_integrity(path, files_list, suffix=""):
    fun_name = "general/check/check_files_integrity"
    if not os.path.isdir(path):
        PrintBasic.print_message("data path is wrong", called_function=fun_name)
        return False
    # check the files in path are match with the files_list or not
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for fn in files_list:
        fn_f = "{}.{}".format(fn, suffix)
        if not os.path.isfile(os.path.join(path, fn_f)):
            PrintBasic.print_message("file {} missing".format(fn_f), called_function=fun_name)
            return False
    PrintBasic.print_message("check files success", called_function=fun_name)
    return True




