from pom_basic_information.pom_tag import has_tag
from pom_basic_information.read_file import get_item_list, read_json_file, get_all_pom_path, get_item_in_one_pom, \
    get_item_in_all_pom
import numpy as np
import os
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
    plugin_num_in_all_pom, plugin_feature_dict = cal_item(pom_file_name_list, "plugin", "plugins", "pluginManagement")
    print(plugin_feature_dict)
    return plugin_num_in_all_pom, plugin_feature_dict


def cal_dependencies():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    dependency_num_in_all_pom, dependency_feature_dict = cal_item(pom_file_name_list, "dependency", "dependencies", "dependencyManagement")
    print(dependency_feature_dict)
    return dependency_num_in_all_pom, dependency_feature_dict


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


def item_list_to_item_dict(item_list_all):
    item_dict = {}
    for one_item_list in item_list_all:
        for item in one_item_list:
            if item in item_dict.keys():
                item_dict[item] +=1
            else:
                item_dict[item] = 1
    return item_dict


def cal_item_type(pom_file_name_list,item_name, items_name,items_name_plus,is_detail):
    item_list_all = get_item_in_all_pom(pom_file_name_list, item_name, items_name,items_name_plus,is_detail)
    item_type_dict = item_list_to_item_dict(item_list_all)
    item_type_dict_sorted = sorted(item_type_dict.items(),key =  lambda item:item[1],reverse=True )
    # item_type_num_list = [value for key, value in item_type_dict.items()]
    # feature_dict = {
    #     "num": len(item_type_num_list),
    #     "mean": np.mean(item_type_num_list),
    #     "median": np.median(item_type_num_list),
    #     "min": np.min(item_type_num_list),
    #     "max": np.max(item_type_num_list)
    # }
    # index = int(len(item_type_num_list) * 0.2)
    # return item_type_num_list,feature_dict,item_type_dict_sorted[index]
    return item_type_dict_sorted

def cal_dependency_type(is_detail=True):
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    dependency_type_num_list, feature_dict, dependency_num_20 = cal_item_type(pom_file_name_list,"dependency", "dependencies", "dependencyManagement",is_detail)
    print( feature_dict)
    print(dependency_num_20)
    return dependency_type_num_list, feature_dict, dependency_num_20


def cal_plugin_type(is_detail=True):
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    plugin_type_num_list, feature_dict, plugin_num_20 = cal_item_type(pom_file_name_list, "plugin", "plugins", "pluginManagement",is_detail)
    print(feature_dict)
    print(plugin_num_20)
    return plugin_type_num_list, feature_dict, plugin_num_20


def get_dependency_dict(is_detail=False):
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    dependency_type_dict_sorted = cal_item_type(pom_file_name_list,"dependency", "dependencies", "dependencyManagement",is_detail)
    for dependency in dependency_type_dict_sorted:
        print(dependency)


def get_plugin_dict(is_detail=False):
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    pluginy_type_dict_sorted = cal_item_type(pom_file_name_list, "plugin", "plugins", "pluginManagement",is_detail)
    for plugin in pluginy_type_dict_sorted:
        print(plugin)


if __name__ == "__main__":
    # cal_has_dep_plu_all_num()
    # cal_plugin_type()
    # cal_dependency_type()
    # get_plugin_dict()


