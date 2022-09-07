# This script was adapted (although largely taken wholesale) from the 
# ReatractTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin

from ..Script import Script
from UM.Application import Application
from UM.Logger import Logger
import re #To perform the search

__version__ = '1.0'

def execute(self, gcode, startSpeed, speedChange, sectionLayers, baseLayers, towerType):
    Logger.log('d', f'Begin SpeedTower post-processing ({towerType})')
    Logger.log('d', f'Starting speed = {startSpeed}')
    Logger.log('d', f'Speed change = {speedChange}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';SpeedTower ({towerType}): start speed = {startSpeed}, speed change = {speedChange}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    currentValue = startSpeed
    comand=''

    idl=0
    
    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:                  
            
            if line.startswith(';LAYER:'):
                lineIndex = lines.index(line)

                if (layerIndex == baseLayers):
                    Logger.log('d', f'Start of first section layer {layerIndex  - 2}')
                    if  (towerType == 'acceleration'):
                        comand = f'M204 S{int(currentValue)} ; Setting acceleration to {int(currentValue)}'
                        lcd_gcode = f'M117 Accel S{int(currentValue)}'
                    if  (towerType=='jerk'):
                        comand = f'M205 X{int(currentValue)} Y{int(currentValue)} ; Setting jerk to {int(currentValue)}'
                        lcd_gcode = f'M117 Jerk X{int(currentValue)} Y{int(currentValue)}'
                    if  (towerType=='junction'):
                        comand = f'M205 J{float(currentValue):.3f} ; Setting junction to {int(currentValue)}'
                        lcd_gcode = f'M117 Junction J{float(currentValue):.3f}'
                    if  (towerType=='Marlin linear'):
                        comand = f'M900 K{float(currentValue):.3f} ; Setting Marlin linear to {int(currentValue)}'
                        lcd_gcode = f'M117 L Advance K{float(currentValue):.3f}'
                    if  (towerType=='RepRap pressure'):
                        comand = f'M572 D0 S{float(currentValue):.3f} ; Setting RepRap pressure to {int(currentValue)}'
                        lcd_gcode = f'M117 P Advance S{float(currentValue):.3f}'
                        
                    lines.insert(lineIndex + 1, comand)
                    lines.insert(lineIndex + 2, lcd_gcode)

                if ((layerIndex-baseLayers) % sectionLayers == 0) and ((layerIndex - baseLayers) > 0):
                        Logger.log('d', f'New section at layer {layerIndex - 2}')
                        currentValue += speedChange
                
                        if  (towerType == 'acceleration'):
                            comand = f'M204 S{int(currentValue)} ; Setting acceleration to {int(currentValue)}'
                            lcd_gcode = f'M117 Accel S{int(currentValue)}'
                        if  (towerType=='jerk'):
                            comand = f'M205 X{int(currentValue)} Y{int(currentValue)} ; Setting jerk to {int(currentValue)}'
                            lcd_gcode = f'M117 Jerk X{int(currentValue)} Y{int(currentValue)}'
                        if  (towerType=='junction'):
                            comand = f'M205 J{float(currentValue):.3f} ; Setting junction to {int(currentValue)}'
                            lcd_gcode = f'M117 Junction J{float(currentValue):.3f}'
                        if  (towerType=='Marlin linear'):
                            comand = f'M900 K{float(currentValue):.3f} ; Setting Marlin linear to {int(currentValue)}'
                            lcd_gcode = f'M117 L Advance K{float(currentValue):.3f}'
                        if  (towerType=='RepRap pressure'):
                            comand = f'M572 D0 S{float(currentValue):.3f} ; Setting RepRap pressure to {int(currentValue)}'
                            lcd_gcode = f'M117 P Advance S{float(currentValue):.3f}'
                            
                        lines.insert(lineIndex + 1, comand)
                        lines.insert(lineIndex + 2, lcd_gcode)                                              
        
        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', f'End SpeedTower post-processing ({towerType})')

    return gcode
