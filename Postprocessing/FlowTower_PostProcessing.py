# This script was adapted (although largely taken wholesale) from the 
# FlowTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 1.0 - 21 Sep 2022: 
#   Taken from version 1.1 of 5axes' FlowTower script

from UM.Logger import Logger
from UM.Application import Application
import re 
from enum import Enum

__version__ = '1.0'

def is_start_of_layer(line: str) -> bool:
    return line.startswith(';LAYER:')



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, towerType):
    Logger.log('d', 'AutoTowersGenerator beginning FlowTower post-processing')
    Logger.log('d', f'Starting value = {startValue}')
    Logger.log('d', f'Value change = {valueChange}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';FlowTower start flow = {startValue}, flow change = {valueChange}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    # Start at the selected starting temperature
    currentValue = startValue

    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:
            # If this is the start of the current layer
            if is_start_of_layer(line):
                lineIndex = lines.index(line)

                # If the end of the base has been reached, start modifying the temperature
                if layerIndex == baseLayers:
                    Logger.log('d', f'Start of first section layer {layerIndex - 2} - setting flow rate to {currentValue}')
                    lines.insert(lineIndex + 1, f'M221 S{currentValue} ; AutoTowersGenerator setting flow rate to {currentValue} for first section')
                    lines.insert(lineIndex + 2, f'M117 Flow {currentValue} ; AutoTowersGenerator added')

                # If the end of a section has been reached, decrease the temperature
                if ((layerIndex - baseLayers) % sectionLayers == 0) and (layerIndex > baseLayers):
                    currentValue += valueChange
                    Logger.log('d', f'New section at layer {layerIndex - 2} - setting flow rate to {currentValue}')
                    lines.insert(lineIndex + 1, f'M221 S{currentValue} ; AutoTowersGenerator setting flow rate to {currentValue} for next section')
                    lines.insert(lineIndex + 2, f'M117 Flow {currentValue} ; AutoTowersGenerator addeds')

        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', 'AutoTowersGenerator completing FlowTower post-processing')
    
    return gcode