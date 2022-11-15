import os

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject
except ImportError:
    from PyQt5.QtCore import QObject


from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

from UM.Application import Application
from UM.Logger import Logger



class ControllerBase(QObject):

    def __init__(self, name, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, openScadFilename, qmlFilename, presetsTable, criticalSettingsTable):
        super().__init__()
        
        self.name = name

        self._guiPath = guiPath
        self._stlPath = stlPath

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._openScadFilename = openScadFilename
        self._qmlFilename = qmlFilename
        self._presetsTable = presetsTable
        self._criticalSettingsTable = criticalSettingsTable



    @property
    def criticalSettingsList(self)->list:
        return list(self._criticalSettingsTable.keys())



    @property
    def presetNames(self)->list:
        return list(self._presetsTable.keys())



    _cachedDialog = None

    @property
    def _dialog(self)->QObject:
        ''' Lazy instantiation of this controller's dialog '''
        if self._cachedDialog is None:
            qmlFilePath = os.path.join(self._guiPath, self._qmlFilename)
            self._cachedDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedDialog

    

    def checkPrintSettings(self)->None:
        ''' Checks the current print settings and warns if they are not compatible with the tower '''

        recommendedSettings = []

        # Iterate over each setting in the critical settings table
        for settingName in self._criticalSettingsTable.keys():
            (settingSource, recommendedValue) = self._criticalSettingsTable[settingName]

            # Get the source object for this setting
            settingSource = self._getSettingSource(settingSource)

            # Get the current value of the setting
            currentValue = settingSource.getProperty(settingName, 'value')

            # Check if the setting should be changed
            if recommendedValue != None and currentValue != recommendedValue:
                # Look up the display name of the setting
                settingDisplayName = settingSource.getProperty(settingName, 'label')

                # Look up the display name of the recommended setting value
                recommendedValueDisplayName = self._getSettingValueDisplayName(settingName, recommendedValue, settingSource)

                recommendedSettings.append((settingDisplayName, recommendedValueDisplayName))

        return recommendedSettings



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self._dialog.show()



    def cleanup(self)->None:
        pass



    def _getSettingSource(self, source_description):
        ''' Retieves and returns a property source based on a description string '''

        settingSource = None

        if source_description == 'global':
            settingSource = Application.getInstance().getGlobalContainerStack()
        elif source_description == 'extruder':
            settingSource = ExtruderManager.getInstance().getActiveExtruderStacks()[0]
        else:
            message = f'"{source_description}" is not a recognized property source description'
            Logger.log('e', message)
            raise Exception(message)

        return settingSource



    def _getSettingValueDisplayName(self, settingName, settingValue, settingSource)->str:
        ''' Looks up and returns the display name for a given setting value '''

        try:
            # Attempt to look up the display name of the value
            settingOptions = settingSource.getProperty(settingName, 'options')
            settingValueDisplayName = settingOptions[settingValue]
        except KeyError:
            # As a last resort, just convert the setting value to a string
            settingValueDisplayName = str(settingValue)

        return settingValueDisplayName



    def _getPrintAreaDimensions(self)->tuple:
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
