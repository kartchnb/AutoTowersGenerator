import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

property int screenScaleFactor: 1
    minimumWidth: screenScaleFactor * 410;
    minimumHeight: screenScaleFactor * 240;
    width: minimumWidth
    height: minimumHeight
    title: "Speed Tower"

    // Create aliases to allow easy access to each of the parameters
    property alias speedType: speedTypeInput.currentText
    property alias startSpeed: startSpeedInput.text
    property alias endSpeed: endSpeedInput.text
    property alias speedChange: speedChangeInput.text
    property alias towerDescription: towerDescriptionInput.text
    property alias displayOnLcd: displayOnLcdInput.checked

    // Common values
    property int textFieldWidth: 50

    Row
    {
        spacing: 10

        Rectangle
        {
            id: sidebar
            width: 100
            height: dialog.height
            color: "#00017b"
            Image
            {
                source: "temptower_icon.png"
                anchors.horizontalCenter: sidebar.horizontalCenter
                anchors.verticalCenter: sidebar.verticalCenter
            }
        }

        GridLayout
        {
            id: gridLayout

            columns: 2

            Label { text: "Speed Type to Control" }

            ComboBox 
            {
                id: speedTypeInput
                model: ["acceleration", "jerk", "junction", "Marlin linear", "RepRap pressure"]
            }

            Label { text: "Starting Speed" }

            TextField
            {
                id: startSpeedInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "009"
                text: "8"
            }

            Label { text: "Ending Speed" }

            TextField
            {
                id: endSpeedInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "009"
                text: "32"
            }

            Label { text: "Speed Change" }

            TextField
            {
                id: speedChangeInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "#009"
                text: "4"
            }
    
            Label { text: "Tower Description" }

            TextField
            {
                id: towerDescriptionInput
                text: ""
            }

            Column
            {
                CheckBox
                {
                    id: displayOnLcdInput
                    text: "Display details on LCD"
                }
            }
        }
    }

    rightButtons: Button
    {
        id: generateButton
        text: "Generate"
        onClicked: dialog.accept()
    }

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
