import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

    minimumWidth: screenScaleFactor * 390;
    minimumHeight: screenScaleFactor * 200;
    width: minimumWidth
    height: minimumHeight
    title: "Retraction Tower (Distance)"

    // Create aliases to allow easy access to each of the parameters
    property alias startValue: startValueInput.text
    property alias endValue: endValueInput.text
    property alias valueChange: valueChangeInput.text
    property alias towerDescription: towerDescriptionInput.text

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

            Label { text: "Starting Distance" }

            TextField
            {
                id: startValueInput
                Layout.preferredWidth: textFieldWidth
                validator : RegExpValidator { regExp : /[0-9]+(\.[0-9]+)?/ }
                text: "1"
            }

            Label { text: "Ending Distance" }

            TextField
            {
                id: endValueInput
                Layout.preferredWidth: textFieldWidth
                validator : RegExpValidator { regExp : /[0-9]+(\.[0-9]+)?/ }
                text: "6"
            }

            Label { text: "Distance Change" }

            TextField
            {
                id: valueChangeInput
                Layout.preferredWidth: textFieldWidth
                validator : RegExpValidator { regExp : /[+-]?[0-9]+(\.[0-9]+)?/ }
                text: "1"
            }

            Label { text: "Tower Description" }

            TextField
            {
                id: towerDescriptionInput
                text: ""
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
