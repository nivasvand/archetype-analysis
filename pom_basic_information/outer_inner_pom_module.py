import os
from bs4 import BeautifulSoup
import numpy as np
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from pom_basic_information.read_file import splice_pom_dir, read_json_file, get_outer_pom_path, get_all_pom_path
from constant import ARCHETYPE_FILES_INFO, PARENT_POM_DIR, STATIC_DIR


def is_inherit(current_file_dir):
    # if os.path.isfile(current_file_dir):
    #     try:
    #         ET.parse(current_file_dir)
    #         tree = ET.ElementTree(file=current_file_dir)
    #         # tree = ET.parse(file=current_file_dir)
    #     except Exception as e:
    #         return None
    #     # root = tree.getroot()
    #     for elem in tree.iter(tag="parent"):
    #         print(current_file_dir)
    #         print(elem.text)
    #     return tree.iter(tag="parent")
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        inherit = soup.find_all('parent')
        return inherit
    return False


def recursive_inherit(current_file_dir, dict):
    if dict["inherit_depth"] == 1:
        dict["module_num"] = has_modules(current_file_dir)
    inherit_list = is_inherit(current_file_dir)
    if inherit_list:
        print(current_file_dir)
        dict["inherit_depth"] += 1
        # print(inherit_depth)
        parent_group_id = inherit_list[0].groupId.text
        parent_artifact_id = inherit_list[0].artifactId.text
        parent_version = inherit_list[0].version.text
        parent_pom_dir = os.path.join(PARENT_POM_DIR,
                                      splice_pom_dir(parent_artifact_id, parent_group_id, parent_version))
        recursive_inherit(parent_pom_dir, dict)
    return dict["inherit_depth"], dict["module_num"]


def has_modules(current_file_dir):
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        modules = soup.find_all(['modules'])
        model_list = []
        if modules:
            model_list = modules[0].find_all("module")
        return len(model_list)
    return 0


def get_parent_pom_num():
    inherit = 0
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, False)
    for pom_file_name in pom_file_name_list:
        current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
        if is_inherit(current_file_dir):
            inherit += 1
    return inherit


def get_inner_pom_module_num(value):
    module_num = 0
    if value[0]["jar"]["exist"]:
        if len(value) > 1:
            module_num = len(value[1]["jar"]["sub_models"])
        else:
            module_num = len(value[0]["jar"]["sub_models"])
    return module_num


def get_structure_info():
    outer_pom_structure_info__dict = {}
    outer_pom_structure_info__dict["inherit_depth"] = 0
    outer_pom_structure_info__dict["module_num"] = 0
    structure_info_list = []
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    for key, value in archetype_files_info_dict.items():
        info_item = {}
        current_outer_pom_file_name = get_outer_pom_path(value)
        current_file_dir = os.path.join(STATIC_DIR, current_outer_pom_file_name)
        # print(current_file_dir)
        # print("\n")
        info_item["file_name"] = current_file_dir
        info_item["inner_pom_module_num"] = get_inner_pom_module_num(value)
        info_item["outer_pom_inherit_depth"], info_item["outer_pom_module_num"] = recursive_inherit(current_file_dir,
                                                                                                    outer_pom_structure_info__dict)
        structure_info_list.append(info_item)
        outer_pom_structure_info__dict["inherit_depth"] = 0
        outer_pom_structure_info__dict["module_num"] = 0
    return structure_info_list


def pre_structure_info_list(structure_info_list):
    no_module = 0
    pre_structure_info_list = []
    outer_pom_module_num_list = []
    for info_item in structure_info_list:
        # if info_item["outer_pom_module_num"] == 0 or info_item["inner_pom_module_num"] == 0:
        # if info_item["outer_pom_module_num"] == 0:
        if info_item["inner_pom_module_num"] == 0:
            no_module += 1
            continue
        else:
            pre_structure_info_list.append(info_item)
            outer_pom_module_num_list.append(info_item["inner_pom_module_num"])
    print(np.mean(outer_pom_module_num_list), "\n")
    print(np.median(outer_pom_module_num_list), "\n")
    print(no_module, "\n")
    print(len(outer_pom_module_num_list))
    return pre_structure_info_list
