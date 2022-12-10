// BAK 9 Dec 2022: Oh, Mama, this model needs to be cleaned up...

/* [General Parameters] */
// A label to add to the tower
Tower_Label = "";

// A description to add to the tower
Tower_Description = "";

// The starting speed value
Starting_Speed_Value = 20;

// The ending speed value
Ending_Speed_Value = 100;

// The amount to change the speed value between sections
Speed_Value_Change = 20;

// The length of each wing of the tower
Wing_Length = 50.001;

// The thickness of each wing of the tower
Wing_Thickness = 3.001;

// The height of the base
Base_Height = 0.841;

// The height of each section of the tower
Section_Height = 8.401;

// The size of the base font
Base_Font_Size = 2.001;



/* [Advanced Parameters] */
// Should labels be hidden?
Hide_Labels = false;

// The font to use for tower text
Label_Font = "Arial:style=Bold";

// The height of the section labels in relation to the height of each section
Section_Label_Height_Multiplier = 0.401;

// The nominal thickness of walls in the model
Wall_Thickness = 0.4001;

// The height of the section label text as a fraction of the section height
Section_Font_Height_Multiplier = .333;

// The depth of inscriptions
Inscription_Depth = 0.201;

// The value to use for creating the model preview (lower is faster)
Preview_Quality_Value = 24;

// The value to use for creating the final model render (higher is more detailed)
Render_Quality_Value = 48;

// A small value used to improve rendering in preview mode
Iota = 0.001;



/* [Development Parameters] */
// Orient the model for creating a screenshot
Orient_for_Screenshot = false;

// The viewport distance for the screenshot 
Screenshot_Vpd = 200.00;

// The viewport field of view for the screenshot
Screenshot_Vpf = 22.50;

// The viewport rotation for the screenshot
Screenshot_Vpr = [ 60.00, 0.00, 60.00 ];

// The viewport translation for the screenshot
Screenshot_Vpt = [ 17.00, 15.00, 15.00 ];


/* [Calculated Parameters] */
// Calculate the rendering quality
$fn = $preview ? Preview_Quality_Value : Render_Quality_Value;

// Ensure the value change has the correct sign
Speed_Value_Change_Corrected = Ending_Speed_Value > Starting_Speed_Value
    ? abs(Speed_Value_Change)
    : -abs(Speed_Value_Change);

// Determine how many sections to generate
Section_Count = ceil(abs(Ending_Speed_Value - Starting_Speed_Value) / abs(Speed_Value_Change) + 1);

// Calculate the distance that the base extends beyond the wings
Base_Extension = Base_Font_Size + Wall_Thickness*2;

// Calculate the font sizes
Section_Label_Font_Size = (Section_Height - Wall_Thickness)*Section_Font_Height_Multiplier;




module Generate_Model()
{
    module double_headed_arrow(dimensions, center=false)
    {
        width = is_list(dimensions) ? dimensions.x : dimensions;
        length = is_list(dimensions) ? dimensions.y : dimensions;

        y_offset = center ? -length/2 : 0;

        arrow_width = width;
        arrow_length = arrow_width;

        shaft_width = width/2;

        arrow_points =
        [
            [0, 0],
            [arrow_width/2, arrow_length],
            [-arrow_width/2, arrow_length],
        ];

        translate([0, y_offset])
        for (side = [0, 1])
        {
            side_y_mir = side;
            side_y_offset = length*side;
            translate([0, side_y_offset])
            mirror([0, side_y_mir])
            {
                polygon(arrow_points);
                translate([-(width - shaft_width)/2, arrow_length])
                    square([shaft_width, length/2 - arrow_length]);
            }
        }
    }



    module Generate_Basic_Base()
    {
        width = Wing_Thickness + Base_Extension*2;
        length = Wing_Length + Base_Extension*2;
        height = Base_Height;

        x_offset = -Base_Extension;
        y_offset = -Base_Extension;

        linear_extrude(height)
        {
            translate([x_offset, y_offset])
                square([width, length]);
            translate([y_offset, x_offset])
                square([length, width]);
        }
    }



    module Generate_Base_Label(label)
    {
        if (Hide_Labels == false)
        {
            thickness = Inscription_Depth*2;

            x_offset = Wing_Length/2 - Wing_Thickness/2;
            y_offset = -Base_Extension/2;
            z_offset = Base_Height;

            translate([x_offset, y_offset, z_offset])
            translate([0, 0, -thickness/2])
            linear_extrude(thickness)
            resize([0, Base_Font_Size], auto=true)
                text(label, Base_Font_Size, Label_Font, halign="center", valign="center");
        }
    }



    module Generate_Base()
    {
        difference()
        {
            Generate_Basic_Base();

            Generate_Base_Label(Tower_Label);

            translate([0, Wing_Length, 0])
            rotate([0, 0, -90])
                Generate_Base_Label(Tower_Description);

            translate([Wing_Length, Wing_Thickness, 0])
            rotate([0, 0, 180])
                Generate_Base_Label("X-AXIS");

            translate([Wing_Thickness, Wing_Thickness, 0])
            rotate([0, 0, 90])
                Generate_Base_Label("Y-AXIS");

            Generate_Base_Axis_Arrow();
        }
    }



    module Generate_Basic_Section()
    {
        body_width = Wing_Thickness;
        body_length = Wing_Length;
        body_height = Section_Height - Wall_Thickness;

        cap_width = body_width - Wall_Thickness;
        cap_length = body_length - Wall_Thickness;
        cap_height = Wall_Thickness;

        cap_x_offset = (body_width - cap_width)/2;
        cap_y_offset = (body_length - cap_length)/2;
        cap_z_offset = body_height;

        cube([body_width, body_length, body_height]);
        translate([cap_x_offset, cap_y_offset, cap_z_offset])
            cube([cap_width, cap_length, cap_height]);
    }



    module Generate_Section_Front_Cutout()
    {
        diameter = Section_Height;
        height = Inscription_Depth*2;

        x_offset = 0;
        y_offset = Wing_Length/2;
        z_offset = (Section_Height - Wall_Thickness)/2;

        translate([x_offset, y_offset, z_offset])
        rotate([0, 90, 0])
        translate([0, 0, -height/2])
            cylinder(d=diameter, height);
    }



    module Generate_Section_Rear_Cutout()
    {
        width = Wing_Length - Wall_Thickness*2 - Wing_Thickness;
        height = Section_Height - Wall_Thickness*3;
        thickness = Inscription_Depth*2;

        diameter = Section_Height;

        x_offset = Wing_Thickness;
        y_offset = Wing_Thickness;
        z_offset = 0;

        x_rot = 90;
        y_rot = 0;
        z_rot = 90;

        circle_x_offset = width/2;
        circle_y_offset = height/2;

        translate([x_offset, y_offset, z_offset])
        rotate([x_rot, y_rot, z_rot])
        translate([0, 0, -thickness/2])
        linear_extrude(thickness)
        translate([Wall_Thickness, Wall_Thickness])
        difference()
        {
            square([width, height]);

            translate([circle_x_offset, circle_y_offset])
                circle(d=diameter);
        }
    }



    module Generate_Section_Label(label)
    {
        if (Hide_Labels == false)
        {
            thickness = Inscription_Depth*2;

            x_offset = 0;
            y_offset = Wing_Length/2;
            z_offset = (Section_Height - Wall_Thickness)/2;

            translate([x_offset, y_offset, z_offset])
            rotate([90, 0, -90])
            translate([0, 0, -thickness/2])
            linear_extrude(thickness)
                text(label, Section_Label_Font_Size, Label_Font, halign="center", valign="center");
        }
    }



    module Generate_Y_Axis_Section(label)
    {
        difference()
        {
            Generate_Basic_Section();
            Generate_Section_Front_Cutout();
            Generate_Section_Rear_Cutout();
        }
        Generate_Section_Label(label);
    }



    module Generate_X_Axis_Section(label)
    {
        x_rot = 0;
        y_rot = 0;
        z_rot = -90;

        rotate([x_rot, y_rot, z_rot])
        {
            mirror([1, 0, 0])
            difference()
            {
                Generate_Basic_Section();
                Generate_Section_Front_Cutout();
                Generate_Section_Rear_Cutout();
            }
            translate([0, Wing_Length, 0])
            rotate([0, 0, 180])
                Generate_Section_Label(label);
        }
    }



    module Generate_Tower()
    {
        // Create each section
        for (section_number = [0: Section_Count - 1])
        {
            // Determine the value and label for this section
            value = Starting_Speed_Value + (Speed_Value_Change_Corrected * section_number);
            label = str(value);

            // Determine the offset of the section
            z_offset = section_number*Section_Height;

            // Generate the x and y sections and move them into place
            translate([0, 0, z_offset])
            {
                Generate_X_Axis_Section(label);
                Generate_Y_Axis_Section(label);
            }
        }
    }



    // Generate the model
    module Generate()
    {
        // Center the tower
        translate([-Wing_Length/2, -Wing_Length/2, 0])
        {
            // Add the base
            Generate_Base();

            translate([0, 0, Base_Height])
                Generate_Tower();
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
