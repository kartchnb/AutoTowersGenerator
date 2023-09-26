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
# Version 3.1 - 28 Aug 2023:
#   Add the option enable_advanced_gcode_comments to reduce the Gcode size
# Version 3.2 - 10 Sep 2023:
#   Prevent the temperature from being changed within a tower section
__version__ = '3.2'

from UM.Logger import Logger

from . import PostProcessingCommon as Common



def execute(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float, start_temp:float, temp_change:float, enable_lcd_messages:bool, enable_advanced_gcode_comments:bool):
    
    # Log the post-processing settings
    Logger.log('d', f'Beginning Temp Tower post-processing script version {__version__}')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Starting temperature = {start_temp} C')
    Logger.log('d', f'Temperature change = {temp_change} C')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')
    Logger.log('d', f'Advanced Gcode Comments = {enable_advanced_gcode_comments}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Temp Tower post-processing script version {__version__}\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Starting temperature = {start_temp} C\n'
    gcode[0] += f'{Common.comment_prefix} Temperature change = {temp_change} C\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'
    gcode[0] += f'{Common.comment_prefix} Advanced Gcode comments = {enable_advanced_gcode_comments}\n'

    # Start at the selected starting temperature
    current_temp = start_temp - temp_change # The current temp will be incremented when the first section is encountered

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height, enable_advanced_gcode_comments):

        # Handle each new tower section
        if start_of_new_section:

            # Increment the temperature for this new tower section
            current_temp += temp_change

            # Configure the new temperature in the gcode
            if enable_advanced_gcode_comments :
                lines.insert(2, f'M109 S{current_temp} {Common.comment_prefix} Wait for the temperature to be reached')
                lines.insert(2, f'M104 S{current_temp} {Common.comment_prefix} setting temperature to {current_temp} C for this tower section')
            else :
                lines.insert(2, f'M109 S{current_temp}')
                lines.insert(2, f'M104 S{current_temp}')

            # Display the new temperature on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, f'M117 TMP {current_temp} C')
                if enable_advanced_gcode_comments :
                    lines.insert(3, f'{Common.comment_prefix} Displaying "TMP {current_temp} C" on the LCD')

        # Handle lines within each section
        else:
            if Common.IsTemperatureChangeLine(line):
                # Comment out the line
                new_line = f';{line}'
                if enable_advanced_gcode_comments:
                    new_line += f' {Common.comment_prefix} preventing a temperature change within the tower section'
                lines[line_index] = line

    Logger.log('d', 'AutoTowersGenerator completing Temp Tower post-processing')
    
    return gcode