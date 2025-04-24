def get_parameter_path(dictionary, path, path_list):
    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            child_path = path.copy()
            child_path.append(key)
            get_parameter_path(dictionary[key], child_path, path_list)
        elif isinstance(dictionary[key], list):
            for i in range(len(dictionary[key])):
                child_path = path.copy()
                child_path.append(key)
                child_path.append(i)
                path_list.append(child_path)
        else:
            child_path = path.copy()
            child_path.append(key)
            path_list.append(child_path)

dictionary = {
    "1": {
        "11": {
            "111": [3,4,5],
            "112": "112a"
        },
        "12" :{
            "121": "121a",
            "122": [1,2,3]
        }
    },
    "2": {
        "21": "21a",
        "22" :{
            "221": "221a",
            "222": "222a"
        }
    }
}

def get_parameter_value(dictionary, path):
    dictionary_copy = dictionary.copy()
    for key in path:
        dictionary = dictionary[key]
    return dictionary


path_list = []
path = []
get_parameter_path(dictionary, [], path_list)
# print(path_list)
for path in path_list:
    print((path, get_parameter_value(dictionary, path)))