// This dialog is a placeholder for when I get around to incorporating a speed tower
import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Speed Tower"

    minimumWidth: screenScaleFactor * 425;
    minimumHeight: screenScaleFactor * 300;
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
                source: "../speedtower_icon.png"
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
                text: "Speed Type to Control" 
            }
            ComboBox 
            {
                id: speedTypeInput
                model: ["acceleration", "jerk", "junction", "Marlin linear", "RepRap pressure"]
            }

            Label 
            { 
                text: "Starting Speed" 
            }
            TextField
            {
                id: startSpeedInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: "8"
            }

            Label 
            { 
                text: "Ending Speed" 
            }
            TextField
            {
                id: endSpeedInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: "32"
            }

            Label 
            { 
                text: "Speed Change" 
            }
            TextField
            {
                id: speedChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: "4"
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
