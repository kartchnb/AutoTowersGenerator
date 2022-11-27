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
__version__ = '1.2'

from UM.Logger import Logger
from UM.Application import Application

from . import PostProcessingCommon as Common



def execute(gcode, start_flow_value, flow_value_change, section_layer_count, base_layer_count, enable_lcd_messages):
    Logger.log('d', 'AutoTowersGenerator beginning FlowTower post-processing')
    Logger.log('d', f'Starting value = {start_flow_value}')
    Logger.log('d', f'Value change = {flow_value_change}')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix}: FlowTower start flow = {start_flow_value}, flow change = {flow_value_change}\n'

    # Calculate the number of layers before the first tower section
    skipped_layer_count = Common.CalculateSkippedLayerCount(base_layer_count)

    # Start at the selected starting temperature
    current_flow_value = start_flow_value - flow_value_change # The current flow value will be corrected when the first section is encountered

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = f'{Common.comment_prefix} post-processing complete\n' + layer
            break

        # Handle each new section
        elif layer_index >= skipped_layer_count and (layer_index - skipped_layer_count) % section_layer_count == 0:
            
            # Update the flow value
            current_flow_value += flow_value_change
            command_line = f'M221 S{current_flow_value} {Common.comment_prefix} setting flow rate to {current_flow_value} for next section'
            lcd_line = f'M117 Flow {current_flow_value} {Common.comment_prefix} added line'

            # Insert the new lines into the layer
            lines = layer.split('\n')
            lines.insert(1, command_line)
            if enable_lcd_messages:
                lines.insert(1, lcd_line)
            gcode[layer_index] = '\n'.join(lines)

    Logger.log('d', 'AutoTowersGenerator completing FlowTower post-processing')
    
    return gcode