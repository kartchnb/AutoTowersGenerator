# This script was adapted (although largely taken wholesale) from the 
# RetractTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 21 Sep 2022: 
#   Updated based on version 1.8 of 5axes' RetractTower processing script
# Version 2.2 - 1 Oct 2022:
#   Updated based on version 1.9 of 5axes' RetractdTower processing script
#   Commented-out gcode is now ignored, as it should be
# Version 2.3 - 25 Nov 2022:
#   Updated to ignore user-specified "End G-Code"
#   Rearchitected how lines are processed
# Version 2.4 - 26 Nov 2022:
#   Moved common code to PostProcessingCommon.py
__version__ = '2.4'

import re 

from UM.Logger import Logger
from UM.Application import Application

from cura.Settings.ExtruderManager import ExtruderManager

import PostProcessingCommon as Common



def execute(gcode, start_retract_value, retract_value_change, section_layer_count, base_layer_count, tower_type, enable_lcd_messages):
    Logger.log('d', 'AutoTowersGenerator beginning RetractTower post-processing')
    Logger.log('d', f'Starting value = {start_retract_value}')
    Logger.log('d', f'Value change = {retract_value_change}')
    Logger.log('d', f'Base layers = {base_layer_count}')
    Logger.log('d', f'Section layers = {section_layer_count}')

    # Document the settings in the g-code
    gcode[0] += f';RetractTower ({tower_type}) start {tower_type} = {start_retract_value}, {tower_type} change = {retract_value_change}\n'

    extruder = ExtruderManager.getInstance().getActiveExtruderStack()
    relative_extrusion = bool(extruder.getProperty('relative_extrusion', 'value'))

    # Calculate the number of layers before the first tower section
    skipped_layer_count = Common.CalculateSkippedLayerCount(base_layer_count)

    current_retract_value = start_retract_value - retract_value_change # The current retract value will be corrected when the first section is encountered
    save_e = -1
    current_e = 0
    current_f = 0
    first_code = False

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = f'{Common.comment_prefix} post-processing complete\n' + layer
            break

        # Only process layers after the base
        elif layer_index >= skipped_layer_count:

            # Process the start of the each section
            if (layer_index - skipped_layer_count) % section_layer_count == 0:

                # Handle the start of the first section
                if layer_index == skipped_layer_count:
                    first_code = True

                current_retract_value += retract_value_change
                layer = f'{Common.comment_prefix} start of the next section (retraction {tower_type} = {current_retract_value})\n' + layer
                Logger.log('d', f'New section at layer {layer_index - 2} - Setting the retraction {tower_type} to {current_retract_value}')

                if enable_lcd_messages:
                    if tower_type == 'Speed':
                        layer = f'M117 SPD {current_retract_value:.1f}mm/s {Common.comment_prefix} added line\n' + layer
                    else:
                        layer = f'M117 DST {current_retract_value:.1f}mm {Common.comment_prefix} added line\n' + layer

            # Iterate over each command line in the layer
            lines = layer.split('\n')
            for line_index, line in enumerate(lines):

                if Common.is_already_processed_line(line):
                    Logger.log('d', f'Found line: {line}')

                if not Common.is_already_processed_line(line):
                    if Common.is_relative_instruction_line(line):
                        relative_extrusion = True

                    elif Common.is_absolute_instruction_line(line):
                        relative_extrusion = False

                    elif Common.is_reset_extruder_line(line):
                        current_e = 0
                        save_e = 0

                    elif Common.is_extrusion_line(line):
                        search_e = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
                        string_e = search_e.group(1)
                        if search_e:
                            save_e=float(string_e)        

                    elif Common.is_retract_line(line):
                        search_f = re.search(r'F([-+]?\d*\.?\d+)', line.split(';')[0])
                        search_e = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])

                        if search_f and search_e:
                            current_f=float(search_f.group(1))
                            current_e=float(search_e.group(1))

                            # Handle relative extrusion
                            if relative_extrusion:
                                # Retracting filament (relative)
                                if current_e<0:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} {Common.comment_prefix} retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/m) (relative)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        lines[line_index] = f'G1 F{int(current_f)} E{-current_retract_value:.5f} {Common.comment_prefix} retracting {current_retract_value:.1f} mm of filament (relative)'
                                
                                 # Extruding filament (relative)
                                else:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} {Common.comment_prefix} extruding filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/m) (relative)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        if first_code:
                                            lines[line_index] = f'G1 F{int(current_f)} E{current_e:.5f} {Common.comment_prefix} extruding {current_e:.1f} mm of filament (relative)'
                                            first_code = False
                                        else:
                                            lines[line_index] = f'G1 F{int(current_f)} E{current_retract_value:.5f} {Common.comment_prefix} extruding {current_retract_value:.1f} mm of filament (relative)'
                            
                            # Handle absolute extrusion
                            else:
                                # Retracting filament (absolute)
                                if save_e > current_e:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} {Common.comment_prefix} retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/m) (absolute)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        current_e = save_e - current_retract_value
                                        lines[line_index] = f'G1 F{int(current_f)} E{current_e:.5f} {Common.comment_prefix} retracting {current_retract_value:.1f} mm of filament (absolute)'
                                
                                # Resetting the retraction
                                else:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} {Common.comment_prefix} setting retraction speed to {current_retract_value} mm/s ({current_retract_value * 60} mm/m)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        lines[line_index] = line

            gcode[layer_index] = '\n'.join(lines)

    Logger.log('d', f'AutoTowersGenerator completing RetractTower post-processing ({tower_type})')

    return gcode
