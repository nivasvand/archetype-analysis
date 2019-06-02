import os
from bs4 import BeautifulSoup
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from constant import  STATIC_DIR


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


def get_tag_in_one_pom(pom_file_name):
    drop_list = ["artifactId", "version", "groupId", "packaging", "modelVersion", "name", "project", "url",
                 "organization", "description", "scm", "parent"]
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


