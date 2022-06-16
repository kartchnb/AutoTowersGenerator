import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "AutoTowersGenerator Settings"

property int screenScaleFactor: 1 // test_gui.sh
    minimumWidth: screenScaleFactor * 445;
    minimumHeight: screenScaleFactor * 245;
    width: minimumWidth
    height: minimumHeight

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
                source: "plugin_icon.png"
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
                text: "OpenSCAD path" 
            }
            TextField
            {
                id: openScadPath
                text: manager.openScadPath
                onTextChanged: if (manager.openScadPath != text) manager.openScadPath = text
            }
        }
    }
}
