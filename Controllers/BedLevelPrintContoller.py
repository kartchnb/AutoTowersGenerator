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



class BedLevelPrintController(QObject):
    _openScadFilename = 'bedlevelprint.scad'
    _qmlFilename = 'BedLevelPrintDialog.qml'

    _bedLevelPrintTypesModel = [
        {'value': 'Concentric Squares', 'icon': 'bedlevelprint_concentric_squares_icon.png'}, 
        {'value': 'X in Square', 'icon': 'bedlevelprint_x_in_square_icon.png'}, 
        {'value': 'Circle in Square', 'icon': 'bedlevelprint_circle_in_square_icon.png'}, 
        {'value': 'Perimeter', 'icon': 'bedlevelprint_perimeter_icon.png'}, 
        {'value': 'Grid', 'icon': 'bedlevelprint_grid_icon.png'}, 
        {'value': 'Five Circles', 'icon': 'bedlevelprint_five_circles_icon.png'}, 
    ]

    _presetTables = {}



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__()

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._guiPath = guiPath
        self._stlPath = stlPath



    @staticmethod
    def getPresetNames()->list:
        return list(BedLevelPrintController._presetTables.keys())



    _cachedSettingsDialog = None

    @property
    def _settingsDialog(self)->QObject:
        ''' Lazy instantiation of this tower's settings dialog '''
        if self._cachedSettingsDialog is None:
            qmlFilePath = os.path.join(self._guiPath, self._qmlFilename)
            self._cachedSettingsDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedSettingsDialog



    # The available tower types
    @pyqtProperty(list)
    def bedLevelPrintTypesModel(self):
        return self._bedLevelPrintTypesModel



    # The selected bed level print type
    _bedLevelPrintType = _bedLevelPrintTypesModel[0]['value']

    bedLevelPrintTypeChanged = pyqtSignal()

    def setBedLevelPrintType(self, value)->None:
        self._bedLevelPrintType = value
        self.bedLevelPrintTypeChanged.emit()

    @pyqtProperty(str, notify=bedLevelPrintTypeChanged, fset=setBedLevelPrintType)
    def bedLevelPrintType(self)->str:
        return self._bedLevelPrintType



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



    def settingsAreCompatible(self)->str:
        ''' Check whether Cura's settings are compatible with this tower '''

        containerStack = Application.getInstance().getGlobalContainerStack()

        # The tower cannot be generated if any type of adhesion is selected
        adhesion_setting = containerStack.getProperty('adhesion_type', 'value')
        if adhesion_setting != 'none':
            setting_label = containerStack.getProperty('adhesion_type', 'label')
            return f'The Cura setting "{setting_label}" must be set to "none" to print a bed level print.'

        return ''



    def generate(self, preset='')->None:
        ''' Generate a bed level print
            Presets are not supported at this time '''
        self._settingsDialog.show()
            


    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetTables[presetName]
        except KeyError:
            Logger.log('e', f'A BedLevel preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for BedLevel preset table "{presetName}" has not been defined')
            return

        # Load the preset's print area width
        try:
            print_width = presetTable['print area width']
        except KeyError:
            Logger.log('e', f'The "print area width" for BedLevel preset table "{presetName}" has not been defined')
            return

        # Load the preset's print area depth
        try:
            print_depth = presetTable['print area depth']
        except KeyError:
            Logger.log('e', f'The "print area depth" for BedLevel preset table "{presetName}" has not been defined')
            return

        # Query the bed size
        containerStack = Application.getInstance().getGlobalContainerStack()
        bed_width = containerStack.getProperty('machine_width', 'value')
        bed_depth = containerStack.getProperty('machine_depth', 'value')

        # Abort if the bed level print is bigger than the print area
        if print_width > bed_width or print_depth > bed_depth:
            message = 'This bed level print preset is too large for your printer\n'
            message += f'Printer bed is {bed_width}x{bed_depth}mm, but the preset is {print_width}x{print_depth}mm'
            Message(message).show()

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Bed Level Print {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
 
        containerStack = Application.getInstance().getGlobalContainerStack()

        fill_percentage = int(self.fillPercentageStr)
        number_of_squares = int(self.numberOfSquaresStr)
        cell_size = int(self.cellSizeStr)

        # Query the bed size
        bed_width = containerStack.getProperty('machine_width', 'value')
        bed_depth = containerStack.getProperty('machine_depth', 'value')

        # Query the current layer height
        layer_height = containerStack.getProperty("layer_height", "value")

        # Query the current line width
        line_width = containerStack.getProperty('line_width', 'value')

        # Adjust the bed size by the line width to keep the print within the bed volume
        bed_width -= 2
        bed_depth -= 2

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Bed_Level_Print_Type'] = self.bedLevelPrintType.lower()
        openScadParameters ['Print_Area_Width'] = bed_width
        openScadParameters ['Print_Area_Depth'] = bed_depth
        openScadParameters ['Line_Width'] = line_width
        openScadParameters ['Line_Height'] = layer_height
        openScadParameters ['Fill_Percentage'] = fill_percentage
        openScadParameters ['Concentric_Ring_Count'] = number_of_squares
        openScadParameters ['Grid_Cell_Count'] = cell_size

        # Determine the tower name
        towerName = f'Auto-Generated Bed Level Print {bed_width}x{bed_depth}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # No post-processing needs to be done for this print
        return gcode
