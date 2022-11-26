import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "AutoTowersGenerator v" + manager.pluginVersion + " Settings"

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
                text: "OpenSCAD path" 
                MouseArea 
                {
                    id: openscad_path_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                id: openScadPath
                Layout.fillWidth: true
                text: manager.openScadPathSetting
            }
            UM.ToolTip
            {
                text: "The path to the OpenSCAD executable.<p>If it is in the current path or installed in an expected location, the plugin should find it automatically.<p>You can manually set or override the path here.<p>Clearing out this value will cause the plugin to attempt to automatically locate OpenSCAD again."
                visible: openscad_path_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Correct print settings" 
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
                text: "When checked, the plugin will automatically correct print settings for best results when printing the selected tower."
                visible: correct_print_settings_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Enable LCD messages" 
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
                text: "Selects whether tower parameter changes (temperature, speed, etc) are displayed to your printer's LCD.<p>Information is displayed using the M117 command, which can cause issues with some printers (The Dremel 3D45, for instance)<p>Deselect this if you are noticing issues."
                visible: enable_lcd_messages_mouse_area.containsMouse
            }
        }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: "Cancel"
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: "OK"
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        manager.openScadPathSetting = openScadPath.text
        manager.enableLcdMessagesSetting = enableLcdMessages.checked
        manager.correctPrintSettings = correctPrintSettings.checked
    }

}
