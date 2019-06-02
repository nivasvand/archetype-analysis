import os
from bs4 import BeautifulSoup
import bs4
from collections import Counter
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from constant import STATIC_DIR


def extract_all(pom, tag_name):
    for item in pom.find_all(tag_name):
        item.extract()


def flat_pom(soup):
    flat_pom_list = []
    pom = soup.project
    # print(dependencies)
    # print(plugins)
    if pom:
        # extract_all(pom, 'dependencies')
        # extract_all(pom, 'plugins')
        # if pom.find("dependencies"):
        #     print("error dependencies")
        #     # print(pom)
        # if pom.find("plugins"):
        #     print("error plugins")
        #     # print(pom, "\n")
        for child in pom.descendants:
            tag_name = ""
            if type(child) == bs4.element.NavigableString and child.encode("utf-8") != b"\n":
                for current_parent in child.parents:
                    if current_parent and current_parent.parent:
                        tag_name = tag_name + "_" + current_parent.name
                # flat_pom_list.append((tag_name, child.encode("utf-8")))
                if tag_name not in flat_pom_list:
                    flat_pom_list.append(tag_name)
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
                    if tag_name in flat_pom_dict.keys():
                        flat_pom_dict[tag_name] += 1
                    else:
                        flat_pom_dict[tag_name] = 1
        return flat_pom_dict


def get_all_flat_pom_tag(pom_file_name_list):
    flat_pom_dic_all = {}
    for pom_path in pom_file_name_list:
        new_flat_pom_dict = flat_pom_tag(pom_path)
        flat_pom_dic_all = dict(Counter(new_flat_pom_dict) + Counter(flat_pom_dic_all))
    flat_pom_dic_all = sorted(flat_pom_dic_all.items(), reverse=True, key=lambda k: k[1])
    for tag_name in flat_pom_dic_all:
        print(tag_name)
    return flat_pom_dic_all


def get_all_flat_pom_list(pom_file_name_list):
    flat_pom_list_all = []
    for pom_path in pom_file_name_list:
        pom_file_dir = os.path.join(STATIC_DIR, pom_path)
        if os.path.isfile(pom_file_dir):
            soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
            current_flat_pom_list = flat_pom(soup)
            for tag in current_flat_pom_list:
                one_tag_list = tag.split("_")
                if "" in one_tag_list:
                    one_tag_list.remove("")
                if "project" in one_tag_list:
                    one_tag_list.remove("project")
                flat_pom_list_all.append(one_tag_list)
    return flat_pom_list_all