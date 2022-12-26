import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11
import QtQuick.Dialogs 1.0

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "AutoTowersGenerator v" + manager.pluginVersion + " Settings"

    minimumWidth: screenScaleFactor * 500
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
            RowLayout
            {
                spacing: UM.Theme.getSize("default_margin").width

                TextField
                {
                    id: openScadPath
                    Layout.fillWidth: true
                    text: manager.openScadPathSetting
                }

                Button
                {
                    text: "..."
                    onClicked: fileDialog.open()
                }
            }
            FileDialog
            {
                id: fileDialog
                onAccepted: openScadPath.text = urlToStringPath(fileUrl)

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

            Label 
            { 
                text: "Correct print settings" 
            }
            CheckBox
            {
                id: correctPrintSettings
                checked: manager.correctPrintSettings
            }

            Label 
            { 
                text: "Enable LCD messages" 
            }
            CheckBox
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
        manager.correctPrintSettings = correctPrintSettings.checked
    }
}
