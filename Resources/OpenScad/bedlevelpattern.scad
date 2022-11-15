// These bed level test patterns are inspired by this All3DP article here: https://all3dp.com/2/ender-3-pro-bed-leveling-gcode/

/* [General Parameters] */
// The type of bed level pattern to generate
Bed_Level_Pattern_Type = "concentric squares"; // ["concentric squares", "concentric circles", "x in square", "circle in square", "grid", "five circles"]

// The width of the bed print area
Print_Area_Width = 220.001;

// The depth of the bed print area
Print_Area_Depth = 220.001;

// The width of the lines to print
Line_Width = 0.401;

// The height of the lines to print
Line_Height = 0.301;

// The percentage of the print area to use for the bed level pattern
Fill_Percentage = 90; // [50: 100]



/* [Bed Level Pattern-Specific Parameters] */
// The number of square to generate for the concentric squares bed level pattern
Concentric_Ring_Count = 7;

// The number of grids (horizontal and vertical) to generate for the grid bed level pattern
Grid_Cell_Count = 4;

// The diameter of the circles to generate for the five circles pattern
Circle_Diameter = 20;

// The distance of the five circles pattern outline from the corner circles
Outline_Distance = 5;



/* [Advanced Parameters] */
// Quality value (higher numbers mean better quality, lower numbers mean faster rendering)
Quality_Value = 128;



/* [Development Parameters] */
// Highlight the print area?
Show_Print_Area = false;

// Orient the model for creating a screenshot?
Orient_for_Screenshot = false;

// The viewport distance for the screenshot 
Screenshot_Vpd = 400.00;

// The viewport field of view for the screenshot
Screenshot_Vpf = 22.50;

// The viewport rotation for the screenshot
Screenshot_Vpr = [ 60.00, 0.00, 300.00 ];

// The viewport translation for the screenshot
Screenshot_Vpt = [ 0.00, -5.00, -16.00 ];



$fn = Quality_Value;



module Generate_Model()
{
    Pattern_Width = Print_Area_Width * (Fill_Percentage/100);
    Pattern_Depth = Print_Area_Depth * (Fill_Percentage/100);



    // This is a generalization of OpenSCAD's circle function
    // If the diameter (d) or radius (r) is a single number, a circle will be drawn
    // If d or r are lists [x, y], an oval will be drawn instead
    module oval(d=1, r=undef)
    {
        diameterX = r == undef 
            ? is_list(d) ? d.x : d
            : is_list(r) ? r.x*2 : r*2;
        diameterY = r == undef 
            ? is_list(d) ? d.y : d
            : is_list(r) ? r.y*2 : r*2;

        diameterCircle = max(diameterX, diameterY);

        resize([diameterX, diameterY])
            circle(d=diameterCircle);
    }



    // Draws an oval outline
    module outlined_oval(thickness=1, d=1, r=undef)
    {
        diameterX = r == undef 
            ? is_list(d) ? d.x : d
            : is_list(r) ? r.x*2 : r*2;
        diameterY = r == undef 
            ? is_list(d) ? d.y : d
            : is_list(r) ? r.y*2 : r*2;

        difference()
        {
            oval(d=[diameterX, diameterY]);
            oval(d=[diameterX-thickness*2, diameterY-thickness*2]);
        }
    }


    // Draws a rectangular outline
    module outlined_square(dimensions=1, thickness=1, center=false)
    {
        width = is_list(dimensions) ? dimensions.x : x;
        height = is_list(dimensions) ? dimensions.y : y;

        difference()
        {
            square([width, height], center=center);
            square([width - thickness*2, height - thickness*2], center=center);
        }
    }



    // Draws an x shape
    module x_shape(dimensions=1, thickness=1)
    {
        width = is_list(dimensions) ? dimensions.x : x;
        height = is_list(dimensions) ? dimensions.y : y;

        // Calculate the angle and length of the diagonal lines
        angle = atan2(height, width);
        length = sqrt(pow(width, 2) + pow(height, 2));

        intersection()
        {
            // Generate each line in the x
            for (z_rot = [angle, -angle])
            rotate([0, 0, z_rot])
                square([length, Line_Width], center=true);

            // Keep the lines within the requested dimensions
            square([width, height], center=true);
        }
    }



    // This is the best name I could come up with for this shape
    // Good luck understanding the code. It's difficult to explain without pictures
    module curved_x_pattern(size=1, thickness=1, cd=1, cr=undef)
    {
        module generate_intersection_shape(x, y)
        {
            points = 
            [
                [0, 0],
                [x + y, 0],
                [0, x + y],
            ];
            polygon(points=points);
        }

        module generate_corner(x, y, corner_radius, thickness)
        {
            difference()
            {
                translate([x, y])
                    outlined_oval(r=corner_radius, thickness);
                generate_intersection_shape(x, y);
            }
        }

        module generate_corners(x, y, corner_radius, thickness)
        {
            for (x_mirror = [0, 1])
            for (y_mirror = [0, 1])
            mirror([x_mirror, 0])
            mirror([0, y_mirror])
                generate_corner(x, y, corner_radius, thickness);
        }

        module generate_side(x, y, corner_radius, thickness)
        {
            side_radius = y * sqrt(2) - corner_radius + thickness;

            intersection()
            {
                translate([x + y, 0])
                    outlined_oval(r=side_radius, thickness);
                generate_intersection_shape(x, y);
            }
        }

        module generate_sides(x, y, corner_radius, thickness)
        {
            for (x_mirror = [0, 1])
            for (y_mirror = [0, 1])
            mirror([x_mirror, 0])
            mirror([0, y_mirror])
            {
                generate_side(x, y, corner_radius, thickness);
                rotate([0, 0, 90])
                    generate_side(y, x, corner_radius, thickness);
            }
        }

        width = is_list(size) ? size.x : size;
        height = is_list(size) ? size.y : size;
        corner_radius = cr == undef ? cd/2 : cr;
        corner_x = width/2 - corner_radius;
        corner_y = height/2 - corner_radius;

        generate_corners(corner_x, corner_y, corner_radius, thickness);
        generate_sides(corner_x, corner_y, corner_radius, thickness);
    }



    module Generate_Concentric_Squares()
    {
        width_delta = Pattern_Width/Concentric_Ring_Count;
        depth_delta = Pattern_Depth/Concentric_Ring_Count;

        for (ring_number = [0 : Concentric_Ring_Count - 1])
        {
            ring_width = width_delta * (ring_number + 1);
            ring_depth = depth_delta * (ring_number + 1);

            outlined_square([ring_width, ring_depth], Line_Width, center=true);
        }
    }



    module Generate_Concentric_Circles()
    {
        width_delta = Pattern_Width/Concentric_Ring_Count;
        depth_delta = Pattern_Depth/Concentric_Ring_Count;

        for (ring_number = [0 : Concentric_Ring_Count - 1])
        {
            ring_width = width_delta * (ring_number + 1);
            ring_depth = depth_delta * (ring_number + 1);

            outlined_oval(d=[ring_width, ring_depth], Line_Width);
        }
    }


    
    module Generate_X_In_Square()
    {
        square_width = Pattern_Width;
        square_depth = Pattern_Depth;

        x_width = square_width - Line_Width*4;
        x_depth = square_depth - Line_Width*4;

        outlined_square([square_width, square_depth], Line_Width, center=true);
        x_shape([x_width, x_depth], Line_Width);
    }



    module Generate_Circle_In_Square()
    {
        square_width = Pattern_Width;
        square_depth = Pattern_Depth;

        circle_width = square_width - Line_Width*4;
        circle_depth = square_depth - Line_Width*4;

        outlined_square([square_width, square_depth], Line_Width, center=true);
        outlined_oval(d=[circle_width, circle_depth], Line_Width);
    }



    module Generate_Grid()
    {
        // Horizontal lines
        for (section_number = [0 : Grid_Cell_Count - 1])
        {
            section_width = Pattern_Width/Grid_Cell_Count;
            section_height = Pattern_Depth;
            x_offset = -Pattern_Width/2 + section_width * section_number + section_width/2;
            y_offset = 0;

            translate([x_offset, y_offset])
                outlined_square([section_width, section_height], Line_Width, center=true);
        }

        // Vertical lines
        for (section_number = [0 : Grid_Cell_Count - 1])
        {
            section_width = Pattern_Width;
            section_height = Pattern_Depth/Grid_Cell_Count;
            x_offset = 0;
            y_offset = -Pattern_Depth/2 + section_height * section_number + section_height/2;

            translate([x_offset, y_offset])
                outlined_square([section_width, section_height], Line_Width, center=true);
        }
    }



    module Generate_Five_Circles()
    {
        width = Pattern_Width;
        height = Pattern_Depth;
        corner_radius = Circle_Diameter/2 + Outline_Distance + Line_Width;
        corner_x = width/2 - corner_radius;
        corner_y = height/2 - corner_radius;

        // Filled circle in the center
        circle(d=Circle_Diameter);

        // Filled circles near the four corners
        for (x_mirror = [0, 1])
        for (y_mirror = [0, 1])
        mirror([x_mirror, 0])
        mirror([0, y_mirror])
        translate([corner_x, corner_y])
        {
            circle(d=Circle_Diameter);
        }

        // Generate the curved outline around the five circles
        curved_x_pattern([width, height], Line_Width, cr=corner_radius);
    }



    module Generate()
    {
        linear_extrude(Line_Height)
        {
            if (Bed_Level_Pattern_Type == "concentric squares")
            {
                Generate_Concentric_Squares();
            }
            else if (Bed_Level_Pattern_Type == "concentric circles")
            {
                Generate_Concentric_Circles();
            }
            else if (Bed_Level_Pattern_Type == "circle in square")
            {
                Generate_Circle_In_Square();
            }
            else if (Bed_Level_Pattern_Type == "x in square")
            {
                Generate_X_In_Square();
            }
            else if (Bed_Level_Pattern_Type == "grid")
            {
                Generate_Grid();
            }
            else if (Bed_Level_Pattern_Type == "five circles")
            {
                Generate_Five_Circles();
            }
        }
    }



    Generate();

    if (Show_Print_Area)
    {
        %square([Print_Area_Width, Print_Area_Depth], center=true);
    }
}



// Generate the model
Generate_Model();

// Orient the viewport
$vpd = Orient_for_Screenshot ? Screenshot_Vpd : $vpd;
$vpf = Orient_for_Screenshot ? Screenshot_Vpf : $vpf;
$vpr = Orient_for_Screenshot ? Screenshot_Vpr : $vpr;
$vpt = Orient_for_Screenshot ? Screenshot_Vpt : $vpt;
