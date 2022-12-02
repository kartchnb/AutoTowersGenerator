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
# Version 3.0 - 1 Dec 2022:
#   Redesigned post-processing to focus on section *height* rather than section *layers*
#   This is more accurate if the section height cannot be evenly divided by the printing layer height
__version__ = '3.0'

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, start_temp:float, temp_change:float, enable_lcd_messages:bool):
    
    # Log the post-processing settings
    Logger.log('d', 'AutoTowersGenerator beginning TempTower post-processing')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Starting temperature = {start_temp}%')
    Logger.log('d', f'Temperature change = {temp_change}%')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Post-processing a TempTower\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Starting temperature = {start_temp}%\n'
    gcode[0] += f'{Common.comment_prefix} Temperature change = {temp_change}%\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'

    # Start at the selected starting temperature
    current_temp = start_temp - temp_change # The current temp will be incremented when the first section is encountered

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:

            # Increment the temperature for this new tower section
            current_temp += temp_change

            # Configure the new temperature in the gcode
            lines.insert(2, f'M104 S{current_temp} {Common.comment_prefix} setting temperature to {current_temp} for this tower section')

            # Display the new temperature on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, f'M117 TMP {current_temp} {Common.comment_prefix} Displaying "TMP {current_temp}" on the LCD')

    Logger.log('d', 'AutoTowersGenerator completing Temp Tower post-processing')
    
    return gcode