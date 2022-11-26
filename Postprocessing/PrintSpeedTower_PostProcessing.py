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
# Version 1.3 - 25 Nov 2022:
#   Updated to ignore user-specified "End G-Code"
#   Rearchitected how lines are processed
__version__ = '1.3'

from UM.Logger import Logger

import re



def is_already_processed_line(line: str) -> bool:
    return ';AutoTowersGenerator' in line

def is_print_speed_line(line: str) -> bool:
    ''' Check if a given line changes the print speed '''
    return (line.strip().startswith('G0') or line.strip().startswith('G1')) and 'F' in line



def execute(gcode, start_speed, speed_change, section_layer_count, base_layer_count, reference_speed, enable_lcd_messages):
    ''' Post-process gcode sliced by Cura
        start_speed = the starting print speed (mm/s)
        speed_change = the amount to change the print speed for each section (mm/s)
        section_layer_count = the number of layers in each tower section
        base_layer_count = the number of layers that make up the base of the tower
        reference_speed = the print speed selection when the gcode was generated 
            This value is used to determine how print speed settings in the
            gcode are modified for each level '''

    Logger.log('d', 'AutoTowersGenerator beginning SpeedTower (Print Speed) post-processing')
    Logger.log('d', f'Starting speed = {start_speed}')
    Logger.log('d', f'Speed change = {speed_change}')
    Logger.log('d', f'Reference speed = {reference_speed}')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')
    Logger.log('d', f'Reference Speed = {reference_speed}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';SpeedTower (Print Speed) start speed = {start_speed}, speed change = {speed_change}, reference speed = {reference_speed}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the bed adhesion code (skirt, brim, etc)
    # Layer index 1 is the initial layer, which has its own settings
    # Our code starts at index 2
    base_layer_count += 2

    current_speed = start_speed - speed_change # The current speed will be corrected when the first section is encountered
    
    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = ';AutoTowersGenerator post-processing complete\n' + layer
            break

        # If this is the start of a new section (after the base)
        elif layer_index >= base_layer_count and (layer_index - base_layer_count) % section_layer_count == 0:

            lines = layer.split('\n')

            # Increment the speed
            current_speed += speed_change
            lines.insert(1, f';Start of next section (speed = {current_speed/60:.1f} mm/s ({current_speed:.1f} mm/m) ;AutoTowersGenerator added')
            if enable_lcd_messages:
                lines.insert(1, f'M117 SPD {current_speed:.1f} mm/s ;AutoTowersGenerator added\n')

            # Iterate over each command line in the layer
            for line_index, line in enumerate(lines):
                
                # Modify lines specifying print speed
                if not is_already_processed_line(line) and is_print_speed_line(line):

                    # Determine the old speed setting in the gcode
                    oldSpeedResult = re.search(r'F(\d+(?:\.\d*)?)', line.split(';')[0])
                    if oldSpeedResult:
                        oldSpeedString = oldSpeedResult.group(1)
                        oldSpeed = float(oldSpeedString)

                        # Determine the new speed to set (converting mm/s to mm/m)
                        # This is done based on the reference speed, or the
                        # "print speed" value when the gcode was generated
                        newSpeed = (current_speed * 60) * oldSpeed / (reference_speed * 60)

                        # Change the speed in the gcode
                        lines[line_index] = line.replace(f'F{oldSpeedString}', f'F{newSpeed:.1f}') + f' ;AutoTowersGenerator changing speed from {(oldSpeed/60):.1f} mm/s ({oldSpeed:.1f} mm/m) to {(newSpeed/60):.1f} mm/s ({newSpeed:.1f} mm/m)'
                                    
            gcode[layer_index] = '\n'.join(lines)
    
    Logger.log('d', f'AutoTowersGenerator completing SpeedTower post-processing (Print Speed)')

    return gcode
