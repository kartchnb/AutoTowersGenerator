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

class TempTowerModel(ModelBase):

    # The available temp tower presets
    _presetsTable = [
        {'name': catalog.i18nc("@model", "Temperature Tower - ABA") , 'filename': 'Temperature Tower - ABA.stl', 'start temp': '260', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - ABS") , 'filename': 'Temperature Tower - ABS.stl', 'start temp': '250', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - Nylon") , 'filename': 'Temperature Tower - Nylon.stl', 'start temp': '260', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - PC") , 'filename': 'Temperature Tower - PC.stl', 'start temp': '310', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - PETG") , 'filename': 'Temperature Tower - PETG.stl', 'start temp': '250', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - PLA") , 'filename': 'Temperature Tower - PLA.stl', 'start temp': '220', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - PLA+") , 'filename': 'Temperature Tower - PLA+.stl', 'start temp': '230', 'temp change': '-5'},
        {'name': catalog.i18nc("@model", "Temperature Tower - TPU") , 'filename': 'Temperature Tower - TPU.stl', 'start temp': '230', 'temp change': '-5'},
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
    def presetStartTempStr(self)->str:
        return self._presetsTable[self.presetIndex]['start temp']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetStartTemp(self)->float:
        return float(self.presetStartTempStr)
    
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetTempChangeStr(self)->str:
        return self._presetsTable[self.presetIndex]['temp change']
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetTempChange(self)->float:
        return float(self.presetTempChangeStr)
    


    # The icon to display on the dialog
    dialogIconChanged = pyqtSignal()

    @pyqtProperty(str, notify=dialogIconChanged)
    def dialogIcon(self)->str:
        return 'temptower_icon.png'



    # The starting temperature value for the tower
    _startTempStr = '220'

    startTempStrChanged = pyqtSignal()
    
    def setStartTempStr(self, value)->None:
        self._startTempStr = value
        self.startTempStrChanged.emit()

    @pyqtProperty(str, notify=startTempStrChanged, fset=setStartTempStr)
    def startTempStr(self)->str:
        # Allow the preset to override this setting
        if self.presetSelected:
            return self.presetStartTempStr
        else:
            return self._startTempStr

    @pyqtProperty(float, notify=startTempStrChanged)
    def startTemp(self)->float:
        return float(self.startTempStr)



    # The ending temperature value for the tower
    _endTempStr = '180'

    endTempStrChanged = pyqtSignal()
    
    def setEndTempStr(self, value)->None:
        self._endTempStr = value
        self.endTempStrChanged.emit()

    @pyqtProperty(str, notify=endTempStrChanged, fset=setEndTempStr)
    def endTempStr(self)->str:
        return self._endTempStr

    @pyqtProperty(float, notify=endTempStrChanged)
    def endTemp(self)->float:
        return float(self.endTempStr)



    # The amount to change the temperature between tower sections
    _tempChangeStr = '-5'

    tempChangeStrChanged = pyqtSignal()
    
    def setTempChangeStr(self, value)->None:
        self._tempChangeStr = value
        self.tempChangeStrChanged.emit()

    @pyqtProperty(str, notify=tempChangeStrChanged, fset=setTempChangeStr)
    def tempChangeStr(self)->str:
        # Allow the preset to override this setting
        if self.presetSelected:
            return self.presetTempChangeStr
        else:
            return self._tempChangeStr

    @pyqtProperty(float, notify=tempChangeStrChanged)
    def tempChange(self)->float:
        return float(self.tempChangeStr)



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
    


    def __init__(self, stlDir):
        super().__init__(stlDir=stlDir)
