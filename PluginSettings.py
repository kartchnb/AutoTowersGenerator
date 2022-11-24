import json



class PluginSettings():

    def __init__(self, filepath=''):
        PluginSettings.__instance = self
        self._settingsDictionary = {}
        
        if filepath != '':
            self.LoadFromFile(filepath)



    def SetValue(self, setting, value)->None:
        self._settingsDictionary[setting] = value



    def GetValue(self, setting, default=''):
        try:
            return self._settingsDictionary[setting]
        except KeyError:
            return default


    
    def SaveToFile(self, filepath)->None:
        with open(filepath, 'w') as settingsFile:
            json.dump(self._settingsDictionary, settingsFile)



    def LoadFromFile(self, filepath)->None:
        try:
            # Load settings from the settings file, if it exists
            with open(filepath, 'r') as settingsFile:
                self._settingsDictionary = json.load(settingsFile)

        except FileNotFoundError:
            pass
