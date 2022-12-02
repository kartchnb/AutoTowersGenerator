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
# Version 3.0 - 1 Dec 2022:
#   Redesigned post-processing to focus on section *height* rather than section *layers*
#   This is more accurate if the section height cannot be evenly divided by the printing layer height
__version__ = '3.0'

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height: float, layer_height:float, start_fan_percent:float, fan_percent_change:float, maintain_bridge_value:bool, enable_lcd_messages:bool):
    
    # Log the post-processing settings
    Logger.log('d', 'AutoTowersGenerator beginning FanTower post-processing')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Starting fan speed = {start_fan_percent}%')
    Logger.log('d', f'Fan speed change = {fan_percent_change}%')
    Logger.log('d', f'Maintain bridge value = {maintain_bridge_value}')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Post-processing a FanTower\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Starting fan speed = {start_fan_percent}%\n'
    gcode[0] += f'{Common.comment_prefix} Fan speed change = {fan_percent_change}%\n'
    gcode[0] += f'{Common.comment_prefix} Maintain bridge value = {maintain_bridge_value}\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'

    # Start at the requested starting fan speed %
    current_fan_percent = start_fan_percent - fan_percent_change # The current fan percent will be corrected when the first section is encountered

    # Keep track of whether a bridge has been completed
    after_bridge = False

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:

            # Increment the fan speed % for this tower section and convert from a range of 0-100 to 0-255
            current_fan_percent += fan_percent_change
            current_fan_value = int((current_fan_percent * 255) / 100)

            # Configure the new fan speed % in the gcode
            lines.insert(2, f'M106 S{current_fan_value} {Common.comment_prefix} setting fan speed to {current_fan_percent}% for the this tower section')

            # Display the new the fan speed % on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, f'M117 Speed {current_fan_percent}% {Common.comment_prefix} displaying "Speed {current_fan_percent}%" on the LCD')

        # Handle fan speed changes in the gcode
        if Common.IsFanSpeedChangeLine(line):

            # If this change is coming after a bridge has been printed or we don't need to maintain the bridge value
            if after_bridge or not maintain_bridge_value:
                
                # Resume the tower section fan speed in the gcode
                lines[line_index] = f'M106 S{current_fan_value} {Common.comment_prefix} Resuming fan speed of {current_fan_percent}% after printing a bridge'

            # If this is the start of a bridge
            else:
                
                # Mark the next fan speed change as coming after a bridge was printed
                after_bridge = True
                
        # If the fan is being turned off for the start of a bridge
        elif Common.IsFanOffLine(line):

            # Mark the next fan speed change as coming after a bridge was printed
            after_bridge = True

        # If this line marks the start of a bridge
        elif Common.IsStartOfBridge(line):

            # Mark the next fan speed change as being the start of a bridge print
            after_bridge = False

    Logger.log('d', 'AutoTowersGenerator completing FanTower post-processing')

    return gcode