import json

class F1Config:

    def __init__(self):
        self._values = {}

    def _load_values(self, data: any, parent_path=""):
        """ 
        Load config values from json recursively, make them
        addressable like unix files
        """

        if type(data) is dict:
            for key in data.keys():
                self._load_values(data[key], parent_path + "/" + str(key))
        else:
            self._values[parent_path] = data
    
    def get(self, value_path:str, default: any=None) -> any:
        """
        Returns the value for given key, or default value if it does not exist
        """

        return self._values.get(value_path, default)

    
    def _load_from_file(self, filename):
        """
        Loads values from given config file
        """

        try:
            with open(filename, "r") as config_file:
                data = json.loads(config_file.read())
            self._load_values(data)
        except IOError as err:
            print(err)


# Global config file object
CONFIG = F1Config()
CONFIG._load_from_file("config.json")

config_files = CONFIG.get("/configFiles")
if type(config_files) is list:
    for config_file in config_files:
        CONFIG._load_from_file(config_file)
del(config_files)

CONFIG._load_from_file("private_config.json")
