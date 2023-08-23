# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject
except ImportError:
    from PyQt5.QtCore import QObject

from enum import IntEnum
import math
import os

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

from UM.Application import Application
from UM.Logger import Logger



class ControllerBase(QObject):
    
    class ContainerId(IntEnum):
        GLOBAL_CONTAINER_STACK = 0
        ACTIVE_EXTRUDER_STACK = 1



    def __init__(self, name, guiDir, loadStlCallback, generateStlCallback, qmlFilename, criticalPropertiesTable, dataModel, pluginName):
        super().__init__()
        
        self.name = name

        self._guiDir = guiDir

        self._loadStlCallback = loadStlCallback
        self._generateStlCallback = generateStlCallback

        self._qmlFilename = qmlFilename
        self._criticalPropertiesTable = criticalPropertiesTable

        self._dataModel = dataModel

        self._pluginName = pluginName
        
        self._backedUpSettings = {}
    


    def settingIsCritical(self, settingKey)->bool:
        return settingKey in self._criticalPropertiesTable.keys()
    


    def checkPrintSettings(self, correctPrintSettings = False)->None:
        ''' Checks the current print settings and warns or changes them if they are not compatible with the tower '''

        correctedSettings = []

        # Iterate over each setting in the critical settings table
        for settingName in self._criticalPropertiesTable.keys():
            (containerStackDescription, recommendedValue) = self._criticalPropertiesTable[settingName]

            # Continue if there is a recommended value for this setting
            if not recommendedValue is None:

                # Get the source object for this setting
                containerStack = self._getContainerStack(containerStackDescription)

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



    _dialog = None

    def generate(self, customizable)->None:
        ''' Generate a tower - either a preset tower or a custom tower '''

        qmlFilePath = os.path.join(self._guiDir, self._qmlFilename)
        self._dialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'controller': self, 'dataModel': self._dataModel, 'enableCustom': customizable})
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
            


    def _getContainerStack(self, sourceDescription: ContainerId):
        ''' Retieves and returns a property source based on a description string '''

        containerStack = None

        if sourceDescription == ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK:
            containerStack = Application.getInstance().getGlobalContainerStack()
        elif sourceDescription == ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK:
            containerStack = ExtruderManager.getInstance().getActiveExtruderStack()
        else:
            message = f'Unrecognized container stack descriptor "{sourceDescription}"'
            raise TypeError(message)

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
