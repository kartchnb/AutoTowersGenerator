# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSignal, pyqtProperty

from UM.Logger import Logger

from .ModelBase import ModelBase



class TempTowerModel(ModelBase):

    # The available temp tower presets
    _presetsTable = [
        {'name': 'Temperature Tower - ABA', 'filename': 'Temperature Tower - ABA.stl', 'start temp': 260, 'temp change': -5},
        {'name': 'Temperature Tower - ABS', 'filename': 'Temperature Tower - ABS.stl', 'start temp': 250, 'temp change': -5},
        {'name': 'Temperature Tower - Nylon', 'filename': 'Temperature Tower - Nylon.stl', 'start temp': 260, 'temp change': -5},
        {'name': 'Temperature Tower - PC', 'filename': 'Temperature Tower - PC.stl', 'start temp': 310, 'temp change': -5},
        {'name': 'Temperature Tower - PETG', 'filename': 'Temperature Tower - PETG.stl', 'start temp': 250, 'temp change': -5},
        {'name': 'Temperature Tower - PLA', 'filename': 'Temperature Tower - PLA.stl', 'start temp': 220, 'temp change': -5},
        {'name': 'Temperature Tower - PLA+', 'filename': 'Temperature Tower - PLA+.stl', 'start temp': 230, 'temp change': -5},
        {'name': 'Temperature Tower - TPU', 'filename': 'Temperature Tower - TPU.stl', 'start temp': 230, 'temp change': -5},
    ]



    # Make the presets availabe to QML
    presetsModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=presetsModelChanged)
    def presetsModel(self):
        return self._presetsTable



    # The selected fan tower preset index
    _presetIndex = 0

    presetIndexChanged = pyqtSignal()

    def setPresetIndex(self, value)->None:
        self._presetIndex = int(value)
        self.presetIndexChanged.emit()

    @pyqtProperty(int, notify=presetIndexChanged, fset=setPresetIndex)
    def presetIndex(self)->int:
        return self._presetIndex
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetName(self)->str:
        try:
            return self._presetsTable[self.presetIndex]['name']
        except IndexError:
            return 'Custom'
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetFileName(self)->str:
        return self._presetsTable[self.presetIndex]['filename']
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetFilePath(self)->str:
        return self._buildStlFilePath(self.presetFileName)
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetStartTemp(self)->float:
        return self._presetsTable[self.presetIndex]['start temp']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetTempChange(self)->float:
        return self._presetsTable[self.presetIndex]['temp change']



    # The starting temperature value for the tower
    _startTemperatureStr = '220'

    startTemperatureStrChanged = pyqtSignal()
    
    def setStartTemperatureStr(self, value)->None:
        self._startTemperatureStr = value
        self.startTemperatureStrChanged.emit()

    @pyqtProperty(str, notify=startTemperatureStrChanged, fset=setStartTemperatureStr)
    def startTemperatureStr(self)->str:
        return self._startTemperatureStr

    @pyqtProperty(float, notify=startTemperatureStrChanged)
    def startTemperature(self)->float:
        return float(self.startTemperatureStr)



    # The ending temperature value for the tower
    _endTemperatureStr = '180'

    endTemperatureStrChanged = pyqtSignal()
    
    def setEndTemperatureStr(self, value)->None:
        self._endTemperatureStr = value
        self.endTemperatureStrChanged.emit()

    @pyqtProperty(str, notify=endTemperatureStrChanged, fset=setEndTemperatureStr)
    def endTemperatureStr(self)->str:
        return self._endTemperatureStr

    @pyqtProperty(float, notify=endTemperatureStrChanged)
    def endTemperature(self)->float:
        return float(self.endTemperatureStr)



    # The amount to change the temperature between tower sections
    _temperatureChangeStr = '-5'

    temperatureChangeStrChanged = pyqtSignal()
    
    def setTemperatureChangeStr(self, value)->None:
        self._temperatureChangeStr = value
        self.temperatureChangeStrChanged.emit()

    @pyqtProperty(str, notify=temperatureChangeStrChanged, fset=setTemperatureChangeStr)
    def temperatureChangeStr(self)->str:
        return self._temperatureChangeStr

    @pyqtProperty(float, notify=temperatureChangeStrChanged)
    def temperatureChange(self)->float:
        return float(self.temperatureChangeStr)



    # The label to add to the tower
    _towerLabel = ''

    towerLabelChanged = pyqtSignal()
    
    def setTowerLabel(self, value)->None:
        self._towerLabel = value
        self.towerLabelChanged.emit()

    @pyqtProperty(str, notify=towerLabelChanged, fset=setTowerLabel)
    def towerLabel(self)->str:
        return self._towerLabel



    # The description to carve up the side of the tower
    _towerDescription = 'TEMP'

    towerDescriptionChanged = pyqtSignal()
    
    def setTowerDescription(self, value)->None:
        self._towerDescription = value
        self.towerDescriptionChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionChanged, fset=setTowerDescription)
    def towerDescription(self)->str:
        return self._towerDescription
    


    def __init__(self, stlPath):
        super().__init__(stlPath=stlPath)
