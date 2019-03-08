import sys
import json
import os
from constant import ARCHETYPE_FILES_INFO, PARENT_POM_DIR, POM_DIR, TAG_NAME_DICT_DIR, STATIC_DIR, STRUCTURE_INFO_DIR, \
    VERSION_CHANGE_DIR
import bs4
from bs4 import BeautifulSoup
import numpy as np
import unicodedata
# from akapriori import apriori
from apriori import self_apriori, gen_rule
from scipy.stats import mannwhitneyu
import re
import sys
import codecs

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

outer_pom_file_name_list = []
inner_pom_file_name_list = []
outer_pom_tag_name_dict_name = "outer_pom_tag_name_dict.txt"
inner_pom_tag_name_dict_name = "inner_pom_tag_name_dict.txt"
pom_structure_info_file_name = "pom_structure_info.txt"
pre_pom_structure_info_file_name = "pre_pom_structure_info.txt"
version_change_file_name = "version_change.txt"
OUTER_POM_TAG_NAME_DICT_NAME = os.path.join(TAG_NAME_DICT_DIR, outer_pom_tag_name_dict_name)
INNER_POM_TAG_NAME_DICT_NAME = os.path.join(TAG_NAME_DICT_DIR, inner_pom_tag_name_dict_name)
POM_STRUCTURE_INFO_FILE_NAME = os.path.join(STRUCTURE_INFO_DIR, pom_structure_info_file_name)
PRE_POM_STRUCTURE_INFO_FILE_NAME = os.path.join(STRUCTURE_INFO_DIR, pre_pom_structure_info_file_name)
VERSION_CHANGE_FILE_NAME = os.path.join(VERSION_CHANGE_DIR, version_change_file_name)


def get_outer_pom_path(value_item):
    pom_path = value_item["pom"]["path"]
    pom_path = "pom/" + pom_path.replace("static/output/pom/", "")
    return pom_path


def get_inner_pom_path(value_item):
    jar_pom_path = value_item["jar"]["path"]
    jar_pom_path = jar_pom_path.replace("static/output/", "", ) + "/pom.xml"
    return jar_pom_path


def get_pom_version(value_item):
    version = value_item["version"]
    return version


def filter_version(value):
    length = len(value)
    version_list = []
    version_order_list = []
    pre_version = get_pom_version(value[0])
    version_list.append(pre_version)
    version_order_list.append(length - 1)
    if length > 1:
        for i in range(1, length):
            flag = True
            version = get_pom_version(value[length - i])
            version_num_list = version.split(".")
            pre_version_num_list = pre_version.split(".")
            if len(version_num_list) > 1 and len(pre_version_num_list) > 1:
                if version_num_list[0] == pre_version_num_list[0] and version_num_list[1] == pre_version_num_list[1]:
                    flag = False
            elif pre_version_num_list[0] < version_num_list[0]:
                flag = True
            if flag:
                version_list.append(version)
                version_order_list.append(length - i)
            pre_version = version
    return version_list, version_order_list


def get_pom_path(value, is_inner, index=1):
    length = len(value)
    if is_inner:
        if length > 1:
            if value[index]["jar"]["exist"]:
                return get_inner_pom_path(value[index])
        else:
            if value[0]["jar"]["exist"]:
                return get_inner_pom_path(value[0])
    else:
        if length > 1:
            return get_outer_pom_path(value[index])
        else:
            return get_outer_pom_path(value[0])
    return None


def filter_pom_version(archetype_files_info_dict, is_inner):
    all_pom_version_list = []
    for key, value in archetype_files_info_dict.items():
        length = len(value)
        one_pom_version_path_list = []
        if length > 1:
            one_pom_vesion_list, one_pom_vesion_order_list = filter_version(value)
            for i in one_pom_vesion_order_list:
                pom_path = get_pom_path(value, is_inner, i)
                if pom_path:
                    one_pom_version_path_list.append(pom_path)
            all_pom_version_list.append(one_pom_version_path_list)
        else:
            continue
    return all_pom_version_list


def read_json_file(json_file_dir):
    with open(json_file_dir, 'r') as load_f:
        json_archetype_files_info_dict = json.load(load_f)
        print("load_dict finish")
    return json_archetype_files_info_dict


def get_all_pom_path(archetype_files_info_dict, is_inner):
    num = 0
    pom_file_name_list = []
    for key, value in archetype_files_info_dict.items():
        # print(get_pom_path(value, is_inner))
        current = get_pom_path(value, is_inner)
        if current:
            pom_file_name_list.append(current)
            num += 1
        else:
            continue
    print(num)
    return pom_file_name_list


def get_tag_name(pom_file_name_list):
    count = 0
    tag_name_dict = {}
    for pom_file_name in pom_file_name_list:
        # print(pom_file_name)
        current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
        if os.path.isfile(current_file_dir):
            try:
                ET.parse(current_file_dir)
                tree = ET.ElementTree(file=current_file_dir)
            except Exception as e:
                continue
        else:
            continue
        for elem in tree.iter():
            if "}" in elem.tag:
                tag_name = elem.tag.split("}")[1]
            else:
                tag_name = elem.tag
            if tag_name in tag_name_dict.keys():
                tag_name_dict[tag_name] += 1
            else:
                tag_name_dict[tag_name] = 1
        count += 1
        print(count)
    return tag_name_dict


def get_sorted_tag_name_dict(tag_name_dict):
    return sorted(tag_name_dict.items(), reverse=True, key=lambda k: k[1])


def write_tag_name_dict_to_file(tag_name_dict_sorted_list, write_file_dir):
    file_object = open(write_file_dir, 'w')
    for tuple_item in tag_name_dict_sorted_list:
        file_object.write(tuple_item[0])
        file_object.write("   ")
        file_object.write(str(tuple_item[1]))
        file_object.write('\n')
    file_object.close()


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


def splice_pom_dir(artifact_id, groupid, version):
    groupid_list = groupid.split(".")
    file_name0 = '='.join(groupid_list)
    file_name1 = artifact_id + '-' + version
    list = [file_name0, artifact_id, version, file_name1]
    pom_dir = '='.join(list) + ".pom"
    return pom_dir


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


def get_test_data(structure_info_list):
    data_outer_has_module = []
    data_outer_no_module = []
    for info_item in structure_info_list:
        if info_item["outer_pom_module_num"] == 0:
            data_outer_no_module.append(info_item["inner_pom_module_num"])
        else:
            data_outer_has_module.append(info_item["inner_pom_module_num"])
    return data_outer_has_module, data_outer_no_module


def write_structure_info_list_to_file(structure_info_list, write_file_dir):
    file_object = open(write_file_dir, 'w')
    file_object.write("file_name")
    for i in range(25):
        file_object.write(" ")
    file_object.write("outer_pom_inherit_depth")
    file_object.write("  ")
    file_object.write("outer_pom_module_num")
    file_object.write("  ")
    file_object.write("inner_pom_module_num")
    file_object.write("\n")
    for value in structure_info_list:
        file_object.write(value["file_name"])
        file_object.write("  ")
        file_object.write(str(value["outer_pom_inherit_depth"]))
        file_object.write("  ")
        file_object.write(str(value["outer_pom_module_num"]))
        file_object.write("  ")
        file_object.write(str(value["inner_pom_module_num"]))
        file_object.write("\n")
    file_object.close()


def get_tag_in_one_pom(pom_file_name):
    drop_list = ["artifactId", "version", "groupId", "packaging", "modelVersion", "name", "project"]
    current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
    tag_in_one_pom = []
    if os.path.isfile(current_file_dir):
        try:
            ET.parse(current_file_dir)
            tree = ET.ElementTree(file=current_file_dir)
            for elem in tree.iter():
                if "}" in elem.tag:
                    tag_name = elem.tag.split("}")[1]
                else:
                    tag_name = elem.tag
                if tag_name not in tag_in_one_pom and tag_name not in drop_list:
                    tag_in_one_pom.append(tag_name)
        except Exception as e:
            return tag_in_one_pom
    return tag_in_one_pom


def get_tag_in_all_pom(pom_file_name_list):
    tag_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_tag_in_one_pom = get_tag_in_one_pom(pom_file_name)
        if len(current_tag_in_one_pom) > 0:
            tag_in_all_pom.append(current_tag_in_one_pom)
    return tag_in_all_pom


# def my_apriori(data_set, support=0.5, confidence=0.5, lift=0, minlen=3, maxlen=6):
#     rules = apriori(data_set, support, confidence, lift, minlen, maxlen)
#     rules_sorted = sorted(rules, key=lambda x: (x[4], x[3], x[2]), reverse=True)
#     return rules_sorted

def get_association_rule(dataset, minSupport=0.01, minConf=0.5):
    L, supportData = self_apriori(dataset, minSupport)
    rule = gen_rule(L, supportData, minConf)
    for r in rule:
        print(r, "\n")
    return rule


def has_tag(pom_file_name, tag_name):
    current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        item = soup.find(tag_name)
        if item:
            return True
        else:
            return False
    return None


def get_dependency_in_one_pom(pom_file_name):
    current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
    dependency_in_one_pom = []
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        dependencies = soup.find_all(['dependencies'])
        dependency_list = []
        if len(dependencies) > 0:
            dependency_list = dependencies[0].find_all("dependency")
        for item in dependency_list:
            item_name = item.find("groupId").text + "_" + item.find("artifactId").text
            if item_name not in dependency_in_one_pom:
                dependency_in_one_pom.append(item_name)
    return dependency_in_one_pom


def cal_item(pom_file_name_list, item_name, items_name):
    dependency_num_in_all_pom = []
    num = 0
    for pom_file_name in pom_file_name_list:
        if num % 100 == 0:
            print(num)
        if has_tag(pom_file_name, "dependencies") and has_tag(pom_file_name, "plugins"):
            num += 1
    return num
    #     current_dependency_num_in_one_pom = len(get_item_list(pom_file_name, item_name,items_name ))
    #     if current_dependency_num_in_one_pom > 0:
    #         dependency_num_in_all_pom.append(current_dependency_num_in_one_pom)
    # print(len(dependency_num_in_all_pom))
    # return np.mean(dependency_num_in_all_pom), np.median(dependency_num_in_all_pom)


def get_dependency_in_all_pom(pom_file_name_list):
    dependency_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_dependency_in_one_pom = get_dependency_in_one_pom(pom_file_name)
        if len(current_dependency_in_one_pom) > 0:
            dependency_in_all_pom.append(current_dependency_in_one_pom)
    return dependency_in_all_pom


# def get_pom_tag()

def extract_all(pom, tag_name):
    for item in pom.find_all(tag_name):
        item.extract()


def flat_pom(soup):
    flat_pom_list = []
    pom = soup.project
    # print(dependencies)
    # print(plugins)
    if pom:
        extract_all(pom, 'dependencies')
        extract_all(pom, 'plugins')
        if pom.find("dependencies"):
            print("error dependencies")
            # print(pom)
        if pom.find("plugins"):
            print("error plugins")
            # print(pom, "\n")
        for child in pom.descendants:
            tag_name = ""
            if type(child) == bs4.element.NavigableString and child.encode("utf-8") != b"\n":
                for current_parent in child.parents:
                    if current_parent and current_parent.parent:
                        tag_name = tag_name + "_" + current_parent.name
                flat_pom_list.append((tag_name, child.encode("utf-8")))
    return flat_pom_list


def get_item_list(pom_file_dir, item_name, items_name):
    current_file_dir = os.path.join(STATIC_DIR, pom_file_dir)
    list = []
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        objs = soup.find(items_name)
        if objs:
            obj_list = objs.find_all(item_name)
            for obj in obj_list:
                item_groupId = obj.find("groupId")
                item_artifactId = obj.find("artifactId")
                if item_groupId and item_artifactId:
                    item_name = item_groupId.text + "_" + item_artifactId.text
                list.append(item_name)
    return list


def get_dependency_list(pom_file_dir):
    dependency_list = []
    soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
    dependencies = soup.dependencies
    if dependencies:
        dependency_raw_list = dependencies.find_all("dependency")
        for item in dependency_raw_list:
            dependency_groupId = item.find("groupId")
            dependency_artifactId = item.find("artifactId")
            if dependency_groupId and dependency_artifactId:
                dependency_name = dependency_groupId.text + "_" + dependency_artifactId.text
            else:
                continue
            dependency_version = item.find("version")
            dependency_scope = item.find("scope")
            dependency_exclutions = item.find("exclusions")
            dependency_exclution_list = []
            if dependency_version == None:
                dependency_version = ""
            if dependency_scope:
                dependency_scope = dependency_scope.text
            else:
                dependency_scope = ""
            if dependency_exclutions:
                dependency_raw_exclution_list = dependency_exclutions.find_all("exclusion")
                for exclution in dependency_raw_exclution_list:
                    exclution_groupId = exclution.find("groupId")
                    exclution_artifactId = exclution.find("artifactId")
                    if exclution_groupId and exclution_artifactId:
                        exclution_name = exclution_groupId.text + "_" + exclution_artifactId.text
                        exclution_version = exclution.find("version")
                        if exclution_version == None:
                            exclution_version = ""
                        dependency_exclution_list.append([exclution_name, exclution_version])
                    else:
                        continue
            dependency_list.append([dependency_name, dependency_version, dependency_scope, dependency_exclution_list])
    # print(dependency_list)
    return dependency_list


def get_plugin_list(pom_file_dir):
    plugin_list = []
    soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
    build = soup.build
    if build:
        plugins = build.plugins
        if plugins:
            plugin_raw_list = plugins.find_all("plugin")
            for item in plugin_raw_list:
                plugin_groupId = item.find("groupId")
                plugin_artifactId = item.find("artifactId")
                if plugin_groupId and plugin_artifactId:
                    plugin_name = plugin_groupId.text + "_" + plugin_artifactId.text
                else:
                    continue

                plugin_version = item.find("version")
                plugin_dependencies = item.find("dependencies")
                pluin_dependency_list = []
                if plugin_version == None:
                    plugin_version = ""
                if plugin_dependencies:
                    pugin_raw_dependency_list = plugin_dependencies.find_all("dependency")
                    for dependency in pugin_raw_dependency_list:
                        dependency_groupId = dependency.find("groupId")
                        dependency_artifactId = dependency.find("artifactId")
                        if dependency_groupId and dependency_artifactId:
                            plugin_name = dependency_groupId.text + "_" + dependency_artifactId.text
                            dependency_version = dependency.find("version")
                            if dependency_version == None:
                                dependency_version = ""
                            pluin_dependency_list.append([plugin_name, dependency_version])
                        else:
                            continue
                plugin_list.append([plugin_name, plugin_version, pluin_dependency_list])
    return plugin_list


def compare_dependency_list(dependency_list1, dependency_list2, diff_tag_dic):
    dependency_del_flag = True
    dependency_add_flag = True
    if len(dependency_list1) > 0 and len(dependency_list2) > 0:
        for dependency1 in dependency_list1:
            for dependency2 in dependency_list2:
                if dependency1[0] == dependency2[0]:
                    dependency_del_flag = False
                    if dependency1[1] != dependency2[1]:
                        diff_tag_dic["dependency_version_change"] += 1
                    elif dependency1[2] != dependency2[2]:
                        diff_tag_dic["dependency_scope_change"] += 1
                    elif dependency1[3] != dependency2[3]:
                        diff_tag_dic["dependency_exclusions_change"] += 1
            if dependency_del_flag:
                diff_tag_dic["dependency_del"] += 1
            dependency_del_flag = True

        for dependency2 in dependency_list2:
            for dependency1 in dependency_list1:
                if dependency1[0] == dependency2[0]:
                    dependency_add_flag = False
            if dependency_add_flag:
                diff_tag_dic["dependency_add"] += 1
            dependency_add_flag = True

    return diff_tag_dic


def compare_plugin_list(plugin_list1, plugin_list2, diff_tag_dic):
    plugin_del_flag = True
    plugin_add_flag = True
    if len(plugin_list1) > 0 and len(plugin_list2) > 0:
        for plugin1 in plugin_list1:
            for plugin2 in plugin_list2:
                if plugin1[0] == plugin2[0]:
                    plugin_del_flag = False
                    if plugin1[1] != plugin2[1]:
                        diff_tag_dic["plugin_version_change"] += 1
                    elif plugin1[2] != plugin2[2]:
                        diff_tag_dic["plugin_dependency_change"] += 1
            if plugin_del_flag:
                diff_tag_dic["plugin_del"] += 1
            plugin_del_flag = True

        for plugin2 in plugin_list2:
            for plugin1 in plugin_list1:
                if plugin1[0] == plugin2[0]:
                    plugin_add_flag = False
            if plugin_add_flag:
                diff_tag_dic["plugin_add"] += 1
            plugin_add_flag = True

    return diff_tag_dic


def set_diff_tag_dic():
    diff_tag_dic = {}
    diff_tag_dic["dependency_version_change"] = 0
    diff_tag_dic["dependency_scope_change"] = 0
    diff_tag_dic["dependency_add"] = 0
    diff_tag_dic["dependency_del"] = 0
    diff_tag_dic["dependency_exclusions_change"] = 0
    diff_tag_dic["plugin_version_change"] = 0
    diff_tag_dic["plugin_add"] = 0
    diff_tag_dic["plugin_del"] = 0
    diff_tag_dic["plugin_dependency_change"] = 0
    return diff_tag_dic


def compare_pom(pom1_path, pom2_path, diff_tag_dic):
    pom1_file_dir = os.path.join(STATIC_DIR, pom1_path)
    pom2_file_dir = os.path.join(STATIC_DIR, pom2_path)
    compare_tag_list1 = {}
    compare_tag_dic2 = {}
    soup1 = BeautifulSoup(open(pom1_file_dir, 'rt', encoding='latin1'), "xml")
    soup2 = BeautifulSoup(open(pom2_file_dir, 'rt', encoding='latin1'), "xml")
    if soup2.find_all("project") == soup1.find_all("project"):
        return
    compare_tag_list1 = flat_pom(soup1)
    compare_tag_list2 = flat_pom(soup2)

    for one_tuple in compare_tag_list1:
        key = one_tuple[0]
        if one_tuple in compare_tag_list2:
            continue
        elif key in diff_tag_dic.keys():
            diff_tag_dic[key] += 1
        else:
            diff_tag_dic[key] = 1
    # print(diff_tag_dic)


def compare_all_pom(archetype_files_info_dict, is_inner):
    all_pom_version_list = filter_pom_version(archetype_files_info_dict, is_inner)
    num = 0
    diff_tag_dic = set_diff_tag_dic()
    for one_pom_version_list in all_pom_version_list:
        num += 1
        if num % 100 == 0:
            print(num, "\n")
        length = len(one_pom_version_list)
        if length == 1:
            continue
        else:
            for i in range(length - 1):
                pom1_path = one_pom_version_list[i]
                pom1_file_dir = os.path.join(STATIC_DIR, pom1_path)
                pom2_path = one_pom_version_list[i + 1]
                pom2_file_dir = os.path.join(STATIC_DIR, pom2_path)
                # print(pom1_file_dir, pom2_file_dir)
                if os.path.isfile(pom1_file_dir) and os.path.isfile(pom2_file_dir):
                    dependency_list1 = get_dependency_list(pom1_file_dir)
                    dependency_list2 = get_dependency_list(pom2_file_dir)
                    plugin_list1 = get_plugin_list(pom1_file_dir)
                    plugin_list2 = get_plugin_list(pom2_file_dir)
                    diff_tag_dic = compare_dependency_list(dependency_list1, dependency_list2, diff_tag_dic)
                    diff_tag_dic = compare_plugin_list(plugin_list1, plugin_list2, diff_tag_dic)
                    compare_pom(pom1_file_dir, pom2_file_dir, diff_tag_dic)
                    # print(diff_tag_dic, "\n")
    diff_tag_dic = sorted(diff_tag_dic.items(), reverse=True, key=lambda k: k[1])
    # print(diff_tag_dic)
    return diff_tag_dic


def write_dic_to_file(dic, write_file_dir):
    file_object = open(write_file_dir, 'w')
    for value in dic:
        file_object.write(value[0])
        file_object.write("   ")
        file_object.write(str(value[1]))
        file_object.write("\n")
    file_object.close()


if __name__ == "__main__":
    # num = 0
    # inherit = 0
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    # structure_info_list = get_structure_info()
    # pre_structure_info_list = pre_structure_info_list(structure_info_list)
    # write_structure_info_list_to_file(structure_info_list, POM_STRUCTURE_INFO_FILE_NAME)
    # write_structure_info_list_to_file(pre_structure_info_list, PRE_POM_STRUCTURE_INFO_FILE_NAME)

    pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    # print(cal_item(pom_file_name_list, "dependency", "dependencies"))
    # tag_in_all_pom = get_tag_in_all_pom(pom_file_name_list)
    dependency_in_all_pom = get_dependency_in_all_pom(pom_file_name_list)
    L, supportData = self_apriori(dependency_in_all_pom, minSupport=0.01)
    bigRuleList = gen_rule(L, supportData)
    # get_association_rule(dependency_in_all_pom)
    #
    # # rules_sorted = my_apriori(tag_in_all_pom,)

    for r in bigRuleList:
        print(r, "\n")

    # for pom_file_name in pom_file_name_list:
    #     current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
    #     inherit_list = is_inherit(current_file_dir)
    #     if inherit_list:
    #         print(inherit_list[0].groupId)

    # dict = {}
    # dict["inherit_depth"] = 0
    # dict["module_num"] = 0
    # test_pom_dir = os.path.join(POM_DIR,"co=cask=cdap=cdap-etl-batch-sink-archetype=3.0.0=cdap-etl-batch-sink-archetype-3.0.0.pom")
    # inherit_depth, module_num = recursive_inherit(test_pom_dir, dict)
    # print(inherit_depth, module_num)

    # tag_name_dict_sorted_list = get_sorted_tag_name_dict(get_tag_name(pom_file_name_list))
    # write_tag_name_dict_to_file(tag_name_dict_sorted_list, INNER_POM_TAG_NAME_DICT_NAME)

    # diff_tag_dic = compare_all_pom(archetype_files_info_dict, True)
    # # print(diff_tag_dic)
    # write_dic_to_file(diff_tag_dic, VERSION_CHANGE_FILE_NAME)