# This script modifies the printing speed for a print speed tower
#
# Cura does not use a single "print speed" when slicing a model, but uses
# different values for infill, inner walls, outer walls, etc.
# This script modifies each section of the speed tower while maintaining the
# different speeds, so it should accurately represent how Cura would slice
# for each speed.
#
# Version 1.0 - 29 Sep 2022:
#   Split off from MiscSpeedTower_PostProcessing to focus exclusively on print speed towers
# Version 1.1 - 05 Nov 2022:
#   Renamed from TravelSpeedTower_PostProcessing.py to PrintSpeedTower_PostProcessing.py 
#       to better match what it actually does
# Version 1.2 - 05 Nov 2022:
#   Fixed an issue with recognizing decimal speeds in gcode
#   Now only displaying LCD messages for the nominal speed for each layer

import re

from UM.Logger import Logger

__version__ = '1.2'



def is_print_speed_line(line: str) -> bool:
    ''' Check if a given line changes the print speed '''
    return (line.strip().startswith('G0') or line.strip().startswith('G1')) and 'F' in line



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, referenceSpeed, displayOnLcd):
    ''' Post-process gcode sliced by Cura
        startValue = the starting print speed (mm/s)
        valueChange = the amount to change the print speed for each section (mm/s)
        sectionLayers = the number of layers in each tower section
        baseLayers = the number of layers that make up the base of the tower
        referenceSpeed = the print speed selection when the gcode was generated 
            This value is used to determine how print speed settings in the
            gcode are modified for each level '''

    Logger.log('d', 'AutoTowersGenerator beginning SpeedTower (Print Speed) post-processing')
    Logger.log('d', f'Starting speed = {startValue}')
    Logger.log('d', f'Speed change = {valueChange}')
    Logger.log('d', f'Reference speed = {referenceSpeed}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')
    Logger.log('d', f'Reference Speed = {referenceSpeed}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';SpeedTower (Print Speed) start speed = {startValue}, speed change = {valueChange}, reference speed = {referenceSpeed}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the bed adhesion code (skirt, brim, etc)
    # Layer index 1 is the initial layer, which has its own settings
    # Our code starts at index 2
    baseLayers += 2

    currentValue = startValue - valueChange
    
    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Process layers 2+
        if (layerIndex >= baseLayers) and ((layerIndex - baseLayers) % sectionLayers == 0):
            currentValue += valueChange

            Logger.log('d', f'Start of next section at layer {layerIndex  - 2}')
            Logger.log('d', f'Section speed is {currentValue:.1f}mm/s')

            # Iterate over each command line in the layer
            lines = layer.split('\n')
            if displayOnLcd:
                lines.insert(0, f'M117 SPD {currentValue:.1f}mm/s ;AutoTowersGenerator added')
            for line in lines:
                lineIndex = lines.index(line)

                # Modify lines specifying print speed
                if is_print_speed_line(line):
                    # Determine the old speed setting in the gcode
                    oldSpeedResult = re.search(r'F(\d+(?:\.\d*)?)', line.split(';')[0])
                    if oldSpeedResult:
                        oldSpeedString = oldSpeedResult.group(1)
                        oldSpeed = float(oldSpeedString)

                        # Determine the new speed to set (converting mm/s to mm/m)
                        # This is done based on the reference speed, or the
                        # "print speed" value when the gcode was generated
                        newSpeed = (currentValue * 60) * oldSpeed / (referenceSpeed * 60)

                        # Change the speed in the gcode
                        if f'{oldSpeed:.1f}' != f'{newSpeed:.1f}':
                            # Change the speed for this line
                            new_line = line.replace(f'F{oldSpeedString}', f'F{newSpeed:.1f}') + f' ;AutoTowersGenerator changing speed from {(oldSpeed/60):.1f}mm/s ({oldSpeed:.1f}mm/m) to {(newSpeed/60):.1f}mm/s ({newSpeed:.1f}mm/m)'
                        else:
                            new_line = line + f' ;AutoTowersGenerator speed is already at desired {(oldSpeed/60):.1f}mm/s ({oldSpeed:.1f}mm/m)'

                        lines[lineIndex] = new_line
                                     
            result = '\n'.join(lines)
            gcode[layerIndex] = result
    
    Logger.log('d', f'AutoTowersGenerator completing SpeedTower post-processing (Print Speed)')

    return gcode
