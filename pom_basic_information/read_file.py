import sys
import json
import os
from constant import ARCHETYPE_FILES_INFO, PARENT_POM_DIR, POM_DIR, TAG_NAME_DICT_DIR, STATIC_DIR, STRUCTURE_INFO_DIR, \
    VERSION_CHANGE_DIR, DEPENDENCY_DIR, PLUGIN_DIR, DEPENDENCY_PLUGIN_DIR, TAG_DIR,TOKEN_DIR
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
import gensim
import nltk
from nltk.tokenize import word_tokenize
import string
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from gensim.models.ldamodel import LdaModel
from nltk.stem import WordNetLemmatizer
from collections import Counter
import javalang
import copy
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
dependency_apriori_file_name  = "dependency_apriori.txt"
plugin_apriori_file_name  = "plugin_apriori.txt"
dependency_plugin_apriori_file_name = "dependency_plugin_apriori.txt"
tag_apriori_file_name  = "tag_apriori.txt"
token_file_name ="token_file_name.txt"
dependency_add_del_file_name = "dependency_add_del.txt"
OUTER_POM_TAG_NAME_DICT_NAME = os.path.join(TAG_NAME_DICT_DIR, outer_pom_tag_name_dict_name)
INNER_POM_TAG_NAME_DICT_NAME = os.path.join(TAG_NAME_DICT_DIR, inner_pom_tag_name_dict_name)
POM_STRUCTURE_INFO_FILE_NAME = os.path.join(STRUCTURE_INFO_DIR, pom_structure_info_file_name)
PRE_POM_STRUCTURE_INFO_FILE_NAME = os.path.join(STRUCTURE_INFO_DIR, pre_pom_structure_info_file_name)
VERSION_CHANGE_FILE_NAME = os.path.join(VERSION_CHANGE_DIR, version_change_file_name)
DENPENDENCY_APRIORI_DIR_NAME = os.path.join(DEPENDENCY_DIR, dependency_apriori_file_name)
PLUGIN_APRIORI_DIR_NAME = os.path.join(PLUGIN_DIR, plugin_apriori_file_name)
DENPENDENCY_PLUGIN_APRIORI_DIR_NAME = os.path.join(DEPENDENCY_PLUGIN_DIR, dependency_plugin_apriori_file_name)
TAG_APRIORI_DIR_NAME = os.path.join(TAG_DIR, tag_apriori_file_name)
TOKEN_FILE_DIR =  os.path.join(TOKEN_DIR, token_file_name)
DEPENDENCY_ADD_DEL_DIR = os.path.join(VERSION_CHANGE_DIR, dependency_add_del_file_name)


def get_outer_pom_path(value_item):
    pom_path = value_item["pom"]["path"]
    pom_path = "pom/" + pom_path.replace("static/output/pom/", "")
    return pom_path


def get_inner_pom_path(value_item):
    jar_pom_path = value_item["jar"]["path"]
    jar_pom_path = jar_pom_path.replace("static/output/", "", ) + "/pom.xml"
    return jar_pom_path

def get_inner_jar_path(value_item):
    jar_pom_path_list = []
    jar_pom_path = value_item["jar"]["path"]
    jar_pom_path = jar_pom_path.replace("static/output/", "", )
    # sub_model_list = value_item["jar"]["sub_models"]
    # if len(sub_model_list)>0:
    #     for sub_model in sub_model_list:
    #         current_jar_pom_path = os.path.join()
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


def get_two_pom_path(value, index=1):
    length = len(value)
    inner_pom_path = ""
    outer_pom_path = ""
    if length > 1:
        if value[index]["jar"]["exist"]:
            inner_pom_path = get_inner_jar_path(value[index])
            outer_pom_path = get_outer_pom_path(value[index])
            return [inner_pom_path, outer_pom_path]
    else:
        if value[0]["jar"]["exist"]:
            inner_pom_path = get_inner_jar_path(value[0])
            outer_pom_path = get_outer_pom_path(value[0])
            return [inner_pom_path, outer_pom_path]
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


def get_all_two_pom_path(archetype_files_info_dict):
    num = 0
    pom_file_name_list = []
    for key, value in archetype_files_info_dict.items():
        # print(get_pom_path(value, is_inner))
        current_two_pom = get_two_pom_path(value)
        if current_two_pom:
            pom_file_name_list.append(current_two_pom)
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
    drop_list = ["artifactId", "version", "groupId", "packaging", "modelVersion", "name", "project", "url",	"organization", "description", "scm", "parent"]
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


def get_description_in_one_pom(pom_file_name):
    current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
    description = ""
    name = " "
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        description = soup.find("description")
        project = soup.project
        if description:
            description = description.text
        if project:
            name = project.find_all("name", recursive=False)
            if len(name)>0:
                name =name[0].text
                description = str(description) +" "+str(name)
    return description


def get_tag_in_all_pom(pom_file_name_list):
    tag_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_tag_in_one_pom = get_tag_in_one_pom(pom_file_name)
        if len(current_tag_in_one_pom) > 0:
            tag_in_all_pom.append(current_tag_in_one_pom)
    return tag_in_all_pom


def get_description_in_all_pom(pom_file_name_list):
    description_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_description_in_one_pom = get_description_in_one_pom(pom_file_name)
        if current_description_in_one_pom:
            description_in_all_pom.append(current_description_in_one_pom)
    return description_in_all_pom


def get_text_in_all_pom(pom_file_name_list):
    print("get text start")
    i = 0
    text_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_description_in_one_pom = get_description_in_one_pom(pom_file_name[1])
        current_java_class_name_list = get_java_class_in_one_archetype(pom_file_name[0])
        current_java_file_list = get_java_file_in_one_archrtype(pom_file_name[0])
        current_java_method_list = get_java_method(current_java_file_list)
        if len(current_java_method_list) == 0:
            i += 1
            # print(pom_file_name)
        if current_description_in_one_pom:
            text_in_all_pom.append([current_description_in_one_pom, current_java_class_name_list, current_java_method_list])
        else:
            text_in_all_pom.append(["",current_java_class_name_list,current_java_method_list])
    print(i)
    print("get text finish")
    return text_in_all_pom


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


def get_item_in_one_pom(pom_file_name, item_name, items_name,items_name_plus):
    current_file_dir = os.path.join(STATIC_DIR, pom_file_name)
    item_in_one_pom = []
    if os.path.isfile(current_file_dir):
        soup = BeautifulSoup(open(current_file_dir, 'rt', encoding='latin1'), "xml")
        items = soup.find_all(items_name)
        items_plus = soup.items_name_plus
        item_raw_list = []
        if len(items) > 0:
            item_raw_list = items[0].find_all(item_name)
        if items_plus:
            item_raw_list = item_raw_list + items_plus.find_all(item_name)
        for item in item_raw_list:
            item_groupId = item.find("groupId")
            # item_artifactId = item.find("artifactId")
            # if item_groupId and item_artifactId:
            #     item_name = item_groupId.text + "_" + item_artifactId.text
            #     item_in_one_pom.append(item_name)
            if item_groupId:
                item_name = item_groupId.text
                # if item_name =="junit":
                #     continue
                if item_name not in item_in_one_pom:
                    item_in_one_pom.append(item_name)

    return item_in_one_pom


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


def get_item_in_all_pom(pom_file_name_list,item_name, items_name,items_name_plus):
    item_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_item_in_one_pom = get_item_in_one_pom(pom_file_name,item_name, items_name,items_name_plus)
        if len(current_item_in_one_pom) > 0:
            item_in_all_pom.append(current_item_in_one_pom)
    return item_in_all_pom


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


def flat_pom_tag(pom_path):
    pom_file_dir = os.path.join(STATIC_DIR, pom_path)
    flat_pom_dict = {}
    if os.path.isfile(pom_file_dir):
        soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
        pom = soup.project
        if pom:
            for child in pom.descendants:
                tag_name = ""
                if type(child) == bs4.element.NavigableString and child.encode("utf-8") != b"\n":
                    for current_parent in child.parents:
                        if current_parent and current_parent.parent:
                            tag_name = tag_name + "_" + current_parent.name
                    if  tag_name in flat_pom_dict.keys():
                        flat_pom_dict[tag_name] +=1
                    else:
                        flat_pom_dict[tag_name] = 1
        return flat_pom_dict


def get_all_flat_pom_tag(pom_file_name_list):
    flat_pom_dic_all = {}
    for pom_path in pom_file_name_list:
        new_flat_pom_dict = flat_pom_tag(pom_path)
        flat_pom_dic_all = dict(Counter(new_flat_pom_dict)+Counter(flat_pom_dic_all))
    flat_pom_dic_all = sorted(flat_pom_dic_all.items(), reverse=True, key=lambda k: k[1])
    for tag_name in flat_pom_dic_all:
        print(tag_name)
    return flat_pom_dic_all


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
    dependency_raw_list = []
    soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
    dependencies = soup.find_all("dependencies")
    if dependencies:
        for dependencies_item in dependencies:
            dependency_raw_list = dependencies_item.find_all("dependency")+ dependency_raw_list

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
        return dependency_list
    else:
        return None


def get_plugin_list(pom_file_dir):
    plugin_list = []
    plugin_raw_list = []
    soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
    build = soup.build
    if build:
        plugins = build.find_all("plugins")
        if plugins:
            for plugin_item in  plugins:
                plugin_raw_list = plugin_item.find_all("plugin") + plugin_raw_list

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
    else:
        return None


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


def compare_item_add_del(item_list1, item_list2):
    item_del_list = []
    item_add_list = []
    for item in item_list1:
        item_del_list.append(item[0])
    for item in item_list2:
        item_add_list.append(item[0])
    if len(item_list1) > 0 and len(item_list2) > 0:
        for item1 in item_list1:
            for item2 in item_list2:
                if item1[0] == item2[0]:
                    if item1[0] in item_del_list:
                        item_del_list.remove(item1[0])

        for item2 in item_list2:
            for item1 in item_list1:
                if item1[0] == item2[0]:
                    if item2[0] in item_add_list:
                        item_add_list.remove(item2[0])
    return [item_del_list, len(item_del_list), item_add_list, len(item_add_list)]


def compare_item_add_del_in_all_pom(archetype_files_info_dict, is_inner):
    all_pom_version_list = filter_pom_version(archetype_files_info_dict, is_inner)
    dependency_comapre_list = []
    dependency_del_dict_all = []
    dependency_add_dict_all = []
    dependency_del_num_list = []
    dependency_add_num_list = []
    plugin_comapre_list = []
    plugin_del_dict_all = []
    plugin_add_dict_all = []
    plugin_del_num_list = []
    plugin_add_num_list = []
    num = 0
    add_num = 0
    del_num = 0
    add_del = 0
    sum_equ = 0
    for one_pom_version_list in all_pom_version_list:
        length = len(one_pom_version_list)
        if length == 1:
            continue
        else:
            for i in range(length - 1):
                pom1_path = one_pom_version_list[i]
                pom1_file_dir = os.path.join(STATIC_DIR, pom1_path)
                pom2_path = one_pom_version_list[i + 1]
                pom2_file_dir = os.path.join(STATIC_DIR, pom2_path)
                if pom1_file_dir == pom2_file_dir:
                    continue
                # print(pom1_file_dir, pom2_file_dir)
                if os.path.isfile(pom1_file_dir) and os.path.isfile(pom2_file_dir):
                    # dependency_list1 = get_dependency_list(pom1_file_dir)
                    # dependency_list2 = get_dependency_list(pom2_file_dir)
                    # if len(dependency_list1) != 0 and len(dependency_list2) !=0:
                    #     num += 1
                    #     if num % 100 == 0:
                    #         print(num, "\n")
                        # dependency_del_list, dependency_del_num, dependency_add_list, dependency_add_num, pre_dependency_del_list, pre_dependency_add_list = compare_item_add_del(dependency_list1, dependency_list2)
                        # if dependency_del_num > 0 and dependency_add_num > 0 :
                        #     if dependency_del_num == dependency_add_num:
                        #         add_del +=1
                            # add_num +=1
                            # del_num +=1
                        # elif dependency_del_num > 0:
                        #     del_num += 1
                        # elif dependency_add_num > 0:
                        #     add_num += 1
                            # dependency_comapre_list.append([dependency_del_list, dependency_del_num, dependency_add_list, dependency_add_num])
                        # dependency_del_dict_all = dict(Counter(dependency_del_dict_all) + Counter(dependency_del_list))
                        # dependency_add_dict_all = dict(Counter(dependency_add_dict_all) + Counter(dependency_add_list))
                        # if dependency_del_num > 0:
                        #     dependency_del_num_list.append(dependency_del_num)
                        # if  dependency_add_num > 0:
                        #     dependency_add_num_list.append(dependency_add_num)
                        # if "junit_junit" in dependency_del_list:
                        #     print(pom1_file_dir, "    ", pom2_file_dir)
                        #     print(pre_dependency_del_list, "\n", pre_dependency_add_list)

                    plugin_list1 = get_plugin_list(pom1_file_dir)
                    plugin_list2 = get_plugin_list(pom2_file_dir)
                    if len(plugin_list1)!=0 and len(plugin_list2)!=0:
                        num += 1
                        if num % 100 == 0:
                            print(num, "\n")
                        plugin_del_list, plugin_del_num, plugin_add_list, plugin_add_num = compare_item_add_del(plugin_list1, plugin_list2)
                        # if plugin_del_num > 0 or plugin_add_num > 0:
                        #     plugin_comapre_list.append([plugin_del_list, plugin_del_num, plugin_add_list, plugin_add_num])
                        # if plugin_del_num > 0 and plugin_add_num > 0:
                        #     add_del += 1
                        #     add_num += 1
                        #     del_num += 1
                        #     if plugin_del_num == plugin_add_num:
                        #         sum_equ += 1
                        # elif plugin_del_num > 0:
                        #     del_num += 1
                        # elif plugin_add_num > 0:
                        #     add_num += 1
                        # plugin_del_dict_all = dict(Counter(plugin_del_dict_all) + Counter(plugin_del_list))
                        # if plugin_del_num > 0:
                        #     plugin_del_num_list.append(plugin_del_num)

                        # plugin_add_dict_all = dict(Counter(plugin_add_dict_all) + Counter(plugin_add_list))
                        if plugin_add_num > 0:
                            plugin_add_num_list.append(plugin_add_num)


    # dependency_del_dict_all= sorted(dependency_del_dict_all.items(), reverse=True, key=lambda k: k[1])
    # dependency_add_dict_all = sorted(dependency_add_dict_all.items(), reverse=True, key=lambda k: k[1])
    # plugin_del_dict_all = sorted(plugin_del_dict_all.items(), reverse=True, key=lambda k: k[1])
    # plugin_add_dict_all = sorted(plugin_add_dict_all.items(), reverse=True, key=lambda k: k[1])
    # print("dependency")
    # for item in dependency_comapre_list:
    #     print(item)
    # write_double_list_to_file(dependency_comapre_list,DEPENDENCY_ADD_DEL_DIR)
    # print("dependency del")
    # for item in dependency_del_dict_all:
    #     print(item)
    # print(np.median(dependency_del_num_list))
    # print(np.mean(dependency_del_num_list))
    # print(num)
    # print("dependency add")
    # for item in dependency_add_dict_all:
    #     print(item)
    # print(np.median(dependency_add_num_list))
    # print(np.mean(dependency_add_num_list))
    # print("plugin")
    # for item in plugin_comapre_list:
    #     print(item)
    # print("plugin del")
    # for item in plugin_del_dict_all:
    #     print(item)
    # print(np.median(plugin_del_num_list))
    # print(np.mean(plugin_del_num_list))
    print("plugin add")
    # for item in plugin_add_dict_all:
    #     print(item)
    print(np.median(plugin_add_num_list))
    print(np.mean(plugin_add_num_list))
    # print(add_del)
    # print(del_num)
    # print(add_num)
    # print(sum_equ)


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
        length = len(one_pom_version_list)
        if length == 1:
            continue
        else:
            for i in range(length - 1):
                pom1_path = one_pom_version_list[i]
                pom1_file_dir = os.path.join(STATIC_DIR, pom1_path)
                pom2_path = one_pom_version_list[i + 1]
                pom2_file_dir = os.path.join(STATIC_DIR, pom2_path)
                if pom1_path == pom2_path:
                    continue
                # print(pom1_file_dir, pom2_file_dir)
                if os.path.isfile(pom1_file_dir) and os.path.isfile(pom2_file_dir):
                    num += 1
                    if num % 100 == 0:
                        print(num, "\n")
                    dependency_list1 = get_dependency_list(pom1_file_dir)
                    dependency_list2 = get_dependency_list(pom2_file_dir)
                    plugin_list1 = get_plugin_list(pom1_file_dir)
                    plugin_list2 = get_plugin_list(pom2_file_dir)
                    if dependency_list1 and dependency_list2:
                        diff_tag_dic = compare_dependency_list(dependency_list1, dependency_list2, diff_tag_dic)
                    if plugin_list1 and plugin_list2:
                        diff_tag_dic = compare_plugin_list(plugin_list1, plugin_list2, diff_tag_dic)
                    compare_pom(pom1_file_dir, pom2_file_dir, diff_tag_dic)
                    # print(diff_tag_dic, "\n")
    diff_tag_dic = sorted(diff_tag_dic.items(), reverse=True, key=lambda k: k[1])
    # print(diff_tag_dic)
    print(num)
    return diff_tag_dic


def write_dic_to_file(dic, write_file_dir):
    file_object = open(write_file_dir, 'w')
    for value in dic:
        file_object.write(value[0])
        file_object.write("   ")
        file_object.write(str(value[1]))
        file_object.write("\n")
    file_object.close()


def write_list_in_list_to_file(file_list, write_file_dir):
    file_object = open(write_file_dir, 'w', encoding='utf-8')
    for list_value in file_list:
        for value in list_value:
            # if type(value) == frozenset:
            #     value = [str(x) for x in value]
            file_object.write(value)
            file_object.write("    ")
        file_object.write("\n")
    file_object.close()


def write_double_list_to_file(double_list,write_file_dir):
    file_object = open(write_file_dir, 'w', encoding='utf-8')
    for item_list in double_list:
        item_list_str = " ".join([str(item) for item in item_list])
        file_object.write(item_list_str)
        file_object.write("\n")
    file_object.close()


def tokenize(description_list, java_class_list,java_method_list):
    i = 0
    word_list = []
    del_list = ["archetype", "project", "maven", "java","something","module","create","template","compare","point", "entry", "execute","set","get","main", "use","controller","hello","none"]
    for text in description_list:
        i += 1
        # print(i)
        text = "".join([ch for ch in text if ch not in string.punctuation])
        text = word_tokenize(text)
        # text = [word.lower() for word in text]
        # tagged_sent = pos_tag(text)
        # wnl = WordNetLemmatizer()
        # text_token = []
        # for tag in tagged_sent:
        #     pos = get_wordnet_pos(tag[1])
        #     wordnet_pos = pos or wordnet.NOUN
        #     if filter_word_pos(wordnet_pos):
        #         word = wnl.lemmatize(tag[0], pos=wordnet_pos)
        #         text_token.append(word)# 词形还原
        #     else:
        #         continue
        # text_token_remove_word = [item for item in text_token if item not in del_list]
        text_word = list(set(text+java_class_list+java_method_list))
        text_word = get_filter_word_list(text_word,del_list)
        text_word = list(set(text_word))
        word_list.append(text_word)
    print("tokenize finish")
    write_list_in_list_to_file(word_list,TOKEN_FILE_DIR)
    return word_list


def get_dic(word_list):
    return corpora.Dictionary(word_list)


def add_dic(dic, add_word_list):
    dic.add_documents(add_word_list, prune_at=2000000)
    return dic


def get_clean_word_list(word_list):
    clean_word_list = []
    for words in word_list:
        clean_word_list.append([w.lower() for w in words if w.lower() not in stopwords.words('english') and w.isdigit() == False])
    return clean_word_list


def get_corpus(dic, text_list):
    corpus = [dic.doc2bow(text) for text in text_list]
    return corpus


def filter_word_pos(pos):
    if pos == wordnet.ADJ:
        return False
    else:
        return True


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def get_filter_word_list(word_list,del_word_list):
    word_list = [word.lower() for word in word_list]
    wnl = WordNetLemmatizer()
    tagged_sent = pos_tag(word_list)
    word_token = []
    for tag in tagged_sent:
        pos = get_wordnet_pos(tag[1])
        wordnet_pos = pos or wordnet.NOUN
        if filter_word_pos(wordnet_pos):
            word = wnl.lemmatize(tag[0], pos=wordnet_pos)
            word_token.append(word)  # 词形还原
        else:
            continue
    word_token_remove_word = [item for item in word_token if item not in del_word_list]
    return word_token_remove_word

def get_word_list_from_pom(pom_file_name_list):
    text_list = get_text_in_all_pom(pom_file_name_list)
    description_list = []
    java_class_list = []
    java_method_list = []
    for text in text_list:
        description_list.append(text[0])
        java_class_list = text[1]
        java_method_list = text[2]
    tokenize_list = tokenize(description_list, java_class_list, java_method_list)
    clean_word_list = get_clean_word_list(tokenize_list)
    return clean_word_list


def build_topicmodel(pom_file_name_list, topic_num):
    # text_list = get_text_in_all_pom(pom_file_name_list)
    # description_list = []
    # java_class_list = []
    # java_method_list = []
    # for text in text_list:
    #     description_list.append(text[0])
    #     java_class_list = text[1]
    #     java_method_list = text[2]
    # tokenize_list = tokenize(description_list,java_class_list,java_method_list)
    # clean_word_list = get_clean_word_list(tokenize_list)
    # for word_list in clean_word_list:
    #     print(word_list)
    clean_word_list = get_word_list_from_pom(pom_file_name_list)
    dic = get_dic(clean_word_list)
    print("dic finish")
    basic_corpus = get_corpus(dic, clean_word_list)
    lda = LdaModel(corpus=basic_corpus, id2word=dic, num_topics=topic_num)
    for i in range(topic_num):
        print(i)
        print(lda.show_topic(i))
        print("-------------------")
    # show_text_topic(lda, dic, clean_word_list[0:50])
    return lda


def show_text_topic(lda_model, dic, text_list):
    i = 0
    for text in text_list:
        i +=1
        print(i)
        doc_bow = dic.doc2bow(text)  # 文档转换成bow
        doc_lda = lda_model[doc_bow]
        # print(doc_lda)
        # for topic in doc_lda:
        #     print("%s\t%f\n" % (lda_model.print_topic(topic[0]), topic[1]))
        print(get_top_topic(lda_model,doc_lda))


def get_java_class_in_one_archetype(path,rule=".java"):
    current_path = os.path.join(STATIC_DIR, path)
    java_class_name_in_one_archetype = []
    for root,dirs,files in os.walk(current_path):   # os.walk获取所有的目录
        for file in files:
            file_name = os.path.join(root,file)
            if file_name.endswith(rule):  # 判断是否是".java"结尾
                java_file_name = os.path.basename(file_name).split(".java")[0]
                java_class_name_list = split_java_name(java_file_name)
                java_class_name_in_one_archetype+= java_class_name_list
    java_class_name_in_one_archetype = list(set(java_class_name_in_one_archetype))
    # print(list(set(java_class_name_in_one_archetype)))
    return java_class_name_in_one_archetype


def get_java_file_in_one_archrtype(path):
    current_path = os.path.join(STATIC_DIR, path)
    java_file_name_in_one_archetype = []
    for root,dirs,files in os.walk(current_path):   # os.walk获取所有的目录
        for file in files:
            file_name = os.path.join(root,file)
            if file_name.endswith(".java"):  # 判断是否是".java"结尾
                java_file_name_in_one_archetype.append(file_name)
    return java_file_name_in_one_archetype


def split_java_name(java_name):
    pattern = "[A-Z][a-z]"
    new_string = re.sub(pattern, lambda x: "_" + x.group(0), java_name)
    java_name_list = new_string.split("_")
    if java_name_list[0]:
        return java_name_list
    else:
        return java_name_list[1:]


def get_java_method(java_file_path_list):
    method_list = []
    split_method_list = []
    for java_path in java_file_path_list:
        with open(java_path, 'rt', encoding='latin1') as fin:
            content = fin.read()
        # content = re.sub('[\w\W]*package .*?;', '', content)
        # content = re.sub('".*?"', '""', content)
        # try:
        #     tree = javalang.parse.parse(content)
        #     for _, node in tree.filter(javalang.tree.MethodDeclaration):
        #         method_list.append(node.name)
        # except:
        #     return None
        current_method_list = get_methods(content)
        method_list += current_method_list
    for method_name in method_list:
        split_method_list += split_java_name(method_name)
    split_method_list = list(set(split_method_list))
    return split_method_list


def get_methods(code: str):
    try:
        code = re.sub('^\\${.+?}$', '', code, flags=re.MULTILINE)
        code = re.sub('\\${.+?}', 'test', code)
        code = re.sub('^#+.*$', '', code, flags=re.MULTILINE)
        code = re.sub('^#set.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'^(package)(.*-.*)(;)$', r'\1 test\3', code, flags=re.MULTILINE)
        code = re.sub(r'(".*)#if.*#end', r'\1test', code)
        code = re.sub(r'#if.*#end', '"test"', code)

        tree = javalang.parse.parse(code)
        return [node.name for _, node in tree.filter(javalang.tree.MethodDeclaration)]
    except:
        return []


def get_top_topic(lda_model,doc_lda):
    top = 0
    top_topic_number = 0
    for topic_item in doc_lda:
        score = topic_item[1]
        number = topic_item[0]
        if score > top:
            top = score
            top_topic_number = number
    top_topic_list = lda_model.show_topic(top_topic_number)
    top_topic_word_list = []
    for item in top_topic_list:
        top_topic_word_list.append(item[0])
    return top_topic_word_list, top


def tf_idf_model(pom_file_name_list):
    clean_word_list = get_word_list_from_pom(pom_file_name_list)
    dic = get_dic(clean_word_list)
    print("dic finish")
    basic_corpus = get_corpus(dic, clean_word_list)
    tfidf = models.TfidfModel(basic_corpus)
    get_tf_idf_words_in_all_text(dic,tfidf,clean_word_list)
    return tfidf,dic,clean_word_list,basic_corpus


def get_tf_idf_words_in_one_text(dic,  tfidf_model, text):
    top_words_dic = {}
    top_words_list = []
    doc_bow = dic.doc2bow(text)  # 文档转换成bow
    corpus_tfidf_current = tfidf_model[doc_bow]
    corpus_tfidf_current = sorted(corpus_tfidf_current, key=lambda item: item[1], reverse=True)
    id2token = dict(zip(dic.token2id.values(), dic.token2id.keys()))
    dict_len = len(text)
    index =5
    if dict_len<index:
        index = dict_len
    for i in range(index):
        top_words_dic[id2token[corpus_tfidf_current[i][0]]] = 1
        top_words_list.append(id2token[corpus_tfidf_current[i][0]])
    return top_words_dic,top_words_list,


def get_tf_idf_words_in_all_text(dic, tfidf_model, text_list):
    word_dic = {}
    i = 0
    top_words_list_all = []
    for text in text_list:
        current_word_dic,current_word_list = get_tf_idf_words_in_one_text(dic, tfidf_model, text)
        word_dic = dict(Counter(current_word_dic) + Counter(word_dic))
        top_words_list_all.append(current_word_list)
    word_dic = sorted(word_dic, key=lambda item: item[1], reverse=True)

    for item in top_words_list_all:
        i+=1
        print(i)
        print(item)
        print("---------------")
    for item in word_dic.items():
        print(item)
    return top_words_list_all, word_dic


def get_depen_plu_tfidf_in_one_pom(inner_pom_file_dir,dic,tfidf_model, text):
    inner_pom_file_dir = inner_pom_file_dir + "/pom.xml"
    current_file_dir = os.path.join(STATIC_DIR, inner_pom_file_dir)
    tfidf_words = get_tf_idf_words_in_one_text(dic, tfidf_model, text)
    dependency_list = get_item_in_one_pom(inner_pom_file_dir,"dependency", "dependencies")
    if "junit_junit" in dependency_list:
        dependency_list.remove("junit_junit")
    plugin_list = get_item_in_one_pom(inner_pom_file_dir,"plugin", "plugins")
    dependency_tfidf_words = list(tfidf_words) + dependency_list
    plugin_tfidf_words = list(tfidf_words) +  plugin_list
    return dependency_tfidf_words, plugin_tfidf_words,tfidf_words,dependency_list,plugin_list


def get_depen_plu_tfidf_in_all_pom(pom_file_name_list):
    tfidf, dic, clean_word_list, basic_corpus = tf_idf_model(pom_file_name_list)
    dependency_tfidf_words_list = []
    plugin_tfidf_words_list = []
    dependency_list_all = []
    plugin_list_all = []
    tfidf_words_all = []
    for i in range(len(pom_file_name_list)):
        dependency_tfidf_words, plugin_tfidf_words,tfidf_words,dependency_list,plugin_list = get_depen_plu_tfidf_in_one_pom(pom_file_name_list[i][0],dic,tfidf,clean_word_list[i])
        dependency_tfidf_words_list.append(dependency_tfidf_words)
        plugin_tfidf_words_list.append(plugin_tfidf_words)
        dependency_list_all += dependency_list
        plugin_list_all += plugin_list
        tfidf_words_all += tfidf_words
    return dependency_tfidf_words_list,plugin_tfidf_words_list,dependency_list_all,plugin_list_all,tfidf_words_all


def get_item_all_dict(pom_file_name_list,item_name,items_name):
    item_dict_all = {}
    item_list_all = get_item_in_all_pom(pom_file_name_list,item_name,items_name)
    item_value_list = []
    for item_list in item_list_all:
        for item in item_list:
            if item in item_dict_all.keys():
                item_dict_all[item]+=1
            else:
                item_dict_all[item] = 1
    item_dict_all=sorted(item_dict_all.items(), reverse=True, key=lambda k: k[1])
    # for value in item_dict_all.values():
    #     # print(item)
    #     item_value_list.append(value)
    # print(np.mean(item_value_list))
    # print(np.median(item_value_list))
    # print(len(item_dict_all))
    print( item_dict_all[636])
    return item_dict_all


if __name__ == "__main__":
    # num = 0
    # inherit = 0
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    # structure_info_list = get_structure_info()
    # pre_structure_info_list = pre_structure_info_list(structure_info_list)
    # write_structure_info_list_to_file(structure_info_list, POM_STRUCTURE_INFO_FILE_NAME)
    # write_structure_info_list_to_file(pre_structure_info_list, PRE_POM_STRUCTURE_INFO_FILE_NAME)

    # compare_item_add_del_in_all_pom(archetype_files_info_dict,True )

    # pom_file_name_list = get_all_pom_path(archetype_files_info_dict, True)
    # get_item_all_dict(pom_file_name_list,"dependency", "dependencies")

    pom_file_name_list = get_all_two_pom_path(archetype_files_info_dict)
    # get_all_flat_pom_tag(pom_file_name_list)
    # print(cal_item(pom_file_name_list, "dependency", "dependencies"))
    # description_in_all_pom = get_description_in_all_pom(pom_file_name_list)
    #
    # lda = build_topicmodel(pom_file_name_list, 100)
    tf_idf_model(pom_file_name_list)

    # dependency_tfidf_words_list, plugin_tfidf_words_list, dependency_list_all, plugin_list_all, tfidf_words_all = get_depen_plu_tfidf_in_all_pom(pom_file_name_list)

    # plugin_in_all_pom = get_item_in_all_pom(pom_file_name_list, "plugin", "plugins")
    # dependency_in_all_pom = get_item_in_all_pom(pom_file_name_list, "dependency", "dependencies","dependencyManagement")
    # plugin_dependency_in_all_pom = plugin_in_all_pom + dependency_in_all_pom


    # L, supportData = self_apriori(dependency_in_all_pom, 0.01)
    # for item in supportData:
    #     print(item)
    # bigRuleList = gen_rule(L, supportData, 0.5)
    # get_association_rule(dependency_in_all_pom)
    #
    # # rules_sorted = my_apriori(tag_in_all_pom,)

    # for r in bigRuleList:
    #     print(r, "\n")

    # write_list_in_list_to_file(bigRuleList, TAG_APRIORI_DIR_NAME)
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
    # print(diff_tag_dic)
    # write_dic_to_file(diff_tag_dic, VERSION_CHANGE_FILE_NAME)

    # list = [["batsà", "a"], ["b"]]
    # write_list_in_list_to_file(list, TOKEN_FILE_DIR)
