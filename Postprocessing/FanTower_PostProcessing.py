# This script was adapted (although largely taken wholesale) from the 
# TempFanTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 21 Sep 2022: 
#   Updated based on Version 1.6 of 5axes' TempFanTower processing script, including the "maintain bridge value" option
# Version 2.2 - 1 Oct 2022:
#   Updated based on 5axes' suggestion to ignore commented-out gcode
# Version 2.3 - 25 Nov 2022:
#   Updated to ignore user-specified "End G-Code"
#   Rearchitected how lines are processed
# Version 2.4 - 26 Nov 2022:
#   Moved common code to PostProcessingCommon.py
__version__ = '2.4'

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, start_fan_percent, fan_percent_change, section_layer_count, base_layer_count, maintain_bridge_value, enable_lcd_messages):
    Logger.log('d', 'AutoTowersGenerator beginning FanTower post-processing')
    Logger.log('d', f'Start speed = {start_fan_percent}%')
    Logger.log('d', f'Speed change = {fan_percent_change}%')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')
    Logger.log('d', f'Display on LCD = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} FanTower start fan % = {start_fan_percent}, fan % change = {fan_percent_change}\n'

    # Calculate the number of layers before the first tower section
    skipped_layer_count = Common.CalculateSkippedLayerCount(base_layer_count)

    # Start at the selected starting percentage
    current_fan_percent = start_fan_percent - fan_percent_change # The current fan percent will be corrected when the first section is encountered

    after_bridge = False

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = f'{Common.comment_prefix} post-processing complete\n' + layer
            break

        # Only process layers after the base
        elif layer_index >= skipped_layer_count:

            lines = layer.split('\n')

            # Process the start of each section
            if (layer_index - skipped_layer_count) % section_layer_count == 0:
                current_fan_percent += fan_percent_change
                current_fan_value = int((current_fan_percent * 255) / 100)
                lines.insert(1, f'M106 S{current_fan_value} {Common.comment_prefix} setting fan speed to {current_fan_percent}% for the next section')
                if enable_lcd_messages:
                    lines.insert(1, f'M117 Speed {current_fan_percent}% {Common.comment_prefix} added')

            # Iterate over each command line in the layer
            for line_index, line in enumerate(lines):

                # Don't re-process lines
                if not Common.is_already_processed_line(line):

                    # If the fan speed is being changed after a bridge section was printed
                    if Common.is_fan_speed_change_line(line):
                        if after_bridge or not maintain_bridge_value:
                            lines[line_index] = f'M106 S{current_fan_value} {Common.comment_prefix} Resuming fan speed of {current_fan_percent}% after bridge'
                            after_bridge = False
                            if enable_lcd_messages:
                                lines.insert(line_index + 1, f'M117 Speed {current_fan_percent}% {Common.comment_prefix} added')
                        else:
                            after_bridge = True

                    elif Common.is_fan_off_line(line):
                        after_bridge = True

                    elif Common.is_start_of_bridge(line):
                        after_bridge = False

            result = '\n'.join(lines)
            gcode[layer_index] = result

    Logger.log('d', 'AutoTowersGenerator completing FanTower post-processing')

    return gcode