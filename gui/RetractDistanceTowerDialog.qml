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

    // Create aliases to allow easy access to each of the parameters
    property alias startValue: startValueInput.text
    property alias endValue: endValueInput.text
    property alias valueChange: valueChangeInput.text
    property alias towerDescription: towerDescriptionInput.text

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

            Label 
            { 
                text: "Starting Distance" 
            }
            TextField
            {
                id: startValueInput
                validator : RegExpValidator { regExp : /[0-9]*(\.[0-9]+)?/ }
                text: "1"
            }

            Label 
            { 
                text: "Ending Distance" 
            }
            TextField
            {
                id: endValueInput
                validator : RegExpValidator { regExp : /[0-9]*(\.[0-9]+)?/ }
                text: "6"
            }

            Label 
            { 
                text: "Distance Change" 
            }
            TextField
            {
                id: valueChangeInput
                validator : RegExpValidator { regExp : /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: "1"
            }

            Label 
            { 
                text: "Tower Description" 
            }
            TextField
            {
                id: towerDescriptionInput
                Layout.fillWidth: true
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
