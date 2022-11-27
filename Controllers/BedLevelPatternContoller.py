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

    _presetsTable = {}

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'adhesion_type': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, 'none'),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'line_width': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, None),
        'machine_width': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'machine_depth': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
    }

    _bedLevelPatternTypesModel = [
        {'value': 'Concentric Squares', 'icon': 'bedlevelpattern_concentric_squares_icon.png'}, 
        {'value': 'Concentric Circles', 'icon': 'bedlevelpattern_concentric_circles_icon.png'},
        {'value': 'X in Square', 'icon': 'bedlevelpattern_x_in_square_icon.png'}, 
        {'value': 'Circle in Square', 'icon': 'bedlevelpattern_circle_in_square_icon.png'}, 
        {'value': 'Grid', 'icon': 'bedlevelpattern_grid_icon.png'}, 
        {'value': 'Five Circles', 'icon': 'bedlevelpattern_five_circles_icon.png'}, 
    ]



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__('Bed Level Pattern', guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable)



    # The available tower types
    @pyqtProperty(list)
    def bedLevelPatternTypesModel(self):
        return self._bedLevelPatternTypesModel



    # The selected bed level pattern type
    _bedLevelPatternType = _bedLevelPatternTypesModel[0]['value']

    bedLevelPatternTypeChanged = pyqtSignal()

    def setBedLevelPatternType(self, value)->None:
        self._bedLevelPatternType = value
        self.bedLevelPatternTypeChanged.emit()

    @pyqtProperty(str, notify=bedLevelPatternTypeChanged, fset=setBedLevelPatternType)
    def bedLevelPatternType(self)->str:
        return self._bedLevelPatternType



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
            


    def _loadPreset(self, presetName)->None:
        # No presets for now
        pass



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
 
        fill_percentage = int(self.fillPercentageStr)
        number_of_squares = int(self.numberOfSquaresStr)
        cell_size = int(self.cellSizeStr)

        # Determine the maximum print area
        (print_area_width, print_area_depth) = self._printArea

        # Query the current layer height
        layer_height = self._layerHeight

        # Query the current line width
        line_width = self._lineWidth

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Bed_Level_Pattern_Type'] = self.bedLevelPatternType.lower()
        openScadParameters ['Print_Area_Width'] = print_area_width
        openScadParameters ['Print_Area_Depth'] = print_area_depth
        openScadParameters ['Line_Width'] = line_width
        openScadParameters ['Line_Height'] = layer_height
        openScadParameters ['Fill_Percentage'] = fill_percentage
        openScadParameters ['Concentric_Ring_Count'] = number_of_squares
        openScadParameters ['Grid_Cell_Count'] = cell_size

        # Determine the tower name
        towerName = f'Auto-Generated Bed Level Pattern {print_area_width}x{print_area_depth}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode, displayOnLcd=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # No post-processing needs to be done for this pattern
        return gcode
