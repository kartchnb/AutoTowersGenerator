from . import AutoTowersGenerator

def getMetaData():
    return {}

def register(app):
    return { 'extension' : AutoTowersGenerator.AutoTowersGenerator() }
