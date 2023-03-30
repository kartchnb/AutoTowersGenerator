# This script was originally adapted (although largely taken wholesale) from the 
# RetractTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 21 Sep 2022: 
#   Updated based on version 1.8 of 5axes' RetractTower processing script
# Version 2.2 - 1 Oct 2022:
#   Updated based on version 1.9 of 5axes' RetractdTower processing script
#   Commented-out gcode is now ignored, as it should be
# Version 2.3 - 25 Nov 2022:
#   Updated to ignore user-specified "End G-Code"
#   Rearchitected how lines are processed
# Version 2.4 - 26 Nov 2022:
#   Moved common code to PostProcessingCommon.py
# Version 3.0 - 1 Dec 2022:
#   Redesigned post-processing to focus on section *height* rather than section *layers*
#   This is more accurate if the section height cannot be evenly divided by the printing layer height
# Version 3.1 - 22 Mar 2023:
#   Rewrote the post-processing code to ensure I understand what it's doing
# Version 4.0 - 25 Mar 2023: 
#   Split this script off from the RetractTower_PostProcessing script
#   This script has been simplified to focus solely on retraction speed
__version__ = '4.0'

import re 

from UM.Logger import Logger
from UM.Application import Application

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, start_retract_speed:float, retract_speed_change:float, enable_lcd_messages:bool):
    
    # Log the post-processing settings
    Logger.log('d', f'Beginning Retract Tower (speed) post-processing script version {__version__}')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Starting retraction speed = {start_retract_speed}')
    Logger.log('d', f'Retraction speed change = {retract_speed_change}')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Retract Tower (speed) post-processing script version {__version__}\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Starting retraction speed = {start_retract_speed}\n'
    gcode[0] += f'{Common.comment_prefix} Retraction speed change = {retract_speed_change}\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'

    # Start at the requested starting retraction value
    current_retract_speed = start_retract_speed - retract_speed_change # The current retract value will be corrected when the first section is encountered

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:

            # Update the retraction value for the new tower section
            current_retract_speed += retract_speed_change

            # Document the new retraction speed in the gcode
            lines.insert(2, f'{Common.comment_prefix} Using a retraction speed of {current_retract_speed} mm/s for this tower section')

            # Display the new retraction value on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, f'M117 SPD {current_retract_speed:.1f} mm/s')
                lines.insert(3, f'{Common.comment_prefix} Displaying "SPD {current_retract_speed:.1f}" on the LCD')

        # Handle retraction commands
        # Retraction commands need to be modified to match the requested speed
        elif Common.IsRetractLine(line):

            # Determine the current retraction speed
            speed_search_results = re.search(r'F([-+]?\d*\.?\d+)', line.split(';')[0])
            if speed_search_results:
                original_speed_string = speed_search_results.group(1)

                # Update the line with the new retraction speed
                new_line = line.replace(f'F{original_speed_string}', f'F{int(current_retract_speed * 60)}')
                new_line += f' {Common.comment_prefix} Changed retraction speed to {current_retract_speed} mm/s ({current_retract_speed * 60} mm/min)' # Speed value must be specified as mm/min for the gcode'

                # Replace the original line with the post-processed line
                lines[line_index] = new_line

                # Leave the original line commented out in the gcode for reference
                #lines.insert(line_index, f';{line} {Common.comment_prefix} This is the original line before it was modified')

    Logger.log('d', f'AutoTowersGenerator completing Retract Tower (speed) post-processing')

    return gcode
