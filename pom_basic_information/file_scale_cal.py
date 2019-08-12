import os
import numpy as np

from constant import STATIC_DIR, ARCHETYPE_FILES_INFO
from pom_basic_information.read_file import read_json_file, get_all_pom_path


def countFileLines(filename):
    count = 0
    handle = open(filename, 'rb')
    for line in handle:
        count += 1
    return count


def listdir(pom_file_name_list):
    pom_lines_list = []
    jave_lines_list = []

    for path in pom_file_name_list:
        current_path = os.path.join(STATIC_DIR, path).split("/archetype-resources/pom.xml")[0]
        print(current_path)
        for root, dirs, files in os.walk(current_path):  # os.walk获取所有的目录
            for file in files:
                file_name = os.path.join(root, file)
                if file_name.endswith('.java'):
                    jave_lines_list.append(countFileLines(file_name))
                elif file_name.endswith('pom.xml'):
                    pom_lines_list.append(countFileLines(file_name))
    return pom_lines_list,jave_lines_list


def get_list_feature(basic_list):
    feature = {
        "num":len(basic_list),
        "median":np.median(basic_list),
        "mean":np.mean(basic_list),
        "sum":np.sum(basic_list)
    }
    return feature


def file_scale_cal():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    pom_lines_list, jave_lines_list = listdir(pom_file_name_list)
    print(get_list_feature(pom_lines_list))
    print(get_list_feature(jave_lines_list))

file_scale_cal()