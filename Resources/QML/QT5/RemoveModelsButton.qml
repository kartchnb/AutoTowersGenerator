import UM 1.2 as UM
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
    iconSource: Qt.resolvedUrl("../../Images/remove_tower_icon.svg")
    visible: manager.autoTowerGenerated
    fixedWidthMode: false
}
