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

__version__ = '2.3'

from UM.Logger import Logger



def execute(gcode, start_speed, speed_change, section_layer_count, base_layer_count, tower_type, enable_lcd_messages):
    Logger.log('d', f'AutoTowersGenerator beginning SpeedTower {tower_type} post-processing')
    Logger.log('d', f'Starting speed = {start_speed}')
    Logger.log('d', f'Speed change = {speed_change}')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')

    # Document the settings in the g-code
    gcode[0] += f';SpeedTower ({tower_type}) start speed = {start_speed}, speed change = {speed_change}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    base_layer_count += 2

    current_speed = start_speed - speed_change # The current speed will be corrected when the first section is encountered

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = ';AutoTowersGenerator post-processing complete\n' + layer
            break

        # If this is the start of a new section (after the base)
        elif layer_index >= base_layer_count and (layer_index - base_layer_count) % section_layer_count == 0:

            # Increment the speed for this section
            current_speed += speed_change
    
            # Handle acceleration speed
            if tower_type == 'Acceleration':
                command_line = f'M204 S{int(current_speed)} ;AutoTowersGenerator setting acceleration to {int(current_speed)}mm/s/s for section {layer_index - base_layer_count}'
                lcd_line = f'M117 ACC S{int(current_speed)}mm/s/s ;AutoTowersGenerator added'

            # Handle jerk speed
            elif tower_type=='Jerk':
                command_line = f'M205 X{int(current_speed)} Y{int(current_speed)} ;AutoTowersGenerator setting jerk speed to {int(current_speed)}mm/s'
                lcd_line = f'M117 JRK X{int(current_speed)} Y{int(current_speed)}'

            # Handle junction speed
            elif tower_type=='Junction':
                command_line = f'M205 J{float(current_speed):.3f} ;AutoTowersGenerator setting junction value to {float(current_speed):.3f}'
                lcd_line = f'M117 JCN J{float(current_speed):.3f}'

            # Handle Marlin linear speed
            elif tower_type=='Marlin linear':
                command_line = f'M900 K{float(current_speed):.3f} ;AutoTowersGenerator setting Marlin linear value to {float(current_speed):.3f}'
                lcd_line = f'M117 LIN {float(current_speed):.3f}'

            # Handle RepRap pressure speed
            elif tower_type=='RepRap pressure':
                command_line = f'M572 D0 S{float(current_speed):.3f} ;AutoTowersGenerator setting RepRap pressure value to {float(current_speed):.3f}'
                lcd_line = f'M117 PRS {float(current_speed):.3f}'

            # Handle unrecognized tower types
            else:  
                Logger.log('e', f'MiscSpeedTower_PostProcessing: unrecognized tower type "{tower_type}"')
                break

            # Insert the new code into the layer
            layer = command_line + layer
            if enable_lcd_messages:
                layer = lcd_line + layer
            gcode[layer_index] = layer

    Logger.log('d', f'AutoTowersGenerator completing SpeedTower post-processing ({tower_type})')

    return gcode
