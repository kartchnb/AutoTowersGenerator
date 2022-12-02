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
__version__ = '2.0'

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, start_flow_value:float, flow_value_change:float, enable_lcd_messages:bool):
    
    # Log the post-processing settings
    Logger.log('d', 'AutoTowersGenerator beginning FlowTower post-processing')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Starting flow = {start_flow_value}%')
    Logger.log('d', f'Flow change = {flow_value_change}%')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Post-processing a FlowTower\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Starting flow = {start_flow_value}%\n'
    gcode[0] += f'{Common.comment_prefix} Flow change = {flow_value_change}%\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'

    # Start at the requested starting flow value
    current_flow_value = start_flow_value - flow_value_change # The current flow value will be corrected when the first section is encountered

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:
            # Update the flow value for the new tower section
            current_flow_value += flow_value_change

            # Configure the new flow value in the gcode
            lines.insert(2, f'M221 S{current_flow_value} {Common.comment_prefix} setting the flow value to {current_flow_value}% for this tower section')

            # Display the new flow value on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, f'M117 FLW {current_flow_value}% {Common.comment_prefix} displaying "FLW {current_flow_value}%" on the LCD')

    Logger.log('d', 'AutoTowersGenerator completing FlowTower post-processing')
    
    return gcode