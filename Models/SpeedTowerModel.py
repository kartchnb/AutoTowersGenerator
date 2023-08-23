# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSignal, pyqtProperty

from UM.Logger import Logger

from .ModelBase import ModelBase



class SpeedTowerModel(ModelBase):

    # The available speed tower presets
    _presetsTable = [
        {'name': 'Speed Tower - Print Speed 20-100', 'filename': 'Speed Tower - Print Speed 20-100.stl', 'start speed': 20, 'speed change': 20, 'tower type': 'Print Speed'},
        {'name': 'Speed Tower - Print Speed 50-150', 'filename': 'Speed Tower - Print Speed 50-150.stl', 'start speed': 50, 'speed change': 20, 'tower type': 'Print Speed'},
        {'name': 'Speed Tower - Print Speed 100-200', 'filename': 'Speed Tower - Print Speed 100-200.stl', 'start speed': 100, 'speed change': 20, 'tower type': 'Print Speed'},
    ]

    # The speed tower types that can been created
    _towerTypesModel = [
        {'name': 'Print Speed', 'label': 'PRINT SPEED'}, 
        {'name': 'Acceleration', 'label': 'ACCELERATION'}, 
        {'name': 'Jerk', 'label': 'JERK'}, 
        {'name': 'Junction', 'label': 'JUNCTION'}, 
        {'name': 'Marlin Linear', 'label': 'MARLIN LINEAR'}, 
        {'name': 'RepRap Pressure', 'label': 'REPRAP PRESSURE'},
    ]



    # Make the presets availabe to QML
    presetsModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=presetsModelChanged)
    def presetsModel(self):
        return self._presetsTable



    # Make the tower types availabe to QML
    towerTypesModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=towerTypesModelChanged)
    def towerTypesModel(self):
        return self._towerTypesModel



    # The selected speed tower preset index
    _presetIndex = 0

    presetIndexChanged = pyqtSignal()

    def setPresetIndex(self, value)->None:
        self._presetIndex = int(value)
        self.presetIndexChanged.emit()

    @pyqtProperty(int, notify=presetIndexChanged, fset=setPresetIndex)
    def presetIndex(self)->int:
        return self._presetIndex
    
    @pyqtProperty(bool, notify=presetIndexChanged)
    def presetSelected(self)->bool:
        return self._presetIndex < len(self._presetsTable)
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetName(self)->str:
        return self._presetsTable[self.presetIndex]['name']
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetFileName(self)->str:
        return self._presetsTable[self.presetIndex]['filename']
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetFilePath(self)->str:
        return self._buildStlFilePath(self.presetFileName)
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetStartPercent(self)->float:
        return self._presetsTable[self.presetIndex]['start percent']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetPercentChange(self)->float:
        return self._presetsTable[self.presetIndex]['percent change']
    


    # The icon to display on the dialog
    dialogIconChanged = pyqtSignal()

    @pyqtProperty(str, notify=dialogIconChanged)
    def dialogIcon(self)->str:
        return 'speedtower_icon.png'



    # The selected tower type index
    _towerTypeIndex = 0

    towerTypeIndexChanged = pyqtSignal()

    def setTowerTypeIndex(self, value)->None:
        newTowerTypeIndex = int(value)

        # The goal here is to keep the tower label in sync with the selected tower type unless the user has manually changed the label
        # Only update the tower label if it matches the name of the currently selected tower type
        if self._towerLabel == self._towerTypesModel[self._towerTypeIndex]['label']:
            # Update the tower label to match the newly-selected tower type
            self.setTowerLabel(self._towerTypesModel[newTowerTypeIndex]['label'])

        # Now, actually update the tower type index
        self._towerTypeIndex = newTowerTypeIndex
        self.towerTypeIndexChanged.emit()

    @pyqtProperty(int, notify=towerTypeIndexChanged, fset=setTowerTypeIndex)
    def towerTypeIndex(self)->int:
        return self._towerTypeIndex
    
    @pyqtProperty(str, notify=towerTypeIndexChanged)
    def towerTypeName(self)->str:
        try:
            return self._towerTypesModel[self.towerTypeIndex]['name']
        except IndexError:
            return 'Custom'

    @pyqtProperty(str, notify=towerTypeIndexChanged)
    def towerTypeFilename(self)->str:
        return self._presetsTable[self._towerTypesModel]['filename']

    @pyqtProperty(str, notify=towerTypeIndexChanged)
    def towerTypeFilePath(self)->str:
        return self._buildStlFilePath(self.towerTypeFilename)

    @pyqtProperty(float, notify=towerTypeIndexChanged)
    def towerTypeStartValue(self)->float:
        return float(self._presetsTable[self._towerTypesModel]['start value'])

    @pyqtProperty(float, notify=towerTypeIndexChanged)
    def towerTypeValueChange(self)->float:
        return float(self._presetsTable[self._towerTypesModel]['value change'])

    @pyqtProperty(str, notify=towerTypeIndexChanged)
    def towerTypeTowerType(self)->str:
        return self._presetsTable[self._towerTypesModel]['tower type']



    # The starting speed value for the tower
    _startSpeedStr = '20'

    startSpeedStrChanged = pyqtSignal()
    
    def setStartSpeedStr(self, value)->None:
        self._startSpeedStr = value
        self.startSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startSpeedStrChanged, fset=setStartSpeedStr)
    def startSpeedStr(self)->str:
        return self._startSpeedStr

    @pyqtProperty(float, notify=startSpeedStrChanged)
    def startSpeed(self)->float:
        return float(self.startSpeedStr)



    # The ending speed value for the tower
    _endSpeedStr = '100'

    endSpeedStrChanged = pyqtSignal()
    
    def setEndSpeedStr(self, value)->None:
        self._endSpeedStr = value
        self.endSpeedStrChanged.emit()

    @pyqtProperty(str, notify=endSpeedStrChanged, fset=setEndSpeedStr)
    def endSpeedStr(self)->str:
        return self._endSpeedStr

    @pyqtProperty(float, notify=endSpeedStrChanged)
    def endSpeed(self)->float:
        return float(self.endSpeedStr)



    # The amount to change the speed between tower sections
    _speedChangeStr = '20'

    speedChangeStrChanged = pyqtSignal()
    
    def setSpeedChangeStr(self, value)->None:
        self._speedChangeStr = value
        self.speedChangeStrChanged.emit()

    @pyqtProperty(str, notify=speedChangeStrChanged, fset=setSpeedChangeStr)
    def speedChangeStr(self)->str:
        return self._speedChangeStr

    @pyqtProperty(float, notify=speedChangeStrChanged)
    def speedChange(self)->float:
        return float(self.speedChangeStr)



    # The length of each of the tower wings
    _wingLengthStr = '50'

    wingLengthStrChanged = pyqtSignal()

    def setWingLengthStr(self, value)->None:
        self._wingLengthStr = value
        self.wingLengthStrChanged.emit()

    @pyqtProperty(str, notify=wingLengthStrChanged, fset=setWingLengthStr)
    def wingLengthStr(self)->str:
        return self._wingLengthStr

    @pyqtProperty(float, notify=wingLengthStrChanged)
    def wingLength(self)->float:
        return float(self.wingLengthStr)



    # The label to add to the tower
    _towerLabel = _towerTypesModel[0]['label']

    towerLabelChanged = pyqtSignal()
    
    def setTowerLabel(self, value)->None:
        self._towerLabel = value
        self.towerLabelChanged.emit()

    @pyqtProperty(str, notify=towerLabelChanged, fset=setTowerLabel)
    def towerLabel(self)->str:
        return self._towerLabel



    # The a description to add to the tower
    _towerDescription = ''

    towerDescriptionChanged = pyqtSignal()
    
    def setTowerDescription(self, value)->None:
        self._towerDescription = value
        self.towerDescriptionChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionChanged, fset=setTowerDescription)
    def towerDescription(self)->str:
        return self._towerDescription
    


    def __init__(self, stlDir):
        super().__init__(stlDir=stlDir)
