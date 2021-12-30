import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

    minimumWidth: screenScaleFactor * 390;
    minimumHeight: screenScaleFactor * 200;
    width: minimumWidth
    height: minimumHeight
    title: "Retraction Tower (Speed)"

    // Create aliases to allow easy access to each of the parameters
    property alias startValue: startValueInput.text
    property alias endValue: endValueInput.text
    property alias valueChange: valueChangeInput.text
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
                source: "retracttower_icon.png"
                anchors.horizontalCenter: sidebar.horizontalCenter
                anchors.verticalCenter: sidebar.verticalCenter
            }
        }

        GridLayout
        {
            id: gridLayout

            columns: 2

            Label { text: "Starting Speed" }

            TextField
            {
                id: startValueInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "09"
                text: "10"
            }

            Label { text: "Ending Speed" }

            TextField
            {
                id: endValueInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "09"
                text: "40"
            }

            Label { text: "Speed Change" }

            TextField
            {
                id: valueChangeInput
                Layout.preferredWidth: textFieldWidth
                inputMask: "09"
                text: "10"
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
