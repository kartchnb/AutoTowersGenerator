import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Fan Tower"

property int screenScaleFactor: 1 // test_gui.sh
    minimumWidth: screenScaleFactor * 445;
    minimumHeight: screenScaleFactor * 245;
    width: minimumWidth
    height: minimumHeight

    // Create aliases to allow easy access to each of the parameters
    property alias percentChange: percentChangeInput.text
    property alias towerDescription: towerDescriptionInput.text

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
            Layout.alignment: Qt.AlignTop

            Label 
            { 
                text: "Starting Fan Percent" 
            }
            TextField
            {
                id: startPercentInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: ""
            }

            Label 
            { 
                text: "Ending Fan Percent" 
            }
            TextField
            {
                id: endPercentInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: ""
            }

            Label 
            { 
                text: "Fan Speed Change" 
            }
            TextField
            {
                id: percentChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: ""
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
onClicked: close() // test_gui.sh
    }

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
