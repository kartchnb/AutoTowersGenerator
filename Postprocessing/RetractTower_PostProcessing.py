# This script was adapted (although largely taken wholesale) from the 
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
#   STL filenames for preset towers must now be specified rather than assuming they are named after the preset
__version__ = '3.1'

import re 

from UM.Logger import Logger
from UM.Application import Application

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, relative_extrusion:bool, start_retract_value:float, retract_value_change:float, tower_type:str, enable_lcd_messages:bool):
    
    # Log the post-processing settings
    Logger.log('d', f'AutoTowersGenerator beginning {tower_type} RetractTower post-processing')
    Logger.log('d', f'Script version {__version__}')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Relative extrusion = {relative_extrusion}')
    Logger.log('d', f'Starting retraction {tower_type.lower()} = {start_retract_value}')
    Logger.log('d', f'Retraction {tower_type.lower()} change = {retract_value_change}')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Post-processing a {tower_type} RetractTower\n'
    gcode[0] += f'{Common.comment_prefix} Script version {__version__}\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Relative extrusion = {relative_extrusion}\n'
    gcode[0] += f'{Common.comment_prefix} Starting retraction {tower_type.lower()} = {start_retract_value}\n'
    gcode[0] += f'{Common.comment_prefix} Retraction {tower_type.lower()} change = {retract_value_change}\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'

    # Start at the requested starting retraction value
    current_retract_value = start_retract_value - retract_value_change # The current retract value will be corrected when the first section is encountered
    
    # Keep track of values throughout the script
    relative_extrusion = False
    reference_extrusion_position = None

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:

            # Update the retraction value for the new tower section
            current_retract_value += retract_value_change

            # Document the new retraction value in the gcode
            if tower_type == 'Speed':
                lines.insert(2, f'{Common.comment_prefix} Using retraction speed {current_retract_value} mm/s for this tower section')
            else:
                lines.insert(2, f'{Common.comment_prefix} Using retraction distance {current_retract_value} mm for this tower section')

            # Display the new retraction value on the printer's LCD
            if enable_lcd_messages:
                if tower_type == 'Speed':
                    lines.insert(3, f'M117 SPD {current_retract_value:.1f} mm/s {Common.comment_prefix} Displaying "SPD {current_retract_value:.1f}" on the LCD')
                else:
                    lines.insert(3, f'M117 DST {current_retract_value:.1f} mm {Common.comment_prefix} Displaying "DST {current_retract_value:.1f}" on the LCD')

        # Record if relative extrusion is now being used
        if Common.IsRelativeInstructionLine(line):
            relative_extrusion = True

        # Record if absolute extrusion is now being used
        elif Common.IsAbsoluteInstructionLine(line):
            relative_extrusion = False

            # The absolute extrusion position data is irrelevant in this mode
            reference_extrusion_position = None

        # Handle resetting the extruder position
        elif Common.IsResetExtruderLine(line):

            # Reset the recorded extrusion position to 0
            reference_extrusion_position = 0

        # Handle extrusion commands
        # For absolute extrusion, the current extrusion position needs to be tracked
        elif Common.IsExtrusionLine(line):

            # Only absolute extrusions need to be tracked
            if not relative_extrusion:

                # Determine the new extrusion position
                position_search_results = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
                if position_search_results:
                    current_extrusion_position_string = position_search_results.group(1)
                    current_extrusion_position = float(current_extrusion_position_string)

                    # Keep track of the current filament position
                    reference_extrusion_position = current_extrusion_position

        # Handle retraction commands
        # Retraction commands need to be modified to match the requested speed or distance
        elif Common.IsRetractLine(line):

            # Determine the new extrusion position
            speed_search_results = re.search(r'F([-+]?\d*\.?\d+)', line.split(';')[0])
            position_search_results = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
            if speed_search_results and position_search_results:
                original_speed_string = speed_search_results.group(1)
                original_speed = float(original_speed_string)
                original_extrusion_position_string = position_search_results.group(1)
                original_extrusion_position = float(original_extrusion_position_string)

                # For retraction speed towers, the speed is simple to update
                if tower_type == 'Speed':

                    # Update the line with the new retraction speed
                    new_line = line.replace(f'F{original_speed_string}', f'F{int(current_retract_value * 60)}')
                    new_line += f' {Common.comment_prefix} Retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/min)'  # Speed value must be specified as mm/min for the gcode'

                # Retraction distance towers are more complicated than retraction speed towers
                else:

                    # Relative retraction is fairly simple since the filament position doesn't need to be tracked
                    if relative_extrusion:

                        # The original retraction distance is just the "extrusion position" in this case
                        original_retraction_distance = original_extrusion_position

                        # If this command is actually retracting filament, update the retraction distance
                        if original_retraction_distance < 0:
                            # Update the line with the new retraction distance
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{-current_retract_value:.5f}')
                            new_line += f' {Common.comment_prefix} Retracting {current_retract_value:.5f} mm of filament using relative positioning'

                        else:
                            # Update the line with the new retraction distance
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{current_retract_value:.5f}')
                            new_line += f' {Common.comment_prefix} Extruding {current_retract_value:.5f} mm of filament using relative positioning to reverse the previous retraction'

                    # Absolute retraction needs to take into account the current absolute filament position
                    else:
                        
                        # If the reference filament position has not been determined yet, then the command won't be changed this time
                        if reference_extrusion_position is None:

                            # Just record this filament position as the reference position and move on to the next line
                            reference_extrusion_position = original_extrusion_position
                            continue

                        # If this command is actually retracting filament, update the retraction distance
                        if original_extrusion_position < reference_extrusion_position:

                            # Determine the new position given the desired retraction distance for this section
                            updated_extrusion_position = reference_extrusion_position - current_retract_value
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{updated_extrusion_position:.5f}')
                            new_line += f' {Common.comment_prefix} Retracting {current_retract_value:.5f} mm of filament using absolute positioning'

                        # If this command is undoing the previous retraction (by extruding the filament back out),
                        # then, since the extrusion is just returning the filament to the previous position, the original line will work unchanged
                        else:

                            # Continue on to process the next line of gcode
                            continue

                # Replace the original line with the post-processed line
                lines[line_index] = new_line

                # Leave the original line commented out in the gcode for reference
                #lines.insert(line_index, f';{line} {Common.comment_prefix} This is the original line before it was modified')

    Logger.log('d', f'AutoTowersGenerator completing RetractTower post-processing ({tower_type})')

    return gcode
