# This script was adapted (although largely taken wholesale) from the 
# SpeedTower script developed by 5axes as part of his excellent 
# CalibrationShapes plugin
#
# Version 2.0 - 17 Sep 2022: 
#   Updates as part of the plugin upgrade for Cura 5.1
# Version 2.1 - 19 Sep 2022: 
#   Updated to match Version 1.7 of 5axes' SpeedTower processing script

from UM.Logger import Logger

__version__ = '2.1'



def execute(gcode, startValue, valueChange, sectionLayers, baseLayers, towerType):
    Logger.log('d', 'AutoTowersGenerator beginning SpeedTower post-processing')
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
    maximumLayer = 9999

    idl=0
    
    # Iterate over each layer in the g-code
    for layer in gcode:
        layerIndex = gcode.index(layer)

        # Iterate over each command line in the layer
        lines = layer.split('\n')
        for line in lines:

            if line.startswith(';LAYER_COUNT:'):
                maximumLayer = int(line.split(':')[1])
            
            if line.startswith(';LAYER:'):
                lineIndex = lines.index(line)

                if (layerIndex == baseLayers):
                    Logger.log('d', f'Start of first section layer {layerIndex  - 2}')
                    if (towerType == 'Speed'):
                        command = f'M220 B\nM220 S{int(currentValue)} ; AutoTowersGenerator setting speed to {int(currentValue)}mm/s'
                        lcd_gcode = f'M117 SPD {int(currentValue)}mm/s ; AutoTowersGenerator added'
                    if (towerType == 'Acceleration'):
                        command = f'M204 S{int(currentValue)} ; AutoTowersGenerator setting acceleration to {int(currentValue)}mm/s/s'
                        lcd_gcode = f'M117 ACC {int(currentValue)}mm/s/s ; AutoTowersGenerator added'
                    if (towerType=='Jerk'):
                        command = f'M205 X{int(currentValue)} Y{int(currentValue)} ; AutoTowersGenerator setting jerk speed to {int(currentValue)}mm/s'
                        lcd_gcode = f'M117 JRK {int(currentValue)}mm/s ; AutoTowersGenerator added'
                    if (towerType=='Junction'):
                        command = f'M205 J{float(currentValue):.3f} ; AutoTowersGenerator setting junction value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 JCN J{float(currentValue):.3f} ; AutoTowersGenerator added'
                    if (towerType=='Marlin linear'):
                        command = f'M900 K{float(currentValue):.3f} ; AutoTowersGenerator setting Marlin linear value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 LIN {float(currentValue):.3f} ; AutoTowersGenerator added'
                    if (towerType=='RepRap pressure'):
                        command = f'M572 D0 S{float(currentValue):.3f} ; AutoTowersGenerator setting RepRap pressure value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 PRS {float(currentValue):.3f} ; AutoTowersGenerator added'
                        
                    lines.insert(lineIndex + 1, command)
                    lines.insert(lineIndex + 2, lcd_gcode)

                if ((layerIndex-baseLayers) % sectionLayers == 0) and ((layerIndex - baseLayers) > 0):
                    Logger.log('d', f'New section at layer {layerIndex - 2}')
                    currentValue += valueChange
            
                    if (towerType == 'Speed'):
                        command=f'M220 S{int(currentValue)} ; AutoTowersGenerator setting speed to {int(currentValue)}mm/s'
                        lcd_gcode = f'M117 SPD {currentValue}mm/s ; AutoTowersGenerator added'
                    if  (towerType == 'Acceleration'):
                        command = f'M204 S{int(currentValue)} ; AutoTowersGenerator setting acceleration to {int(currentValue)}mm/s/s'
                        lcd_gcode = f'M117 ACC S{int(currentValue)}mm/s/s ; AutoTowersGenerator added'
                    if  (towerType=='Jerk'):
                        command = f'M205 X{int(currentValue)} Y{int(currentValue)} ; AutoTowersGenerator setting jerk speed to {int(currentValue)}mm/s'
                        lcd_gcode = f'M117 JRK X{int(currentValue)} Y{int(currentValue)}'
                    if  (towerType=='Junction'):
                        command = f'M205 J{float(currentValue):.3f} ; AutoTowersGenerator setting junction value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 JCN J{float(currentValue):.3f}'
                    if  (towerType=='Marlin linear'):
                        command = f'M900 K{float(currentValue):.3f} ; AutoTowersGenerator setting Marlin linear value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 LIN {float(currentValue):.3f}'
                    if  (towerType=='RepRap pressure'):
                        command = f'M572 D0 S{float(currentValue):.3f} ; AutoTowersGenerator setting RepRap pressure value to {float(currentValue):.3f}'
                        lcd_gcode = f'M117 PRS {float(currentValue):.3f}'
                        
                    lines.insert(lineIndex + 1, command)
                    lines.insert(lineIndex + 2, lcd_gcode)                                              
        
        if towerType == 'Speed' and layerIndex > maximumLayer:
            lineIndex = len(lines)
            lines.insert(lineIndex, 'M220 R\n')

        result = '\n'.join(lines)
        gcode[layerIndex] = result

    Logger.log('d', f'AutoTowersGenerator completing SpeedTower post-processing ({towerType})')

    return gcode
