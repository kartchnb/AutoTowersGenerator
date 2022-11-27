# This script was adapted (although largely taken wholesale) from the 
# TempFanTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 21 Sep 2022: 
#   Updated to match Version 1.6 of 5axes' TempFanTower processing script
# Version 2.2 - 25 Nov 2022:
#   Updated to ignore user-specified "End G-Code"
#   Rearchitected how lines are processed
# Version 2.3 - 26 Nov 2022:
#   Moved common code to PostProcessingCommon.py
__version__ = '2.3'

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, start_temp, temp_change, section_layer_count, base_layer_count, enable_lcd_messages):
    Logger.log('d', 'AutoTowersGenerator beginning TempTower post-processing')
    Logger.log('d', f'Starting temperature = {start_temp}')
    Logger.log('d', f'Temperature change = {temp_change}')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')

    # Document the settings in the g-code
    gcode[0] += f';TempTower start temp = {start_temp}, temp change = {temp_change}\n'

    # Calculate the number of layers before the first tower section
    skipped_layer_count = Common.CalculateSkippedLayerCount(base_layer_count)

    # Start at the selected starting temperature
    current_temp = start_temp - temp_change # The current temp will be incremented when the first section is encountered

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = f'{Common.comment_prefix} post-processing complete\n' + layer
            break

        # Only process layers after the base
        elif layer_index >= skipped_layer_count and (layer_index - skipped_layer_count) % section_layer_count == 0:

            # Increment the temperature
            current_temp += temp_change
            layer = f'M104 S{current_temp} {Common.comment_prefix} setting temperature to {current_temp} for the next section\n' + layer
            if enable_lcd_messages:
                layer = f'M117 Temp {current_temp} {Common.comment_prefix} added line\n' + layer

            gcode[layer_index] = layer

    Logger.log('d', 'AutoTowersGenerator completing Temp Tower post-processing')
    
    return gcode