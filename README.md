# AutoTowersPlugin
This is a Cura plugin that automates the creation of 3D printer calibration towers.

"I ... am rarely happier than when spending an entire day programming my computer to perform automatically a task that would otherwise take me a good ten seconds to do by hand."
- Douglas Adams

This project stemmed from my own laziness and a love of automation.

There are instructions all over explaining how to generate temperature towers and 5axes even created the incredibly useful "Calibration Shapes" plugin, which does most of the work for you - one click to create the tower model, another few clicks to add a temperature change script.  Viola!

And, yet, it was still too much work for me.  I wondered if it would be possible to automate the process even further.

So, with the goal of saving myself a good 10 seconds of work, I set out to learn how to write a Cura plugin to automate this entire process.  This plugin is the result.

With this plugin, printing a temperature tower is as easy as:
  1) Click "Auto Towers" from the "Extensions" menu in Cura.
  2) Select the appropriate temperature tower for the material you're using (or create your own custom tower!)
  3) Wait for OpenSCAD to generate the tower.
  4) Click "Slice" and print, just as you normally would.
  
It's a similar process to create a retraction tower or a fan tower!

This plugin relies on OpenSCAD being installed in the default location (on Windows and Mac) or in the current path (on Linux) to work.  This is because your calibration tower is customized to meet the parameters you set and the layer height you are printing at.

A couple of things to note:

- There is no need to add a post-processing script after creating the tower.  The post-processing is automatically done for you!  

- The tower is generated based on your current layer height.  If the layer height is changed after a tower is created, it will automatically be removed from the scene.  It's easy to recreate it, though!

- I love OpenSCAD, but it's a bit slow.  It can take a few minutes to create a tower for a particular combination of parameters and layer height.  However, once a tower has been created, the model is cached so it will be much faster the next time.  If you ever decide you need to clear out this cache, you can do that from the "Settings" menu by clicking "Clear STL Cache" button.

- The plugin should be able to find the location of OpenSCAD on your system.  If, for some reason, this doesn't work, you can configure the location by changing the "OpenSCAD Path" value in the "Settings" menu.

- I've done my best with this plugin, but I'm far from understanding everything about Cura and I'm still fairly new to Python.  I'm confident there are many things that are wrong or could be improved and suggestions are heartily welcomed.  There are few things I excel at, but getting things wrong is one of them.

- Finally, please enjoy the 10 seconds you save printing your calibration tower!  
