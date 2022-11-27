# Code common among multiple post-processing scripts

# A string to use when commenting added or modified lines
comment_prefix = ';AutoTowersGenerator:'

# The number of layers that are automatically inserted into the gcode before the actual printed layers
# Layer index 0 contains comments added by Cura
# Layer index 1 contains the user-specified start gcode
# Layer index 2 is the first official layer (Cura calls it "Layer 0" in the gcode)
inserted_layer_count = 2



def CalculateSkippedLayerCount(base_layer_count):
    ''' Returns the number of layers before the first tower section '''
    return base_layer_count + inserted_layer_count



def is_already_processed_line(line: str) -> bool:
    ''' Check if the given line has already been processed '''
    return comment_prefix in line



def is_fan_speed_change_line(line: str) -> bool:
    ''' Check if the given line changes the fan speed '''
    return line.strip().startswith('M106 S')



def is_fan_off_line(line: str) -> bool:
    ''' Check if the given line turns the fan off '''
    return line.strip().startswith('M107')



def is_start_of_bridge(line: str) -> bool:
    ''' Check if the given line is the start of a bridge '''
    return line.strip().startswith(';BRIDGE')



def is_print_speed_line(line: str) -> bool:
    ''' Check if the given line changes the print speed '''
    return line.strip().startswith('G1') and 'F' in line



def is_retract_line(line: str) -> bool:
    ''' Check if the given line is a retraction command '''
    return line.strip().startswith('G1') and 'F' in line and 'E' in line and not 'X' in line and not 'Y' in line and not 'Z' in line



def is_extrusion_line(line: str) -> bool:
    ''' Check if the given line is an extrusion command '''
    return line.strip().startswith('G1') and 'X' in line and 'Y' in line and 'E' in line



def is_relative_instruction_line(line: str) -> bool:
    ''' Check if the given line selectx relative positioning '''
    return line.strip().startswith('G91') or line.strip().startswith('M83')



def is_absolute_instruction_line(line: str) -> bool:
    ''' Check if the given line selects absolute positioning '''
    return line.strip().startswith('G90') or line.strip().startswith('M82')



def is_reset_extruder_line(line: str) -> bool:
    ''' Check if the given line resets the current position for relative positioning '''
    return line.strip().startswith('G92') and 'E0' in line
