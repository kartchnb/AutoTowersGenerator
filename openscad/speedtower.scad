/* [General Parameters] */
// The label to add to the tower
Tower_Label = "";

// The temperature the tower was printed at
Temperature_Label = "";

// Text to prefix to the section labels
Section_Label_Prefix = "";

// Text to suffix to the section labels
Section_Label_Suffix = "";

// The starting value
Starting_Value = 20;

// The ending value
Ending_Value = 100;

// The amount to change the value between sections
Value_Change = 10;

// The height of the base
Base_Height = 0.801;

// The height of each section of the tower
Section_Height = 8.001;



/* [Advanced Parameters] */
// The font to use for tower text
Font = "Arial:style=Bold";

// Should sections be labeled?
Label_Sections = true;

// The angle of the slope of each section
Slope_Angle = 45.001;

// The height of the section labels in relation to the height of each section
Section_Label_Height_Multiplier = 0.401;

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

// A small value used to improve rendering in preview mode
Iota = 0.001;



/* [Development Parameters] */
// Orient the model for creating a screenshot
Orient_for_Screenshot = false;

// The viewport distance for the screenshot 
Screenshot_Vpd = 140.00;

// The viewport field of view for the screenshot
Screenshot_Vpf = 22.50;

// The viewport rotation for the screenshot
Screenshot_Vpr = [ 75.00, 0.00, 45.00 ];

// The viewport translation for the screenshot
Screenshot_Vpt = [ 0.00, 0.00, 15.00 ];



/* [Calculated Parameters] */
// Calculate the rendering quality
$fn = $preview ? Preview_Quality_Value : Render_Quality_Value;

// Ensure the value change has the correct sign
Value_Change_Corrected = Ending_Value > Starting_Value
    ? abs(Value_Change)
    : -abs(Value_Change);

// Determine how many sections to generate
Section_Count = ceil(abs(Ending_Value - Starting_Value) / abs(Value_Change) + 1);

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


module Generate_Model()
{
    // Generate the base of the tower independantly of the tower sections
    module Generate_Base()
    {
        translate([-Base_Size/2, -Base_Size/2, 0])
            cube([Base_Size, Base_Size, Base_Height]);
    }



    // Generate the tower proper by iteritively generating a section for each retraction value
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



    // Generate a single section of the tower with a given label
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
                cube([Panel_Width, Panel_Inset + Iota, Panel_Height]);

            // Carve away the angled wall
            translate([-Column_Size/2, -Column_Size/2, Section_Height - Cap_Height])
            rotate([0, 0, 45])
            rotate([0, -45, 0])
            translate([-Column_Size, -Column_Size/3, -Column_Size*3])
                cube([Column_Size, Column_Size/1.5, Column_Size*3]);
        }

        // Carve out the label for this section
        if (Label_Sections)
            Generate_SectionLabel(label);
    }



    // Generate the text that will be carved into the square section column
    module Generate_SectionLabel(label)
    {
        full_label = str(Section_Label_Prefix, label, Section_Label_Suffix);

        translate([0, Column_Size/2 - Panel_Inset + Label_Depth, (Section_Height - Cap_Height)/2])
        rotate([90, 0, 180])
        translate([0, 0, -Label_Depth])
        linear_extrude(Label_Depth)
            text(text=full_label, font=Font, size=Section_Label_Font_Size, halign="center", valign="center");
    }



    // Generate the text that will be carved up the side of the tower
    module Generate_TowerLabel(label)
    {
        translate([Column_Size/2 - Label_Depth, 0, Wall_Thickness])
        rotate([0, -90, 180])
        linear_extrude(Label_Depth + Iota)
            text(text=label, font=Font, size=Tower_Label_Font_Size, halign="left", valign="center");
    }



    // Generate the text that will be carved up the side of the tower indicating the temperature the speed tower
    // was printed at
    module Generate_TemperatureLabel(label)
    {
        translate([Column_Size/4, -Column_Size/2 + Label_Depth, Wall_Thickness])
        rotate([0, -90, 90])
        linear_extrude(Label_Depth + Iota)
            text(text=label, font=Font, size=Temperature_Label_Font_Size, halign="left", valign="center");
    }



    // Generate the model
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



    Generate();
}



// Generate the model
rotate([0, 0, 180])
    Generate_Model();

// Orient the viewport
$vpd = Orient_for_Screenshot ? Screenshot_Vpd : $vpd;
$vpf = Orient_for_Screenshot ? Screenshot_Vpf : $vpf;
$vpr = Orient_for_Screenshot ? Screenshot_Vpr : $vpr;
$vpt = Orient_for_Screenshot ? Screenshot_Vpt : $vpt;
