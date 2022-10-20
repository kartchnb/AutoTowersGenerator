# This script was adapted (although largely taken wholesale) from the 
# TempFanTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 21 Sep 2022: 
#   Updated based on Version 1.6 of 5axes' TempFanTower processing script, including the "maintain bridge value" option
# Version 2.2 - 1 Oct 2022:
#   Updated based on 5axes' suggestion to ignore commented-out gcode

from UM.Logger import Logger

__version__ = '2.2'



def is_fan_speed_change_line(line: str) -> bool:
    return line.strip().startswith('M106 S')

def is_fan_off_line(line: str) -> bool:
    return line.strip().startswith('M107')

def is_start_of_bridge(line: str) -> bool:
    return line.strip().startswith(';BRIDGE')

def is_start_of_layer(line: str) -> bool:
    return line.strip().startswith(';LAYER:')



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, maintainBridgeValue, displayOnLcd):
    Logger.log('d', 'AutoTowersGenerator beginning FanTower post-processing')
    Logger.log('d', f'Start speed = {startValue}%')
    Logger.log('d', f'Speed change = {valueChange}%')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')
    Logger.log('d', f'Display on LCD = {displayOnLcd}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';FanTower start fan % = {startValue}, fan % change = {valueChange}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    # Start at the selected starting percentage
    currentValue = startValue

    afterBridge = False

    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:
            # If the fan speed is being changed after a bridge section was printed
            if is_fan_speed_change_line(line) and layerIndex > baseLayers and afterBridge:
                if afterBridge or not maintainBridgeValue:
                    Logger.log('d', f'Resuming fan speed of {currentValue}% after bridge at layer {layerIndex - 2}')
                    lineIndex = lines.index(line)
                    currentFanValue = int((currentValue * 255)/100)  #  100% = 255 pour ventilateur
                    lines[lineIndex] = f'M106 S{currentFanValue} ; AutoTowersGenerator Resuming fan speed of {currentValue}% after bridge'
                    afterBridge = False
                    if displayOnLcd:
                        lines.insert(lineIndex + 1, f'M117 Speed {currentValue}%; AutoTowersGenerator added')
                else:
                    lineIndex = lines.index(line)
                    afterBridge = True

            if is_fan_off_line(line) and layerIndex > baseLayers:
                Logger.log('d', f'Just completed a bridge at layer {layerIndex - 2}')
                afterBridge = True
                lineIndex = lines.index(line)

            if is_start_of_bridge(line):
                afterBridge = False
                lineIndex = lines.index(line)

            if is_start_of_layer(line):
                lineIndex = lines.index(line)

                if layerIndex==baseLayers:
                    Logger.log('d', f'Start of first section at layer {layerIndex - 2} - setting fan speed to {currentValue}%')
                    currentFanValue = int((currentValue * 255)/100)  #  100% = 255 pour ventilateur
                    lines.insert(lineIndex + 1, f'M106 S{currentFanValue} ; AutoTowersGenerator setting fan speed to {currentValue}% for the first section')
                    if displayOnLcd:
                        lines.insert(lineIndex + 2, f'M117 Speed {currentValue}% ; AutoTowersGenerator added')

                if ((layerIndex-baseLayers) % sectionLayers == 0) and (layerIndex > baseLayers):
                    currentValue += valueChange
                    Logger.log('d', f'Start of new section at layer {layerIndex - 2} - setting fan speed to {currentValue}%')
                    currentFanValue = int((currentValue * 255)/100)  #  100% = 255 pour ventilateur
                    lines.insert(lineIndex + 1, f'M106 S{currentFanValue} ; AutoTowersGenerator setting fan speed to {currentValue}% for the next section')
                    if displayOnLcd:
                        lines.insert(lineIndex + 2, f'M117 Speed {currentValue}% ; AutoTowersGenerator added')


        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', 'AutoTowersGenerator completing FanTower post-processing')

    return gcode