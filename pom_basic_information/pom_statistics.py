from pom_basic_information.pom_tag import has_tag
from pom_basic_information.read_file import get_item_list, read_json_file, get_all_pom_path, get_item_in_one_pom
import numpy as np

from constant import ARCHETYPE_FILES_INFO


def cal_item(pom_file_name_list, item_name, items_name,items_name_plus):
    item_num_in_all_pom = []
    num = 0
    for pom_file_name in pom_file_name_list:
        if num % 100 == 0:
            print(num)
    #     if has_tag(pom_file_name, "dependencies") and has_tag(pom_file_name, "plugins"):
    #         num += 1
    # return num
        current_item_num_in_one_pom = len(get_item_in_one_pom(pom_file_name, item_name, items_name, items_name_plus))
        if current_item_num_in_one_pom > 0:
            item_num_in_all_pom.append(current_item_num_in_one_pom)
        num += 1
    feature_dict = {
        "num": len(item_num_in_all_pom),
        "mean": np.mean(item_num_in_all_pom),
        "median": np.median(item_num_in_all_pom),
        "min":np.min(item_num_in_all_pom),
        "max":np.max(item_num_in_all_pom)
    }
    return item_num_in_all_pom, feature_dict


def cal_plugins():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    item_num_in_all_pom, feature_dict = cal_item(pom_file_name_list, "plugin", "plugins", "pluginManagement")
    print(feature_dict)
    return item_num_in_all_pom, feature_dict


def cal_dependencies():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    item_num_in_all_pom, feature_dict = cal_item(pom_file_name_list, "dependency", "dependencies", "dependencyManagement")
    print(feature_dict)
    return item_num_in_all_pom, feature_dict


def cal_has_dep_plu_all_num():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    num = 0
    has_all = 0
    for pom_file_name in pom_file_name_list:
        num += 1
        if num % 100 == 0:
            print(num)
        if has_tag(pom_file_name, "dependencies") or has_tag(pom_file_name, "dependencyManagement") and has_tag(pom_file_name, "plugins") or has_tag(pom_file_name, "pluginManagement") :
            has_all += 1
    print(has_all)
    return has_all

cal_dependency_type()
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)

if __name__ == "__main__":
    cal_has_dep_plu_all_num()
