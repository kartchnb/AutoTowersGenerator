# This script was adapted (although largely taken wholesale) from the 
# TempFanTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1

from UM.Logger import Logger

__version__ = '2.0'



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers):
    Logger.log('d', 'AutoTowersGenerator beginning FanTower post-processing')
    Logger.log('d', f'Start speed = {startValue}%')
    Logger.log('d', f'Speed change = {valueChange}%')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';FanTower start fan % = {startValue}, fan % change = {valueChange}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    # Start at the selected starting percentage
    currentValue = startValue

    afterbridge = False

    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:
            if line.startswith('M106 S') and (layerIndex-baseLayers)>0 and afterbridge:
                Logger.log('d', f'Resuming fan speed of {currentValue}% after bridge at layer {layerIndex - 2}')
                lineIndex = lines.index(line)
                currentFanValue = int((currentValue * 255)/100)  #  100% = 255 pour ventilateur
                lines[lineIndex] = f'M106 S{currentFanValue} ; AutoTowersGenerator Resuming fan speed of {currentValue}% after bridge'
                afterbridge = False
                lines.insert(lineIndex + 1, f'M117 Speed {currentValue}%')

            if line.startswith('M107') and (layerIndex-baseLayers)>0:
                Logger.log('d', f'Just completed a bridge at layer {layerIndex - 2}')
                afterbridge = True
                lineIndex = lines.index(line)

            if line.startswith(";LAYER:"):
                lineIndex = lines.index(line)

                if (layerIndex==baseLayers):
                    Logger.log('d', f'Start of first section at layer {layerIndex - 2} - setting fan speed to {currentValue}%')
                    currentFanValue = int((currentValue * 255)/100)  #  100% = 255 pour ventilateur
                    lines.insert(lineIndex + 1, f'M106 S{currentFanValue} ; AutoTowersGenerator setting fan speed to {currentValue}% for the first section')
                    lines.insert(lineIndex + 2, f'M117 Speed {currentValue}% ; AutoTowersGenerator added')

                if ((layerIndex-baseLayers) % sectionLayers == 0) and ((layerIndex-baseLayers)>0):
                    currentValue += valueChange
                    Logger.log('d', f'Start of new section at layer {layerIndex - 2} - setting fan speed to {currentValue}%')
                    currentFanValue = int((currentValue * 255)/100)  #  100% = 255 pour ventilateur
                    lines.insert(lineIndex + 1, f'M106 S{currentFanValue} ; AutoTowersGenerator setting fan speed to {currentValue}% for the next section')
                    lines.insert(lineIndex + 2, f'M117 Speed {currentValue}% ; AutoTowersGenerator added')


        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', 'AutoTowersGenerator completing FanTower post-processing')

    return gcode