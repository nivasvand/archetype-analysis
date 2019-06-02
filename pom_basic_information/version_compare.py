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

from pom_basic_information.draw_figures import get_pom_date
from pom_basic_information.pom_flat_tag import flat_pom
from pom_basic_information.read_file import filter_pom_version, get_dependency_list, get_plugin_list

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


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
    dependency_del_time_list = []
    dependency_add_time_list = []

    plugin_comapre_list = []
    plugin_del_dict_all = []
    plugin_add_dict_all = []
    plugin_del_num_list = []
    plugin_del_time_list =[]
    plugin_add_num_list = []
    plugin_add_time_list = []
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
                    dependency_list1 = get_dependency_list(pom1_file_dir)
                    dependency_list2 = get_dependency_list(pom2_file_dir)
                    if dependency_list1 and dependency_list2 and len(dependency_list1) != 0 and len(dependency_list2) !=0:
                        num += 1
                        if num % 100 == 0:
                            print(num, "\n")
                        dependency_del_list, dependency_del_num, dependency_add_list, dependency_add_num = compare_item_add_del(dependency_list1, dependency_list2)
                    # # if dependency_del_num > 0 and dependency_add_num > 0 :
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
                        if dependency_del_num > 0:
                            dependency_del_num_list.append(dependency_del_num)
                            current_del_time = get_pom_date(pom2_path)
                            dependency_del_time_list.append(current_del_time)

                        if  dependency_add_num > 0:
                            dependency_add_num_list.append(dependency_add_num)
                            current_add_time = get_pom_date(pom2_path)
                            dependency_add_time_list.append(current_add_time)

                    # if "junit_junit" in dependency_del_list:
                    #     print(pom1_file_dir, "    ", pom2_file_dir)
                    #     print(pre_dependency_del_list, "\n", pre_dependency_add_list)

                    # plugin_list1 = get_plugin_list(pom1_file_dir)
                    # plugin_list2 = get_plugin_list(pom2_file_dir)
                    # if plugin_list1 and plugin_list2 and len(plugin_list1) != 0 and len(plugin_list2) != 0:
                    #     num += 1
                    #     if num % 100 == 0:
                    #         print(num, "\n")
                    #     plugin_del_list, plugin_del_num, plugin_add_list, plugin_add_num = compare_item_add_del(
                    #         plugin_list1, plugin_list2)
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
                        #     current_del_time = get_pom_date(pom2_path)
                        #     plugin_del_time_list.append(current_del_time)
                        # plugin_add_dict_all = dict(Counter(plugin_add_dict_all) + Counter(plugin_add_list))
                        # if plugin_add_num > 0:
                        #     plugin_add_num_list.append(plugin_add_num)
                        #     current_add_time = get_pom_date(pom2_path)
                        #     plugin_add_time_list.append(current_add_time)
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
    # print("plugin add")
    # for item in plugin_add_dict_all:
    #     print(item)
    # print(np.median(plugin_add_num_list))
    # print(np.mean(plugin_add_num_list))
    # print(add_del)
    # print(del_num)
    # print(add_num)
    # print(sum_equ)
    # return [ plugin_del_num_list, plugin_add_num_list],[plugin_del_time_list,plugin_add_time_list]
    return [dependency_del_num_list,  dependency_add_num_list], [dependency_del_time_list, dependency_add_time_list]


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