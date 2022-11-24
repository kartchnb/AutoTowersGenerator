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

        self._backedUpSettings = {}



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

    

    def checkPrintSettings(self, correctPrintSettings = False)->None:
        ''' Checks the current print settings and warns or changes them if they are not compatible with the tower '''

        correctedSettings = []

        # Iterate over each setting in the critical settings table
        for settingName in self._criticalSettingsTable.keys():
            (containerStackDescription, recommendedValue) = self._criticalSettingsTable[settingName]

            # Continue if there is a recommended value for this setting
            if not recommendedValue is None:

                # Get the source object for this setting
                containerStack = self._getcontainerStack(containerStackDescription)

                # Look up the current value of the setting
                currentValue = containerStack.getProperty(settingName, 'value')

                # If the current value does not match the recommended value
                if currentValue != recommendedValue:

                    # Look up the display name of the setting and the current and recommended values
                    settingDisplayName = containerStack.getProperty(settingName, 'label')
                    currentValueDisplayName = self._getSettingValueDisplayName(containerStack, settingName, currentValue)
                    recommendedValueDisplayName = self._getSettingValueDisplayName(containerStack, settingName, recommendedValue)

                    # Report the setting as changed or just recommended to be changed
                    correctedSettings.append((settingDisplayName, currentValueDisplayName, recommendedValueDisplayName))

                    # If the setting should be automatically changed
                    if correctPrintSettings == True:

                        # Backup and change the setting
                        self._backedUpSettings[settingName] = (containerStack, currentValue, currentValueDisplayName, settingDisplayName)
                        containerStack.setProperty(settingName, 'value', recommendedValue)

        return correctedSettings



    def _lookupStackValue(self, stack, settingName)->list:
        containerList = []

        # Iterate over each container in the stack
        for container in stack.getContainers():

            # Check if this container contains the setting
            result = container.hasProperty(settingName, 'value')
            if container.hasProperty(settingName, 'value'):
                currentValue = container.getProperty(settingName, 'value')
                containerList.append((container, currentValue))

        return containerList



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self._dialog.show()



    def cleanup(self)->tuple:
        restoredSettings = []

        # Iterate over each backed up setting
        for settingName in self._backedUpSettings.keys():
            # Get the backed up setting value
            (containerStack, originalValue, originalValueDisplayName, settingDisplayName) = self._backedUpSettings[settingName]

            # Restore the original setting
            containerStack.setProperty(settingName, 'value', originalValue)
            containerStack.setDirty(False)

            # Report the restored setting
            restoredSettings.append((settingDisplayName, originalValueDisplayName))

        self._backedUpSettings = {}

        return restoredSettings
            


    def _getcontainerStack(self, sourceDescription):
        ''' Retieves and returns a property source based on a description string '''

        containerStack = None

        if sourceDescription == 'global':
            containerStack = Application.getInstance().getGlobalContainerStack()
        elif sourceDescription == 'extruder':
            # BAK: Try getActiveExtruderStack()
            containerStack = ExtruderManager.getInstance().getActiveExtruderStack()
        else:
            Logger.log('e', message)

        return containerStack



    def _getSettingValueDisplayName(self, containerStack, settingName, settingValue)->str:
        ''' Looks up and returns the display name for a given setting value '''

        try:
            # Attempt to look up the display name of the value
            settingOptions = containerStack.getProperty(settingName, 'options')
            displayName = settingOptions[settingValue]
        except (KeyError, TypeError):
            # As a last resort, just convert the setting value to a string
            displayName = str(settingValue)

        return displayName



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
