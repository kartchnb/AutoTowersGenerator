import math
import os
import subprocess

nominalBaseHeight_fanTower = 0.8
nominalSectionHeight_fanTower = 8.0

nominalBaseHeight_retractTower = 0.8
nominalSectionHeight_retractTower = 8.0

nominalBaseHeight_tempTower = 0.8
nominalSectionHeight_tempTower = 8.0

# A full list of layerheights to generate for
layerHeights = [0.1, 0.2, 0.3]

# These values must mirror the _presets in TempTowerController.py
tempTowerPresets = {
    'ABS' : 
    {
        'startTemp' : 250,
        'endTemp' : 210,
        'tempChange' : -5,
        'materialLabel': 'ABS',
        'towerDescription': '',
        'displayOnLcd': True,
    },

    'PETG' : 
    {
        'startTemp' : 260,
        'endTemp' : 230,
        'tempChange' : -5,
        'materialLabel': 'PETG',
        'towerDescription': '',
        'displayOnLcd': True,
    },

    'PLA' : 
    {
        'startTemp' : 220,
        'endTemp' : 180,
        'tempChange' : -5,
        'materialLabel': 'PLA',
        'towerDescription': '',
        'displayOnLcd': True,
    },

    'PLA+' :
    {
        'startTemp' : 230,
        'endTemp' : 200,
        'tempChange' : -5,
        'materialLabel': 'PLA+',
        'towerDescription': '',
        'displayOnLcd': True,
    },

    'TPU' : 
    {
        'startTemp' : 210,
        'endTemp' : 170,
        'tempChange' : -5,
        'materialLabel': 'TPU',
        'towerDescription': '',
        'displayOnLcd': True,
    },
}



# This method should mirror the _generateStlFilename member method in AutoTowersPlugin.py
def generateStlFilename(openScadFilename, openScadParameters):
    # Start by stripping the ".scad" extension from the OpenSCAD filename
    stlFilename = openScadFilename.replace('.scad', '')

    # Append each parameter and its value to the file name
    for parameter in openScadParameters:
        # Retrieve the parameter value
        value = openScadParameters[parameter]

        # Limit the parameter name to just the first 3 characters
        parameter = parameter[:3]

        # Add the parameter and value to the filename
        if isinstance(value, float):
            stlFilename += f'_{parameter}_{value:.3f}'
        else:
            stlFilename += f'_{parameter}_{value}'

    # Finally, add a ".stl" extension
    stlFilename += '.stl'

    return stlFilename



# this method combines a stripped-down version of the _modelCallback member 
# method in AutoTowersPlugin.py and GenerateStl from OpenScadInterface.py
def generateStl(openScadFilename, parameters):
    # Compile the STL file name
    inputFilePath = os.path.join('openscad', openScadFilename)
    stlFilename = generateStlFilename(openScadFilename, parameters)
    outputFilePath = os.path.join('stl', stlFilename)

    print(f'Generating {stlFilename}')

    # Start the command array with the OpenSCAD command
    command = ['openscad']

    # Tell OpenSCAD to automatically generate an STL file
    command.append(f'-o{outputFilePath}')

    # Add each variable setting parameter
    for parameter in parameters:
        # Retrieve the parameter value
        value = parameters[parameter]

        # If the value is a string, add escaped quotes around it
        if type(value) == str:
            value = f'\"{value}\"'

        command.append(f'-D{parameter}={value}')

    # Finally, specify the OpenSCAD source file
    command.append(inputFilePath)

    # Execute the command
    subprocess.run(command)



def calculateSectionHeight(nominalHeight, layerHeight):
    layers = math.ceil(nominalHeight / layerHeight)
    height = layers * layerHeight
    return height



def generateFanTower(layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_fanTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_fanTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = 100
    parameters ['Ending_Value'] = 50
    parameters ['Value_Change'] = -10
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Column_Label'] = 'FAN'
    parameters ['Tower_Label'] = ''

    generateStl('temptower.scad', parameters)



def generateRetractDistanceTower(layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_retractTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_retractTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = 1
    parameters ['Ending_Value'] = 6
    parameters ['Value_Change'] = 1
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Tower_Label'] = ''
    parameters ['Column_Label'] = 'DIST'

    generateStl('retracttower.scad', parameters)



def generateRetractSpeedTower(layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_retractTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_retractTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = 10
    parameters ['Ending_Value'] = 40
    parameters ['Value_Change'] = 10
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Tower_Label'] = ''
    parameters ['Column_Label'] = 'SPD'

    generateStl('retracttower.scad', parameters)
    


def generateTempTower(preset, layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_tempTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_tempTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = preset['startTemp']
    parameters ['Ending_Value'] = preset['endTemp']
    parameters ['Value_Change'] = preset['tempChange']
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Column_Label'] = preset['materialLabel']
    parameters ['Tower_Label'] = preset['towerDescription']

    generateStl('temptower.scad', parameters)



# Fan Towers
for layerHeight in layerHeights:
    generateFanTower(layerHeight)

# Retraction Towers
for layerHeight in layerHeights:
    generateRetractDistanceTower(layerHeight)
    generateRetractSpeedTower(layerHeight)

# Temperature Towers
for layerHeight in layerHeights:
    for presetName in tempTowerPresets:
        preset = tempTowerPresets[presetName]
        generateTempTower(preset, layerHeight)
