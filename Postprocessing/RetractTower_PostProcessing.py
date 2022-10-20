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

from UM.Logger import Logger
from UM.Application import Application
import re 

__version__ = '2.2'



def is_begin_layer_line(line: str) -> bool:
    '''Check if current line is the start of a layer section.'''
    return line.strip().startswith(";LAYER:")

def is_retract_line(line: str) -> bool:
    '''Check if current line is a retract segment'''
    return line.strip().startswith('G1') and 'F' in line and 'E' in line and not 'X' in line and not 'Y' in line and not 'Z' in line
    
def is_extrusion_line(line: str) -> bool:
    '''Check if current line is a standard printing segment'''
    return line.strip().startswith('G1') and 'X' in line and 'Y' in line and 'E' in line

def is_relative_instruction_line(line: str) -> bool:
    '''Check if current line contain a M83 / G91 towerType'''
    return line.strip().startswith('G91') or line.strip().startswith('M83')

def is_not_relative_instruction_line(line: str) -> bool:
    '''Check if current line contain a M82 / G90 towerType'''
    return line.strip().startswith('G90') or line.strip().startswith('M82')

def is_reset_extruder_line(line: str) -> bool:
    '''Check if current line contain a G92 E0'''
    return line.strip().startswith('G92') and 'E0' in line



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, towerType, displayOnLcd):
    Logger.log('d', 'AutoTowersGenerator beginning RetractTower post-processing')
    Logger.log('d', f'Starting value = {startValue}')
    Logger.log('d', f'Value change = {valueChange}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';RetractTower ({towerType}) start {towerType} = {startValue}, {towerType} change = {valueChange}\n'

    extruder = Application.getInstance().getGlobalContainerStack().extruderList[0]
    relative_extrusion = bool(extruder.getProperty('relative_extrusion', 'value'))

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    currentValue = -1
    save_e = -1

    if towerType == 'Speed':
        lcd_gcode = f'M117 SPD {startValue:.1f}mm/s ; AutoTowersGenerator added'
    else:
        lcd_gcode = f'M117 DST {startValue: .1f}mm ; AutoTowersGenerator added'
    
    current_e = 0
    current_f = 0
    first_code = False

    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)
        
        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:                  
            lineIndex = lines.index(line)
            
            if is_relative_instruction_line(line):
                relative_extrusion = True
            if is_not_relative_instruction_line(line):
                relative_extrusion = False
            if is_reset_extruder_line(line):
                current_e = 0
                save_e = 0
                
            # If we have defined a value
            if currentValue >= 0:
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
                                if towerType == 'Speed':
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; AutoTowersGenerator retracting filament at {currentValue} mm/s (relative)' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'M117 SPD {int(currentValue)}mm/s ; AutoTowersGenerator added'
                                else:
                                    lines[lineIndex] = f'G1 F{int(current_f)} E{-currentValue:.5f} ; AutoTowersGenerator retracting {currentValue:.1f} mm of filament (relative)'
                                    lcd_gcode = f'M117 DST {currentValue:.1f}mm ; AutoTowersGenerator added'
                            # Extruding filament (relative)
                            else:
                                if towerType == 'Speed':
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; AutoTowersGenerator extruding filament at {currentValue} mm/s (relative)' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'M117 SPD {int(currentValue)}mm/s ; AutoTowersGenerator added'
                                else:
                                    if first_code:
                                        lines[lineIndex] = f'G1 F{int(current_f)} E{current_e:.5f} ; AutoTowersGenerator extruding {current_e:.1f} mm of filament (relative)'
                                        first_code = False
                                    else:
                                        lines[lineIndex] = f'G1 F{int(current_f)} E{currentValue:.5f} ; AutoTowersGenerator extruding {currentValue:.1f} mm of filament (relative)'
                                    lcd_gcode = f'M117 DST {currentValue:.1f}mm ; AutoTowersGenerator added'
                        else:
                            # Retracting filament (absolute)
                            if save_e > current_e:
                                if towerType == 'Speed':
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; AutoTowersGenerator retracting filament at {currentValue} mm/s (absolute)' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'M117 SPD {int(currentValue)}mm/s ; AutoTowersGenerator added'
                                else:
                                    current_e = save_e - currentValue
                                    lines[lineIndex] = f'G1 F{int(current_f)} E{current_e:.5f} ; AutoTowersGenerator retracting {currentValue:.1f} mm of filament (absolute)o'
                                    lcd_gcode = f'M117 DST {currentValue:.1f}mm ; AutoTowersGenerator added'
                            # Resetting the retraction
                            else:
                                if towerType == 'Speed':
                                    lines[lineIndex] = f'G1 F{int(currentValue * 60)} E{current_e:.5f} ; AutoTowersGenerator setting retraction speed to {currentValue} mm/s' # Speed value must be multiplied by 60 for the gcode
                                    lcd_gcode = f'M117 SPD {int(currentValue)}mm/s ; AutoTowersGenerator added'

            if is_extrusion_line(line):
                searchE = re.search(r'E([-+]?\d*\.?\d*)', line)
                if searchE:
                    save_e=float(searchE.group(1))             
            
            if is_begin_layer_line(line):
                # Initialize the change
                if (layerIndex == baseLayers):
                    currentValue = startValue
                    first_code = True
                    lines.insert(lineIndex + 1, '; AutoTowersGenerator start of the first section')
                    Logger.log('d', f'Start of first section at layer {layerIndex  - 2} - Setting the retraction {towerType} to {currentValue}')
                    if towerType == 'Speed':
                        lcd_gcode = f'M117 SPD {startValue:.1f}mm/s ; AutoTowersGenerator added'
                    else:
                        lcd_gcode = f'M117 DST {startValue:.1f}mm ; AutoTowersGenerator added'
                
                # Change the current value   
                if ((layerIndex - baseLayers) % sectionLayers == 0) and (layerIndex > baseLayers):
                    currentValue += valueChange
                    lines.insert(lineIndex + 1, '; AutoTowersGenerator start of the next section')
                    Logger.log('d', f'New section at layer {layerIndex - 2} - Setting the retraction {towerType} to {currentValue}')
                    if towerType == 'Speed':
                        lcd_gcode = f'M117 SPD {startValue:.1f}mm/s ; AutoTowersGenerator added'
                    else:
                        lcd_gcode = f'M117 DST {startValue:.1f}mm ; AutoTowersGenerator added'

                # Add M117 to add message on LCD
                if displayOnLcd:
                    lines.insert(lineIndex + 1, lcd_gcode)
                                            
        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', f'AutoTowersGenerator completing RetractTower post-processing ({towerType})')

    return gcode
