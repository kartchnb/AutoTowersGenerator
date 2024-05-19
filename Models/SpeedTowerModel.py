# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSignal, pyqtProperty

import os

from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Resources import Resources

from .ModelBase import ModelBase

Resources.addSearchPath(
    os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'),'Resources')
)  # Plugin translation file import
catalog = i18nCatalog("autotowers")

class SpeedTowerModel(ModelBase):

    # The available speed tower presets
    _presetsTable = [
        {'name': catalog.i18nc("@model", "Speed Tower - 20-100"), 'filename': 'Speed Tower - Print Speed 20-100.stl', 'start speed': '20', 'speed change': '20', 'tower type': 'Print Speed'},
        {'name': catalog.i18nc("@model", "Speed Tower - 50-150"), 'filename': 'Speed Tower - Print Speed 50-150.stl', 'start speed': '50', 'speed change': '20', 'tower type': 'Print Speed'},
        {'name': catalog.i18nc("@model", "Speed Tower - 100-200"), 'filename': 'Speed Tower - Print Speed 100-200.stl', 'start speed': '100', 'speed change': '20', 'tower type': 'Print Speed'},
    ]

    # The speed tower types that can been created
    _towerTypesTable = [
        {'ident': 'Print Speed' ,'name': catalog.i18nc("@type", "Print Speed") , 'label': 'PRINT SPEED'}, 
        {'ident': 'Acceleration' , 'name': catalog.i18nc("@type", "Acceleration") , 'label': 'ACCELERATION'}, 
        {'ident': 'Jerk' , 'name': catalog.i18nc("@type", "Jerk") , 'label': 'JERK'}, 
        {'ident': 'Junction' , 'name': catalog.i18nc("@type", "Junction") , 'label': 'JUNCTION'}, 
        {'ident': 'Marlin Linear' , 'name': catalog.i18nc("@type", "Marlin Linear") , 'label': 'MARLIN LINEAR'}, 
        {'ident': 'RepRap Pressure' , 'name': catalog.i18nc("@type", "RepRap Pressure") , 'label': 'REPRAP PRESSURE'},
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
        return self._towerTypesTable



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
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetStartSpeedStr(self)->str:
        return self._presetsTable[self.presetIndex]['start speed']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetStartSpeed(self)->float:
        return float(self.presetStartSpeedStr)
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetSpeedChangeStr(self)->str:
        return self._presetsTable[self.presetIndex]['speed change']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetSpeedChange(self)->float:
        return float(self.presetSpeedChangeStr)
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetTowerTypeName(self)->str:
        return self._presetsTable[self.presetIndex]['tower type']
    


    # The icon to display on the dialog
    dialogIconChanged = pyqtSignal()

    @pyqtProperty(str, notify=dialogIconChanged)
    def dialogIcon(self)->str:
        return 'speedtower_icon.png'



    # The selected tower type index
    _towerTypeIndex = 0

    towerTypeIndexChanged = pyqtSignal()

    def setTowerTypeIndex(self, value)->None:
        self._towerTypeIndex = int(value)
        self.towerTypeIndexChanged.emit()

    @pyqtProperty(int, notify=towerTypeIndexChanged, fset=setTowerTypeIndex)
    def towerTypeIndex(self)->int:
        # Allow the preset to override this setting
        # 5@xes Log and modification due to issue in the Code 
        if self.presetSelected:
            # Logger.log('d', f'_towerTypesTable         {self._towerTypesTable}')
            # Logger.log('d', f'_towerTypeIndex          {self._towerTypeIndex}')
            # Logger.log('d', f'presetTowerTypeName      {self.presetTowerTypeName}')
            # return next((i for i, item in enumerate(self._towerTypesTable) if item["ident"] == self.presetTowerTypeName), None)
            for i, item in enumerate(self._towerTypesTable):
                # Logger.log('d', f'Item   {item["ident"]}')
                # Logger.log('d', f'I      {i}')
                if item["ident"] == self.presetTowerTypeName:
                    return i
            return None          
        else:
            return self._towerTypeIndex
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def towerTypeName(self)->str:
        return self._towerTypesTable[self.towerTypeIndex]['ident']

    @pyqtProperty(str, notify=presetIndexChanged)
    def towerTypeLabel(self)->str:
        return self._towerTypesTable[self.towerTypeIndex]['label']
        

    # The starting speed value for the tower
    _startSpeedStr = '20'

    startSpeedStrChanged = pyqtSignal()
    
    def setStartSpeedStr(self, value)->None:
        self._startSpeedStr = value
        self.startSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startSpeedStrChanged, fset=setStartSpeedStr)
    def startSpeedStr(self)->str:
        # Allow the preset to override this setting
        if self.presetSelected:
            return self.presetStartSpeedStr
        else:
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
    
    def setSpeedChange(self, value)->None:
        self._speedChangeStr = value
        self.speedChangeStrChanged.emit()

    @pyqtProperty(str, notify=speedChangeStrChanged, fset=setSpeedChange)
    def speedChangeStr(self)->str:
        # Allow the preset to override this setting
        if self.presetSelected:
            return self.presetSpeedChangeStr
        else:
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
    _towerLabel = _towerTypesTable[0]['label']

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
