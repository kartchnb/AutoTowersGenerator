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

class BedLevelPatternModel(ModelBase):

    # The available bed level presets
    _presetsTable = [
        {'name': catalog.i18nc("@model", "Bed Size 220x220") , 'filename': 'Bed Level Pattern - Spiral Squares 220x220.stl', 'icon': 'bedlevelpattern_spiral_squares_icon.png'},
        {'name': catalog.i18nc("@model", "Bed Size 200x200") , 'filename': 'Bed Level Pattern - Spiral Squares 200x200.stl', 'icon': 'bedlevelpattern_spiral_squares_icon.png'},
        {'name': catalog.i18nc("@model", "Bed Size 180x180") , 'filename': 'Bed Level Pattern - Spiral Squares 180x180.stl', 'icon': 'bedlevelpattern_spiral_squares_icon.png'},
        {'name': catalog.i18nc("@model", "Bed Size 150x150") , 'filename': 'Bed Level Pattern - Spiral Squares 150x150.stl', 'icon': 'bedlevelpattern_spiral_squares_icon.png'},
    ]

    # The available bed level patterns
    _patternsTable = [
        {'name': catalog.i18nc("@pattern", "Spiral Squares") , 'icon': 'bedlevelpattern_spiral_squares_icon.png'}, 
        {'name': catalog.i18nc("@pattern", "Concentric Squares") , 'icon': 'bedlevelpattern_concentric_squares_icon.png'}, 
        {'name': catalog.i18nc("@pattern", "Concentric Circles") , 'icon': 'bedlevelpattern_concentric_circles_icon.png'},
        {'name': catalog.i18nc("@pattern", "X in Square") , 'icon': 'bedlevelpattern_x_in_square_icon.png'}, 
        {'name': catalog.i18nc("@pattern", "Circle in Square") , 'icon': 'bedlevelpattern_circle_in_square_icon.png'}, 
        {'name': catalog.i18nc("@pattern", "Grid") , 'icon': 'bedlevelpattern_grid_icon.png'}, 
        {'name': catalog.i18nc("@pattern", "Padded Grid") , 'icon': 'bedlevelpattern_padded_grid_icon.png'},
        {'name': catalog.i18nc("@pattern", "Five Circles") , 'icon': 'bedlevelpattern_five_circles_icon.png'}, 
    ]



    # Make the presets available to QML
    presetsModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=presetsModelChanged)
    def presetsModel(self):
        return self._presetsTable
    

    
    # Make the patterns available to QML
    patternsModelChanged = pyqtSignal()

    @pyqtProperty(list, notify=patternsModelChanged)
    def patternsModel(self):
        return self._patternsTable



    # The selected bed level preset index
    _presetIndex = 0

    presetIndexChanged = pyqtSignal()

    def setPresetIndex(self, value)->None:
        self._presetIndex = int(value)
        self.presetIndexChanged.emit()
        self.dialogIconChanged.emit()

    @pyqtProperty(int, notify=presetIndexChanged, fset=setPresetIndex)
    def presetIndex(self)->int:
        return self._presetIndex
    
    @pyqtProperty(bool, notify=presetIndexChanged)
    def presetSelected(self)->bool:
        return self._presetIndex < len(self._presetsTable)
    
    @pyqtProperty(str, notify=presetIndexChanged, fset=setPresetIndex)
    def presetName(self)->str:
        return self._presetsTable[self.presetIndex]['name']
    
    @pyqtProperty(str, notify=presetIndexChanged, fset=setPresetIndex)
    def presetFileName(self)->str:
        return self._presetsTable[self.presetIndex]['filename']
    
    @pyqtProperty(str, notify=presetIndexChanged, fset=setPresetIndex)
    def presetFilePath(self)->str:
        return self._buildStlFilePath(self.presetFileName)
        
    @pyqtProperty(str, notify=presetIndexChanged)
    def presetIcon(self)->str:
        return self._presetsTable[self.presetIndex]['icon']


    # The selected pattern type
    _patternIndex = 0

    patternIndexChanged = pyqtSignal()

    def setPatternIndex(self, value)->None:
        self._patternIndex = int(value)
        self.patternIndexChanged.emit()
        self.dialogIconChanged.emit()

    @pyqtProperty(int, notify=patternIndexChanged, fset=setPatternIndex)
    def patternIndex(self)->int:
        return self._patternIndex

    @pyqtProperty(str, notify=patternIndexChanged)
    def patternName(self)->str:
        return self._patternsTable[self.patternIndex]['name']

    @pyqtProperty(str, notify=patternIndexChanged)
    def patternIcon(self)->str:
        return self._patternsTable[self.patternIndex]['icon']
    


    # The icon to display on the dialog
    dialogIconChanged = pyqtSignal()

    @pyqtProperty(str, notify=dialogIconChanged)
    def dialogIcon(self)->str:
        try:
            return self.presetIcon
        except IndexError:
            return self.patternIcon



    # The selected bed fill percentage
    _fillPercentageStr = '90'

    fillPercentageStrChanged = pyqtSignal()

    def setFillPercentageStr(self, value)->None:
        self._fillPercentageStr = value
        self.fillPercentageStrChanged.emit()

    @pyqtProperty(str, notify=fillPercentageStrChanged, fset=setFillPercentageStr)
    def fillPercentageStr(self)->str:
        return self._fillPercentageStr
    
    @pyqtProperty(int, notify=fillPercentageStrChanged)
    def fillPercentage(self)->int:
        return int(self.fillPercentageStr)



    # The selected number of rings
    _numberOfRingsStr = '7'

    numberOfRingsStrChanged = pyqtSignal()

    def setNumberOfRingsStr(self, value)->None:
        self._numberOfRingsStr = value
        self.numberOfRingsStrChanged.emit()

    @pyqtProperty(str, notify=numberOfRingsStrChanged, fset=setNumberOfRingsStr)
    def numberOfRingsStr(self)->str:
        return self._numberOfRingsStr
    
    @pyqtProperty(int, notify=numberOfRingsStrChanged)
    def numberOfRings(self)->int:
        return int(self.numberOfRingsStr)



    # The selected cell size
    _cellSizeStr = '4'

    cellSizeStrChanged = pyqtSignal()

    def setCellSizeStr(self, value)->None:
        self._cellSizeStr = value
        self.cellSizeStrChanged.emit()

    @pyqtProperty(str, notify=cellSizeStrChanged, fset=setCellSizeStr)
    def cellSizeStr(self)->str:
        return self._cellSizeStr

    @pyqtProperty(int, notify=cellSizeStrChanged)
    def cellSize(self)->int:
        return int(self.cellSizeStr)
    


    # The selected pad size
    _padSizeStr = '20'

    padSizeStrChanged = pyqtSignal()

    def setPadSizeStr(self, value)->None:
        self._padSizeStr = value
        self.padSizeStrChanged.emit()

    @pyqtProperty(str, notify=padSizeStrChanged, fset=setPadSizeStr)
    def padSizeStr(self)->str:
        return self._padSizeStr

    @pyqtProperty(int, notify=padSizeStrChanged)
    def padSize(self)->int:
        return int(self.padSizeStr)
    


    def __init__(self, stlDir):
        super().__init__(stlDir=stlDir)
