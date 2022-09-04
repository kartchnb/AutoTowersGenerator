import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Retraction Tower (Distance)"

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
                source: "../retracttower_icon.png"
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

            Label 
            { 
                text: "Starting Distance" 
            }
            TextField
            {
                id: startValueInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startDistanceStr
                onTextChanged: if (manager.startDistanceStr != text) manager.startDistanceStr = text
            }

            Label 
            { 
                text: "Ending Distance" 
            }
            TextField
            {
                id: endValueInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endDistanceStr
                onTextChanged: if (manager.endDistanceStr != text) manager.endDistanceStr = text
            }

            Label 
            { 
                text: "Distance Change" 
            }
            TextField
            {
                id: valueChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.distanceChangeStr
                onTextChanged: if (manager.distanceChangeStr != text) manager.distanceChangeStr = text
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
