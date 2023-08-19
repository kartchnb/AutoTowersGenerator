# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSlot
except ImportError:
    from PyQt5.QtCore import pyqtSlot


from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message

from .ControllerBase import ControllerBase
from ..Models.BedLevelPatternModel import BedLevelPatternModel



class BedLevelPatternController(ControllerBase):

    _openScadFilename = 'bedlevelpattern.scad'
    _qmlFilename = 'BedLevelPatternDialog.qml'



    # The print settings that are considered critical for this tower
    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'adhesion_type': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, 'none'),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'line_width': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, None),
        'machine_width': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'machine_depth': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
    }




    def __init__(self, guiPath, stlPath, loadStlCallback, generateStlCallback, pluginName):
        dataModel = BedLevelPatternModel(stlPath=stlPath)
        super().__init__(name='Bed Level Pattern', guiPath=guiPath, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetName != 'Custom':
            # Load a preset tower
            self._loadPresetBedLevelPattern()
        else:
            # Generate a custom tower using the user's settings
            self._generateCustomBedLevelPattern()



    def postProcess(self, gcode, displayOnLcd=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # No post-processing needs to be done for bed level prints
        return gcode



    def _loadPresetBedLevelPattern(self)->None:
        ''' Load a preset tower '''

        # Determine the path of the STL file to load
        stlFilePath = self._dataModel.presetFilePath

        # Determine the tower name
        towerName = f'Preset {self._dataModel.presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    def _generateCustomBedLevelPattern(self)->None:
        ''' Generate a custom tower '''

        # Collect data from the data model
        patternName = self._dataModel.patternName.lower()
        fill_percentage = self._dataModel.fillPercentage
        number_of_rings = self._dataModel.numberOfRings
        cell_size = self._dataModel.cellSize
        pad_size = self._dataModel.padSize

        # Determine the maximum print area
        (print_area_width, print_area_depth) = self._dataModel.printArea

        # Query the current layer height
        layer_height = self._dataModel.layerHeight

        # Query the current line width
        line_width = self._dataModel.lineWidth

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {
            'Bed_Level_Pattern_Type': patternName,
            'Print_Area_Width': print_area_width,
            'Print_Area_Depth': print_area_depth,
            'Line_Width': line_width,
            'Line_Height': layer_height,
            'Fill_Percentage': fill_percentage,
            'Concentric_Ring_Count': number_of_rings,
            'Grid_Cell_Count': cell_size,
            'Grid_Pad_Size': pad_size,
        }

        # Determine the tower name
        towerName = f'Custom Bed Level Pattern - {self._dataModel.patternName} {print_area_width}x{print_area_depth}'

        # Send the filename and parameters to the STL generation callback
        self._generateStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)
