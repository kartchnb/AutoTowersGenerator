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
__version__ = '2.2'

from UM.Logger import Logger



def execute(gcode, start_temp, temp_change, section_layer_count, base_layer_count, enable_lcd_messages):
    Logger.log('d', 'AutoTowersGenerator beginning TempTower post-processing')
    Logger.log('d', f'Starting temperature = {start_temp}')
    Logger.log('d', f'Temperature change = {temp_change}')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')

    # Document the settings in the g-code
    gcode[0] += f';TempTower start temp = {start_temp}, temp change = {temp_change}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    base_layer_count += 2

    # Start at the selected starting temperature
    current_temp = start_temp - temp_change # The current temp will be incremented when the first section is encountered

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = ';AutoTowersGenerator post-processing complete\n' + layer
            break

        # Only process layers after the base
        elif layer_index >= base_layer_count and (layer_index - base_layer_count) % section_layer_count == 0:

            # Increment the temperature
            current_temp += temp_change
            layer = f'M104 S{current_temp} ;AutoTowersGenerator setting temperature to {current_temp} for the next section' + layer
            if enable_lcd_messages:
                layer = f'M117 Temp {current_temp} ;AutoTowersGenerator added' + layer

            gcode[layer_index] = layer

    Logger.log('d', 'AutoTowersGenerator completing Temp Tower post-processing')
    
    return gcode