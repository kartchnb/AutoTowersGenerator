import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "Bed Level Print"

    buttonSpacing: UM.Theme.getSize("default_margin").width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height) + UM.Theme.getSize("button").height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor("main_background")

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
                source: Qt.resolvedUrl("../../Images/" + selectedBedLevelPrintType.model[selectedBedLevelPrintType.currentIndex]["icon"])
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

            UM.Label
            {
                text: "Bed Level Print Type"
                MouseArea 
                {
                    id: bed_level_print_type_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                id: selectedBedLevelPrintType
                Layout.fillWidth: true
                model: manager.bedLevelPrintTypesModel
                textRole: "value"

                onCurrentIndexChanged: 
                {
                    manager.bedLevelPrintType = model[currentIndex]["value"]
                }
            }
            UM.ToolTip
            {
                text: "The type of bed level print to generate."
                visible: bed_level_print_type_mouse_area.containsMouse
            }

            UM.Label
            {
                text: "Bed Inset %"
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*/ }
                text: manager.bedInsetPercentageStr
                onTextChanged: if (manager.bedInsetPercentageStr != text) manager.bedInsetPercentageStr = text
            }

            UM.Label
            {
                text: "Number of Squares"
                visible: manager.bedLevelPrintType == "Concentric Squares"
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*/ }
                text: manager.numberOfSquaresStr
                onTextChanged: if (manager.numberOfSquaresStr != text) manager.numberOfSquaresStr = text
                visible: manager.bedLevelPrintType == "Concentric Squares"
            }

            UM.Label
            {
                text: "Size in Cells"
                visible: manager.bedLevelPrintType == "Grid"
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*/ }
                text: manager.cellSizeStr
                onTextChanged: if (manager.cellSizeStr != text) manager.cellSizeStr = text
                visible: manager.bedLevelPrintType == "Grid"
            }
        }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: "Cancel"
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: "OK"
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
