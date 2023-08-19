# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSignal, pyqtProperty

from UM.Logger import Logger

from .ModelBase import ModelBase



class FanTowerModel(ModelBase):

    # The available fan tower presets
    _presetsTable = [
        {'name': 'Fan Tower - 0-100%', 'filename': 'Fan Tower - Fan 0-100.stl', 'start percent': 0, 'percent change': 20,}
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
            return self._presetsTable[self._presetIndex]['name']
        except IndexError:
            return 'Custom'
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetFileName(self)->str:
        return self._presetsTable[self._presetIndex]['filename']
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetFilePath(self)->str:
        return self._buildStlFilePath(self.presetFileName)
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetStartPercent(self)->float:
        return self._presetsTable[self._presetIndex]['start percent']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetPercentChange(self)->float:
        return self._presetsTable[self._presetIndex]['percent change']



    # The starting percent for the tower
    _startFanPercentStr = '0'

    startFanPercentStrChanged = pyqtSignal()
    
    def setstartFanPercentStr(self, value)->None:
        self._startFanPercentStr = value
        self.startFanPercentStrChanged.emit()

    @pyqtProperty(str, notify=startFanPercentStrChanged, fset=setstartFanPercentStr)
    def startFanPercentStr(self)->str:
        return self._startFanPercentStr
    
    @pyqtProperty(float, notify=startFanPercentStrChanged)
    def startFanPercent(self)->float:
        return float(self._startFanPercentStr)



    # The ending percent for the tower
    _endFanPercentStr = '100'

    endFanPercentStrChanged = pyqtSignal()
    
    def setEndFanPercentStr(self, value)->None:
        self._endFanPercentStr = value
        self.endFanPercentStrChanged.emit()

    @pyqtProperty(str, notify=endFanPercentStrChanged, fset=setEndFanPercentStr)
    def endFanPercentStr(self)->str:
        return self._endFanPercentStr

    @pyqtProperty(float, notify=endFanPercentStrChanged)
    def endFanPercent(self)->float:
        return float(self._endFanPercentStr)



    # The amount to change the percentage between tower sections
    _fanPercentChangeStr = '20'

    fanPercentChangeStrChanged = pyqtSignal()
    
    def setFanPercentChangeStr(self, value)->None:
        self._fanPercentChangeStr = value
        self.fanPercentChangeStrChanged.emit()

    @pyqtProperty(str, notify=fanPercentChangeStrChanged, fset=setFanPercentChangeStr)
    def fanPercentChangeStr(self)->str:
        return self._fanPercentChangeStr

    @pyqtProperty(float, notify=fanPercentChangeStrChanged)
    def fanPercentChange(self)->float:
        fanPercentChange = float(self._fanPercentChangeStr)
        # Ensure the sign of the fan percent change is appropriate for the starting and end percentages
        return self._correctChangeValueSign(fanPercentChange, self.startFanPercent, self.endFanPercent)



    # The label to carve at the bottom of the tower
    _towerLabel = ''

    towerLabelChanged = pyqtSignal()
    
    def setTowerLabel(self, value)->None:
        self._towerLabel = value
        self.towerLabelChanged.emit()

    @pyqtProperty(str, notify=towerLabelChanged, fset=setTowerLabel)
    def towerLabel(self)->str:
        return self._towerLabel



    # The description to carve up the side of the tower
    _towerDescription = 'FAN'

    towerDescriptionChanged = pyqtSignal()
    
    def setTowerDescription(self, value)->None:
        self._towerDescription = value
        self.towerDescriptionChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionChanged, fset=setTowerDescription)
    def towerDescription(self)->str:
        return self._towerDescription



    # Determine if the same fan value is maintained while bridges are being printed
    _maintainBridgeValue = False

    maintainBridgeValueChanged = pyqtSignal()

    def setMaintainBridgeValue(self, value)->None:
        self._maintainBridgeValue = value
        self.maintainBridgeValueChanged.emit()

    @pyqtProperty(bool, notify=maintainBridgeValueChanged, fset=setMaintainBridgeValue)
    def maintainBridgeValue(self)->bool:
        return self._maintainBridgeValue
    


    def __init__(self, stlPath):
        super().__init__(stlPath=stlPath)
