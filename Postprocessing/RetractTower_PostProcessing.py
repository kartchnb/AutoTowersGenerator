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
__version__ = '3.0'

import re 

from UM.Logger import Logger
from UM.Application import Application

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, relative_extrusion:bool, start_retract_value:float, retract_value_change:float, tower_type:str, enable_lcd_messages:bool):
    
    # Log the post-processing settings
    Logger.log('d', f'AutoTowersGenerator beginning {tower_type} RetractTower post-processing')
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
    saved_extrusion_position = -1
    current_extrusion_position = 0
    current_extrusion_speed = 0
    first_code = True

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new section
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
                        lines.insert(3, f'M117 SPD {current_retract_value:.1f} mm/s {Common.comment_prefix} Displaying "SPD {current_retract_value:.1f} mm/s" on the LCD')
                    else:
                        lines.insert(3, f'M117 DST {current_retract_value:.1f} mm {Common.comment_prefix} Displaying "DST {current_retract_value:.1f} mm" on the LCD')

        # Record if relative extrusion is now being used
        if Common.IsRelativeInstructionLine(line):
            relative_extrusion = True

        # Record if absolute extrusion is now being used
        elif Common.IsAbsoluteInstructionLine(line):
            relative_extrusion = False

        # Handle reseting the extruder position
        elif Common.IsResetExtruderLine(line):
            current_extrusion_position = 0
            saved_extrusion_position = 0

        # Handle extrusion commands
        elif Common.IsExtrusionLine(line):
            # Record the new extrusion position
            position_search_results = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
            if position_search_results:
                extrusion_position_string_value = position_search_results.group(1)
                saved_extrusion_position=float(extrusion_position_string_value)        

        # Handle retraction commands
        elif Common.IsRetractLine(line):
            speed_search_results = re.search(r'F([-+]?\d*\.?\d+)', line.split(';')[0])
            position_search_results = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
            if speed_search_results and position_search_results:
                current_extrusion_speed=float(speed_search_results.group(1))
                current_extrusion_position=float(position_search_results.group(1))

                new_line = ''

                # Handle relative extrusion
                if relative_extrusion:

                    # Retracting filament (relative)
                    if current_extrusion_position < 0:
                        if tower_type == 'Speed':
                            new_line = f'G1 F{int(current_retract_value * 60)} E{current_extrusion_position:.5f} {Common.comment_prefix} retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/min) (relative)'  # Speed value must be specified as mm/min for the gcode
                        else:
                            new_line = f'G1 F{int(current_extrusion_speed)} E{-current_retract_value:.5f} {Common.comment_prefix} retracting {current_retract_value:.1f} mm of filament (relative)'
                    
                    # Extruding filament (relative)
                    else:
                        if tower_type == 'Speed':
                            new_line = f'G1 F{int(current_retract_value * 60)} E{current_extrusion_position:.5f} {Common.comment_prefix} extruding filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/min) (relative)' # Speed value must be specified as mm/min for the gcode
                        else:
                            if first_code:
                                new_line = f'G1 F{int(current_extrusion_speed)} E{current_extrusion_position:.5f} {Common.comment_prefix} extruding {current_extrusion_position:.1f} mm of filament (relative)'
                                first_code = False
                            else:
                                new_line = f'G1 F{int(current_extrusion_speed)} E{current_retract_value:.5f} {Common.comment_prefix} extruding {current_retract_value:.1f} mm of filament (relative)'
                
                # Handle absolute extrusion
                else:

                    # Retracting filament (absolute)
                    if saved_extrusion_position > current_extrusion_position:
                        if tower_type == 'Speed':
                            new_line = f'G1 F{int(current_retract_value * 60)} E{current_extrusion_position:.5f} {Common.comment_prefix} retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/min) (absolute)' # Speed value must be specified as mm/min for the gcode
                        else:
                            current_extrusion_position = saved_extrusion_position - current_retract_value
                            new_line = f'G1 F{int(current_extrusion_speed)} E{current_extrusion_position:.5f} {Common.comment_prefix} retracting {current_retract_value:.1f} mm of filament (absolute)'
                    
                    # Resetting the retraction 
                    else:
                        if tower_type == 'Speed':
                            new_line = f'G1 F{int(current_retract_value * 60)} E{current_extrusion_position:.5f} {Common.comment_prefix} setting retraction speed to {current_retract_value} mm/s ({current_retract_value * 60} mm/min)' # Speed value must be specified as mm/min for the gcode

                # If the current line needs to be modified
                if new_line != '':

                    # Keep the original line in the gcode, but comment it out
                    lines[line_index] = f';{line} {Common.comment_prefix} This is the original line before being modified'

                    # Insert the new line
                    lines.insert(line_index, new_line)



    Logger.log('d', f'AutoTowersGenerator completing RetractTower post-processing ({tower_type})')

    return gcode
