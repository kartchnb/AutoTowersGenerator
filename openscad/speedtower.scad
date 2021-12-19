/* [General Parameters] */
// The label to add to the tower
Tower_Label = "DESCRIPTION";

// The temperature the tower was printed at
Temperature_Label = "180° C";

// The starting speed
Starting_Speed = 20;

// The ending speed
Ending_Speed = 100;

// The amount to change the speed between sections
Speed_Change = 10;

// The height of the base
Base_Height = 0.801;

// The height of each section of the tower
Section_Height = 8.001;



/* [Advanced] */
// The font to use for tower text
Font = "Arial:style=Bold";

// The angle of the slope of each section
Slope_Angle = 45.001;

// The height of the section labels in relation to the height of each section
Section_Label_Height_Multiplier = 0.301;

// The height of the tower label in relation to the length of the column
Tower_Label_Height_Multiplier = 0.601;

// The height of the temperature label in relation to the height of each section
Temperature_Label_Height_Multiplier = 0.301;

// The thickness of walls in the tower
Wall_Thickness = 0.601;

// The amount to inset the panels in each section
Panel_Inset = 0.501;

// The value to use for creating the model preview (lower is faster)
Preview_Quality_Value = 24;

// The value to use for creating the final model render (higher is more detailed)
Render_Quality_Value = 24;



module Generate()
{
    // Add the base
    Generate_Base();

    translate([0, 0, Base_Height])
    difference()
    {
        // set the tower on top of the base
        Generate_Tower();

        // Create the tower label
        Generate_TowerLabel(Tower_Label);

        // Create the column label
        Generate_TemperatureLabel(Temperature_Label);
    }
}



module Generate_Base()
{
    translate([-Base_Size/2, -Base_Size/2, 0])
        cube([Base_Size, Base_Size, Base_Height]);
}



module Generate_Tower()
{
    // Create each section
    for (section = [0: Section_Count - 1])
    {
        // Determine the value for this section
        value = Starting_Speed + (Speed_Change_Corrected * section);

        // Determine the offset of the section
        z_offset = section*Section_Height;

        // Generate the section itself and move it into place
        translate([0, 0, z_offset])
            Generate_Section(str(value));
    }
}



module Generate_Section(label)
{
    difference()
    {
        union()
        {
            // Create the main body of the section
            translate([-Column_Size/2, -Column_Size/2, 0])
                cube([Column_Size, Column_Size, Section_Height - Cap_Height]);

            // Generate the cap on top of the section cube
            translate([-Cap_Size/2, -Cap_Size/2, Section_Height - Cap_Height])
                cube([Cap_Size, Cap_Size, Cap_Height]);
        }

        // Carve out an inset panel on the side of the column
        translate([-Panel_Width/2, Column_Size/2 - Panel_Inset, (Section_Height - Cap_Height - Panel_Height)/2])
            cube([Panel_Width, Panel_Inset + iota, Panel_Height]);

        // Carve away the angled wall
        translate([-Column_Size/2, -Column_Size/2, Section_Height - Cap_Height])
        rotate([0, 0, 45])
        rotate([0, -45, 0])
        translate([-Column_Size, -Column_Size/3, -Column_Size*3])
            cube([Column_Size, Column_Size/1.5, Column_Size*3]);
    }

    // Carve out the label for this section
    Generate_SectionLabel(label);
}



module Generate_SectionLabel(label)
{
    translate([0, Column_Size/2 - Panel_Inset + Label_Depth, (Section_Height - Cap_Height)/2])
    rotate([90, 0, 180])
    translate([0, 0, -Label_Depth])
    linear_extrude(Label_Depth)
        text(text=label, font=Font, size=Section_Label_Font_Size, halign="center", valign="center");
}



module Generate_TowerLabel(label)
{
    translate([Column_Size/2 - Label_Depth, 0, Wall_Thickness])
    rotate([0, -90, 180])
    linear_extrude(Label_Depth + iota)
        text(text=label, font=Font, size=Tower_Label_Font_Size, halign="left", valign="center");
}



module Generate_TemperatureLabel(label)
{
    translate([Column_Size/4, -Column_Size/2 + Label_Depth, Wall_Thickness])
    rotate([0, -90, 90])
    linear_extrude(Label_Depth + iota)
        text(text=label, font=Font, size=Temperature_Label_Font_Size, halign="left", valign="center");
}



// Global parameters
iota = 0.001;
$fn = $preview ? Preview_Quality_Value : Render_Quality_Value;



// Calculated parameters

// Ensure the value change has the correct sign
Speed_Change_Corrected = Ending_Speed > Starting_Speed
    ? abs(Speed_Change)
    : -abs(Speed_Change);

// Determine how many sections to generate
Section_Count = ceil(abs(Ending_Speed - Starting_Speed) / abs(Speed_Change) + 1);

// Determine the size (width and length) of each column cube
Column_Size = Section_Height*1.5;

// Determine the size (width and length) of the inset cap at the top of each column cube
Cap_Size = Column_Size - Wall_Thickness;

// Determine the height of the inset cap at the top of each column cube
Cap_Height = Wall_Thickness;

// Calculate the amount to expand the base beyond the size of the tower
Base_Extension = Wall_Thickness*4;

// Calculate the width (in the x direction) of the base of the tower
Base_Size = Column_Size + Base_Extension*2;

// Calculate the dimensions of the inset panel in each section
Panel_Width = Column_Size - Wall_Thickness*2;
Panel_Height = Section_Height - Cap_Height - Wall_Thickness*2;

// Calculate the font size
Section_Label_Font_Size = Section_Height * Section_Label_Height_Multiplier;
Tower_Label_Font_Size = Column_Size * Tower_Label_Height_Multiplier;
Temperature_Label_Font_Size = Column_Size * Temperature_Label_Height_Multiplier; 

// Calculate the depth of the labels
Label_Depth = Wall_Thickness/2;



// Generate the model
color("white")
Generate();
$vpt=[0, 0, 35];
$vpr=[90, 0, -60];
$vpd=220;