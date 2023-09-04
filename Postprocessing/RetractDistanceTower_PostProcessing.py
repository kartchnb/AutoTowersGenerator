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
#   This script has been simplified to focus solely on retraction distance
# Version 4.1 - 28 Aug 2023:
#   Add the option enable_advanced_gcode_comments to reduce the Gcode size
__version__ = '4.1'

import re 

from UM.Logger import Logger
from UM.Application import Application

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, relative_extrusion:bool, start_retract_distance:float, retract_distance_change:float, enable_lcd_messages:bool, enable_advanced_gcode_comments:bool):

    # Log the post-processing settings
    Logger.log('d', f'Beginning Retract Tower (distance) post-processing script version {__version__}')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Relative extrusion = {relative_extrusion}')
    Logger.log('d', f'Starting retraction distance = {start_retract_distance}')
    Logger.log('d', f'Retraction distance change = {retract_distance_change}')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')
    Logger.log('d', f'Advanced Gcode Comments = {enable_advanced_gcode_comments}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Retract Tower (distance) post-processing script version {__version__}\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Relative extrusion = {relative_extrusion}\n'
    gcode[0] += f'{Common.comment_prefix} Starting retraction distance = {start_retract_distance}\n'
    gcode[0] += f'{Common.comment_prefix} Retraction distance change = {retract_distance_change}\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'
    gcode[0] += f'{Common.comment_prefix} Advanced Gcode comments = {enable_advanced_gcode_comments}\n'

    # Start at the requested starting retraction value
    current_retract_distance = start_retract_distance - retract_distance_change # The current retract value will be corrected when the first section is encountered
    
    # Keep track of the absolute retraction position throughout the script
    reference_extrusion_position = None

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height, enable_advanced_gcode_comments):

        # Handle each new tower section
        if start_of_new_section:

            # Update the retraction value for the new tower section
            current_retract_distance += retract_distance_change

            # Document the new retraction value in the gcode
            lines.insert(2, f'{Common.comment_prefix} Using a retraction distance of {current_retract_distance} mm for this tower section')

            # Display the new retraction value on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, f'M117 DST {current_retract_distance:.1f} mm')
                if enable_advanced_gcode_comments :
                    lines.insert(3, f'{Common.comment_prefix} Displaying "DST {current_retract_distance:.1f}" on the LCD')

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

        # Handle extrusion and retraction lines
        elif Common.IsExtrusionLine(line) or Common.IsRetractLine(line):

            # Determine the current extrusion position
            position_search_results = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
            if position_search_results:
                original_extrusion_position_string = position_search_results.group(1)
                original_extrusion_position = float(original_extrusion_position_string)

                # Record the first reference position
                if reference_extrusion_position is None and not relative_extrusion:
                    reference_extrusion_position = original_extrusion_position

                # For extrusion commands, the absolute extrusion position just needs to be updated
                elif Common.IsExtrusionLine(line) and not relative_extrusion:
                    reference_extrusion_position = original_extrusion_position

                # Retraction commands need to be processed to achieve the requested retraction distance
                elif Common.IsRetractLine(line):

                    # Relative retraction is fairly simple since the filament position doesn't need to be tracked
                    if relative_extrusion:

                        # The original retraction distance is just the "extrusion position" in this case
                        original_retraction_distance = original_extrusion_position

                        # Update actual retraction lines (filament being pulled in)
                        if original_retraction_distance < 0:

                            # Update the line with the new retraction distance
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{-current_retract_distance:.5f}')
                            if enable_advanced_gcode_comments :
                                new_line += f' {Common.comment_prefix} Retracting {-current_retract_distance:.5f} mm of filament using relative positioning'

                        # Update filament extrusion (reversing the previous retraction)
                        else:

                            # Update the line with the new retraction distance
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{current_retract_distance:.5f}')
                            if enable_advanced_gcode_comments :
                                new_line += f' {Common.comment_prefix} Extruding {current_retract_distance:.5f} mm of filament using relative positioning to reverse the previous retraction'

                    # Absolute retraction needs to take into account the current absolute filament position
                    else:

                        # Update actual retraction lines (filament being pulled in)
                        if original_extrusion_position < reference_extrusion_position:

                            # Determine the new position given the desired retraction distance for this section
                            updated_extrusion_position = reference_extrusion_position - current_retract_distance
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{updated_extrusion_position:.5f}')
                            if enable_advanced_gcode_comments :
                                new_line += f' {Common.comment_prefix} Retracting {current_retract_distance:.5f} mm of filament using absolute positioning'

                        # Update filament extrusion (reversing the previous retraction)
                        # Since the extrusion is just returning the filament to the previous position, the original line will work unchanged
                        else:

                            # Just comment the line for informational purposes
                            if enable_advanced_gcode_comments :
                                new_line = line + f' {Common.comment_prefix} Extruding {current_retract_distance:.5f} mm of filament using absolute positioning to reverse the previous retraction'
                            else :
                                new_line = line
                                
                    # Replace the original line with the post-processed line
                    lines[line_index] = new_line

                    # Leave the original line commented out in the gcode for reference
                    #lines.insert(line_index, f';{line} {Common.comment_prefix} This is the original line before it was modified')

    Logger.log('d', f'AutoTowersGenerator completing RetractTower (distance) post-processing')

    return gcode
