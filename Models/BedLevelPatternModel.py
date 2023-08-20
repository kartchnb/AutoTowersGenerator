# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSignal, pyqtProperty


from UM.Logger import Logger

from .ModelBase import ModelBase



class BedLevelPatternModel(ModelBase):

    # The available bed level presets
    _presetsTable = [
        {'name': 'Bed Size 220x220', 'filename': 'Bed Level Pattern - Spiral Squares 220x220.stl'},
        {'name': 'Bed Size 200x200', 'filename': 'Bed Level Pattern - Spiral Squares 200x200.stl'},
        {'name': 'Bed Size 180x180', 'filename': 'Bed Level Pattern - Spiral Squares 180x180.stl'},
        {'name': 'Bed Size 150x150', 'filename': 'Bed Level Pattern - Spiral Squares 150x150.stl'},
    ]

    # The available bed level patterns
    _patternsTable = [
        {'name': 'Spiral Squares', 'icon': 'bedlevelpattern_spiral_squares_icon.png'}, 
        {'name': 'Concentric Squares', 'icon': 'bedlevelpattern_concentric_squares_icon.png'}, 
        {'name': 'Concentric Circles', 'icon': 'bedlevelpattern_concentric_circles_icon.png'},
        {'name': 'X in Square', 'icon': 'bedlevelpattern_x_in_square_icon.png'}, 
        {'name': 'Circle in Square', 'icon': 'bedlevelpattern_circle_in_square_icon.png'}, 
        {'name': 'Grid', 'icon': 'bedlevelpattern_grid_icon.png'}, 
        {'name': 'Padded Grid', 'icon': 'bedlevelpattern_padded_grid_icon.png'},
        {'name': 'Five Circles', 'icon': 'bedlevelpattern_five_circles_icon.png'}, 
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

    @pyqtProperty(int, notify=presetIndexChanged, fset=setPresetIndex)
    def presetIndex(self)->int:
        return self._presetIndex
    
    @pyqtProperty(str, notify=presetIndexChanged, fset=setPresetIndex)
    def presetName(self)->str:
        try:
            return self._presetsTable[self.presetIndex]['name']
        except IndexError:
            return 'Custom'
    
    @pyqtProperty(str, notify=presetIndexChanged, fset=setPresetIndex)
    def presetFileName(self)->str:
        return self._presetsTable[self.presetIndex]['filename']
    
    @pyqtProperty(str, notify=presetIndexChanged, fset=setPresetIndex)
    def presetFilePath(self)->str:
        return self._buildStlFilePath(self.presetFileName)
    


    # The selected pattern type
    _patternIndex = 0

    patternIndexChanged = pyqtSignal()

    def setPatternIndex(self, value)->None:
        try:
            self._patternIndex = int(value)
            self.patternIndexChanged.emit()
        except ValueError:
            Logger.log('e', f'Attempted to set patternIndex to "{value}", which could not be converted to an integer')

    @pyqtProperty(int, notify=patternIndexChanged, fset=setPatternIndex)
    def patternIndex(self)->int:
        return self._patternIndex

    @pyqtProperty(str, notify=patternIndexChanged)
    def patternName(self)->str:
        return self._patternsTable[self.patternIndex]['name']

    @pyqtProperty(str, notify=patternIndexChanged)
    def patternIcon(self)->str:
        return self._patternsTable[self.patternIndex]['icon']



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
    


    def __init__(self, stlPath):
        super().__init__(stlPath=stlPath)
