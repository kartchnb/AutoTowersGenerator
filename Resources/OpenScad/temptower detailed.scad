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
// The thickness of walls in the tower
Wall_Thickness = 0.601;

// The font to use for tower text
Font = "Arial:style=Bold";

// Should sections be labeled?
Label_Sections = true;

// The amount to expand the tower base beyond the outline of each section
Base_Extension = Wall_Thickness * 4;

// The angle of the left slope of each section
Left_Slope_Angle = 35;

// The angle of the right slope of each section
Right_Slope_Angle = 45;

// The height of the section labels in relation to the height of each section
Section_Label_Height_Multiplier = 0.401;

// The height of the tower label in relation to the length of the column
Tower_Label_Height_Multiplier = 0.601;

// The height of the column label in relation to the height of each section
Column_Label_Height_Multiplier = 0.301;

// The width of the tower as multiples of the section height
Section_Width_Multiplier = 8.001;

// The value to use for creating the model preview (lower is faster)
Preview_Quality_Value = 24;

// The value to use for creating the final model render (higher is more detailed)
Render_Quality_Value = 24;



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

// Calculate the length (in the y direction) of each section
Section_Length = Section_Height;

// Calculate the width (in the x direction) of the sloped portion at the left of each section
Left_Slope_Width = Section_Height / tan(Left_Slope_Angle);

// Calculate the width (in the x direction) of the compartment on the left of each section
Left_Compartment_Width = Section_Height * 2;

// Calculate the width (in the x direction) of the sloped portion at the right of each section
Right_Slope_Width = Section_Height / tan(Right_Slope_Angle);

// Calculate the overall width (in the x direction) of each section
Section_Width = (Left_Compartment_Width + Left_Slope_Width) * 2;

// Calculate the width (in the x direction) of the compartment on the right of each section
Right_Compartment_Width = Section_Width/2 - Right_Slope_Width;

// Calculate the height of each spike
Spike_Height = Section_Height - Wall_Thickness * 2;

// Calculate the base diameter of the wide spike
Wide_Spike_Diameter = Section_Length * .75;

// Calculate the base diameter of the thin spike
Thin_Spike_Diameter = Section_Length * .50;

// Calculate the diameter of the holes in the tower
Hole_Diameter = Section_Length / 4;

// Calculate the width (in the x direction) of the base of the tower
Base_Width = Section_Width + Base_Extension*2;

// Calculate the length (in the y direction) of the base of the tower
Base_Length = Section_Length + Base_Extension*2;

// Calculate the font size
Section_Label_Font_Size = Section_Height * Section_Label_Height_Multiplier;

// Calculate the depth of the labels
Label_Depth = Wall_Thickness/2;

// A small value used to improve rendering in preview mode
Iota = 0.001;



// Generate the model
module Generate_Model()
{
    module Generate_Slope_End(slope_width)
    {
        slope_height = Section_Height;
        hole_diameter = Hole_Diameter;
        hole_inset = Hole_Diameter/2 + Wall_Thickness*2;
        hole_height = Section_Height*2;

        points = 
        [
            [0, 0],
            [0, slope_height],
            [-slope_width, slope_height],
        ];

        difference()
        {
            rotate([90, 0, 0])
                linear_extrude(Section_Length, center=true)
                polygon(points=points);

            translate([-slope_width + hole_inset, 0, Section_Height/2 - hole_height/2])
                cylinder(d=hole_diameter, hole_height);
        }
    }



    module Generate_Left_Slope_End()
    {
        Generate_Slope_End(Left_Slope_Width);
    }


    module Generate_Left_Compartment_Curved_Point()
    {
        height = Section_Height/2;
        width = height;
        length = Section_Length;

        translate([0, 0, height/2])
        rotate([90, 0, 0])
            linear_extrude(length, center=true)
            intersection()
            {
                translate([0, -height])
                    square([width, height]);
                circle(r=height);
            }
    }



    module Generate_Left_Compartment_Curved_Wall()
    {
        width = Left_Compartment_Width/2 - Wall_Thickness;
        height = width;
        length = Section_Length;

        rotate([90, 0, 0])
            linear_extrude(length, center=true)
            difference()
            {
                translate([-width, 0])
                    square([width, height]);
                translate([-width, 0])
                    circle(r=width);
            }
    }



    module Generate_Left_Compartment()
    {
        // In a file full of atrocious OpenSCAD code, this module stands out as some of the worst I've ever written
        // But I'm in a hurry, so...
        outer_length = Section_Length;
        outer_width = Left_Compartment_Width;
        outer_height = Section_Height;
        inner_length = outer_length;
        inner_width = outer_width - Wall_Thickness * 3;
        inner_height = outer_height - Wall_Thickness * 3;
        hole_diameter = Hole_Diameter;
        hole_length = outer_width/2;

        difference()
        {
            union()
            {
                translate([-outer_width, -outer_length/2, 0])
                difference()
                {
                    cube([outer_width, outer_length, outer_height]);
                    translate([Wall_Thickness*2, Wall_Thickness, Wall_Thickness*2])
                        cube([inner_width, inner_length, inner_height]);
                }

                translate([-inner_width - Wall_Thickness, 0, Section_Height/2 + Wall_Thickness/2])
                    Generate_Left_Compartment_Curved_Point();

                translate([-Wall_Thickness, 0, 0])
                    Generate_Left_Compartment_Curved_Wall();
            }

            translate([0, 0, outer_height/2])
                rotate([0, 90, 0])
                cylinder(d=hole_diameter, h=hole_length, center=true);
        }
    }



    module Generate_Right_Slope_End()
    {
        mirror([1, 0, 0])
            Generate_Slope_End(Right_Slope_Width);
    }



    module Generate_Right_Compartment()
    {
        length = Section_Length;
        outer_width = Right_Compartment_Width;
        outer_height = Section_Height;
        inner_width = outer_width - Wall_Thickness * 2;
        inner_height = outer_height - Wall_Thickness;

        rotate([90, 0, 0])
            linear_extrude(length, center=true)
            difference()
            {
                square([outer_width, outer_height]);
                    square([inner_width, inner_height]);
            }

        translate([Wide_Spike_Diameter/2 + Wall_Thickness, 0])
            cylinder(h=Spike_Height, d1=Wide_Spike_Diameter, d2=Iota);

        translate([inner_width - Thin_Spike_Diameter/2 - Wall_Thickness, 0])
            cylinder(h=Spike_Height, d1=Thin_Spike_Diameter, d2=Iota);
    }



    module Generate_Section_Inset_Cutout()
    {
        width = Section_Width*4;
        length = Wall_Thickness;
        height = Wall_Thickness;

        for(y_mirror = [0, 1])
            mirror([0, y_mirror, 0])
            translate([-width/2, Section_Length/2 - Label_Depth, 0])
            cube([width, length, height]);
    }



    module Generate_Label_Cutout(label)
    {
        rotate([90, 0, 0])
            translate([0, 0, -Label_Depth])
            linear_extrude(Wall_Thickness)
            text(text=label, size=Section_Label_Font_Size, font=Font, halign="center", valign="center");
    }



    // Generate a single section of the tower with a given label
    module Generate_Section(label)
    {
        difference()
        {
            union()
            {
                translate([-Left_Compartment_Width, 0])
                    Generate_Left_Slope_End();

                Generate_Left_Compartment();

                translate([Right_Compartment_Width, 0])
                    Generate_Right_Slope_End();

                Generate_Right_Compartment();
            }

            Generate_Section_Inset_Cutout();

            translate([-Left_Compartment_Width/2, -Section_Length/2, Section_Height/2])
                Generate_Label_Cutout(label);
        }
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



    module Generate_Tower_Inscription()
    {
        rotate([0, 0, -90])
            translate([0, 0, -Label_Depth])
            linear_extrude(Wall_Thickness)
            text(text=Tower_Label, font=Font, size=Section_Label_Font_Size, halign="center", valign="center");
    }



    module Generate_Base()
    {
        difference()
        {
            linear_extrude(Base_Height)
                square([Base_Width, Base_Length], center=true);

            translate([-Base_Width/2 + Left_Slope_Width/2, 0, Base_Height])
                Generate_Tower_Inscription();
        }
    }



    module Generate()
    {
        Generate_Base();
        translate([0, 0, Base_Height])
            Generate_Tower();
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
