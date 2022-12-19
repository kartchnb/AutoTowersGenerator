import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "Bed Level Pattern"

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
                source: Qt.resolvedUrl("../../Images/" + selectedBedLevelPattern.model[selectedBedLevelPattern.currentIndex]["icon"])
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
                text: "Bed Level Pattern Type"
                MouseArea 
                {
                    id: bed_level_Pattern_type_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                id: selectedBedLevelPattern
                Layout.fillWidth: true
                model: manager.bedLevelPatternsModel
                textRole: "value"

                onCurrentIndexChanged: 
                {
                    manager.bedLevelPattern = model[currentIndex]["value"]
                }
            }
            UM.ToolTip
            {
                text: "The type of bed level Pattern to generate.<p>Each pattern covers different parts of the bed in different ways and some are faster than others.<p>The icon on the left side of this dialog will give an idea of what the bed level Pattern type will look like."
                visible: bed_level_Pattern_type_mouse_area.containsMouse
            }

            UM.Label
            {
                text: "Bed Fill %"
                MouseArea 
                {
                    id: bed_inset_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /^[1-9][0-9]?$|^100$/ }
                text: manager.fillPercentageStr
                onTextChanged: if (manager.fillPercentageStr != text) manager.fillPercentageStr = text
            }
            UM.ToolTip
            {
                text: "This controls how much of the printer area the pattern should take up.<p>A value of 100 will result in the entire print area being used and may not work.<p>Values below 75 probably don't make much sense."
                visible: bed_inset_mouse_area.containsMouse
            }

            UM.Label
            {
                text: "Number of Rings"
                visible: manager.bedLevelPattern == "Concentric Squares" || manager.bedLevelPattern == "Concentric Circles"
                MouseArea 
                {
                    id: number_of_squares_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
             }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*/ }
                text: manager.numberOfSquaresStr
                onTextChanged: if (manager.numberOfSquaresStr != text) manager.numberOfSquaresStr = text
                visible: manager.bedLevelPattern == "Concentric Squares" || manager.bedLevelPattern == "Concentric Circles"
            }
            UM.ToolTip
            {
                text: "The number of concentric rings to generate in the pattern."
                visible: number_of_squares_mouse_area.containsMouse
            }

            UM.Label
            {
                text: "Size in Cells"
                visible: manager.bedLevelPattern == "Grid" || manager.bedLevelPattern == "Padded Grid"
                MouseArea 
                {
                    id: size_in_cells_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
             }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*/ }
                text: manager.cellSizeStr
                onTextChanged: if (manager.cellSizeStr != text) manager.cellSizeStr = text
                visible: manager.bedLevelPattern == "Grid" || manager.bedLevelPattern == "Padded Grid"
            }
            UM.ToolTip
            {
                text: "The size of the grid in cells."
                visible: size_in_cells_mouse_area.containsMouse
            }

            UM.Label
            {
                text: "Pad Size"
                visible: manager.bedLevelPattern == "Padded Grid"
                MouseArea 
                {
                    id: pad_size_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
             }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*/ }
                text: manager.padSizeStr
                onTextChanged: if (manager.padSizeStr != text) manager.padSizeStr = text
                visible: manager.bedLevelPattern == "Padded Grid"
            }
            UM.ToolTip
            {
                text: "The size of each of the pads in the pattern."
                visible: pad_size_mouse_area.containsMouse
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
