import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Retraction Tower (Speed)"

    minimumWidth: screenScaleFactor * 435;
    minimumHeight: screenScaleFactor * 245;
    width: minimumWidth
    height: minimumHeight

    // Define the width of the text input text boxes
    property int numberInputWidth: screenScaleFactor * 100

    RowLayout
    {
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").width

        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.fillHeight: true
            color: '#00017b'

            Image
            {
                id: icon
                source: "retracttower_icon.png"
                anchors.verticalCenter: parent.verticalCenter
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
                text: "Starting Speed" 
            }
            TextField
            {
                id: startValueInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startSpeedStr
                onTextChanged: if (manager.startSpeedStr != text) manager.startSpeedStr = text
            }

            Label 
            { 
                text: "Ending Speed" 
            }
            TextField
            {
                id: endValueInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endSpeedStr
                onTextChanged: if (manager.endSpeedStr != text) manager.endSpeedStr = text
            }

            Label 
            { 
                text: "Speed Change" 
            }
            TextField
            {
                id: valueChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.speedChangeStr
                onTextChanged: if (manager.speedChangeStr != text) manager.speedChangeStr = text
            }

            Label 
            { 
                text: "Tower Description" 
            }
            TextField
            {
                id: towerDescriptionInput
                Layout.fillWidth: true
                text: manager.towerDescriptionStr
                onTextChanged: if (manager.towerDescriptionStr != text) manager.towerDescriptionStr = text
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
