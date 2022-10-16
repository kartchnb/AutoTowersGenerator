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
        'adhesion_type': 'none',
        'layer_height': None,
        'line_width': None,
        'machine_width': None,
        'machine_depth': None,
    }

    _bedLevelPatternTypesModel = [
        {'value': 'Concentric Squares', 'icon': 'bedlevelpattern_concentric_squares_icon.png'}, 
        {'value': 'X in Square', 'icon': 'bedlevelpattern_x_in_square_icon.png'}, 
        {'value': 'Circle in Square', 'icon': 'bedlevelpattern_circle_in_square_icon.png'}, 
        {'value': 'Perimeter', 'icon': 'bedlevelpattern_perimeter_icon.png'}, 
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



    # The selected circle diameter for the five circles pattern
    _circleDiameterStr = "20"

    circleDiameterStrChanged = pyqtSignal()

    def setCircleDiameterStr(self, value)->None:
        self._circleDiameterStr = value
        self.circleDiameterStrChanged.emit()

    @pyqtProperty(str, notify=circleDiameterStrChanged, fset=setCircleDiameterStr)
    def circleDiameterStr(self)->str:
        return self._circleDiameterStr



    # The selected outline distance for the five circles pattern
    _outlineDistanceStr = "5"

    outlineDistanceStrChanged = pyqtSignal()

    def setOutlineDistanceStr(self, value)->None:
        self._outlineDistanceStr = value
        self.outlineDistanceStrChanged.emit()

    @pyqtProperty(str, notify=outlineDistanceStrChanged, fset=setOutlineDistanceStr)
    def outlineDistanceStr(self)->str:
        return self._outlineDistanceStr
            


    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A BedLevel preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for BedLevel preset table "{presetName}" has not been defined')
            return

        # Load the preset's pattern width
        try:
            pattern_width = presetTable['pattern width']
        except KeyError:
            Logger.log('e', f'The "pattern width" for BedLevel preset table "{presetName}" has not been defined')
            return

        # Load the preset's pattern depth
        try:
            pattern_depth = presetTable['pattern depth']
        except KeyError:
            Logger.log('e', f'The "pattern depth" for BedLevel preset table "{presetName}" has not been defined')
            return

        # Query the bed size
        containerStack = Application.getInstance().getGlobalContainerStack()
        bed_width = containerStack.getProperty('machine_width', 'value')
        bed_depth = containerStack.getProperty('machine_depth', 'value')

        # Abort if the bed level pattern is bigger than the print area
        if pattern_width > bed_width or pattern_depth > bed_depth:
            message = 'This bed level pattern preset is too large for your printer\n'
            message += f'Printer bed is {bed_width}x{bed_depth} mm, but the preset is {pattern_width}x{pattern_depth} mm'
            Message(message).show()

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Bed Level Pattern {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
 
        containerStack = Application.getInstance().getGlobalContainerStack()

        fill_percentage = int(self.fillPercentageStr)
        number_of_squares = int(self.numberOfSquaresStr)
        cell_size = int(self.cellSizeStr)
        circle_diameter = float(self.circleDiameterStr)
        outline_distance = float(self.outlineDistanceStr)

        # Query the bed size
        bed_width = containerStack.getProperty('machine_width', 'value')
        bed_depth = containerStack.getProperty('machine_depth', 'value')

        # Query the current layer height
        layer_height = containerStack.getProperty("layer_height", "value")

        # Query the current line width
        line_width = containerStack.getProperty('line_width', 'value')

        # Adjust the bed size by the line width to keep the pattern within the bed volume
        bed_width -= 2
        bed_depth -= 2

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Bed_Level_Pattern_Type'] = self.bedLevelPatternType.lower()
        openScadParameters ['Pattern_Area_Width'] = bed_width
        openScadParameters ['Pattern_Area_Depth'] = bed_depth
        openScadParameters ['Line_Width'] = line_width
        openScadParameters ['Line_Height'] = layer_height
        openScadParameters ['Fill_Percentage'] = fill_percentage
        openScadParameters ['Concentric_Ring_Count'] = number_of_squares
        openScadParameters ['Grid_Cell_Count'] = cell_size
        #openScadParameters ['Circle Diameter'] = circle_diameter
        #openScadParameters ['Outline Distance'] = outline_distance

        # Determine the tower name
        towerName = f'Auto-Generated Bed Level Pattern {bed_width}x{bed_depth}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # No post-processing needs to be done for this pattern
        return gcode
