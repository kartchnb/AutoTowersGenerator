// These bed level test prints are inspired by this All3DP article here: https://all3dp.com/2/ender-3-pro-bed-leveling-gcode/

/* [General Parameters] */
// The type of bed level print to generate
Bed_Level_Print_Type = "concentric squares"; // ["concentric squares", "x in square", "circle in square", "perimeter", "five circles"]

// The width of the bed print area
Print_Area_Width = 220.001;

// The depth of the bed print area
Print_Area_Depth = 220.001;

// The width of the lines to print
Line_Width = 0.401;

// The height of the lines to print
Line_Height = 0.301;



/* [Advanced Parameters] */
// The number of concentric rectanglular rings to print (also effects the actual print size)
Number_of_Concentric_Rings = 7;

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
    Reference_Size = min(Print_Area_Width, Print_Area_Depth)/Number_of_Concentric_Rings;
    Print_Width = Print_Area_Width - Reference_Size;
    Print_Depth = Print_Area_Depth - Reference_Size;



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
    module oval_ring(thickness=1, d=1, r=undef)
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


    // Draws a rectangular ring
    module square_ring(dimensions=1, thickness=1, center=false)
    {
        width = is_list(dimensions) ? dimensions.x : x;
        height = is_list(dimensions) ? dimensions.y : y;

        difference()
        {
            square([width, height], center=center);
            square([width - thickness*2, height - thickness*2], center=center);
        }
    }



    // I don't have a good way of describing this shape
    // It's inspired by the "five circles" bed level print discussed here: https://all3dp.com/2/ender-3-pro-bed-leveling-gcode/
    // It also doesn't entirely work and needs to be rethought out or abandoned entirely
    // Specifically, it only really works if the width and height are the same
    module curved_x_pattern(size=2, thickness=1, cd=1, cr=undef)
    {
        // Draw a curved line running between the curved corners on each side
        // I'm not prepared to document this calcualation right now
        // Maybe I can scan in my notes?
        // Note that, at the moment, this doesn't work correctly for non-square print beds
        // Hopefully, I can figure this out at some point, but this is it for now
        module curved_side(X, Y, THETA, Rc, line_width)
        {
            xc = (Rc - line_width) * sin(THETA);
            yc = (Rc - line_width) * cos(THETA);
            ys = Y - yc;
            rs = ys/cos(THETA);
            xs = rs * sin(THETA);

            rsx = rs * (xs/ys);
            rsy = rs * (ys/xs);

            translate([X + xc + xs, 0])
                oval_ring(r=[rsx, rsy], line_width);
        }



        // Determine the characteristics of the rounded x
        width = is_list(size) ? size.x : size;
        height = is_list(size) ? size.y : size;
        corner_diameter = cr == undef ? cd : cr*2;
        corner_radius = corner_diameter/2;

        // Calculate the center offset of the curves that make up the corners of the x
        corner_x_offset = width/2 - corner_radius;
        corner_y_offset = height/2 - corner_radius;

        // Calculate the angle of the line running from the center of the x to the center of one of the corners
        intersection_angle = atan2(height, width);

        // Determine the diameters of an oval that passes through the center of each of the corners
        intersection_oval_diameter = sqrt(pow(corner_x_offset,2) + pow(corner_y_offset, 2))*2;
        intersection_oval_x_diameter = intersection_oval_diameter * (corner_x_offset/corner_y_offset);
        intersection_oval_y_diameter = intersection_oval_diameter * (corner_y_offset/corner_x_offset);

        // Generate the curves at each corner of the x
        difference()
        {
            for (x_mirror = [0, 1])
            for (y_mirror = [0, 1])
            mirror([x_mirror, 0])
            mirror([0, y_mirror])
            translate([corner_x_offset, corner_y_offset])
                oval_ring(d=corner_diameter, thickness);

            // Erase everything inside the intersection oval
            oval(d=[intersection_oval_x_diameter, intersection_oval_y_diameter]);
        }

        intersection()
        {
            union()
            {
                // Draw the curved sides on the left and right of the x
                for (x_mirror = [0, 1])
                mirror([x_mirror, 0])
                    curved_side(corner_x_offset, corner_y_offset, intersection_angle, corner_radius, Line_Width);
                
                // Draw the curved sides on the top and bottom of the x
                for (y_mirror = [0, 1])
                mirror([0, y_mirror])
                rotate([0, 0, 90])
                    curved_side(corner_y_offset, corner_x_offset, 90 - intersection_angle, corner_radius, Line_Width);
            }

            // Erase everything outside the intersection oval
            oval(d=[intersection_oval_x_diameter, intersection_oval_y_diameter]);
        }
    }



    module Generate_Concentric_Squares()
    {
        width_delta = Print_Area_Width/(Number_of_Concentric_Rings + 1);
        depth_delta = Print_Area_Depth/(Number_of_Concentric_Rings + 1);

        for (ring_number = [0 : Number_of_Concentric_Rings - 1])
        {
            ring_width = width_delta * (ring_number + 1);
            ring_depth = depth_delta * (ring_number + 1);

            square_ring([ring_width, ring_depth], Line_Width, center=true);
        }
    }


    
    module Generate_X_In_Square()
    {
        square_ring([Print_Width, Print_Depth], Line_Width, center=true);

        // Calculate the angle and length of the diagonal lines
        angle = atan2(Print_Depth, Print_Width);
        length = sqrt(pow(Print_Width, 2) + pow(Print_Depth, 2));

        intersection()
        {
            // Generate each line in the x
            for (z_rot = [angle, -angle])
            rotate([0, 0, z_rot])
                square([length, Line_Width], center=true);

            square([Print_Width, Print_Depth], center=true);
        }
    }



    module Generate_Circle_In_Square()
    {
        square_ring([Print_Width, Print_Depth], Line_Width, center=true);
        oval_ring(d=[Print_Width, Print_Depth], Line_Width);
    }



    module Generate_Perimeter()
    {
        square_ring([Print_Width, Print_Depth], Line_Width, center=true);
    }



    module Generate_Five_Circles()
    {
        // The curved x pattern doesn't work correctly with non-square sizes yet
        // For now, size the pattern for the smallest bed dimension
        width = min(Print_Width, Print_Depth);
        height = width;

        circle_diameter = Reference_Size/2;
        border_offset = circle_diameter/2;
        corner_x_offset = width/2 - circle_diameter/2 - border_offset;
        corner_y_offset = height/2 - circle_diameter/2 - border_offset;

        // Filled circle in the center
        circle(d=circle_diameter);

        // Filled circles near the four corners
        for (x_mirror = [0, 1])
        mirror([x_mirror, 0])
        for (y_mirror = [0, 1])
        mirror([0, y_mirror])
        translate([corner_x_offset, corner_y_offset])
        {
            circle(d=circle_diameter);
        }

        // Generate the curved outline around the five circles
        corner_diameter = circle_diameter + border_offset*2;
        curved_x_pattern([width, height], Line_Width, cd=corner_diameter);
    }



    module Generate()
    {
        linear_extrude(Line_Height)
        {
            if (Bed_Level_Print_Type == "concentric squares")
            {
                Generate_Concentric_Squares();
            }
            else if (Bed_Level_Print_Type == "x in square")
            {
                Generate_X_In_Square();
            }
            else if (Bed_Level_Print_Type == "circle in square")
            {
                Generate_Circle_In_Square();
            }
            else if (Bed_Level_Print_Type == "perimeter")
            {
                Generate_Perimeter();
            }
            else if (Bed_Level_Print_Type == "five circles")
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
