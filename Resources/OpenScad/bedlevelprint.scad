/* [General Parameters] */
// The width of the bed print area
Print_Area_Width = 220.001;

// The depth of the bed print area
Print_Area_Depth = 220.001;

// The width of the lines to print
Line_Width = 0.401;

// The height of the lines to print
Line_Height = 0.101;

// The number of concentric rectanglular rings to print
Number_Of_Rings = 7;



/* [Development Parameters] */
// Orient the model for creating a screenshot
Orient_for_Screenshot = false;

// The viewport distance for the screenshot 
Screenshot_Vpd = 400.00;

// The viewport field of view for the screenshot
Screenshot_Vpf = 22.50;

// The viewport rotation for the screenshot
Screenshot_Vpr = [ 60.00, 0.00, 300.00 ];

// The viewport translation for the screenshot
Screenshot_Vpt = [ 0.00, -5.00, -16.00 ];



module Generate_Model()
{
    module Generate_Ring(width, depth, line_width)
    {
        difference()
        {
            square([width, depth], center=true);
            square([width - line_width*2, depth - line_width*2], center=true);
        }
    }



    module Generate()
    {
        width_delta = Print_Area_Width/(Number_Of_Rings + 1);
        depth_delta = Print_Area_Depth/(Number_Of_Rings + 1);

        linear_extrude(Line_Height)
        for (ring_number = [0 : Number_Of_Rings - 1])
        {
            ring_width = width_delta * (ring_number + 1);
            ring_depth = depth_delta * (ring_number + 1);

            Generate_Ring(ring_width, ring_depth, Line_Width);
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
