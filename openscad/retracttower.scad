/* [General Parameters] */
// The label to add to the side of the tower
Tower_Label = "";

// The label to add to the bottom of the right column
Column_Label = "";

// The starting value (speed or distance) for the tower
Starting_Value = 1.0;

// The ending value (speed or distance) for the tower
Ending_Value = 6.0;

// The amount to change the value (speed or distance) between sections
Value_Change = 1.0;

// The height of the base
Base_Height = 0.801;

// The height of each section of the tower
Section_Height = 8;



/* [Advanced] */
// The font to use for tower text
Font = "Arial:style=Bold";

// The height of the section labels in relation to the height of each section
Section_Label_Height_Multiplier = 0.301;

// The height of the tower label in relation to the length of the column
Tower_Label_Height_Multiplier = 0.601;

// The height of the column label in relation to the height of each section
Column_Label_Height_Multiplier = 0.301;

// The amount to space the letters in the column label as a multiple of the font height
Column_Label_Letter_Spacing_Multiplier = 1.001;

// The thickness of walls in the tower
Wall_Thickness = 0.601;

// The width of the tower as multiples of the section height
Tower_Width_Multiplier = 5.001;

// The value to use for creating the model preview (lower is faster)
Preview_Quality_Value = 24;

// The value to use for creating the final model render (higher is more detailed)
Render_Quality_Value = 24;



module Generate()
{
    // Add the base
    Generate_Base();

    difference()
    {
        // set the tower on top of the base
        translate([0, 0, Base_Height])
            Generate_Tower();

        // Create the tower label
        Generate_TowerLabel(Tower_Label);

        // Create the column label
        Generate_ColumnLabel(Column_Label);
    }
}



module Generate_Base()
{
    translate([-Base_Width/2, -Base_Length/2, 0])
        cube([Base_Width, Base_Length, Base_Height]);
}



module Generate_Tower()
{
    // Create each section
    for (section = [0: Section_Count - 1])
    {
        // Determine the value for this section
        value = Starting_Value + (Value_Change_Corrected * section);

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
            // Generate the columns on either side of the tower
            translate([-Tower_Width/2 + Cube_Size/2, 0, 0])
                Generate_SquareSectionColumn();
            translate([Tower_Width/2 - Cube_Size/2, 0, 0])
                Generate_RoundSectionColumn();

            // Generate the bridge at the top of the section
            Generate_SectionBridge();
        }

        // Carve out the text for this section
        Generate_SectionLabel(label);
    }
}




module Generate_SquareSectionColumn()
{
    hollow_size = Cube_Size - Wall_Thickness*3;

    difference()
    {
        union()
        {
            // Create the main body of the column
            translate([-Cube_Size/2, -Cube_Size/2, 0])
                cube([Cube_Size, Cube_Size, Cube_Size - Cap_Height]);

            // Create inset caps on top of the column
            translate([-Cap_Size/2, -Cap_Size/2, Cube_Size - Cap_Height])
                cube([Cap_Size, Cap_Size, Cap_Height]);
        }

        translate([-hollow_size/2, -hollow_size/2, -iota])
            cube([hollow_size, hollow_size, Cube_Size + iota*2]);
    }
}



module Generate_RoundSectionColumn()
{
    hollow_size = Cube_Size - Wall_Thickness*3;

    difference()
    {
        union()
        {
            // Create the main body of the column
            cylinder(d=Cube_Size, Cube_Size - Cap_Height);

            // Create inset caps on top of the column
            translate([0, 0, Cube_Size - Cap_Height])
                cylinder(d=Cap_Size, Cap_Height);
        }

        translate([0, 0, -iota])
            cylinder(d=hollow_size, Cube_Size + iota*2);
    }
}



module Generate_SectionBridge()
{
    // Generate the bridge proper
    translate([0, 0, Cube_Size - Bridge_Thickness - Cap_Height])
    difference()
    {
        translate([-Tower_Width/2 + Cube_Size, -Bridge_Length/2, 0])
            cube([Tower_Width - Cube_Size - Cube_Size/2, Bridge_Length, Bridge_Thickness]);
        translate([Tower_Width/2 - Cube_Size/2, 0, -iota])
            cylinder(d=Cube_Size, Cube_Size);
    }
}



module Generate_SectionLabel(label)
{
    label_depth = Wall_Thickness/2;

    translate([-Tower_Width/2 + Cube_Size/2, -Cube_Size/2 - iota, Cube_Size/2])
    rotate([90, 0, 0])
    translate([0, 0, -label_depth])
    linear_extrude(label_depth + iota)
        text(text=label, font=Font, size=Section_Label_Font_Size, halign="center", valign="center");
}



module Generate_TowerLabel(label)
{
    translate([-Tower_Width/2 - iota, 0, Cube_Size/2])
    rotate([90, -90, -90])
    translate([0, 0, -Label_Depth])
    linear_extrude(Label_Depth + iota)
        text(text=label, font=Font, size=Tower_Label_Font_Size, halign="left", valign="center");
}



module Generate_ColumnLabel(label)
{
    // This function is rushed and hacky, but it works...

    letter_radius = Cube_Size/2 - Label_Depth;
    letter_sweep_angle = (Column_Label_Font_Size / (2 * PI * letter_radius)) * 360;
    label_sweep_angle = len(label) * letter_sweep_angle + (len(label) - 1) * letter_sweep_angle * Column_Label_Letter_Spacing_Multiplier;
    start_angle = -label_sweep_angle/4;
    echo(start_angle=start_angle);

    translate([Tower_Width/2 - Cube_Size/2, 0, Base_Height + Cube_Size/2])
    difference()
    {
        for (i = [0: 1: len(label)-1])
        {
            letter = label[i];
            z_angle = (i-(len(label)-1)/2)*letter_sweep_angle*Column_Label_Letter_Spacing_Multiplier;
            rotate([0, 0, z_angle])
            rotate([90, 0, 0])
            linear_extrude(Cube_Size)
                text(text=letter, font=Font, size=Column_Label_Font_Size, halign="center", valign="center");
        }

        translate([0, 0, -Column_Label_Font_Size])
            cylinder(r=letter_radius, Column_Label_Font_Size*3);
    }
}



// Global parameters
iota = 0.001;
$fn = $preview ? Preview_Quality_Value : Render_Quality_Value;



// Calculated parameters

// Ensure the value change has the correct sign
Value_Change_Corrected = Ending_Value > Starting_Value
    ? abs(Value_Change)
    : -abs(Value_Change);

// Determine how many sections to generate
Section_Count = ceil(abs(Ending_Value - Starting_Value) / abs(Value_Change) + 1);

// Determine the size (width and length) of each column cube
Cube_Size = Section_Height;

// Determine the size (width and length) of the inset cap at the top of each column cube
Cap_Size = Cube_Size - Wall_Thickness;

// Determine the height of the inset cap at the top of each column cube
Cap_Height = Wall_Thickness;

// Determine the bridge thickness
Bridge_Thickness = Wall_Thickness;

// Deteermine the length (in the y direction) of the bridge
Bridge_Length = Cube_Size/2;


// Calculate the width (in the x direction) of the tower
Tower_Width = Cube_Size*Tower_Width_Multiplier;

// Calculate the length (in the y direction) of the tower
Tower_Length = Cube_Size;

// Calculate the amount to expand the base beyond the size of the tower
Base_Extension = Wall_Thickness*4;

// Calculate the width (in the x direction) of the base of the tower
Base_Width = Tower_Width + Base_Extension*2;

// Calculate the length (in the y direction) of the base of the tower
Base_Length = Tower_Length + Base_Extension*2;

// Calculate the font sizes
Section_Label_Font_Size = Cube_Size * Section_Label_Height_Multiplier;
Tower_Label_Font_Size = Cube_Size * Tower_Label_Height_Multiplier;
Column_Label_Font_Size = Cube_Size * Column_Label_Height_Multiplier; 

// Calculate the depth of the labels
Label_Depth = Wall_Thickness/2;



// Generate the model
color("white")
Generate();
$vpt=[0, 0, 35];
$vpr=[90, 0, -60];
$vpd=220;