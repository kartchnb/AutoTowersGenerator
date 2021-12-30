import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

    minimumWidth: screenScaleFactor * 390;
    minimumHeight: screenScaleFactor * 210;
    width: minimumWidth
    height: minimumHeight
    title: "Temperature Tower"

    // Create aliases to allow easy access to each of the parameters
    property alias startTemp: startTempInput.text
    property alias endTemp: endTempInput.text
    property alias tempChange: tempChangeInput.text
    property alias materialLabel: materialLabelInput.text
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

            Label { text: "Starting Temperature" }

            TextField
            {
                id: startTempInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "009"
                text: "220"
            }

            Label { text: "Ending Temperature" }

            TextField
            {
                id: endTempInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "009"
                text: "180"
            }

            Label { text: "Temperature Change" }

            TextField
            {
                id: tempChangeInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "#009"
                text: "-5"
            }

            Label { text: "Material Label" }

            TextField
            {
                id: materialLabelInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "Xxxx"
                text: "PLA"
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
                    checked: true
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
