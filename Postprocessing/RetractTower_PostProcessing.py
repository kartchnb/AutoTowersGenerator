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
__version__ = '2.3'

import re 

from UM.Logger import Logger
from UM.Application import Application

from cura.Settings.ExtruderManager import ExtruderManager



def is_already_processed_line(line: str) -> bool:
    return ';AutoTowersGenerator' in line

def is_retract_line(line: str) -> bool:
    '''Check if current line is a retract segment'''
    return line.strip().startswith('G1') and 'F' in line and 'E' in line and not 'X' in line and not 'Y' in line and not 'Z' in line
    
def is_extrusion_line(line: str) -> bool:
    '''Check if current line is a standard printing segment'''
    return line.strip().startswith('G1') and 'X' in line and 'Y' in line and 'E' in line

def is_relative_instruction_line(line: str) -> bool:
    '''Check if current line contain a M83 / G91 instruction'''
    return line.strip().startswith('G91') or line.strip().startswith('M83')

def is_not_relative_instruction_line(line: str) -> bool:
    '''Check if current line contain a M82 / G90 instruction'''
    return line.strip().startswith('G90') or line.strip().startswith('M82')

def is_reset_extruder_line(line: str) -> bool:
    '''Check if current line contain a G92 E0'''
    return line.strip().startswith('G92') and 'E0' in line



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

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    base_layer_count += 2

    current_retract_value = start_retract_value - retract_value_change # The current retract value will be corrected when the first section is encountered
    save_e = -1

    if tower_type == 'Speed':
        lcd_gcode = f'M117 SPD {start_retract_value:.1f}mm/s ;AutoTowersGenerator added'
    else:
        lcd_gcode = f'M117 DST {start_retract_value: .1f}mm ;AutoTowersGenerator added'
    
    current_e = 0
    current_f = 0
    first_code = False

    # Iterate over each layer in the g-code
    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= len(gcode) - 1:
            gcode[layer_index] = ';AutoTowersGenerator post-processing complete\n' + layer
            break

        # Only process layers after the base
        elif layer_index >= base_layer_count:

            # Process the start of the each section
            if (layer_index - base_layer_count) % section_layer_count == 0:

                # Handle the start of the first section
                if layer_index == base_layer_count:
                    first_code = True

                current_retract_value += retract_value_change
                layer = f';AutoTowersGenerator start of the next section (retraction {tower_type} = {current_retract_value})\n' + layer
                Logger.log('d', f'New section at layer {layer_index - 2} - Setting the retraction {tower_type} to {current_retract_value}')

                if enable_lcd_messages:
                    if tower_type == 'Speed':
                        layer = f'M117 SPD {current_retract_value:.1f}mm/s ;AutoTowersGenerator added\n' + layer
                    else:
                        layer = f'M117 DST {current_retract_value:.1f}mm ;AutoTowersGenerator added\n' + layer

            # Iterate over each command line in the layer
            lines = layer.split('\n')
            for line_index, line in enumerate(lines):

                if is_already_processed_line(line):
                    Logger.log('d', f'Found line: {line}')

                if not is_already_processed_line(line):
                    if is_relative_instruction_line(line):
                        relative_extrusion = True

                    elif is_not_relative_instruction_line(line):
                        relative_extrusion = False

                    elif is_reset_extruder_line(line):
                        current_e = 0
                        save_e = 0

                    elif is_extrusion_line(line):
                        search_e = re.search(r'E([-+]?\d*\.?\d+)', line.split(';')[0])
                        string_e = search_e.group(1)
                        if search_e:
                            save_e=float(string_e)        

                    elif is_retract_line(line):
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
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} ;AutoTowersGenerator retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/m) (relative)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        command_line = f'G1 F{int(current_f)} E{-current_retract_value:.5f} ;AutoTowersGenerator retracting {current_retract_value:.1f} mm of filament (relative)'
                                
                                 # Extruding filament (relative)
                                else:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} ;AutoTowersGenerator extruding filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/m) (relative)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        if first_code:
                                            lines[line_index] = f'G1 F{int(current_f)} E{current_e:.5f} ;AutoTowersGenerator extruding {current_e:.1f} mm of filament (relative)'
                                            first_code = False
                                        else:
                                            lines[line_index] = f'G1 F{int(current_f)} E{current_retract_value:.5f} ;AutoTowersGenerator extruding {current_retract_value:.1f} mm of filament (relative)'
                            
                            # Handle absolute extrusion
                            else:
                                # Retracting filament (absolute)
                                if save_e > current_e:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} ;AutoTowersGenerator retracting filament at {current_retract_value} mm/s ({current_retract_value * 60} mm/m) (absolute)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        current_e = save_e - current_retract_value
                                        lines[line_index] = f'G1 F{int(current_f)} E{current_e:.5f} ;AutoTowersGenerator retracting {current_retract_value:.1f} mm of filament (absolute)'
                                
                                # Resetting the retraction
                                else:
                                    if tower_type == 'Speed':
                                        lines[line_index] = f'G1 F{int(current_retract_value * 60)} E{current_e:.5f} ;AutoTowersGenerator setting retraction speed to {current_retract_value} mm/s ({current_retract_value * 60} mm/m)' # Speed value must be multiplied by 60 for the gcode
                                    else:
                                        lines[line_index] = line

            gcode[layer_index] = '\n'.join(lines)

    Logger.log('d', f'AutoTowersGenerator completing RetractTower post-processing ({tower_type})')

    return gcode
