from . import AutoTowersPlugin

def getMetaData():
    return {}

def register(app):
    return { 'extension' : AutoTowersPlugin.AutoTowersPlugin() }
