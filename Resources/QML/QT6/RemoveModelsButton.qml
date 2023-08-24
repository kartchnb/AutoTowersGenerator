import UM 1.6 as UM
import Cura 1.7 as Cura

Cura.SecondaryButton
{
    height: UM.Theme.getSize("action_button").height
	
	property variant catalog: UM.I18nCatalog { name: "autotowers" }
	
    tooltip:
    {
        var tipText = catalog.i18nc("@text", "Remove the AutoTower Model");
        return tipText
    }
    toolTipContentAlignment: UM.Enums.ContentAlignment.AlignLeft
    onClicked: manager.removeButtonClicked()
    iconSource: Qt.resolvedUrl("../../Images/remove_tower_icon.svg")
    visible: manager.autoTowerGenerated
    fixedWidthMode: false
	
}
