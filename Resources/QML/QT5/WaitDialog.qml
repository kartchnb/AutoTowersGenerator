import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Generating the Tower"

    width: screenScaleFactor * 445
    height: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height)
    minimumWidth: width
    minimumHeight: height
    maximumWidth: width
    maximumHeight: height
    flags: Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint;

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
                source: Qt.resolvedUrl("../../Images/openscad_icon.png")
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

       Label
        {
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: "Please wait while OpenSCAD generates the Auto Tower\n\nThis may take a few minutes"
            wrapMode: Text.Wrap
        }
    }
}
