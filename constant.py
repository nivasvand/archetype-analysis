import os

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
POM_DIR = os.path.join(STATIC_DIR, 'pom')
PARENT_POM_DIR = os.path.join(STATIC_DIR, 'parent_pom')
UNJAR_DIR = os.path.join(STATIC_DIR, 'unjar')
ARCHETYPE_FILES_INFO = os.path.join(STATIC_DIR, 'archetype_files_info.json')
OUT_DIR = os.path.join(STATIC_DIR, 'out')
TAG_NAME_DICT_DIR = os.path.join(OUT_DIR, 'tag_name_dict')
STRUCTURE_INFO_DIR = os.path.join(OUT_DIR, 'structure_info')
VERSION_CHANGE_DIR = os.path.join(OUT_DIR, 'version_change')