# Code common among multiple post-processing scripts

from decimal import Decimal # Used to prevent floating-point inaccuracies from creeping into calculations



# A string to use when commenting added or modified lines
comment_prefix = ';AutoTowersGenerator:'

# The number of layers that are automatically inserted into the gcode before the actual printed layers
# Layer index 0 contains comments added by Cura
# Layer index 1 contains the user-specified start gcode
# Layer index 2 is the first official layer (Cura calls it "Layer 0" in the gcode)
initial_inserted_layer_count = 2

# The number of layers that are automatically inserted into the gcode after the printed layers
trailing_inserted_layer_count = 2



def LayerEnumerate(gcode, base_height:float, section_height:float, initial_layer_height:float, layer_height:float):
    ''' Iterates over the lines in the gcode that is passed in 
        skipping Cura's comment layer and the user-specified start gcode 
        and ignoring post-printing layers '''

    # Convert the heights to decimal numbers for better mathematical accuracy
    base_height = Decimal(str(base_height))
    section_height = Decimal(str(section_height))
    initial_layer_height = Decimal(str(initial_layer_height))
    layer_height = Decimal(str(layer_height))

    # Keep track of the current print height
    current_print_height = Decimal('0')

    # Keep track of where the next section should start
    next_section_start_height = base_height

    # Keep track of the tower section number
    tower_section_number = 0

    # Determine the number of layers in the gcode
    layer_count = len(gcode)

    for layer_index, layer in enumerate(gcode):

        # The last layer contains user-specified end gcode, which should not be processed
        if layer_index >= layer_count - trailing_inserted_layer_count:
            gcode[layer_index] = f'{comment_prefix} post-processing complete\n' + layer
            break

        # Ignore Cura's comment layer and the user-specified code layer
        elif layer_index < initial_inserted_layer_count:
            continue

        # Increment the print height
        if current_print_height == 0:
            current_print_height += initial_layer_height
        else:
            current_print_height += layer_height

        # Don't process layers until after the base has been printed
        if current_print_height <= base_height:
            continue

        # Split the layer into lines
        lines = layer.split('\n')

        # Determine if this is the start of a new tower section
        if current_print_height > next_section_start_height:
            
            # Indicate this is the start of a new tower section
            start_of_new_section = True

            # Update the starting height of the next tower section
            next_section_start_height += section_height

            # Increment the tower section number
            tower_section_number += 1
            
            # Comment the start of the tower section in the gcode
            cura_layer_number = layer_index - 1
            lines.insert(1, f'{comment_prefix} Starting tower section number {tower_section_number} at Cura layer number {cura_layer_number}')

        # If this is not the start of a new tower section
        else:

            # Indicate this is NOT the start of a new tower section
            start_of_new_section = False

        # Iterate over each line in the layer
        for line_index, line in enumerate(lines):

            # Don't reprocess lines
            if not IsAlreadyProcessedLine(line):
                
                # Yield the values for this layer
                yield line_index, line, lines, start_of_new_section

            # Once the first line in a new tower section has been processed, remove the new section indicator
            start_of_new_section = False

        # Reassemble the layer
        gcode[layer_index] = '\n'.join(lines)



def CalculateCuraLayerNumber(layer_index):
    ''' Converts a gcode layer index to the layer number that is shown in the Cura preview '''
    return layer_index - 1



def IsAlreadyProcessedLine(line: str) -> bool:
    ''' Check if the given line has already been processed '''
    return comment_prefix in line



def IsFanSpeedChangeLine(line: str) -> bool:
    ''' Check if the given line changes the fan speed '''
    return line.strip().startswith('M106 S')



def IsFanOffLine(line: str) -> bool:
    ''' Check if the given line turns the fan off '''
    return line.strip().startswith('M107')



def IsStartOfBridge(line: str) -> bool:
    ''' Check if the given line is the start of a bridge '''
    return line.strip().startswith(';BRIDGE')



def IsPrintSpeedLine(line: str) -> bool:
    ''' Check if the given line changes the print speed '''
    return line.strip().startswith('G1') and 'F' in line and 'X' in line and 'Y' in line



def IsRetractLine(line: str) -> bool:
    ''' Check if the given line is a retraction command '''
    return line.strip().startswith('G1') and 'F' in line and 'E' in line and not 'X' in line and not 'Y' in line and not 'Z' in line



def IsExtrusionLine(line: str) -> bool:
    ''' Check if the given line is an extrusion command '''
    return line.strip().startswith('G1') and 'X' in line and 'Y' in line and 'E' in line



def IsRelativeInstructionLine(line: str) -> bool:
    ''' Check if the given line selectx relative positioning '''
    return line.strip().startswith('G91') or line.strip().startswith('M83')



def IsAbsoluteInstructionLine(line: str) -> bool:
    ''' Check if the given line selects absolute positioning '''
    return line.strip().startswith('G90') or line.strip().startswith('M82')



def IsResetExtruderLine(line: str) -> bool:
    ''' Check if the given line resets the current position for relative positioning '''
    return line.strip().startswith('G92') and 'E0' in line
