import os
import math

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty


from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message

from .ControllerBase import ControllerBase



class BedLevelPatternController(ControllerBase):
    _openScadFilename = 'bedlevelpattern.scad'
    _qmlFilename = 'BedLevelPatternDialog.qml'

    _presetsTable = {
        'Bed Level Pattern - Concentric Squares 220x220': {},
        'Bed Level Pattern - Concentric Squares 200x200': {},
        'Bed Level Pattern - Concentric Squares 180x180': {},
        'Bed Level Pattern - Concentric Squares 150x150': {},
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'adhesion_type': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, 'none'),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'line_width': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, None),
        'machine_width': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'machine_depth': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
    }

    _bedLevelPatternsModel = [
        {'value': 'Concentric Squares', 'icon': 'bedlevelpattern_concentric_squares_icon.png'}, 
        {'value': 'Concentric Circles', 'icon': 'bedlevelpattern_concentric_circles_icon.png'},
        {'value': 'X in Square', 'icon': 'bedlevelpattern_x_in_square_icon.png'}, 
        {'value': 'Circle in Square', 'icon': 'bedlevelpattern_circle_in_square_icon.png'}, 
        {'value': 'Grid', 'icon': 'bedlevelpattern_grid_icon.png'}, 
        {'value': 'Padded Grid', 'icon': 'bedlevelpattern_padded_grid_icon.png'},
        {'value': 'Five Circles', 'icon': 'bedlevelpattern_five_circles_icon.png'}, 
    ]



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__('Bed Level Pattern', guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable, pluginName)



    # The available tower types
    @pyqtProperty(list)
    def bedLevelPatternsModel(self):
        return self._bedLevelPatternsModel



    # The selected bed level pattern type
    _bedLevelPattern = _bedLevelPatternsModel[0]['value']

    bedLevelPatternChanged = pyqtSignal()

    def setBedLevelPattern(self, value)->None:
        self._bedLevelPattern = value
        self.bedLevelPatternChanged.emit()

    @pyqtProperty(str, notify=bedLevelPatternChanged, fset=setBedLevelPattern)
    def bedLevelPattern(self)->str:
        return self._bedLevelPattern



    # The selected bed fill percentage
    _fillPercentageStr = "90"

    fillPercentageStrChanged = pyqtSignal()

    def setFillPercentageStr(self, value)->None:
        self._fillPercentageStr = value
        self.fillPercentageStrChanged.emit()

    @pyqtProperty(str, notify=fillPercentageStrChanged, fset=setFillPercentageStr)
    def fillPercentageStr(self)->str:
        return self._fillPercentageStr



    # The selected number of squares
    _numberOfSquaresStr = "7"

    numberOfSquaresStrChanged = pyqtSignal()

    def setNumberOfSquaresStr(self, value)->None:
        self._numberOfSquaresStr = value
        self.numberOfSquaresStrChanged.emit()

    @pyqtProperty(str, notify=numberOfSquaresStrChanged, fset=setNumberOfSquaresStr)
    def numberOfSquaresStr(self)->str:
        return self._numberOfSquaresStr



    # The selected cell size
    _cellSizeStr = "4"

    cellSizeStrChanged = pyqtSignal()

    def setCellSizeStr(self, value)->None:
        self._cellSizeStr = value
        self.cellSizeStrChanged.emit()

    @pyqtProperty(str, notify=cellSizeStrChanged, fset=setCellSizeStr)
    def cellSizeStr(self)->str:
        return self._cellSizeStr



    # The selected pad size
    _padSizeStr = "20"

    padSizeStrChanged = pyqtSignal()

    def setPadSizeStr(self, value)->None:
        self._padSizeStr = value
        self.padSizeStrChanged.emit()

    @pyqtProperty(str, notify=padSizeStrChanged, fset=setPadSizeStr)
    def padSizeStr(self)->str:
        return self._padSizeStr



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''

        # Determine the STL file name
        stlFileName = f'{presetName}.stl'
        stlFilePath = self._getStlFilePath(stlFileName)

        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A Bed Level Pattern preset named "{presetName}" was requested, but has not been defined')
            return

        # Determine the tower name
        towerName = f'Preset {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
 
        fill_percentage = int(self.fillPercentageStr)
        number_of_squares = int(self.numberOfSquaresStr)
        cell_size = int(self.cellSizeStr)
        pad_size = int(self.padSizeStr)

        # Determine the maximum print area
        (print_area_width, print_area_depth) = self._printArea

        # Query the current layer height
        layer_height = self._layerHeight

        # Query the current line width
        line_width = self._lineWidth

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Bed_Level_Pattern_Type'] = self.bedLevelPattern.lower()
        openScadParameters ['Print_Area_Width'] = print_area_width
        openScadParameters ['Print_Area_Depth'] = print_area_depth
        openScadParameters ['Line_Width'] = line_width
        openScadParameters ['Line_Height'] = layer_height
        openScadParameters ['Fill_Percentage'] = fill_percentage
        openScadParameters ['Concentric_Ring_Count'] = number_of_squares
        openScadParameters ['Grid_Cell_Count'] = cell_size
        openScadParameters ['Grid_Pad_Size'] = pad_size

        # Determine the tower name
        towerName = f'Custom Bed Level Pattern - {self.bedLevelPattern} {print_area_width}x{print_area_depth}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode, displayOnLcd=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # No post-processing needs to be done for this pattern
        return gcode
