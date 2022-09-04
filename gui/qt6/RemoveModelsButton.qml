import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM

Cura.SecondaryButton
{
    height: UM.Theme.getSize("action_button").height
    tooltip:
    {
        var tipText = "Remove the AutoTower Model";
        return tipText
    }
    toolTipContentAlignment: UM.Enums.ContentAlignment.AlignLeft
    onClicked: manager.removeButtonClicked()
    iconSource: "../remove_tower_icon.png"
    visible: manager.autoTowerGenerated
    fixedWidthMode: false
}
