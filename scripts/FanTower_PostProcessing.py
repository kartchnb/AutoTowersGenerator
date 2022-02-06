# This script was heavily adapted from the TempFanTower script developed by
# 5@xes as part of his excellent CalibrationShapes plugin
from UM.Logger import Logger

__version__ = '1.0'

def execute(gcode, startPercent, percentChange, sectionLayers, baseLayers):
    Logger.log('d', f'Start speed = {startPercent}%')
    Logger.log('d', f'Speed change = {percentChange}%')
    Logger.log('d', f'Base layers = {baseLayers}')
    Logger.log('d', f'Section layers = {sectionLayers}')

    # The number of base layers needs to be modified to take into account the numbering offset in the g-code
    # Layer index 0 is the initial block?
    # Layer index 1 is the start g-code?
    # Our code starts at index 2?
    baseLayers += 2

    currentPercent = startPercent

    afterbridge = False

    for layer in gcode:
        layerIndex = gcode.index(layer)

        lines = layer.split('\n')
        for line in lines:
            if line.startswith('M106 S') and (layerIndex-baseLayers)>0 and afterbridge:
                Logger.log('d', f'Resuming fan speed of {currentPercent}% after bridge at layer {layerIndex - 2}')
                lineIndex = lines.index(line)
                currentFanValue = int((currentPercent * 255)/100)  #  100% = 255 pour ventilateur
                lines[lineIndex] = f'M106 S{currentFanValue} ; Resuming fan speed of {currentPercent}% after bridge'
                afterbridge = False
                lines.insert(lineIndex + 1, f'M117 Fan Speed: {currentPercent}%')

            if line.startswith('M107') and (layerIndex-baseLayers)>0:
                Logger.log('d', f'Just completed a bridge at layer {layerIndex - 2}')
                afterbridge = True
                lineIndex = lines.index(line)

            if line.startswith(";LAYER:"):
                lineIndex = lines.index(line)

                if (layerIndex==baseLayers):
                    Logger.log('d', f'Start of first section at layer {layerIndex - 2} - setting fan speed to {currentPercent}%')
                    currentFanValue = int((currentPercent * 255)/100)  #  100% = 255 pour ventilateur
                    lines.insert(lineIndex + 1, f'M106 S{currentFanValue} ; Setting fan speed to {currentPercent}% for the first section')
                    lines.insert(lineIndex + 2, f'M117 Fan Speed: {currentPercent}%')

                if ((layerIndex-baseLayers) % sectionLayers == 0) and ((layerIndex-baseLayers)>0):
                    currentPercent += percentChange
                    Logger.log('d', f'Start of new section at layer {layerIndex - 2} - setting fan speed to {currentPercent}%')
                    currentFanValue = int((currentPercent * 255)/100)  #  100% = 255 pour ventilateur
                    lines.insert(lineIndex + 1, f'M106 S{currentFanValue} ; Setting fan speed to {currentPercent}% for the next section')
                    lines.insert(lineIndex + 2, f'M117 Fan Speed: {currentPercent}%')


        result = '\n'.join(lines)
        gcode[layerIndex] = result

    return gcode