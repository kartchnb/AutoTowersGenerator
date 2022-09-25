// OpenSCAD Template v1.6

/* [General Parameters] */
// The width of the print area (side to side along the X-axis)
Print_Area_Width = 220.001;

// The length of the print area (front to back along the Y-axis)
Print_Area_Depth = 220.001;

// The width of the ring lines
Line_Width = 0.401;

// The height to print at
Ring_Height = .101;

// The number of rings to print
Ring_Count = 5;



/* [Development Parameters] */
// Orient the model for creating a screenshot
Orient_for_Screenshot = false;

// The viewport distance for the screenshot 
Screenshot_Vpd = 550.78;

// The viewport field of view for the screenshot
Screenshot_Vpf = 22.50;

// The viewport rotation for the screenshot
Screenshot_Vpr = [ 0.00, 0.00, 0.00 ];

// The viewport translation for the screenshot
Screenshot_Vpt = [ 8.10, 0.44, -4.44 ];




module Generate()
{
    width_delta = Print_Area_Width / (Ring_Count + 1);
    length_delta = Print_Area_Depth / (Ring_Count + 1);

    for (ring_num = [0: Ring_Count])
    {
        width = width_delta * ring_num;
        length = length_delta * ring_num;
        Generate_Ring([width, length]);
    }
}



module Generate_Ring(size)
{
    linear_extrude(Ring_Height)
    difference()
    {
        square(size, center=true);
        square(size - [Line_Width*2, Line_Width*2], center=true);
    }
}


// Generate the model
Generate();

// Orient the viewport
$vpd = Orient_for_Screenshot ? Screenshot_Vpd : $vpd;
$vpf = Orient_for_Screenshot ? Screenshot_Vpf : $vpf;
$vpr = Orient_for_Screenshot ? Screenshot_Vpr : $vpr;
$vpt = Orient_for_Screenshot ? Screenshot_Vpt : $vpt;
