/* [General Parameters] */
// The label to add to the tower
Tower_Label = "";

// The label to add the to right column
Column_Label = "";

// Text to prefix to the section labels
Section_Label_Prefix = "";

// Text to suffix to the section labels
Section_Label_Suffix = "";

// The starting value (temperature or fan speed)
Starting_Value = 220;

// The ending value (temperature or fan speed) of the tower
Ending_Value = 180;

// The amount to change the value (temperature or fan speed) between sections
Value_Change = -5;

// The height of the base
Base_Height = 0.801;

// The height of each section of the tower
Section_Height = 8.001;



/* [Advanced Parameters] */
// The font to use for tower text
Font = "Arial:style=Bold";

// Should sections be labeled?
Label_Sections = true;

// The height of the section labels in relation to the height of each section
Section_Label_Height_Multiplier = 0.401;

// The height of the tower label in relation to the length of the column
Tower_Label_Height_Multiplier = 0.601;

// The height of the column label in relation to the height of each section
Column_Label_Height_Multiplier = 0.301;

// The thickness of walls in the tower
Wall_Thickness = 0.601;

// The width of the tower as multiples of the section height
Tower_Width_Multiplier = 5.001;

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
Screenshot_Vpr = [ 75.00, 0.00, 300.00 ];

// The viewport translation for the screenshot
Screenshot_Vpt = [ 0.00, 0.00, 15.00 ];



/* [Calculated parameters] */
// Calculate the rendering quality
$fn = $preview ? Preview_Quality_Value : Render_Quality_Value;

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

// Determine the size (width and height) of the supports on either side of the bridge
Support_Size = Cube_Size/2;

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

// Calculate the font size
Section_Label_Font_Size = Cube_Size * Section_Label_Height_Multiplier;
Tower_Label_Font_Size = Cube_Size * Tower_Label_Height_Multiplier;
Column_Label_Font_Size = Cube_Size * Column_Label_Height_Multiplier; 

// Calculate the depth of the labels
Label_Depth = Wall_Thickness/2;



// Generate the model
module Generate_Model()
{
    // Generate the base of the tower independantly of the tower sections
    module Generate_Base()
    {
        translate([-Base_Width/2, -Base_Length/2, 0])
            cube([Base_Width, Base_Length, Base_Height]);
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
                // Generate the columns on either side of the tower
                for(x_offset = [-Tower_Width/2 + Cube_Size/2, Tower_Width/2 - Cube_Size/2])
                translate([x_offset, 0, 0])
                    Generate_SectionColumn();

                // Generate the bridge at the top of the section
                Generate_SectionBridge();

                // Generate the angled supports for the bridge
                Generate_LeftBridgeSupport();
                Generate_RightBridgeSupport();
            }

            // Carve out the label for this section
            if (Label_Sections)
                Generate_SectionLabel(label);
        }
    }



    // Generate the columns on either side of the section
    module Generate_SectionColumn()
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

            // Hollow out the inside of the column
            translate([-hollow_size/2, -hollow_size/2, -Iota])
                cube([hollow_size, hollow_size, Cube_Size + Iota*2]);
        }
    }



    // Generate a bridge connecting the two section columns
    module Generate_SectionBridge()
    {
        // Generate the bridge proper
        translate([-Tower_Width/2 + Cube_Size, -Cube_Size/2, Cube_Size - Bridge_Thickness - Cap_Height])
            cube([Tower_Width - Cube_Size*2, Cube_Size, Bridge_Thickness]);
    }



    // Generate an angled bridge support on the left side of a section
    module Generate_LeftBridgeSupport()
    {
        // Generate the left bridge support
        translate([-Tower_Width/2 + Cube_Size, 0, Cube_Size - Support_Size - Cap_Height - Bridge_Thickness])
        difference()
        {
            // Solid cube support
            translate([0, -Cube_Size/2, 0])
                cube([Support_Size, Cube_Size, Support_Size]);

            // Chop the cube off at a 45 degree angle
            angled_height = sqrt(pow(Support_Size, 2)*2);
            translate([0, -Cube_Size/2, 0])
            rotate([0, 45, 0])
            translate([-Iota, -Iota, 0])
                cube([Support_Size, Cube_Size + Iota*2, angled_height]);
        }
    }



    // Generate a curved bridge support on the right side of a section
    module Generate_RightBridgeSupport()
    {
        // Generate the left bridge support
        translate([Tower_Width/2 - Cube_Size, 0, Cube_Size - Support_Size - Cap_Height - Bridge_Thickness])
        difference()
        {
            // Solid cube support
            translate([-Support_Size, -Cube_Size/2, 0])
                cube([Support_Size, Cube_Size, Support_Size]);

            // Round out this support
            translate([-Support_Size, 0, 0])
            rotate([90, 0, 0])
                cylinder(r=Support_Size, Cube_Size + Iota*2, center=true);
        }
    }



    // Generate the text that will be carved into the square section column
    module Generate_SectionLabel(label)
    {
        full_label = str(Section_Label_Prefix, label, Section_Label_Suffix);
        translate([-Tower_Width/2 + Cube_Size/2, -Cube_Size/2 - Iota, Cube_Size/2])
        rotate([90, 0, 0])
        translate([0, 0, -Label_Depth])
        linear_extrude(Label_Depth + Iota)
            text(text=full_label, font=Font, size=Section_Label_Font_Size, halign="center", valign="center");
    }



    // Generate the text that will be carved along the left side of the tower
    module Generate_TowerLabel(label)
    {
        translate([-Tower_Width/2 - Iota, 0, Cube_Size/2])
        rotate([90, -90, -90])
        translate([0, 0, -Label_Depth])
        linear_extrude(Label_Depth + Iota)
            text(text=label, font=Font, size=Tower_Label_Font_Size, halign="left", valign="center");
    }



    // Generate the curved text that will be carved into the first rounded section column
    module Generate_ColumnLabel(label)
    {
        translate([Tower_Width/2 - Cube_Size/2, -Cube_Size/2 - Iota, Cube_Size/2])
        rotate([90, 0, 0])
        translate([0, 0, -Label_Depth])
        linear_extrude(Label_Depth + Iota)
            text(text=label, font=Font, size=Column_Label_Font_Size, halign="center", valign="center");
    }



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



    Generate();
}



// Generate the model
Generate_Model();

// Orient the viewport
$vpd = Orient_for_Screenshot ? Screenshot_Vpd : $vpd;
$vpf = Orient_for_Screenshot ? Screenshot_Vpf : $vpf;
$vpr = Orient_for_Screenshot ? Screenshot_Vpr : $vpr;
$vpt = Orient_for_Screenshot ? Screenshot_Vpt : $vpt;
