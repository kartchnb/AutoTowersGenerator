#!/usr/bin/python3

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

# Fan tower presets
fanTowerPresets = {
    'default' :
    {
        'startValue' : 100,
        'endValue' : 50,
        'valueChange' : -10,
        'columnLabel' : 'FAN',
        'towerLabel' : '',
    },
}

# Retract distance tower presets
retractDistanceTowerPresets = {
    'default' :
    {
        'startValue' : 10,
        'endValue' : 40,
        'valueChange' : 10,
        'columnLabel' : 'SPD',
        'towerLabel' : '',
    },

}

# Retract speed tower presets
retractSpeedTowerPresets = {
    'default' :
    {
        'startValue' : 1,
        'endValue' : 6,
        'valueChange' : 1,
        'columnLabel' : 'DIST',
        'towerLabel' : '',
    },

}

# Temperature tower presets
# These values must mirror the _presets in TempTowerController.py
tempTowerPresets = {
    'ABS' : 
    {
        'startValue' : 250,
        'endValue' : 210,
        'valueChange' : -5,
        'columnLabel': 'ABS',
        'towerLabel': '',
    },

    'PETG' : 
    {
        'startValue' : 260,
        'endValue' : 230,
        'valueChange' : -5,
        'columnLabel': 'PETG',
        'towerLabel': '',
    },

    'PLA' : 
    {
        'startValue' : 220,
        'endValue' : 180,
        'valueChange' : -5,
        'columnLabel': 'PLA',
        'towerLabel': '',
    },

    'PLA+' :
    {
        'startValue' : 230,
        'endValue' : 200,
        'valueChange' : -5,
        'columnLabel': 'PLA+',
        'towerLabel': '',
    },

    'TPU' : 
    {
        'startValue' : 210,
        'endValue' : 170,
        'valueChange' : -5,
        'columnLabel': 'TPU',
        'towerLabel': '',
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



def generateFanTower(preset, layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_fanTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_fanTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = preset['startValue']
    parameters ['Ending_Value'] = preset['endValue']
    parameters ['Value_Change'] = preset['valueChange']
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Column_Label'] = preset['columnLabel']
    parameters ['Tower_Label'] = preset['towerLabel']

    generateStl('temptower.scad', parameters)



def generateRetractDistanceTower(preset, layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_retractTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_retractTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = preset['startValue']
    parameters ['Ending_Value'] = preset['endValue']
    parameters ['Value_Change'] = preset['valueChange']
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Column_Label'] = preset['columnLabel']
    parameters ['Tower_Label'] = preset['towerLabel']

    generateStl('retracttower.scad', parameters)



def generateRetractSpeedTower(preset, layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_retractTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_retractTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = preset['startValue']
    parameters ['Ending_Value'] = preset['endValue']
    parameters ['Value_Change'] = preset['valueChange']
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Column_Label'] = preset['columnLabel']
    parameters ['Tower_Label'] = preset['towerLabel']

    generateStl('retracttower.scad', parameters)
    


def generateTempTower(preset, layerHeight):
    baseHeight = calculateSectionHeight(nominalBaseHeight_tempTower, layerHeight)
    sectionHeight = calculateSectionHeight(nominalSectionHeight_tempTower, layerHeight)

    parameters = {}
    parameters ['Starting_Value'] = preset['startValue']
    parameters ['Ending_Value'] = preset['endValue']
    parameters ['Value_Change'] = preset['valueChange']
    parameters ['Base_Height'] = baseHeight
    parameters ['Section_Height'] = sectionHeight
    parameters ['Column_Label'] = preset['columnLabel']
    parameters ['Tower_Label'] = preset['towerLabel']

    generateStl('temptower.scad', parameters)



for layerHeight in layerHeights:
    # Fan towers
    for presetName in fanTowerPresets:
        generateFanTower(fanTowerPresets[presetName], layerHeight)

    # Retraction distance towers
    for presetName in retractDistanceTowerPresets:
        generateRetractDistanceTower(retractDistanceTowerPresets[presetName], layerHeight)
    
    # Retraction speed towers
    for presetName in retractSpeedTowerPresets:
        generateRetractSpeedTower(retractSpeedTowerPresets[presetName], layerHeight)

    # Temperature towers
    for presetName in tempTowerPresets:
        generateTempTower(tempTowerPresets[presetName], layerHeight)
