import os
from bs4 import BeautifulSoup
import re
import string
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from gensim.models.ldamodel import LdaModel
from nltk.stem import WordNetLemmatizer
from collections import Counter
import javalang

from pom_basic_information.read_file import get_all_two_pom_path, TOKEN_FILE_DIR, get_item_in_one_pom, get_item_in_all_pom
from pom_basic_information.write_file import write_list_in_list_to_file
from constant import STATIC_DIR

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
            if len(name) > 0:
                name = name[0].text
                return str(description) + " " + str(name)
    return description


def get_description_in_all_pom(pom_file_name_list):
    description_in_all_pom = []
    name_in_all_pom = []
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
        # current_java_class_name_list = get_java_class_in_one_archetype(pom_file_name[0])
        # current_java_file_list = get_java_file_in_one_archrtype(pom_file_name[0])
        # current_java_method_list = get_java_method(current_java_file_list)
        # if len(current_java_method_list) == 0:
        #     i += 1

        # text_in_all_pom.append([current_description_in_one_pom, current_java_class_name_list, current_java_method_list])
        text_in_all_pom.append([current_description_in_one_pom])
    print(i)
    print("get text finish")
    return text_in_all_pom


def tokenize(text_list):
    i = 0
    word_list = []
    del_list = ["archetype", "project", "maven", "java", "something", "module", "create", "template", "compare",
                "point", "entry", "execute", "set", "get", "main", "use", "controller", "hello", "none"]
    for text in text_list:
        i += 1
        # print(i)
        description = text[0]
        # java_class_name = text[1]
        # java_method_name = text[2]
        if description:
            # description = "".join([ch for ch in description if ch not in string.punctuation])
            description_tokenize = word_tokenize(description)
            description_tokenize = [ch for ch in description_tokenize if ch not in string.punctuation]
        else:
            description_tokenize = []
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
        # text_word = list(set(description_tokenize + java_class_name + java_method_name))
        text_word = description_tokenize
        text_word = get_filter_word_list(text_word, [])
        text_word = list(set(text_word))
        word_list.append(text_word)
    print("tokenize finish")
    write_list_in_list_to_file(word_list, TOKEN_FILE_DIR)
    return word_list


def get_dic(word_list):
    return corpora.Dictionary(word_list)


def add_dic(dic, add_word_list):
    dic.add_documents(add_word_list, prune_at=2000000)
    return dic


def get_clean_word_list(word_list):
    clean_word_list = []
    for words in word_list:
        clean_word_list.append(
            [w.lower() for w in words if w.lower() not in stopwords.words('english') and w.isdigit() == False])
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


def get_filter_word_list(word_list, del_word_list):
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
    # description_list = []
    # name_list = []
    # java_class_list = []
    # java_method_list = []
    # for text in text_list:
    #     description_list.append(text[0])
    #     name_list.append(text[1])
    #     java_class_list = text[2]
    #     java_method_list = text[3]
    # tokenize_list = tokenize(description_list,name_list,java_class_list, java_method_list)
    tokenize_list = tokenize(text_list)
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
    # for i in range(topic_num):
    #     print(i)
    #     print(lda.show_topic(i))
    #     print("-------------------")
    show_text_topic(lda, dic, clean_word_list[1500:])
    return lda


def show_text_topic(lda_model, dic, text_list):
    i = 1500
    for text in text_list:
        i += 1
        print(i)
        doc_bow = dic.doc2bow(text)  # 文档转换成bow
        doc_lda = lda_model[doc_bow]
        print(doc_lda)
        for topic in doc_lda:
            print("%s\t%f\n" % (lda_model.print_topic(topic[0]), topic[1]))
        print(get_top_topic(lda_model, doc_lda))


def get_java_class_in_one_archetype(path, rule=".java"):
    current_path = os.path.join(STATIC_DIR, path)
    java_class_name_in_one_archetype = []
    for root, dirs, files in os.walk(current_path):  # os.walk获取所有的目录
        for file in files:
            file_name = os.path.join(root, file)
            if file_name.endswith(rule):  # 判断是否是".java"结尾
                java_file_name = os.path.basename(file_name).split(".java")[0]
                java_class_name_list = split_java_name(java_file_name)
                java_class_name_in_one_archetype += java_class_name_list
    java_class_name_in_one_archetype = list(set(java_class_name_in_one_archetype))
    # print(list(set(java_class_name_in_one_archetype)))
    return java_class_name_in_one_archetype


def get_java_file_in_one_archrtype(path):
    current_path = os.path.join(STATIC_DIR, path)
    java_file_name_in_one_archetype = []
    for root, dirs, files in os.walk(current_path):  # os.walk获取所有的目录
        for file in files:
            file_name = os.path.join(root, file)
            if file_name.endswith(".java"):  # 判断是否是".java"结尾
                java_file_name_in_one_archetype.append(file_name)
    return java_file_name_in_one_archetype


def split_java_name(java_name):
    pattern = "[A-Z][a-z]"
    new_string = re.sub(pattern, lambda x: "_" + x.group(0), java_name)
    java_name_list = new_string.split("_")
    java_name_list = [name for name in java_name_list if name != ""]
    return java_name_list


def get_java_method(java_file_path_list):
    method_list = []
    split_method_list = []
    for java_path in java_file_path_list:
        if os.path.isfile(java_path):
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


def get_top_topic(lda_model, doc_lda):
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
    return tfidf, dic, clean_word_list, basic_corpus


def get_tf_idf_words_in_one_text(dic, tfidf_model, text):
    top_words_dic = {}
    top_words_list = []
    doc_bow = dic.doc2bow(text)  # 文档转换成bow
    corpus_tfidf_current = tfidf_model[doc_bow]
    corpus_tfidf_current = sorted(corpus_tfidf_current, key=lambda item: item[1], reverse=True)
    id2token = dict(zip(dic.token2id.values(), dic.token2id.keys()))
    dict_len = len(text)
    index = 5
    if dict_len < index:
        index = dict_len
    for i in range(index):
        top_words_dic[id2token[corpus_tfidf_current[i][0]]] = 1
        top_words_list.append(id2token[corpus_tfidf_current[i][0]])
    return top_words_dic, top_words_list,


def get_tf_idf_words_in_all_text(dic, tfidf_model, text_list, model_submodel_index_dict = {}):
    word_dic = {}
    i = 0
    top_words_list_all = []
    if len(model_submodel_index_dict) > 0:
        for key,value in model_submodel_index_dict.items():
            model = key
            text_index_list = value
            print(model)
            for index in text_index_list:
                text = text_list[index]
                current_word_dic, current_word_list = get_tf_idf_words_in_one_text(dic, tfidf_model, text)
                word_dic = dict(Counter(current_word_dic) + Counter(word_dic))
                top_words_list_all.append(current_word_list)
                print(current_word_list)
            print("------------------")
    else:
        for text in text_list:
            current_word_dic, current_word_list = get_tf_idf_words_in_one_text(dic, tfidf_model, text)
            word_dic = dict(Counter(current_word_dic) + Counter(word_dic))
            top_words_list_all.append(current_word_list)
    # print(word_dic)
    word_items = sorted(word_dic.items(), key=lambda item: item[1], reverse=True)

    for item in top_words_list_all:
        i+=1
        print(i)
        print(item)
        print("---------------")
    for item in word_items:
        print(item)
    return top_words_list_all, word_items


def get_depen_plu_tfidf_in_one_pom(inner_pom_file_dir, dic, tfidf_model, text):
    inner_pom_file_dir = inner_pom_file_dir + "/pom.xml"
    current_file_dir = os.path.join(STATIC_DIR, inner_pom_file_dir)
    top_words_dic, tfidf_words_list = get_tf_idf_words_in_one_text(dic, tfidf_model, text)
    dependency_list = get_item_in_one_pom(inner_pom_file_dir, "dependency", "dependencies", "dependencyManagement")
    # if "junit_junit" in dependency_list:
    #     dependency_list.remove("junit_junit")
    plugin_list = get_item_in_one_pom(inner_pom_file_dir, "plugin", "plugins", "pluginManagement")
    dependency_tfidf_words = list(tfidf_words_list) + dependency_list
    plugin_tfidf_words = list(tfidf_words_list) + plugin_list
    return dependency_tfidf_words, plugin_tfidf_words, tfidf_words_list, dependency_list, plugin_list


def get_depen_plu_tfidf_in_all_pom(pom_file_name_list):
    tfidf, dic, clean_word_list, basic_corpus = tf_idf_model(pom_file_name_list)
    dependency_tfidf_words_list = []
    plugin_tfidf_words_list = []
    dependency_list_all = []
    plugin_list_all = []
    tfidf_words_all = []
    for i in range(len(pom_file_name_list)):
        dependency_tfidf_words, plugin_tfidf_words, tfidf_words, dependency_list, plugin_list = get_depen_plu_tfidf_in_one_pom(
            pom_file_name_list[i][0], dic, tfidf, clean_word_list[i])
        dependency_tfidf_words_list.append(dependency_tfidf_words)
        plugin_tfidf_words_list.append(plugin_tfidf_words)
        dependency_list_all += dependency_list
        plugin_list_all += plugin_list
        tfidf_words_all += tfidf_words
    return dependency_tfidf_words_list, plugin_tfidf_words_list, dependency_list_all, plugin_list_all, tfidf_words_all


def get_item_all_dict(pom_file_name_list, item_name, items_name):
    item_dict_all = {}
    item_list_all = get_item_in_all_pom(pom_file_name_list, item_name, items_name)
    item_value_list = []
    for item_list in item_list_all:
        for item in item_list:
            if item in item_dict_all.keys():
                item_dict_all[item] += 1
            else:
                item_dict_all[item] = 1
    item_dict_all = sorted(item_dict_all.items(), reverse=True, key=lambda k: k[1])
    # for value in item_dict_all.values():
    #     # print(item)
    #     item_value_list.append(value)
    # print(np.mean(item_value_list))
    # print(np.median(item_value_list))
    # print(len(item_dict_all))
    print(item_dict_all[636])
    return item_dict_all


def get_submodel_text(submodel_path_list_all):
    submodel_text_all = []
    submodel_text_all2= []
    for submodel_path_list in submodel_path_list_all:
        submodel_text_list = []
        for submodel_path in submodel_path_list:
            java_class = get_java_class_in_one_archetype(submodel_path)
            java_method = get_java_method(submodel_path)
            submodel_text = java_class+java_method
            submodel_text_list.append(submodel_text)
            submodel_text_all2.append(submodel_text)
        submodel_text_all.append(submodel_text_list)
    print(len(submodel_text_all))
    return submodel_text_all, submodel_text_all2


def get_submodel_tf_idf(submodel_text_all2, model_submodel_dict_all,archetype_files_info_dict):
    pom_file_name_list = get_all_two_pom_path(archetype_files_info_dict)
    clean_word_list = get_word_list_from_pom(pom_file_name_list)
    dic = get_dic(clean_word_list)

    submodel_text_all2_clean_words = get_clean_word_list(submodel_text_all2)
    submodel_text_all2_filter_words = [list(set(get_filter_word_list(clean_words,[]))) for clean_words in  submodel_text_all2_clean_words]
    print(len(submodel_text_all2_filter_words))
    # dic2= get_dic(submodel_text_all2_filter_words)
    #
    # transformer = dic.merge_with(dic2)
    # print("dic finish")
    #
    #
    # basic_corpus = get_corpus(dic, submodel_text_all2_filter_words)
    # tfidf = models.TfidfModel(basic_corpus)
    # get_tf_idf_words_in_all_text(dic, tfidf,  submodel_text_all2_filter_words, model_submodel_dict_all)
    # return tfidf, dic,  submodel_text_all2_filter_words, basic_corpus
