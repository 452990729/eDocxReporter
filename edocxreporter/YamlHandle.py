import yaml

def MakeDictFromYaml(file_in):
    yaml_str = open(file_in, 'r')
    yaml_dict = yaml.load(yaml_str, Loader=yaml.FullLoader)
    return yaml_dict

def MakeYamlFromDict(dict_in, file_out):
    with open(file_out, 'w') as f:
        yaml.dump(dict_in, f, allow_unicode=True)
