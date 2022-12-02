import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Fan Tower"

    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height) + UM.Theme.getSize("button").height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    // Define the width of the number input text boxes
    property int numberInputWidth: UM.Theme.getSize("button").width

    RowLayout
    {
        id: contents
        width: dialog.width - 2 * UM.Theme.getSize("default_margin").width
        spacing: UM.Theme.getSize("default_margin").width

        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.preferredHeight: icon.height
            Layout.fillHeight: true
            color: UM.Theme.getColor("primary_button")

            Image
            {
                id: icon
                source: Qt.resolvedUrl("../../Images/fantower_icon.png")
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
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
                text: "Starting Fan Speed %"
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startFanSpeedStr
                onTextChanged: if (manager.startFanSpeedStr != text) manager.startFanSpeedStr = text
            }

            Label 
            { 
                text: "Ending Fan Speed %" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endFanSpeedStr
                onTextChanged: if (manager.endFanSpeedStr != text) manager.endFanSpeedStr = text
            }

            Label 
            { 
                text: "Fan Speed % Change" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.fanSpeedChangeStr
                onTextChanged: if (manager.fanSpeedChangeStr != text) manager.fanSpeedChangeStr = text
            }

            Label 
            { 
                text: "Tower Label" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /.{0,3}/ }
                text: manager.towerLabelStr
                onTextChanged: if (manager.towerLabelStr != text) manager.towerLabelStr = text
            }

            Label 
            { 
                text: "Tower Description" 
            }
            TextField
            {
                Layout.fillWidth: true
                text: manager.towerDescriptionStr
                onTextChanged: if (manager.towerDescriptionStr != text) manager.towerDescriptionStr = text
            }

            Label
            {
                text: "Maintain Value for Bridges"
            }
            CheckBox
            {
                id: maintainBridgeValue
                checked: manager.maintainBridgeValue
                onClicked: manager.maintainBridgeValue = maintainBridgeValue.checked
            }
        }
    }

    rightButtons: Button
    {
        text: "OK"
        onClicked: dialog.accept()
    }

    leftButtons: Button
    {
        text: "Cancel"
        onClicked: dialog.reject()
    }

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
