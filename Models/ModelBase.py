import os
import math

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject
except ImportError:
    from PyQt5.QtCore import QObject

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

from UM.Application import Application
from UM.Logger import Logger



class ModelBase(QObject):

    # The initial values used for the base and section heights of the tower
    _nominalBaseHeight = 0.84
    _nominalSectionHeight = 8.4



    @property
    def optimalBaseHeight(self)->int:
        return self._calculateOptimalHeight(self._nominalBaseHeight)
    


    @property
    def optimalSectionHeight(self)->int:
        return self._calculateOptimalHeight(self._nominalSectionHeight)



    @property
    def flowRate(self)->float:
        ''' Return the current flow rate setting '''
        return ExtruderManager.getInstance().getActiveExtruderStack().getProperty('material_flow', 'value')


    @property
    def initialLayerHeight(self)->float:
        ''' Return the current initial layer height setting '''
        return Application.getInstance().getGlobalContainerStack().getProperty("layer_height_0", "value")



    @property
    def layerHeight(self)->float:
        ''' Return the current layer height setting '''
        return Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")



    @property
    def lineWidth(self)->float:
        ''' Return the current line width setting '''
        return Application.getInstance().getGlobalContainerStack().getProperty("line_width", "value")



    @property
    def printSpeed(self)->float:
        ''' Return the current print speed setting '''
        return ExtruderManager.getInstance().getActiveExtruderStack().getProperty('speed_print', 'value')



    @property
    def relativeExtrusion(self)->bool:
        ''' Returns whether relative extrusion is being used (True or False) '''
        return bool(ExtruderManager.getInstance().getActiveExtruderStack().getProperty('relative_extrusion', 'value'))



    @property
    def printArea(self)->tuple:
        containerStack = Application.getInstance().getGlobalContainerStack()

        # Determine the maximum print area
        disallowedAreas = containerStack.getProperty('machine_disallowed_areas', 'value')
        if len(disallowedAreas) > 0:
            # Calculate the print area based on the disallowed areas
            flattenedList = [coord for section in disallowedAreas for coord in section]
            minX = max([coord[0] for coord in flattenedList if coord[0] < 0])
            maxX = min([coord[0] for coord in flattenedList if coord[0] >= 0])
            minY = max([coord[1] for coord in flattenedList if coord[1] < 0])
            maxY = min([coord[1] for coord in flattenedList if coord[1] >= 0])
            printAreaWidth = maxX - minX
            printAreaDepth = maxY - minY
        else:
            # Calculate the print area based on the bed size
            printAreaWidth = containerStack.getProperty('machine_width', 'value')
            printAreaDepth = containerStack.getProperty('machine_depth', 'value')

        # Query the current line width
        lineWidth = containerStack.getProperty('line_width', 'value')

        # Adjust for the selected bed adhesion
        bedAdhesionType = containerStack.getProperty('adhesion_type', 'value')
        if bedAdhesionType == 'skirt':
            skirtGap = containerStack.getProperty('skirt_gap', 'value')
            printAreaWidth -= skirtGap*2
            printAreaDepth -= skirtGap*2

        elif bedAdhesionType == 'brim':
            brimWidth = containerStack.getProperty('brim_width', 'value')
            brimGap = containerStack.getProperty('brim_gap', 'value')
            printAreaWidth -= (brimWidth*2 + brimGap*2)
            printAreaDepth -= (brimWidth*2 + brimGap*2)

        elif bedAdhesionType == 'raft':
            raftMargin = containerStack.getProperty('raft_margin', 'value')
            printAreaWidth -= raftMargin*2
            printAreaDepth -= raftMargin*2

        # Adjust the print_area size by the line width to keep the pattern within the volume
        printAreaWidth -= lineWidth*2
        printAreaDepth -= lineWidth*2

        return (printAreaWidth, printAreaDepth)



    def __init__(self, stlPath):
        super().__init__()

        self._stlPath = stlPath



    def _correctChangeValueSign(self, changeValue, startValue, endValue)->float:
        ''' Ensure the sign of a change value is appropriate for the start and end values '''

        if endValue >= startValue:
            return abs(changeValue)
        else:
            return -abs(changeValue)



    def _calculateOptimalHeight(self, nominal_height)->int:
        ''' Calculates an optimal height from a nominal height, based on the current printed layer height 
            For example, given a nominal height of 1 mm and a current printed layer height of 0.12 mm, 
            this function will return 9 mm
            The optimal height will always be equal to or larger than the nominal height '''
        optimal_height = self.layerHeight * math.ceil(nominal_height / self.layerHeight)
        return optimal_height



    def _buildStlFilePath(self, filename)->str:
        ''' Determine the full path to an STL file '''

        return os.path.join(self._stlPath, filename)
