# This script was adapted (although largely taken wholesale) from the 
# ReatractTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin

from UM.Logger import Logger
from UM.Application import Application
import re # To perform the search
from enum import Enum

__version__ = '1.0'

class Section(Enum):
    '''Enum for section type.'''

    NOTHING = 0
    SKIRT = 1
    INNER_WALL = 2
    OUTER_WALL = 3
    INFILL = 4
    SKIN = 5
    SKIN2 = 6

def is_begin_layer_line(line: str) -> bool:
    '''Check if current line is the start of a layer section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a layer section
    '''
    return line.startswith(';LAYER:')

def is_retract_line(line: str) -> bool:
    '''Check if current line is a retract segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a retract segment
    '''
    return 'G1' in line and 'F' in line and 'E' in line and not 'X' in line and not 'Y' in line and not 'Z' in line
    
def is_extrusion_line(line: str) -> bool:
    '''Check if current line is a standard printing segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    '''
    return 'G1' in line and 'X' in line and 'Y' in line and 'E' in line

def is_not_extrusion_line(line: str) -> bool:
    '''Check if current line is a rapid movement segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    '''
    return 'G0' in line and 'X' in line and 'Y' in line and not 'E' in line

def is_relative_instruction_line(line: str) -> bool:
    '''Check if current line contain a M83 / G91 towerType

    Args:
        line (str): Gcode line

    Returns:
        bool: True contain a M83 / G91 towerType
    '''
    return 'G91' in line or 'M83' in line

def is_not_relative_instruction_line(line: str) -> bool:
    '''Check if current line contain a M82 / G90 towerType

    Args:
        line (str): Gcode line

    Returns:
        bool: True contain a M82 / G90 towerType
    '''
    return 'G90' in line or 'M82' in line

def is_reset_extruder_line(line: str) -> bool:
    '''Check if current line contain a G92 E0

    Args:
        line (str): Gcode line

    Returns:
        bool: True contain a G92 E0 towerType
    '''
    return 'G92' in line and 'E0' in line
    

def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, towerType):
    Logger.log('d', f'Post-processing for retraction {towerType} tower')
    Logger.log('d', f'Starting value = {startValue}')
    Logger.log('d', f'Value change = {valueChange}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')
   
    extruder = Application.getInstance().getGlobalContainerStack().extruderList[0]
    relative_extrusion = bool(extruder.getProperty('relative_extrusion', 'value'))

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    currentValue = -1
    save_e = -1

    lcd_gcode = f'M117 {towerType} ({startValue:.1f}/{valueChange:.1f}'
    
    current_e = 0

    for layer in gcode:
        layerIndex = gcode.index(layer)
        
        lines = layer.split('\n')
        for line in lines:                  
            lineIndex = lines.index(line)
            
            if is_relative_instruction_line(line):
                relative_extrusion = True
            if is_not_relative_instruction_line(line):
                relative_extrusion = False
            if is_reset_extruder_line(line):
                current_e = 0
                
            # If we have defined a value
            if currentValue>=0:
                if is_retract_line(line):
                    searchF = re.search(r'F(\d*)', line)
                    if searchF:
                        current_f=float(searchF.group(1))
                        
                    searchE = re.search(r'E([-+]?\d*\.?\d*)', line)
                    if searchE:
                        current_e=float(searchE.group(1))
                        if relative_extrusion:
                            # Retracting filament (relative)
                            if current_e<0:
                                if  (towerType == 'speed'):
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; Setting retraction speed to {currentValue}' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'Retract speed: {int(currentValue)}mm/s'
                                else:
                                    lines[lineIndex] = f'G1 F{int(current_f)} E{-currentValue:.5f} ; Setting retraction distance to {currentValue}'
                                    lcd_gcode = f'Retract distance: {currentValue:.3f}mm'
                            # Extruding filament (relative)
                            else:
                                if  (towerType == 'speed'):
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; Setting retraction speed to {currentValue}' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'Retract speed: {int(currentValue)}mm/s'
                                else:
                                    lines[lineIndex] = f'G1 F{int(current_f)} E{currentValue:.5f} ; Setting retraction distance to {currentValue}'
                                    lcd_gcode = f'Retract distance: {currentValue:.3f}mm'
                        else:
                            # Retracting filament (absolute)
                            if save_e>current_e:
                                if  (towerType == 'speed'):
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; Setting retraction speed to {currentValue}' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'Retract speed: {int(currentValue)}mm/s'
                                else:
                                    current_e = save_e - currentValue
                                    lines[lineIndex] = f'G1 F{int(current_f)} E{current_e:.5f} ; Setting retraction distance to {currentValue}'
                                    lcd_gcode = f'Retract distance: {currentValue:.3f}mm'
                            # Extruding filament (absolute)
                            else:
                                if  (towerType == 'speed'):
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; Setting retraction speed to {currentValue}' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'Retract speed: {int(currentValue)}mm/s'

            if is_extrusion_line(line):
                searchE = re.search(r'E([-+]?\d*\.?\d*)', line)
                if searchE:
                    save_e=float(searchE.group(1))             
            
            if line.startswith(';LAYER:'):
                # Initialize the change
                if (layerIndex==baseLayers):
                    currentValue = startValue
                    Logger.log('d', f'Start of first section at layer {layerIndex  - 2} - Setting the retraction {towerType} to {currentValue}')
                    lcd_gcode = f'Retract {towerType} starting at {startValue:.1f}'
                    lines.insert(lineIndex + 1, 'Start of the first section')
                
                # Change the current value   
                if ((layerIndex-baseLayers) % sectionLayers == 0) and ((layerIndex-baseLayers)>0):
                    currentValue += valueChange
                    Logger.log('d', f'New section at layer {layerIndex - 2} - Setting the retraction {towerType} to {currentValue}')
                    lcd_gcode = f'New section {towerType} {currentValue:.1f}'
                    lines.insert(lineIndex + 1, 'Start of the next section')

                # Add M117 to add message on LCD
                lines.insert(lineIndex + 1, lcd_gcode)
                                            
        result = '\n'.join(lines)
        gcode[layerIndex] = result

    return gcode
