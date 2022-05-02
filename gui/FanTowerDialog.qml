import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Fan Tower"

    minimumWidth: screenScaleFactor * 445;
    minimumHeight: screenScaleFactor * 245;
    width: minimumWidth
    height: minimumHeight

    // Create aliases to allow easy access to each of the parameters
    property alias startPercent: startPercentInput.text
    property alias endPercent: endPercentInput.text
    property alias percentChange: percentChangeInput.text
    property alias towerDescription: towerDescriptionInput.text

    RowLayout
    {
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").width

        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.fillHeight: true
            color: "#00017b"

            Image
            {
                id: icon
                source: "fantower_icon.png"
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
                text: "Starting Fan Percent" 
            }
            TextField
            {
                id: startPercentInput
                validator : RegExpValidator { regExp : /[0-9]*(\.[0-9]+)?/ }
                text: "100"
            }

            Label 
            { 
                text: "Ending Fan Percent" 
            }
            TextField
            {
                id: endPercentInput
                validator : RegExpValidator { regExp : /[0-9]*(\.[0-9]+)?/ }
                text: "50"
            }

            Label 
            { 
                text: "Fan Speed Change" 
            }
            TextField
            {
                id: percentChangeInput
                validator : RegExpValidator { regExp : /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: "-10"
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
