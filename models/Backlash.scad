// Backlash Quick calibration test 
// https://www.thingiverse.com/thing:4594731
// Author : https://www.thingiverse.com/quas7/designs (Tillmann Krauss)
// Calibrate X axis
// Set backlash compensation to 0 in your software while sampling an axis.
// Each step up increases backlash offset with 0.01
// Each step right increases backlash offset with 0.10
// locate the figure with the smallest offset value and add backlash offset to it. This calculated value is your backlash offset to be entered in the printer sotware.
// E.g. if the correct figure is number 7 to the right and number 4 from the bottom and backlashstartvalue is 0.7:
// 0.7 + 0.03 + 0.5 = 1.23
// To make files for  calibrating the Y axis turn the print 90 degrees in the slicer.

/* [Size and start point] */
//Number of strips to print.
Rows = 10; //[1:1:20]
//What is the starting point? Make sure that the end-value is no more than 1.99 (Rows/10+Backlashstartvalue <= 2) because the "reset-loops" are only 2 mm
Backlashstartvalue = 0.00; // [0.0:0.1:1.9]
/* [Print thickness and height] */
//Suggestion: Wallheight = Nozzle diameter.
wallheight = 0.8; //[0.2:0.05:0.8]

//Suggestion: Wallthickness = 2 or 2.5 times the Wallheight. Those are values that work for me. Your mileage may vary a lot. Your slicer of course needs to be set acordingly so the print is made in a single layer. Fatter lines stick better to the plate but thinner lines are easier to interpret.
wallthickness = 0.4; //[0.2:0.05:1.6]

rowspacing = 1;

mirror_spacing = 3.5; // spacing between the mirrored patterns

//Each sample right handed
module unit_r(sx, sy, bl)
{
color("red")
    translate([(sx+0), (sy+0), 0])
        cube([3, wallthickness, wallheight], center=false);
    
color("green")
    translate([(sx+3-wallthickness), (sy+0), 0])
        cube([wallthickness, 1, wallheight], center=false);

color("pink")    
   linear_extrude(height = wallheight, center = false, convexity = 10, twist = 0)
    polygon(points=[[sx+3-wallthickness,sy+1],[sx+3-wallthickness+wallthickness,sy++1],[sx+3-wallthickness-bl+wallthickness,sy+3],[sx+3-wallthickness-bl,sy+3]]);
    
color("purple")
    translate([(sx+3-wallthickness-bl), (sy+3), 0])
        cube([wallthickness, 2, wallheight], center=false);    

color("yellow")
    linear_extrude(height = wallheight, center = false, convexity = 10, twist = 0)
   polygon(points=[[sx+3-wallthickness-bl,sy+5],[sx+3-wallthickness-bl+wallthickness,sy+5],[sx+3-wallthickness+wallthickness,sy+7],[sx+3-wallthickness,sy+7]]);
    
color("blue")
    translate([(sx+3-wallthickness+0), (sy+7), 0])
            cube([wallthickness, 1, wallheight], center=false);
        
color("brown")
    translate([(sx+0), (sy+8-wallthickness), 0])
        cube([3, wallthickness, wallheight], center=false);
        
//Connect each sample
    if (sy>0)
     {
color("black")
    translate([(sx), (sy-2), 0])
        cube([wallthickness, 2, wallheight], center=false);
     }
}

module unit_l(sx, sy, bl)
{
    sx = sx+mirror_spacing; 
    
color("red")
    translate([(sx+0), (sy+0), 0])
        cube([3, wallthickness, wallheight], center=false);
    
color("green")
    translate([(sx+0), (sy+0), 0])
        cube([wallthickness, 1, wallheight], center=false);

color("pink")    
   linear_extrude(height = wallheight, center = false, convexity = 10, twist = 0)
    polygon(points=[[sx,sy+1],[sx+wallthickness,sy++1],[sx+bl+wallthickness,sy+3],[sx+bl,sy+3]]);
    
color("purple")
    translate([(sx+bl), (sy+3), 0])
        cube([wallthickness, 2, wallheight], center=false);    

color("yellow")
    linear_extrude(height = wallheight, center = false, convexity = 10, twist = 0)
   polygon(points=[[sx+bl,sy+5],[sx+bl+wallthickness,sy+5],[sx+wallthickness,sy+7],[sx,sy+7]]);
    
color("blue")
    translate([(sx+0), (sy+7), 0])
            cube([wallthickness, 1, wallheight], center=false);
        
color("brown")
    translate([(sx+0), (sy+8-wallthickness), 0])
        cube([3, wallthickness, wallheight], center=false);
        
//Connect each sample
    if (sy>0)
     {
color("black")
    translate([(sx+3-wallthickness), (sy-2), 0])
        cube([wallthickness, 2, wallheight], center=false);
     }
}


//draw y strips right handed --> how to invert??
translate([-48, -49, 0]) {
for (soffsy=[0:20:(Rows*20-10)])
{
    //draw 10 samples
   for (soffsx=[0:10:90])
    {
        
        sbl = (Backlashstartvalue + soffsy/100+ soffsx/1000);

        echo("Backlash is  ", sbl);
        
      unit_r(soffsy/2, soffsx, sbl  );    
    }
}


//draw y strips left handed
for (soffsy=[0:20:(Rows*20-10)])
{
    //draw 10 samples
   for (soffsx=[0:10:90])
    {
        
        sbl = (Backlashstartvalue + soffsy/100+ soffsx/1000);

        echo("Backlash is  ", sbl);
        
      unit_l(soffsy/2, soffsx, sbl  );    
    }
}


// The blob that marks zero
//color("black")
    translate([1.6, 3, 0])
        cube([(3*wallthickness), (3*wallthickness), wallheight], center=false);
}
