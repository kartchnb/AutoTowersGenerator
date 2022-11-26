import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "AutoTowersGenerator v" + manager.pluginVersion + " Settings"

    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height) + UM.Theme.getSize("button").height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

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

            Label 
            { 
                text: "OpenSCAD path" 
            }
            TextField
            {
                id: openScadPath
                text: manager.openScadPathSetting
            }

            UM.Label 
            { 
                text: "Correct print settings" 
            }
            UM.CheckBox
            {
                id: correctPrintSettings
                checked: manager.correctPrintSettings
            }

            UM.Label 
            { 
                text: "Enable LCD messages" 
            }
            Cura.CheckBox
            {
                id: enableLcdMessages
                checked: manager.enableLcdMessagesSetting
            }
        }
    }

    rightButtons: Button
    {
        text: "OK"
        onClicked: dialog.accept()
    }

    leftButtons: Button
    {
        text: "Cancel"
        onClicked: dialog.reject()
    }

    onAccepted:
    {
        manager.openScadPathSetting = openScadPath.text
        manager.enableLcdMessagesSetting = enableLcdMessages.checked
        manager.correctPrintSettings = correctPrintSettings
    }
}
