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

from UM.Logger import Logger

__version__ = '2.2'



def is_start_of_layer(line: str) -> bool:
    return line.strip().startswith(';LAYER:')



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, towerType):
    Logger.log('d', f'AutoTowersGenerator beginning SpeedTower {towerType} post-processing')
    Logger.log('d', f'Starting speed = {startValue}')
    Logger.log('d', f'Speed change = {valueChange}')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # Document the settings in the g-code
    gcode[0] = gcode[0] + f';SpeedTower ({towerType}) start speed = {startValue}, speed change = {valueChange}\n'

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    currentValue = startValue
    command=''
    
    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:

            if is_start_of_layer(line):
                lineIndex = lines.index(line)

                if (layerIndex == baseLayers):
                    Logger.log('d', f'Start of first section layer {layerIndex  - 2}')
                    if (towerType == 'Acceleration'):
                        command = f'M204 S{int(currentValue)} ; AutoTowersGenerator setting acceleration to {int(currentValue)}mm/s/s'
                        lcd_gcode = f'M117 ACC {int(currentValue)}mm/s/s ; AutoTowersGenerator added'
                        Logger.log('d', f'Setting acceleration to {int(currentValue)}mm/s/s')
                    if (towerType=='Jerk'):
                        command = f'M205 X{int(currentValue)} Y{int(currentValue)} ; AutoTowersGenerator setting jerk speed to {int(currentValue)}mm/s'
                        lcd_gcode = f'M117 JRK {int(currentValue)}mm/s ; AutoTowersGenerator added'
                        Logger.log('d', f'Setting jerk speed to {int(currentValue)}mm/s')
                    if (towerType=='Junction'):
                        command = f'M205 J{float(currentValue):.3f} ; AutoTowersGenerator setting junction value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 JCN J{float(currentValue):.3f} ; AutoTowersGenerator added'
                        Logger.log('d', f'Setting junction value to {float(currentValue):.3f}')
                    if (towerType=='Marlin linear'):
                        command = f'M900 K{float(currentValue):.3f} ; AutoTowersGenerator setting Marlin linear value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 LIN {float(currentValue):.3f} ; AutoTowersGenerator added'
                        Logger.log('d', f'Setting Marlin linear value to {float(currentValue):.3f}')
                    if (towerType=='RepRap pressure'):
                        command = f'M572 D0 S{float(currentValue):.3f} ; AutoTowersGenerator setting RepRap pressure value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 PRS {float(currentValue):.3f} ; AutoTowersGenerator added'
                        Logger.log('d', f'Setting RepRap pressure value to {float(currentValue):.3f}')
                        
                    lines.insert(lineIndex + 1, command)
                    lines.insert(lineIndex + 2, lcd_gcode)

                if ((layerIndex-baseLayers) % sectionLayers == 0) and ((layerIndex - baseLayers) > 0):
                    Logger.log('d', f'New section at layer {layerIndex - 2}')
                    currentValue += valueChange
            
                    if  (towerType == 'Acceleration'):
                        command = f'M204 S{int(currentValue)} ; AutoTowersGenerator setting acceleration to {int(currentValue)}mm/s/s'
                        lcd_gcode = f'M117 ACC S{int(currentValue)}mm/s/s ; AutoTowersGenerator added'
                        Logger.log('d', f'Setting acceleration to {int(currentValue)}mm/s/s')
                    if  (towerType=='Jerk'):
                        command = f'M205 X{int(currentValue)} Y{int(currentValue)} ; AutoTowersGenerator setting jerk speed to {int(currentValue)}mm/s'
                        lcd_gcode = f'M117 JRK X{int(currentValue)} Y{int(currentValue)}'
                        Logger.log('d', f'Setting jerk speed to {int(currentValue)}mm/s')
                    if  (towerType=='Junction'):
                        command = f'M205 J{float(currentValue):.3f} ; AutoTowersGenerator setting junction value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 JCN J{float(currentValue):.3f}'
                        Logger.log('d', f'Setting junction value to {float(currentValue):.3f}')
                    if  (towerType=='Marlin linear'):
                        command = f'M900 K{float(currentValue):.3f} ; AutoTowersGenerator setting Marlin linear value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 LIN {float(currentValue):.3f}'
                        Logger.log('d', f'Setting Marlin linear value to {float(currentValue):.3f}')
                    if  (towerType=='RepRap pressure'):
                        command = f'M572 D0 S{float(currentValue):.3f} ; AutoTowersGenerator setting RepRap pressure value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 PRS {float(currentValue):.3f}'
                        Logger.log('d', f'Setting RepRap pressure value to {float(currentValue):.3f}')
                        
                    lines.insert(lineIndex + 1, command)
                    lines.insert(lineIndex + 2, lcd_gcode)                                              

        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', f'AutoTowersGenerator completing SpeedTower post-processing ({towerType})')

    return gcode
