# This script was heavily adapted from the TempFanTower script developed by
# 5axes as part of his excellent CalibrationShapes plugin

from UM.Logger import Logger

__version__ = '1.0'

def execute(gcode, startTemp, tempChange, sectionLayers, baseLayers):
    Logger.log('d', 'Begin TempTower post-processing')
    Logger.log('d', f'Starting temperature = {startTemp}')
    Logger.log('d', f'Temperature change = {tempChange}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';TempTower start temp = {startTemp}, temp change = {tempChange}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    # Start at the selected starting temperature
    currentTemp = startTemp

    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:
            # If this is the start of the current layer
            if line.startswith(';LAYER:'):
                lineIndex = lines.index(line)

                # If the end of the base has been reached, start modifying the temperature
                if (layerIndex == baseLayers):
                    Logger.log('d', f'Start of first section layer {layerIndex - 2} - setting temp to {currentTemp}')
                    lines.insert(lineIndex + 1, f'M104 S{currentTemp} ; AutoTowersGenerator Setting temperature to {currentTemp} for first section')
                    lines.insert(lineIndex + 2, f'M117 Temp {currentTemp} ; AutoTowersGenerator Added')

                # If the end of a section has been reached, decrease the temperature
                if ((layerIndex - baseLayers) % sectionLayers == 0) and ((layerIndex - baseLayers) > 0):
                    currentTemp += tempChange
                    Logger.log('d', f'New section at layer {layerIndex - 2} - setting temp to {currentTemp}')
                    lines.insert(lineIndex + 1, f'M104 S{currentTemp} ; AutoTowersGenerator Setting temperature to {currentTemp} for next section')
                    lines.insert(lineIndex + 2, f'M117 Temp {currentTemp} ; AutoTowersGenerator Addeds')

        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', 'End Temp Tower post-processing')
    
    return gcode