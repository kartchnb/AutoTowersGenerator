# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSignal, pyqtProperty
from UM.Logger import Logger

from .ModelBase import ModelBase



class FlowTowerModel(ModelBase):

    # The available flow tower presets
    _presetsTable = [
        {'name': 'Flow Tower - Flow 115-85', 'filename': 'Flow Tower - Flow 115-85.stl', 'start flow': 115, 'flow change': -5},
        {'name': 'Flow Tower (Spiral) - Flow 115-85', 'filename': 'Flow Tower Spiral - Flow 115-85.stl', 'start flow': 115, 'flow change': -5},
    ]

    # The available flow tower designs
    _towerDesignsTable = [
        {'name': 'Standard', 'icon': 'flowtower_icon.png', 'filename': 'temptower.scad'}, 
        {'name': 'Spiral', 'icon': 'spiral_flowtower_icon.png', 'filename': 'flowtower.scad'}, 
    ]



    # Make the presets availabe to QML
    presetsModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=presetsModelChanged)
    def presetsModel(self):
        return self._presetsTable



    # Make the flow tower designs available to QML
    towerDesignsChanged = pyqtSignal()

    @pyqtProperty(list, notify=towerDesignsChanged)
    def towerDesignsModel(self):
        return self._towerDesignsTable
    


    # The selected flow tower preset index
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
    def presetStartFlowPercent(self)->float:
        return float(self._presetsTable[self.presetIndex]['start flow'])
    
    @pyqtProperty(float, notify=presetIndexChanged)
    def presetFlowPercentChange(self)->float:
        return float(self._presetsTable[self.presetIndex]['flow change'])



    # The selected tower design
    _towerDesignIndex = 0

    towerDesignIndexChanged = pyqtSignal()

    def setTowerDesignIndex(self, value)->None:
        self._towerDesignIndex = int(value)
        self.towerDesignIndexChanged.emit()

    @pyqtProperty(int, notify=towerDesignIndexChanged, fset=setTowerDesignIndex)
    def towerDesignIndex(self)->int:
        return self._towerDesignIndex
    
    @pyqtProperty(str, notify=towerDesignIndexChanged)
    def towerDesignName(self)->str:
        return self._towerDesignsTable[self.towerDesignIndex]['name']
        
    @pyqtProperty(str, notify=towerDesignIndexChanged)
    def towerDesignFileName(self)->str:
        return self._towerDesignsTable[self.towerDesignIndex]['filename']

    @pyqtProperty(str, notify=towerDesignIndexChanged)
    def towerDesignIcon(self)->str:
        return self._towerDesignsTable[self.towerDesignIndex]['icon']



    # The starting flow percent for the tower
    _startFlowPercentStr = '115'

    startFlowPercentStrChanged = pyqtSignal()
    
    def setStartFlowPercentStr(self, value)->None:
        self._startFlowPercentStr = value
        self.startFlowPercentStrChanged.emit()

    @pyqtProperty(str, notify=startFlowPercentStrChanged, fset=setStartFlowPercentStr)
    def startFlowPercentStr(self)->str:
        return self._startFlowPercentStr
    
    @pyqtProperty(float, notify=startFlowPercentStrChanged)
    def startFlowPercent(self)->float:
        return float(self.startFlowPercentStr)



    # The ending flow percent for the tower
    _endFlowPercentStr = '85'

    endFlowPercentStrChanged = pyqtSignal()
    
    def setEndFlowPercentStr(self, value)->None:
        self._endFlowPercentStr = value
        self.endFlowPercentStrChanged.emit()

    @pyqtProperty(str, notify=endFlowPercentStrChanged, fset=setEndFlowPercentStr)
    def endFlowPercentStr(self)->str:
        return self._endFlowPercentStr
    
    @pyqtProperty(float, notify=endFlowPercentStrChanged)
    def endFlowPercent(self)->float:
        return float(self.endFlowPercentStr)



    # The amount to change the flow between tower sections
    _flowPercentChangeStr = '5'

    flowPercentChangeStrChanged = pyqtSignal()
    
    def setFlowPercentChangeStr(self, value)->None:
        self._flowPercentChangeStr = value
        self.flowPercentChangeStrChanged.emit()

    @pyqtProperty(str, notify=flowPercentChangeStrChanged, fset=setFlowPercentChangeStr)
    def flowPercentChangeStr(self)->str:
        return self._flowPercentChangeStr
    
    @pyqtProperty(float, notify=flowPercentChangeStrChanged)
    def flowPercentChange(self)->float:
        return float(self.flowPercentChangeStr)



    # The label to add to the tower
    _towerLabel = 'FLW'

    towerLabelChanged = pyqtSignal()
    
    def setTowerLabel(self, value)->None:
        self._towerLabel = value
        self.towerLabelChanged.emit()

    @pyqtProperty(str, notify=towerLabelChanged, fset=setTowerLabel)
    def towerLabel(self)->str:
        return self._towerLabel



    # The description to add to the side of the tower
    _towerDescription = 'FLOW'

    towerDescriptionChanged = pyqtSignal()
    
    def setTowerDescription(self, value)->None:
        self._towerDescription = value
        self.towerDescriptionChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionChanged, fset=setTowerDescription)
    def towerDescription(self)->str:
        return self._towerDescription



    def __init__(self, stlPath):
        super().__init__(stlPath=stlPath)
