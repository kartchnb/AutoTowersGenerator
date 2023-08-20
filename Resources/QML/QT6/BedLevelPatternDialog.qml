import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: 'Bed Level Pattern'

    buttonSpacing: UM.Theme.getSize('default_margin').width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize('default_margin').height) + UM.Theme.getSize('button').height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor('main_background')

    // Define the width of the number input text boxes
    property int numberInputWidth: UM.Theme.getSize('button').width

    // Only display customizable options when a prest is not selected
    property bool show_custom_options: dataModel.presetName == 'Custom'
    


    RowLayout
    {
        id: contents
        width: dialog.width - 2 * UM.Theme.getSize('default_margin').width
        spacing: UM.Theme.getSize('default_margin').width

        // Display the icon for this tower
        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.preferredHeight: icon.height
            Layout.fillHeight: true
            color: UM.Theme.getColor('primary_button')

            Image
            {
                id: icon
                source: Qt.resolvedUrl('../../Images/' + dataModel.patternIcon)
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        GridLayout
        {
            columns: 2
            rowSpacing: UM.Theme.getSize('default_lining').height
            columnSpacing: UM.Theme.getSize('default_margin').width
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignTop

            // Preset option
            UM.Label
            {
                text: 'Preset'
                MouseArea
                {
                    id: preset_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                Layout.fillWidth: true
                model: allow_customization ? dataModel.presetsModel.concat({'name': 'Custom'}) : dataModel.presetsModel
                textRole: 'name'
                currentIndex: dataModel.presetIndex

                onCurrentIndexChanged:
                {
                    dataModel.presetIndex = currentIndex
                }
            }

            // Bed level pattern option
            UM.Label
            {
                text: 'Pattern'
                visible: show_custom_options
                MouseArea 
                {
                    id: pattern_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                id: selected_pattern
                Layout.fillWidth: true
                model: dataModel.patternsModel
                textRole: 'name'
                visible: show_custom_options
                currentIndex: dataModel.patternIndex

                onCurrentIndexChanged: 
                {
                    dataModel.patternIndex = currentIndex
                }
            }
            UM.ToolTip
            {
                text: 'The type of bed level Pattern to generate.<p>Each pattern covers different parts of the bed in different ways and some are faster than others.<p>The icon on the left side of this dialog will give an idea of what the bed level Pattern type will look like.'
                visible: pattern_mouse_area.containsMouse
            }

            // Bed fill %
            UM.Label
            {
                text: 'Bed Fill %'
                visible: show_custom_options
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
                text: dataModel.fillPercentageStr
                visible: show_custom_options

                onTextChanged: 
                {
                    if (dataModel.fillPercentageStr != text) dataModel.fillPercentageStr = text
                }
            }
            UM.ToolTip
            {
                text: 'This controls how much of the printer area the pattern should take up.<p>A value of 100 will result in the entire print area being used and may not work.<p>Values below 75 are probably not useful.<p>90 is a good default.'
                visible: bed_inset_mouse_area.containsMouse
            }

            // The number of rings
            UM.Label
            {
                text: 'Number of Rings'
                visible: show_custom_options && (selected_pattern.currentText == 'Spiral Squares' || selected_pattern.currentText == 'Concentric Squares' || selected_pattern.currentText == 'Concentric Circles')
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
                text: dataModel.numberOfRingsStr
                visible: show_custom_options && (selected_pattern.currentText == 'Spiral Squares' || selected_pattern.currentText == 'Concentric Squares' || selected_pattern.currentText == 'Concentric Circles')
                
                onTextChanged: 
                {
                    if (dataModel.numberOfRingsStr != text) dataModel.numberOfRingsStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The number of concentric rings to generate in the pattern.'
                visible: number_of_squares_mouse_area.containsMouse
            }

            // Size in cells
            UM.Label
            {
                text: 'Size in Cells'
                visible: show_custom_options && (selected_pattern.currentText == 'Grid' || selected_pattern.currentText == 'Padded Grid')
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
                text: dataModel.cellSizeStr
                visible: show_custom_options && (selected_pattern.currentText == 'Grid' || selected_pattern.currentText == 'Padded Grid')
                
                onTextChanged: 
                {
                    if (dataModel.cellSizeStr != text) dataModel.cellSizeStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The size of the grid in cells.'
                visible: size_in_cells_mouse_area.containsMouse
            }

            // Pad size
            UM.Label
            {
                text: 'Pad Size'
                visible: show_custom_options && (selected_pattern.currentText == 'Padded Grid')
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
                text: dataModel.padSizeStr
                visible: show_custom_options && selected_pattern.currentText == 'Padded Grid'
                
                onTextChanged: 
                {
                    if (dataModel.padSizeStr != text) dataModel.padSizeStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The size of each of the pads in the pattern.'
                visible: pad_size_mouse_area.containsMouse
            }
        }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: 'Cancel'
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: 'OK'
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        controller.dialogAccepted()
    }
}
