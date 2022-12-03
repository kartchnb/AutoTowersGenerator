<a href="https://www.buymeacoffee.com/kartchnb"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a soda&emoji=&slug=kartchnb&button_colour=40DCA5&font_colour=ffffff&font_family=Bree&outline_colour=000000&coffee_colour=FFDD00" /></a>

[![Github All Releases](https://img.shields.io/github/downloads/kartchnb/AutoTowersGenerator/total.svg)]()

# AutoTowersGenerator

### "I ... am rarely happier than when spending an entire day programming my computer to perform automatically a task that would otherwise take me a good ten seconds to do by hand." - Douglas Adams

This Cura plugin automates the creation of 3D printer calibration towers.  You can choose from preset towers to test different temperatures, print and fan speeds, flow rates, etc.  No more messing around with gcode!

And, if you have [OpenSCAD](https://openscad.org/) installed, you can generate custom versions of these towers to suit your own needs as well.

The following "towers" are supported:

## Bed Level Patterns
These aren't "towers", per se, but I've included them anyway since it's my plugin and I can do what I want.

These can help ensure your printer bed is properly leveled and your first layer is adhering well.  You can find some good tips on how to best use these on this [Filament Friday Video](https://www.youtube.com/watch?v=_EfWVUJjBdA&ab_channel=CHEP) or this [All 3DP article](https://all3dp.com/2/ender-3-pro-bed-leveling-gcode/).

There are several bed print patterns available, although the concentric squares is probably all you really need.  Note that these all require OpenSCAD to be installed, since they are customized to your print bed size.  

### Concentric Squares
![Concentric Squares Bed Level Pattern Icon](Resources/Images/bedlevelpattern_concentric_squares_icon.png?raw=true "Concentric Squares Bed Level Pattern Icon")

### Concentric Circles
![Concentric Circles Bed Level Pattern Icon](Resources/Images/bedlevelpattern_concentric_circles_icon.png?raw=true "Concentric Circles Bed Level Pattern Icon")

### Circle in Square
![Circle in Square Bed Level Pattern Icon](Resources/Images/bedlevelpattern_circle_in_square_icon.png?raw=true "Circle in Square Bed Level Pattern Icon")

### X in Square
![X in Square Bed Level Pattern Icon](Resources/Images/bedlevelpattern_x_in_square_icon.png?raw=true "X in Square Bed Level Pattern Icon")

### Grid
![Grid Bed Level Pattern Icon](Resources/Images/bedlevelpattern_grid_icon.png?raw=true "Grid Bed Level Pattern Icon")

### Five Circles
![Five Circles Bed Level Pattern Icon](Resources/Images/bedlevelpattern_five_circles_icon.png?raw=true "Five Circles Bed Level Pattern Icon")


## Fan Towers
![Fan Tower Icon](Resources/Images/fantower_icon.png?raw=true "Fan Tower Icon")

A fan tower uses a different fan speed percentage for each section of the tower and is equivalent to changing Cura's "fan speed" setting in the "Cooling" menu.  The fan speed percentage for each section is printed on the tower itself.  Once you've printed the tower, just find the fan speed that works best for you.  Look for sections that bridge well and don't have gaps between layers.

## Flow Towers
![Flow Tower Icon](Resources/Images/flowtower_icon.png?raw=true "Flow Tower Icon")

A flow tower uses a different flow percentage for each section of the tower and is equivalent to changing Cura's "flow" setting in the "Material" menu. The flow percentage for each section is printed on the tower itself.  Once you've printed the tower, a visual inspection should help you identify the flow setting that works best.  Look for sections that don't have gaps between the printed lines.  

All3DP has a [good article](https://all3dp.com/2/extrusion-multiplier-cura-ways-to-improve-your-prints/) with some visual examples of what good and bad flow might look like.

## Retraction Towers
![Retraction Tower Icon](Resources/Images/retracttower_icon.png?raw=true "Retraction Tower Icon")

This is a useful way to tune your retraction settings.

A retraction tower uses a different retraction speed or retraction distance for each section of the tower.  This is equivalent to changing Cura's "Retraction Speed" or "Retraction Distance" settings in the "Travel" menu.  The speed or distance for each section is printed on the tower.  Look for settings that give the least stringing between the two sides of the tower.

[This All3DP Article](https://all3dp.com/2/cura-retraction-settings-how-to-avoid-stringing/) may help in understanding the different retraction settings.

## Speed Towers
![Speed Tower Icon](Resources/Images/speedtower_icon.png?raw=true "Speed Tower Icon")

Speed towers can be generated to evaluate different speed settings.

### Print Speed
Print speed towers are intended to simulate changing Cura's "print speed" setting in the "Speed" menu.  The print speed for each section is printed on the tower itself.  Look for tower sections that don't have gaps or extra blobs.

Please note that I'm still trying to figure out the best way to change print speed during post-processing and this tower is not entirely accurate.  However, it should give you a decent idea of what speed setting is best for your printer and filament.

### Other Speed Settings
Speed towers can also be generated to test acceleration speed, jerk speed, junction speed, marlin linear speed, and RepRap pressure.  Honestly, I don't fully understand these settings - I just vary them for you.  If you're smart enough to know what these do, you don't need me to explain them to you.

## Temperature Towers
![Temperature Tower Icon](Resources/Images/temptower_icon.png?raw=true "Temperature Tower Icon")

The correct print temperature is one of the most important things to get right and is the reason I created this plugin in the first place.

A temperature tower will print with different print temperatures for each section of the tower. There are presets for the most common filaments or you can create a custom one for your needs.  The print temperature for each section is printed right on the tower itself, so it's a simple matter of choosing the one that gives the best results.

# Plugin Settings
There are just a couple of settings for this plugin at the moment.

## OpenSCAD Path
This is used to specify the path to where OpenSCAD is installed.  Most of the time, this will be detected automatically but, if you have it installed in a non-standard location, you may need to configure this manually.  

## Enable LCD Messages
With this selected, the plugin will send updates to your printer's LCD as the tower is printed.  Some printers don't handle the M117 gcode command that is used to send these messages, so deselect it if it causes you problems.

# Some Final Notes
 
 - Preset towers are designed to work best with the most common layer heights that I use: 0.10, 0.12, 0.20, 0.24, and 0.30.  The plugin will accomodate for other layer heights, but may not work perfectly.

- There is no need to add a post-processing script after creating the tower.  The post-processing is automatically done for you!  

- To remove the tower and its post-processing, you can either select the model in Cura and delete it, or click the "A" button that will show up next to Cura's slicing button.

- Depending on the tower that you select, this plugin may adjust some of your settings automatically (for example, to turn off supports when printing temperature towers).  These settings should be restored just as automatically when you remove the tower or close Cura.

- Although this plugin can be used without having OpenSCAD installed, you'll get much more flexibility and power out of it if you do.  Download and install from [openscad.org](https://openscad.org/).

- I owe a huge debt to 5axes and his [Calibration Shapes plugin](https://marketplace.ultimaker.com/app/cura/plugins/5axes/CalibrationShapes).  The post-processing code was adapted directly from his plugin and I learned a lot from reviewing his code.  If you haven't installed his plugin yet, stop reading this and install it now.

- Although I've attempted to maintain compatibility with Cura version 4.13.0, I haven't tested with anything earlier than Cura 5.0.0 for some time now and can't guarantee that it still works.  If you find compatibility issues, please let me know.

- I gladly welcome bug reports or ideas for enhancements and try to respond as quickly as I can.

- Finally, share and enjoy!
