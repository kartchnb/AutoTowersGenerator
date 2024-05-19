import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Dialogs 6.2
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
	
	property variant catalog: UM.I18nCatalog { name: "autotowers" }
	
    title: catalog.i18nc("@title", "AutoTowersGenerator v") + manager.pluginVersion + catalog.i18nc("@title", " Settings")

    buttonSpacing: UM.Theme.getSize("default_margin").width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height) + UM.Theme.getSize("button").height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor("main_background")

    RowLayout
    {
        id: contents
        width: dialog.width - 2 * UM.Theme.getSize("default_margin").width
        spacing: UM.Theme.getSize("default_margin").width

        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.preferredHeight: icon.height
            Layout.fillHeight: true
            color: UM.Theme.getColor("primary_button")

            Image
            {
                id: icon
                source: Qt.resolvedUrl("../../Images/autotowersgenerator_icon.png")
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        } 

        GridLayout
        {
            columns: 2
            rowSpacing: UM.Theme.getSize("default_lining").height
            columnSpacing: UM.Theme.getSize("default_margin").width
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignTop

            UM.Label 
            { 
                text: catalog.i18nc("@label", "OpenSCAD path")
                MouseArea 
                {
                    id: openscad_path_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            RowLayout
            {
                spacing: UM.Theme.getSize("default_margin").width
                
                Cura.TextField
                {
                    id: openScadPath
                    Layout.fillWidth: true
                    text: manager.openScadPathSetting
                }

                Cura.PrimaryButton
                {
                    text: catalog.i18nc("@button", "...")
                    onClicked: fileDialog.open()
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The path to the OpenSCAD executable.<p>If it is in the current path or installed in an expected location, the plugin should find it automatically.<p>You can manually set or override the path here.<p>Clearing out this value will cause the plugin to attempt to automatically locate OpenSCAD again.")
                visible: openscad_path_mouse_area.containsMouse
            }
            FileDialog
            {
                id: fileDialog
                options: FileDialog.ReadOnly
                onAccepted: openScadPath.text = urlToStringPath(selectedFile)

                function urlToStringPath(url)
                {
                    // Convert the url to a usable string path
                    var path = url.toString()
                    path = path.replace(/^(file:\/{3})|(qrc:\/{2})|(http:\/{2})/, "")
                    path = decodeURIComponent(path)

                    // On Linux, a forward slash needs to be prepended to the resulting path
                    // I'm guessing this is needed on Mac OS, as well, but can't test it
                    if (manager.os == "linux" || manager.os == "darwin") path = "/" + path
                    
                    // Return the resulting path
                    return path
                }
            }

            UM.Label 
            { 
                text: catalog.i18nc("@label", "Correct print settings")
                MouseArea 
                {
                    id: correct_print_settings_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            UM.CheckBox
            {
                id: correctPrintSettings
                checked: manager.correctPrintSettings
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "When checked, the plugin will automatically correct print settings for best results when printing the selected tower.")
                visible: correct_print_settings_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: catalog.i18nc("@label", "Enable LCD messages")
                MouseArea 
                {
                    id: enable_lcd_messages_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            UM.CheckBox
            {
                id: enableLcdMessages
                checked: manager.enableLcdMessagesSetting
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "Selects whether tower parameter changes (temperature, speed, etc) are displayed to your printer's LCD.<p>Information is displayed using the M117 command, which can cause issues with some printers (The Dremel 3D45, for instance)<p>Deselect this if you are noticing issues.")
                visible: enable_lcd_messages_mouse_area.containsMouse
            }
			
			UM.Label 
            { 
                text: catalog.i18nc("@label", "Advanced GCode Comments")
                MouseArea 
                {
                    id: enable_advanced_gcode_comments_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            UM.CheckBox
            {
                id: enableAdvancedGcodeComments
                checked: manager.enableAdvancedGcodeCommentsSetting
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "If enabled, this option allows more comments to be added to the modified GCode.<p>The use of more comments allows better control of the modifications made, but increases the size of the final code.")
                visible: enable_advanced_gcode_comments_mouse_area.containsMouse
            }
			
			UM.Label 
            { 
                text: catalog.i18nc("@label", "Descriptive File Names")
                MouseArea 
                {
                    id: enable_descriptive_file_names_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            UM.CheckBox
            {
                id: enableDescriptiveFileNames
                checked: manager.enableDescriptiveFileNamesSetting
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "If enabled, gcode will be created with descriptive file names.<p>These file names may be too long for some printers to handle and can be deselected if needed.")
                visible: enable_descriptive_file_names_mouse_area.containsMouse
            }
        }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: catalog.i18nc("@button", "Cancel")
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: catalog.i18nc("@button", "OK")
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        manager.openScadPathSetting = openScadPath.text
        manager.enableLcdMessagesSetting = enableLcdMessages.checked
        manager.enableAdvancedGcodeCommentsSetting = enableAdvancedGcodeComments.checked
        manager.enableDescriptiveFileNamesSetting = enableDescriptiveFileNames.checked
		manager.correctPrintSettings = correctPrintSettings.checked
    }

}
