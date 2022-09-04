import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.5 as UM
import Cura 1.0 as Cura

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
