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

class RetractTowerModel(ModelBase):

    # The available retract tower presets
    _presetsTable = [
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Distance 0.4-1.2") , 'filename': 'Retract Tower - Retract Distance 0.4-1.2.stl', 'start value': '0.4', 'value change': '0.1', 'tower type': 'Distance'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Distance 1.2-2.0") , 'filename': 'Retract Tower - Retract Distance 1.2-2.0.stl', 'start value': '1.2', 'value change': '0.1', 'tower type': 'Distance'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Distance 1-6") , 'filename': 'Retract Tower - Retract Distance 1-6.stl', 'start value': '1', 'value change': '1', 'tower type': 'Distance'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Distance 4-9") , 'filename': 'Retract Tower - Retract Distance 4-9.stl', 'start value': '4', 'value change': '1', 'tower type': 'Distance'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Distance 7-12") , 'filename': 'Retract Tower - Retract Distance 7-12.stl', 'start value': '7', 'value change': '1', 'tower type': 'Distance'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Speed 10-50") , 'filename': 'Retract Tower - Retract Speed 10-50.stl', 'start value': '10', 'value change': '10', 'tower type': 'Speed'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Speed 35-75") , 'filename': 'Retract Tower - Retract Speed 35-75.stl', 'start value': '35', 'value change': '10', 'tower type': 'Speed'},
        {'name': catalog.i18nc("@model", "Retract Tower - Retract Speed 60-100") , 'filename': 'Retract Tower - Retract Speed 60-100.stl', 'start value': '60', 'value change': '10', 'tower type': 'Speed'},
    ]
 
    _towerTypesTable = [
        {'ident': 'Distance' ,'name': catalog.i18nc("@type","Distance") , 'label': 'DST'}, 
        {'ident': 'Speed' ,'name': catalog.i18nc("@type","Speed") , 'label': 'SPD'}, 
    ]

    # Make the presets availabe to QML
    presetsModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=presetsModelChanged)
    def presetsModel(self):
        return self._presetsTable



    # Make the tower types available to QML
    towerTypesModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=towerTypesModelChanged)
    def towerTypesModel(self):
        return self._towerTypesTable



    # The selected retract tower preset index
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
    def presetStartValueStr(self)->str:
        return self._presetsTable[self.presetIndex]['start value']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetStartValue(self)->float:
        return float(self.presetStartValueStr)
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetValueChangeStr(self)->str:
        return self._presetsTable[self.presetIndex]['value change']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetValueChange(self)->float:
        return float(self.presetValueChangeStr)
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetTowerTypeName(self)->str:
        return self._presetsTable[self.presetIndex]['tower type']
    


    # The icon to display on the dialog
    dialogIconChanged = pyqtSignal()

    @pyqtProperty(str, notify=dialogIconChanged)
    def dialogIcon(self)->str:
        return 'retracttower_icon.png'
    


    # The tower type index
    _towerTypeIndex = 0

    towerTypeIndexChanged = pyqtSignal()

    def setTowerTypeIndex(self, value)->None:
        self._towerTypeIndex = int(value)
        self.towerTypeIndexChanged.emit()

    @pyqtProperty(int, notify=towerTypeIndexChanged, fset=setTowerTypeIndex)
    def towerTypeIndex(self)->int:
        # Allow the preset to override this setting
        if self.presetSelected:
            return next((i for i, item in enumerate(self._towerTypesTable) if item["name"] == self.presetTowerTypeName), None)
        else:
            return self._towerTypeIndex
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def towerTypeName(self)->str:
        return self._towerTypesTable[self.towerTypeIndex]['ident']
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def towerTypeLabel(self)->str:
        return self._towerTypesTable[self.towerTypeIndex]['label']



    # The start retraction value for the tower
    _startValueStr = '1'

    startValueStrChanged = pyqtSignal()

    def setStartValueStr(self, value)->None:
        self._startValueStr = value
        self.startValueStrChanged.emit()

    @pyqtProperty(str, notify=startValueStrChanged, fset=setStartValueStr)
    def startValueStr(self)->str:
        # Allow the preset to override this setting
        if self.presetSelected:
            return self.presetStartValueStr
        else:
            return self._startValueStr
    
    @pyqtProperty(float, notify=startValueStrChanged)
    def startValue(self)->float:
        return float(self.startValueStr)
    


    # The ending retraction value for the tower
    _endValueStr = '6'
    
    endValueStrChanged = pyqtSignal()

    def setEndValueStr(self, value)->None:
        self._endValueStr = value
        self.endValueStrChanged.emit()

    @pyqtProperty(str, notify=endValueStrChanged, fset=setEndValueStr)
    def endValueStr(self)->str:
        return self._endValueStr

    @pyqtProperty(float, notify=endValueStrChanged)
    def endValue(self)->float:
        return float(self.endValueStr)
    


    # The amount to change the retraction value between tower sections
    _valueChangeStr = '1'

    valueChangeStrChanged = pyqtSignal()

    def setValueChangeStr(self, value)->None:
        self._valueChangeStr = value
        self.valueChangeStrChanged.emit()

    @pyqtProperty(str, notify=valueChangeStrChanged, fset=setValueChangeStr)
    def valueChangeStr(self)->str:
        # Allow the preset to override this setting
        if self.presetSelected:
            return self.presetValueChangeStr
        else:
            return self._valueChangeStr

    @pyqtProperty(float, notify=valueChangeStrChanged)
    def valueChange(self)->float:
        return float(self.valueChangeStr)



    # The label to carve at the bottom of the tower
    _towerLabel = _towerTypesTable[0]['label']

    towerLabelChanged = pyqtSignal()
    
    def setTowerLabel(self, value)->None:
        self._towerLabel = value
        self.towerLabelChanged.emit()

    @pyqtProperty(str, notify=towerLabelChanged, fset=setTowerLabel)
    def towerLabel(self)->str:
        return self._towerLabel



    # The description to carve up the side of the tower
    _towerDescription = 'RETRAC'

    towerDescriptionChanged = pyqtSignal()
    
    def setTowerDescription(self, value)->None:
        self._towerDescription = value
        self.towerDescriptionChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionChanged, fset=setTowerDescription)
    def towerDescription(self)->str:
        return self._towerDescription
    


    def __init__(self, stlDir):
        super().__init__(stlDir=stlDir)
