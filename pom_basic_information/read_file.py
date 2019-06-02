import colorsys
import sys
import json
import os
from constant import ARCHETYPE_FILES_INFO, PARENT_POM_DIR, POM_DIR, TAG_NAME_DICT_DIR, STATIC_DIR, STRUCTURE_INFO_DIR, \
    VERSION_CHANGE_DIR, DEPENDENCY_DIR, PLUGIN_DIR, DEPENDENCY_PLUGIN_DIR, TAG_DIR, TOKEN_DIR
import bs4
from bs4 import BeautifulSoup
import numpy as np
import unicodedata
# from akapriori import apriori
from pom_basic_information.my_apriori import self_apriori,gen_rule
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
import datetime
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

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
dependency_apriori_file_name = "dependency_apriori.txt"
plugin_apriori_file_name = "plugin_apriori.txt"
dependency_plugin_apriori_file_name = "dependency_plugin_apriori.txt"
tag_apriori_file_name = "tag_apriori.txt"
token_file_name = "token_file_name.txt"
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
TOKEN_FILE_DIR = os.path.join(TOKEN_DIR, token_file_name)
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


def get_submodel_path_in_one_pom(value, i,index=1):
    length = len(value)
    submodel_path_list =[]
    model_submodel_dict = {}
    if length > 1:
        if value[index]["jar"]["exist"]:
            jar_path = value[index]["jar"]["path"]
            jar_path_replace = jar_path.replace("static/output/", "")
            jar_pom_path = jar_path_replace + "/pom.xml"
            sub_model_list = value[index]["jar"]["sub_models"]
            sub_model_len = len(sub_model_list)
            if sub_model_len > 0:
                # print(jar_path)
                model_submodel_dict[jar_pom_path] = []
                submodel_list = [x for x in range(i, i+sub_model_len)]
                model_submodel_dict[jar_pom_path] = model_submodel_dict[jar_pom_path] + submodel_list
                # print(model_submodel_dict)
                i = i+sub_model_len
                # print(submodel_list)
                for sub_model in sub_model_list:
                    sub_model_path = jar_path_replace + "/" + sub_model
                    submodel_path_list.append(sub_model_path)

    return submodel_path_list, model_submodel_dict,i


def get_submodel_path_in_all_pom(archetype_files_info_dict):
    submodel_path_list_all = []
    model_submodel_dict_all = {}
    i = 0
    for key, value in archetype_files_info_dict.items():
        submodel_path_list, model_submodel_dict, i = get_submodel_path_in_one_pom(value, i)
        if len(submodel_path_list) > 0:
            submodel_path_list_all.append(submodel_path_list)
        if len( model_submodel_dict) > 0:
            model_submodel_dict_all = dict(model_submodel_dict_all, **model_submodel_dict)

    return submodel_path_list_all, model_submodel_dict_all


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


def splice_pom_dir(artifact_id, groupid, version):
    groupid_list = groupid.split(".")
    file_name0 = '='.join(groupid_list)
    file_name1 = artifact_id + '-' + version
    list = [file_name0, artifact_id, version, file_name1]
    pom_dir = '='.join(list) + ".pom"
    return pom_dir


def get_test_data(structure_info_list):
    data_outer_has_module = []
    data_outer_no_module = []
    for info_item in structure_info_list:
        if info_item["outer_pom_module_num"] == 0:
            data_outer_no_module.append(info_item["inner_pom_module_num"])
        else:
            data_outer_has_module.append(info_item["inner_pom_module_num"])
    return data_outer_has_module, data_outer_no_module


def get_item_in_one_pom(pom_file_name, item_name, items_name, items_name_plus):
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
            item_artifactId = item.find("artifactId")
            if item_groupId and item_artifactId:
                item_name = item_groupId.text + "_" + item_artifactId.text
                item_in_one_pom.append(item_name)
            # if item_groupId:
            #     item_name = item_groupId.text
            #     # if item_name =="junit":
            #     continue
            # if item_name not in item_in_one_pom:
            #     item_in_one_pom.append(item_name)

    return item_in_one_pom


def get_item_in_all_pom(pom_file_name_list, item_name, items_name, items_name_plus):
    item_in_all_pom = []
    for pom_file_name in pom_file_name_list:
        current_item_in_one_pom = get_item_in_one_pom(pom_file_name, item_name, items_name, items_name_plus)
        if len(current_item_in_one_pom) > 0:
            item_in_all_pom.append(current_item_in_one_pom)
    return item_in_all_pom


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
            dependency_raw_list = dependencies_item.find_all("dependency") + dependency_raw_list

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
            for plugin_item in plugins:
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


if __name__ == "__main__":
    # num = 0
    # inherit = 0
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    # structure_info_list = get_structure_info()
    # pre_structure_info_list = pre_structure_info_list(structure_info_list)
    # write_structure_info_list_to_file(structure_info_list, POM_STRUCTURE_INFO_FILE_NAME)
    # write_structure_info_list_to_file(pre_structure_info_list, PRE_POM_STRUCTURE_INFO_FILE_NAME)

    # y_list_all,x_list_all = compare_item_add_del_in_all_pom(archetype_files_info_dict,True )
    #
    # label_list1 = [" dependency delete", " dependency add"]
    # draw_digram (x_list_all,y_list_all,label_list1)

    # pom_file_name_list = get_all_pom_path(archetype_files_info_dict, False)
    # pom_file_name_list = get_all_two_pom_path(archetype_files_info_dict)
    # i =1
    # for file in pom_file_name_list :
    #     print(i)
    #     i += 1
    #     print(file)
    #     print("--------------")
    # get_item_all_dict(pom_file_name_list,"dependency", "dependencies")


    # flat_pom_list_all = get_all_flat_pom_list(pom_file_name_list)
    # jersey_version_list_all = get_all_jersey_time_version(archetype_files_info_dict)
    # x1_list_all, y1_list_all, label1_list, x2_list_all, y2_list_all, label2_list = get_digram_data(
    #     jersey_version_list_all)
    # draw_jersey_version_digram(x1_list_all,y1_list_all, label1_list)
    # print(cal_item(pom_file_name_list, "dependency", "dependencies"))
    # description_in_all_pom = get_description_in_all_pom(pom_file_name_list)
    #
    # lda = build_topicmodel(pom_file_name_list, 100)
    # tf_idf_model(pom_file_name_list)

    # dependency_tfidf_words_list, plugin_tfidf_words_list, dependency_list_all, plugin_list_all, tfidf_words_all = get_depen_plu_tfidf_in_all_pom(pom_file_name_list)

    # plugin_in_all_pom = get_item_in_all_pom(pom_file_name_list, "plugin", "plugins","pluginManagement")
    # dependency_in_all_pom = get_item_in_all_pom(pom_file_name_list, "dependency", "dependencies","dependencyManagement")
    # plugin_dependency_in_all_pom = plugin_in_all_pom + dependency_in_all_pom

    # L, supportData = self_apriori(flat_pom_list_all,0.01)
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
    # submodel_path_list_all, model_submodel_dict_all = get_submodel_path_in_all_pom(archetype_files_info_dict)
    # for key,value in model_submodel_dict_all.items():
    #     print(value)
    # submodel_text_all, submodel_text_all2 = get_submodel_text(submodel_path_list_all)
    # for index in  range(len(submodel_text_all2)):
    #     print(index)
    #     print(submodel_text_all2[index])
    # get_submodel_tf_idf(submodel_text_all2, model_submodel_dict_all)


