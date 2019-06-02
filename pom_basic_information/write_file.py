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


def write_double_list_to_file(double_list, write_file_dir):
    file_object = open(write_file_dir, 'w', encoding='utf-8')
    for item_list in double_list:
        item_list_str = " ".join([str(item) for item in item_list])
        file_object.write(item_list_str)
        file_object.write("\n")
    file_object.close()


def write_tag_name_dict_to_file(tag_name_dict_sorted_list, write_file_dir):
    file_object = open(write_file_dir, 'w')
    for tuple_item in tag_name_dict_sorted_list:
        file_object.write(tuple_item[0])
        file_object.write("   ")
        file_object.write(str(tuple_item[1]))
        file_object.write('\n')
    file_object.close()


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