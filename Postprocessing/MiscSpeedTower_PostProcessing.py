# This script was adapted (although largely taken wholesale) from the 
# SpeedTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 19 Sep 2022: 
#   Updated to match Version 1.7 of 5axes' SpeedTower processing script
# Version 2.2 - 29 Sep 2022:
#   Removed travel speed post-processing to TravelSpeedTower_PostProcessing.py
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



def execute(gcode, base_height: float, section_height: float, initial_layer_height:float, layer_height:float, start_speed:float, speed_change:float, tower_type:str, enable_lcd_messages:bool):

    # Log the post-processing settings
    Logger.log('d', f'AutoTowersGenerator beginning {tower_type} SpeedTower post-processing')
    Logger.log('d', f'Base height = {base_height} mm')
    Logger.log('d', f'Section height = {section_height} mm')
    Logger.log('d', f'Initial printed layer height = {initial_layer_height}')
    Logger.log('d', f'Printed layer height = {layer_height} mm')
    Logger.log('d', f'Starting speed = {start_speed} mm/s')
    Logger.log('d', f'Speed change = {speed_change} mm/s')
    Logger.log('d', f'Enable LCD messages = {enable_lcd_messages}')

    # Document the settings in the g-code
    gcode[0] += f'{Common.comment_prefix} Post-processing a {tower_type} SpeedTower\n'
    gcode[0] += f'{Common.comment_prefix} Base height = {base_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Section height = {section_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Initial printed layer height = {initial_layer_height}\n'
    gcode[0] += f'{Common.comment_prefix} Printed layer height = {layer_height} mm\n'
    gcode[0] += f'{Common.comment_prefix} Starting speed = {start_speed} mm/s\n'
    gcode[0] += f'{Common.comment_prefix} Speed change = {speed_change} mm/s\n'
    gcode[0] += f'{Common.comment_prefix} Enable LCD messages = {enable_lcd_messages}\n'

    # Start at the requested starting speed
    current_speed = start_speed - speed_change # The current speed will be corrected when the first section is encountered

    # Iterate over each line in the g-code
    for line_index, line, lines, start_of_new_section in Common.LayerEnumerate(gcode, base_height, section_height, initial_layer_height, layer_height):

        # Handle each new tower section
        if start_of_new_section:
            
            # Increment the speed for this tower section
            current_speed += speed_change
    
            # Handle acceleration speed
            if tower_type == 'Acceleration':
                command_line = f'M204 S{int(current_speed)} {Common.comment_prefix} setting acceleration to {int(current_speed)} mm/s/s for this tower section'
                lcd_line = f'M117 ACC S{int(current_speed)} mm/s/s {Common.comment_prefix} Displaying "ACC S{int(current_speed)} mm/s/s" on the LCD'

            # Handle jerk speed
            elif tower_type=='Jerk':
                command_line = f'M205 X{int(current_speed)} Y{int(current_speed)} {Common.comment_prefix} setting jerk speed to {int(current_speed)} mm/s for this tower section'
                lcd_line = f'M117 JRK X{int(current_speed)} Y{int(current_speed)} {Common.comment_prefix} Displaying "JRK X{int(current_speed)} Y{int(current_speed)}" on the LCD'

            # Handle junction speed
            elif tower_type=='Junction':
                command_line = f'M205 J{float(current_speed):.3f} {Common.comment_prefix} setting junction value to {float(current_speed):.3f} for this tower section'
                lcd_line = f'M117 JCN J{float(current_speed):.3f} {Common.comment_prefix} Displaying "JCN J{float(current_speed):.3f}" on the LCD'

            # Handle Marlin linear speed
            elif tower_type=='Marlin linear':
                command_line = f'M900 K{float(current_speed):.3f} {Common.comment_prefix} setting Marlin linear value to {float(current_speed):.3f} for this tower section'
                lcd_line = f'M117 LIN {float(current_speed):.3f} {Common.comment_prefix} Displaying "LIN {float(current_speed):.3f}" on the LCD'

            # Handle RepRap pressure speed
            elif tower_type=='RepRap pressure':
                command_line = f'M572 D0 S{float(current_speed):.3f} {Common.comment_prefix} setting RepRap pressure value to {float(current_speed):.3f} for this tower section'
                lcd_line = f'M117 PRS {float(current_speed):.3f} {Common.comment_prefix} Displaying "PRS {float(current_speed):.3f}" on the LCD'

            # Handle unrecognized tower types
            else:  
                Logger.log('e', f'MiscSpeedTower_PostProcessing: unrecognized tower type "{tower_type}"')
                break

            # Configure the new speed in the gcode
            lines.insert(2, command_line)

            # Display the new speed on the printer's LCD
            if enable_lcd_messages:
                lines.insert(3, lcd_line)

    Logger.log('d', f'AutoTowersGenerator completing {tower_type} SpeedTower post-processing')

    return gcode
