# This script was adapted (although largely taken wholesale) from the 
# FlowTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 1.0 - 21 Sep 2022: 
#   Based on version 1.1 of 5axes' FlowTower script
# Version 1.1 - 25 Nov 2022:
#   Updated to ignore user-specified "End G-Code"
#   Rearchitected how lines are processed
# Version 1.2 - 26 Nov 2022:
#   Moved common code to PostProcessingCommon.py
# Version 2.0 - 1 Dec 2022:
#   Redesigned post-processing to focus on section *height* rather than section *layers*
#   This is more accurate if the section height cannot be evenly divided by the printing layer height
# Version 3.0 - 29 Mar 2023:
#   Corrected the method of simulating flow rate changes from using the M221 command to 
#   changing the extrusion distance
# Version 3.1 - 28 Aug 2023:
#   Add the option enable_advanced_gcode_comments to reduce the Gcode size
__version__ = '3.1'

import re

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, relative_extrusion:bool, start_flow_rate:float, flow_rate_change:float, reference_flow_rate:float, enable_lcd_messages:bool, enable_advanced_gcode_comments:bool):

    # Log the post-processing settings
    Logger.log('d', f'Beginning Flow Tower post-processing script version {__version__}')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Relative extrusion = {relative_extrusion}')
    Logger.log('d', f'Starting flow rate = {start_flow_rate}%')
    Logger.log('d', f'Flow rate change = {flow_rate_change}%')
    Logger.log('d', f'Reference flow rate = {reference_flow_rate}%')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')
    Logger.log('d', f'Advanced Gcode Comments = {enable_advanced_gcode_comments}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Flow Tower post-processing script version {__version__}\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Relative extrusion = {relative_extrusion}\n'
    gcode[0] += f'{Common.comment_prefix} Starting flow rate = {start_flow_rate}%\n'
    gcode[0] += f'{Common.comment_prefix} Flow rate change = {flow_rate_change}%\n'
    gcode[0] += f'{Common.comment_prefix} Reference flow rate = {reference_flow_rate}%\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'
    gcode[0] += f'{Common.comment_prefix} Advanced Gcode comments = {enable_advanced_gcode_comments}\n'

    # Start at the requested starting flow value
    current_flow_rate = start_flow_rate - flow_rate_change # The current flow value will be corrected when the first section is encountered

    # Keep track of values throughout the script
    reference_extrusion_position = None
    updated_extrusion_position = None

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:

            # Update the flow value for the new tower section
            current_flow_rate += flow_rate_change

            # Document the new flow rate in the gcode
            if enable_advanced_gcode_comments :
                lines.insert(2, f'{Common.comment_prefix} Using flow rate {current_flow_rate}% for this tower section')

                # Display the new flow rate on the printer's LCD
                if enable_lcd_messages:
                    lines.insert(3, f'M117 FLOW {current_flow_rate:.1f}%')
                    lines.insert(3, f'{Common.comment_prefix} Displaying "FLOW {current_flow_rate:.1f}% on the LCD')
            else :
                # Display the new flow rate on the printer's LCD
                if enable_lcd_messages:
                    lines.insert(2, f'M117 FLOW {current_flow_rate:.1f}%')
                    
        # Record if relative extrusion is now being used
        if Common.IsRelativeInstructionLine(line):
            relative_extrusion = True

        # Record if absolute extrusion is now being used
        elif Common.IsAbsoluteInstructionLine(line):
            relative_extrusion = False

            # The absolute extrusion position data will need to be redetermined
            reference_extrusion_position = None
            updated_extrusion_position = None

        # Handle resetting the extruder position
        elif Common.IsResetExtruderLine(line) and relative_extrusion == False:

            # Reset the recorded extrusion positions to 0
            reference_extrusion_position = 0
            updated_extrusion_position = 0

        # Handle extrusion or retraction lines that need to be processed
        # All extrusion commands will need to be modified to achieve the requested flow rate
        # Absolute retraction commands will need to modified to account for flow rate extrusion changes
        # Relative retraction commands can be left unchanged 
        elif (Common.IsExtrusionLine(line) or (Common.IsRetractLine(line) and not relative_extrusion)):

            # Determine the new extrusion position
            position_search_results = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
            if position_search_results:
                original_extrusion_position_string = position_search_results.group(1)
                original_extrusion_position = float(original_extrusion_position_string)

                # If the absolute filament reference extrusion position hasn't been read yet, read it from this command and move to the next line
                if reference_extrusion_position is None and relative_extrusion == False:

                    # Record the original extrusion position as the reference position for future updates
                    reference_extrusion_position = original_extrusion_position
                    updated_extrusion_position = original_extrusion_position
                    continue

                # Handle absolute retraction commands
                elif Common.IsRetractLine(line):

                    # Only absolute extrusions need to be tracked and modified
                    if not relative_extrusion:

                        # Determine how far the filament is being extruded or retracted
                        original_extruded_distance = original_extrusion_position - reference_extrusion_position
                        
                        # Update the referenced extrusion positions
                        reference_extrusion_position = original_extrusion_position
                        updated_extrusion_position += original_extruded_distance

                        # Update the gcode line
                        new_line = line.replace(f'E{original_extrusion_position_string}', f'E{updated_extrusion_position:.5f}')
                        if enable_advanced_gcode_comments :
                            if original_extruded_distance < 0:
                                new_line += f' {Common.comment_prefix} Retracting {-original_extruded_distance:.5f} mm of filament'
                            else:
                                new_line += f' {Common.comment_prefix} Extruding {original_extruded_distance:.5f} mm of filament to reverse the last retraction'

                # Handle extrusion commands
                elif Common.IsExtrusionLine(line):

                        # Handle relative extrusion commands
                        # Relative extrusion is pretty simple
                        if relative_extrusion:

                            # With relative extrusion, the "extrusion position" is simply the distance of filament being extruded
                            original_extruded_distance = original_extrusion_position

                            # Modify positive extrusion (filament being pushed out) to achieve the requested flow rate
                            if original_extruded_distance > 0:
                                
                                # Update the extruded distance to reflect the current flow rate
                                nominal_extruded_distance = original_extruded_distance / (reference_flow_rate / 100) # Correct for the reference flow rate
                                updated_extruded_distance = nominal_extruded_distance * (current_flow_rate / 100) # Convert to the current flow rate

                                # Update the gcode line
                                new_line = line.replace(f'E{original_extrusion_position_string}', f'E{updated_extruded_distance:.5f}')
                                if enable_advanced_gcode_comments :
                                    new_line += f' {Common.comment_prefix} Extruding {updated_extruded_distance:.5f} mm of filament to achieve a {current_flow_rate}% flow rate (originally {original_extruded_distance:.5f} mm at {reference_flow_rate}% flow rate)'

                        # Handle absolute extrusion commands
                        # This is more complicated than relative extrusion since we need to keep track of how much 
                        # filament the script originally extruded and how much our modifications are extruding
                        else:

                            # Calculate how much filament is being extruded by the script
                            original_extruded_distance = original_extrusion_position - reference_extrusion_position
                            
                            # Update the referenced extrusion position
                            reference_extrusion_position = original_extrusion_position

                            # Update the extruded distance to reflect the current flow rate
                            nominal_extruded_distance = original_extruded_distance / (reference_flow_rate / 100) # Correct for the reference flow rate
                            updated_extruded_distance = nominal_extruded_distance * (current_flow_rate / 100) # Convert to the current flow rate
                            updated_extrusion_position += updated_extruded_distance

                            # Update the gcode line
                            new_line = line.replace(f'E{original_extrusion_position_string}', f'E{updated_extrusion_position:.5f}')
                            if enable_advanced_gcode_comments :
                                new_line += f' {Common.comment_prefix} Extruding {updated_extruded_distance:.5f} mm of filament to achieve a {current_flow_rate}% flow rate (originally {original_extruded_distance:.5f} mm at {reference_flow_rate}% flow rate)'
                    
                # Replace the original line with the post-processing modifications
                lines[line_index] = new_line

                # Leave the original line commented out in the gcode for reference
                #lines.insert(line_index, f';{line} {Common.comment_prefix} This is the original line before it was modified')

    Logger.log('d', 'AutoTowersGenerator completing FlowTower post-processing')
    
    return gcode