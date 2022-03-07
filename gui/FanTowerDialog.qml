import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

    minimumWidth: screenScaleFactor * 445;
    minimumHeight: screenScaleFactor * 235;
    width: minimumWidth
    height: minimumHeight
    title: "Fan Tower"

    // Create aliases to allow easy access to each of the parameters
    property alias startPercent: startPercentInput.text
    property alias endPercent: endPercentInput.text
    property alias percentChange: percentChangeInput.text
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
                source: "temptower_icon.png"
                anchors.horizontalCenter: sidebar.horizontalCenter
                anchors.verticalCenter: sidebar.verticalCenter
            }
        }

        GridLayout
        {
            id: gridLayout

            columns: 2

            Label { text: "Starting Fan Percent" }

            TextField
            {
                id: startPercentInput
                Layout.preferredWidth: textFieldWidth
                validator : RegExpValidator { regExp : /[0-9]*(\.[0-9]+)?/ }
                text: "100"
            }

            Label { text: "Ending Fan Percent" }

            TextField
            {
                id: endPercentInput
                Layout.preferredWidth: textFieldWidth
                validator : RegExpValidator { regExp : /[0-9]*(\.[0-9]+)?/ }
                text: "50"
            }

            Label { text: "Temperature Change" }

            TextField
            {
                id: percentChangeInput
                Layout.preferredWidth: textFieldWidth
                validator : RegExpValidator { regExp : /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: "-10"
            }

            Label { text: "Tower Description" }

            TextField
            {
                id: towerDescriptionInput
                text: ""
                width: parent.width
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
