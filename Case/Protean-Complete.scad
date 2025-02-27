pi=3.14159265359*1;

/* [Main Dimensions] */
// Length of the mount
mount_length = 33;
// Width of the mount
mount_width = 30;
// Total height of the mount
clamp_height=13;
// Radius of the edge smoothing
edge_radius = 3;

// How acute the angle for the flashlight cutout is. (Higher = More Acute)
cutout_angle_acuteness=0.1; //[0.1:40]
// Cutout Height for Flashlight
cutout_height=clamp_height/2+cutout_angle_acuteness;

// Whether your rail is curved like mine
rail_has_arc=0; // [1:Yes, 0:Nope]
// My rail had a curved exterior, select a radius for the curve
rail_cylinder_radius = 15; // [15, 20, 25, 30]
rail_cylinder_offset =  (rail_cylinder_radius == 15 ) ? -7.02 ://rail_cylinder_radius*-1+6.635;
                        (rail_cylinder_radius == 20 ) ? -13.65 :
                        (rail_cylinder_radius == 25 ) ? -19.05 : -24.47;
               

/* [Screw For Mounting] */

// Diameter of the screw
screw_d = 3;
screw_r = screw_d / 2;
// Diameter of the Screw Head
bolt_head_d=6.5; //5.6;
// How Deep to cut out of the screw head
bolt_thickness = 2.5;


/* [Ziptie] */
// Ziptie Cutout Width
ziptie_w=5;
// Ziptie Cutout Height
ziptie_h=4;
// Vertical offset of Zipties
ziptie_h_offset=8;


/* [NATO Rail] */
// Width of the stem, default was 15.6;
stem_width = 10.2; 
inner_box_width = 20.25; //og 20.05
//inner_box_height = 2.74;
inner_box_height = 1.5;

bounding_box_width = 21.5; //changed og 20
bounding_box_toprise = 4.17;
bounding_box_height = 9.4;

recoil_depth = 2.59;
recoil_width = 5.15;
recoil_spacing = 10;



// Misc
$fn = 64+0;
eps = 0.001+0;
eps2 = eps *2+0;

if (make_top) {
translate([0,0,-5]){
rotate(a=90, v=[1,0,0])
flashlight_mount();
}
}
module flashlight_mount() {
    rotate([90,90,0]){
    translate([0,3.75,-48]){
    difference() {
      color("Gray")  clamp();
      color("pink")  rail();
      //color("blue")  flashlight_cutout();
      color("Fuchsia")  bolt_cutout();
      color("Orange") screw_cutout();
      color("SlateBlue")  screw_head_cutout();
      color("yellow")  ziptie();
    }
}
}
}

module ziptie() {
    translate([-mount_width/2-3,mount_length/8,ziptie_h_offset])
        cube([mount_width+6, ziptie_w, ziptie_h]);
    translate([-mount_width/2-3,mount_length/8*6,ziptie_h_offset])
        cube([mount_width+6, ziptie_w, ziptie_h]);
}


module screw_cutout() {
    translate([-(mount_width+2)/2,recoil_width*3+recoil_width/2-screw_r/2,6.405-screw_r])
        rotate([0,90,0])
            cylinder(r=screw_r+.02, h=mount_width+2);
}

module screw_head_cutout() {
    translate([(mount_width)/2-3+eps2*2,recoil_width*3+recoil_width/2-screw_r/2,6.405-screw_r])
        rotate([0,90,0])
            cylinder(r=bolt_head_d/2+.02, h=3);
}

module bolt_cutout() {
    translate([-(mount_width+2)/2+bolt_thickness-1.6, recoil_width*3+recoil_width/2-screw_r/2,6.405-screw_r])
            rotate([0,90,0]) rotate(a=30, v=[0,0,1]) 
                    cylinder(r=bolt_head_d/2+.02, h=bolt_thickness, $fn=6);
}



module flashlight_cutout() {
    translate([0,mount_length/2,9]){
        rotate([90,0,0]) {
            linear_extrude(height=mount_length+2,center=true) {
                polygon(points=[[0,0],[-mount_width/2,cutout_height],[mount_width/2,cutout_height]]);
            }
        }
    }
}

/*
module rail_arc() {
    difference() {
        translate([0,eps,rail_cylinder_offset+eps]) {
            rotate([90,0,0]){
                cylinder(r=rail_cylinder_radius,h=mount_length+2+eps2, center=true, $fn=128);
            }
        }
        translate([0,eps,rail_cylinder_radius*-1+3.59]) {
            cube([rail_cylinder_radius*2,mount_length+2,rail_cylinder_radius*2], center=true);
            echo(rail_cylinder_radius*-1+3.59);
        }
    }
}
*/

/*
module rail_arc() {
    difference() {
        // Straight cutout replacing arc, matching rail width
        translate([-stem_width / 2, -mount_length / 2, rail_cylinder_offset]) {
            cube([stem_width, mount_length+1, rail_cylinder_radius-2]);
        }
    }
}
*/
/*
module rail_arc() {
   // difference() {
        // Main straight cutout matching the rail width
        translate([-stem_width / 2, -mount_length / 2, rail_cylinder_offset]) {
            cube([stem_width, mount_length+1, rail_cylinder_radius * 2]);
        }

        // 45-degree cutouts on the top edges (perpendicular)
        translate([-stem_width / 2, -mount_length / 2, rail_cylinder_offset + rail_cylinder_radius * 2]) 
            rotate([0, 0, 45]) 
                cube([stem_width * 1.5, mount_length, rail_cylinder_radius]);

        translate([-stem_width / 2, -mount_length / 2, rail_cylinder_offset + rail_cylinder_radius * 2]) 
            rotate([0, 0, -45]) 
                cube([stem_width * 1.5, mount_length, rail_cylinder_radius]);
  //  }
}
*/




module clamp() {
    difference() {
        translate([0,mount_length/2+eps2*2,clamp_height/2])
            cube([ mount_width,mount_length, clamp_height], center=true);
        
        // curve edge
        translate([mount_width/2-edge_radius,mount_length/2+.5,edge_radius])
            rotate([90,90,0])
                createMeniscus(mount_length+1,edge_radius);
        
        // curve second edge
        translate([-mount_width/2+edge_radius,mount_length/2+.5,edge_radius])
            rotate([90,90,180])
                createMeniscus(mount_length+1,edge_radius);
        
        // top curved edge
        translate([-mount_width/2+edge_radius,mount_length/2+.5,clamp_height-edge_radius])
            rotate([90,0,180])
                createMeniscus(mount_length+1,edge_radius);
    }

}


module rail() {
    union() {
        difference() {
        rotate([0,0,0])
            translate([0,-eps,-3.3])
                NATO_rail( l=35+eps2, slots=0);
            
         //   translate([-mount_width/2,-2.5,3.59])
         //       cube([mount_width,mount_length+5,10]);
        }
        if (rail_has_arc) {
            translate([0,mount_length/2,-eps])
                rail_arc();
        }
    }
}

// This module creates the shape that needs to be substracted from a cube to make its corners rounded.
module createMeniscus(h,radius) {
//This shape is basicly the difference between a quarter of cylinder and a cube
    difference() {        
       translate([radius/2+0.1,radius/2+0.1,0]){
          cube([radius+0.202,radius+0.1,h+0.2],center=true);         // All that 0.x numbers are to avoid "ghost boundaries" when substracting
       }

       cylinder(h=h+0.3,r=radius,center=true);
    }
}


// This file defines a module that creates a NATO acessory rail on the xy plane, running up the y axis from the origin,
// with the top in the z-direction. The dimensions of this rail are as in standardization agreement 4694 (but of course 
// results will depend on your printer).

// This style of rail is backwards-compatiable with picatinny rails - and for most intents and purpouses may as well *be*
// a picatinny rail - though it is technically a distinct standard. 

// This is primarily intended to be of use to OpenSCAD users who want to incorporate rails into their designs. To do this,
// include this scad file in the same directory as your project's scad file, type "use<Parametric_NATO_rail>;" into that 
// file, and use the NATO_rail module where you want a rail. You could also print standalone pieces with this - but then
// your only options for mounting them would be to use glue or drill your own holes. 

// This module throws warning messages when asked to make a very short rail. I know. Hopefully that's not too much of a 
// problem and I do intend to fix this at some point. 

// This module accepts four paramiters, none of which are manditory:

// "l" sets the length of the rail - if unspecified, a length will be automatically sleected based on the number of slots

// "n" sets the number of slots - if unspecified, an apropriate number of slots will be selected based on the length (and 
// if that is also unspecified you get 7 slots).

// "d" extends the base of the rail below the xy plane, which is useful if you want to avoid zero-width gaps, which can 
// cause rendering errors. 

// "c" creates a chamfer at the ends of the rail.

// Examples:
//translate([-30,0,0]) NATO_rail(d=5);
//NATO_rail();
//translate([30,0,0]) NATO_rail(n=5);
//translate([60,0,0]) NATO_rail(l=50);
//translate([90,0,0]) NATO_rail(l=50, n=3);

module NATO_rail(n=-1, d=0, l=0, c=0, slots=1){
    
// Standard STANAG 4694 rail dimensions
    

    

// Derived dimensions
    
    // Slot number
    // If defined, set to what it was defined as
    number_of_slots = (n>-1) ? n :
    // If not defined, derive from length
    (
        (l>0) ? floor((l+recoil_width)/recoil_spacing - 1) :
    // Length also not defined? Then you get 7 slots
        7
    );
    
    // Rail length
    // If defined, set to what it was defined as
    rail_length = (l>0) ? l :
    // If not defined, derive from slots
    recoil_spacing * (number_of_slots + 1) - recoil_width;
    // Note that this is possiable becasue we know 
    // that the number of slots must be defined
    
    slots_offset = (rail_length - (recoil_spacing * (number_of_slots + 1) - recoil_width))/2;

    diamond_box_height = bounding_box_height - bounding_box_toprise + inner_box_height/2;
    
    diamond_box_dimension = (inner_box_width + inner_box_height)/sqrt(2);
    
    
    
    

// Basic shapes that make up the rail
    
    module bounding_box(){
        translate([-bounding_box_width/2,0,-d])
        cube([bounding_box_width,rail_length,bounding_box_height + d]);
       };
       
   module chamfer_plugs(){
       
       translate([0,0,bounding_box_height-c])
       rotate([-45,0,0])
       translate([0,-bounding_box_width,0])
       cube(bounding_box_width*2, center=true);
       
       translate([0,rail_length,bounding_box_height-c])
       rotate([45,0,0])
       translate([0,bounding_box_width,0])
       cube(bounding_box_width*2, center=true);
       
   };

    module stem(){
        translate([-stem_width/2,0,-d])
        cube([stem_width, rail_length, diamond_box_height + d]);
    };


    module diamond_box(){
        translate([0,0,diamond_box_height])
        rotate([0,45,0])
        translate([-diamond_box_dimension/2, 0, -diamond_box_dimension/2])
        cube([diamond_box_dimension, rail_length, diamond_box_dimension]);
    };

    module recoil(){
        translate([-bounding_box_width, (recoil_spacing - recoil_width), bounding_box_height - recoil_depth])
        cube([2 * bounding_box_width, recoil_width, 2 * recoil_depth]);
    };

    module recoils(){
        for(i = [0:number_of_slots - 1]){
            if (slots) {
            translate([0,slots_offset + i * recoil_spacing,0])
            recoil();
            }
        };
    };


// Put the rail together
    intersection(){
        union(){
            stem();
            diamond_box();
        };
        difference(){
            bounding_box();
            union(){
                recoils();
                chamfer_plugs();
            };
        };
    };
};






/*
    A box for the pizero(/w).
    Designed to allow the pizero to be completely in the box, resiliant to
    dust and pokey fingers.
    
    * Configurable connector holes
    * Either holes, for screws/bolts, or mounting pins for the pizero
    * Engineering model of a pizero, so you can check if it looks right
        - remember to turn this off before generating an STL
        
    TODO:
    * Calculate everything, remove magic numbers
    * Cut outs the gland on the lid to allow connectors right into the pizero
*/

// THINGIVERSE customizer does not understand true/flase, so use 1/0 instead

/* [parts] */
make_bottom=1;   // [0:No,1:Yes] 
make_top=0;      // [0:No,1:Yes] 

/* [connectors] */
sdcard_hole = 0; // [0:No,1:Yes] 
power_hole = 0;  // [0:No,1:Yes] 
hdmi_hole = 1;   // [0:No,1:Yes] 
usb_hole = 1;    // [0:No,1:Yes] 
camera_hole = 0; // [0:No,1:Yes] 
gpio_hole = 0;   // [0:No,1:Yes] 
pins = 1;        // [0:No,1:Yes] 

/* [box] */
// gap around pizero inside the box
gap = 1.0;
// wall thickness of box
shell_thickness = 1.6;
// standoffs pizero sits on in the box
standoffs = 1.5;

/* [Text on lid] */
// Add an engraved text on the top, 'help->font list' for available
add_text = 0;  // [0:No,1:Yes]
lid_text = "P0W      ";
text_font="Comic Sans MS"; 

/* [pizero options] */
// show an engineering model
dummy_pizero = 0;  // [0:No,1:Yes] 
// do we need height for a header
//pz_header = 0; // not tested, problems with heights 
// allow for solder on bottom, standoffs take care of this
//pz_solder = 0;    // don't need to allow for this as we have standoffs

// the pizero engineering model with the measurements we use, includes don't work in thingiverse customizer
//include <pizerow.scad>;

//////////////////////////////
//
// Start of included pizero engineering model
//
////////////////////
/* [pizero dimensions DO NOT ALTER] */
pz_length = 65; // not including sd card protrusion
pz_width = 30;  // not including any connector protrusions
pz_pcb_thickness = 1.45; // including solder mask
pz_component_max_height = (3.1 - pz_pcb_thickness); // hdmi is max
pz_rounded_edge_offset = 3.0;
pz_botton_pin_height = 1.0;  // solder pins for gpio connector

pz_mount_hole_dia = 2.75; 
pz_mount_hole_offset = 3.5; // from edge
pz_mount_hole_dia_clearance = 6; 

pz_gpio_length = 50.8; // total 
pz_gpio_width = 5;  // total
pz_gpio_x_offset = 32.5;  // from left hand edge to centre of connector
pz_gpio_y_offset = 3.5; // long edge centre form pcb edge
pz_gpio_height = 15+(9.8 - pz_pcb_thickness); // wihtout pcb thickness

pz_sdcard_y_offset = 16.9;
pz_sdcard_length = 15.4; // sdcard present
pz_sdcard_width = 12;
pz_sdcard_protrusion = 2.3; // sdcard present
pz_sdcard_height = (2.8 - pz_pcb_thickness); 

pz_camera_y_offset = 19;
pz_camera_length = 4.43;
pz_camera_width = 22;
pz_camera_protrusion = 1.1; // no cable present
pz_camera_height = (2.65 - pz_pcb_thickness);

pz_hdmi_x_offset = 12.4;
pz_hdmi_length = 11.2;
pz_hdmi_width = 7.6;
pz_hdmi_protrusion = 0.5; // no cable present
pz_hdmi_height = (4.7 - pz_pcb_thickness);

pz_usb_power_x_offset = 54;
pz_usb_x_offset = 41.4;
pz_usb_length = 8;
pz_usb_width = 5.6;
pz_usb_protrusion = 1; // no cable present
pz_usb_height = (3.96 - pz_pcb_thickness);

pz_max_length = pz_length + pz_sdcard_protrusion + pz_camera_protrusion;
pz_max_width = pz_width + pz_usb_protrusion;
///////////////////////////////////
//
// End of pizero definitions
//
////////////////////

//////////////////////////////////
//
// Start of pizero functions/modules
//
////////////////////////
function pz_get_max_height(gpio_header, gpio_solder) =
    pz_pcb_thickness  + 
    (pz_botton_pin_height * (gpio_solder?1:0)) + 
    (pz_gpio_height * (gpio_header?1:0)) +
    (pz_component_max_height * (gpio_header?0:1));


module pzw(gpio_header = true, gpio_solder = true) { 

    pz_max_height = pz_get_max_height(gpio_header, gpio_solder);
    
    echo("pi max length ", pz_max_length);
    echo("pi max width  ", pz_max_width);
    echo("pi max height ", pz_max_height);

    module pzw_solid() {
        // rounded edges on pcb
        x_round = [pz_rounded_edge_offset, (pz_length - pz_rounded_edge_offset)];
        y_round= [pz_rounded_edge_offset, (pz_width - pz_rounded_edge_offset)];
        for (x = x_round, y = y_round)
            translate([x, y, 0])
            {
                $fn = 40;
                cylinder(d=(2*pz_rounded_edge_offset), h=pz_pcb_thickness);
            }  

        // pcb split into bits to conform with rounded edges
        translate([pz_rounded_edge_offset, 0, 0])
            cube([pz_length - (2 * pz_rounded_edge_offset), pz_width, pz_pcb_thickness]);
        translate([0, pz_rounded_edge_offset, 0])
            cube([pz_length, pz_width - (2 * pz_rounded_edge_offset), pz_pcb_thickness]);

        // gpio 
        if (gpio_header)
        translate([pz_gpio_x_offset-(pz_gpio_length/2), 
                  (pz_width-pz_gpio_y_offset-(pz_gpio_width/2)), 
                  pz_pcb_thickness])
            cube([pz_gpio_length, pz_gpio_width, pz_gpio_height]);

        // gpio underside solder
        if (gpio_solder)
        translate([pz_gpio_x_offset-(pz_gpio_length/2), 
                  (pz_width-pz_gpio_y_offset-(pz_gpio_width/2)), 
                  -pz_botton_pin_height])
            cube([pz_gpio_length, pz_gpio_width, pz_botton_pin_height]);
        
        // sdcard 
        translate([-pz_sdcard_protrusion, 
                  (pz_sdcard_y_offset-(pz_sdcard_width/2)), 
                  pz_pcb_thickness])
            cube([pz_sdcard_length, pz_sdcard_width, pz_sdcard_height]);

        // camera
        
        translate([(pz_length - pz_camera_length + pz_camera_protrusion), 
                   (pz_camera_y_offset-(pz_camera_width/2)), 
                    pz_pcb_thickness])
            cube([pz_camera_length, pz_camera_width, pz_camera_height]);
            
        // hdmi 
        translate([(pz_hdmi_x_offset - (pz_hdmi_length/2)), 
                   -pz_hdmi_protrusion, 
                    pz_pcb_thickness])
            cube([pz_hdmi_length, pz_hdmi_width, pz_hdmi_height]);
            
        // usb power 
        translate([(pz_usb_power_x_offset - (pz_usb_length/2)), 
                   -pz_usb_protrusion, 
                    pz_pcb_thickness])
            cube([pz_usb_length, pz_usb_width, pz_usb_height]);
        
        // usb 
        translate([(pz_usb_x_offset - (pz_usb_length/2)), 
                   -pz_usb_protrusion, 
                    pz_pcb_thickness])
            cube([pz_usb_length, pz_usb_width, pz_usb_height]);
            
            
          
    }
    
    // make 0,0,0 centre
    translate([pz_camera_protrusion+pz_camera_protrusion-pz_max_length/2, 
               pz_usb_protrusion-pz_max_width/2, 
               0])
    difference () {
        pzw_solid();

        // mounting holes
        x_holes = [pz_mount_hole_offset, (pz_length - pz_mount_hole_offset)];
        y_holes = [pz_mount_hole_offset, (pz_width - pz_mount_hole_offset)];
        for (x = x_holes, y = y_holes)
            translate([x, y, -pz_pcb_thickness])
            {
                $fn = 40;
                cylinder(d=pz_mount_hole_dia, h=10);
            }
   }
}

case_inside_length = pz_max_length + 2*gap;
case_inside_width = pz_max_width + 2*gap;
case_inside_height = pz_get_max_height(true, true) + standoffs; 

case_outside_length = case_inside_length + (2*shell_thickness);
case_outside_width = case_inside_width + (2*shell_thickness);
case_outside_height = case_inside_height; //+ (2*shell_thickness);

module rounded_box(length, 
             width, 
             height, 
             rounded_edge_radius) 
{    
    
    // rounded edges
    x_round = [rounded_edge_radius, (length - rounded_edge_radius)];
    y_round= [rounded_edge_radius, (width - rounded_edge_radius)];
    for (x = x_round, y = y_round)
        translate([x, y, 0])
        {
            $fn = 40;
            cylinder(d=(2*rounded_edge_radius), h=height);
        }  

    // pcb split into bits to conform with rounded edges
    translate([rounded_edge_radius, 0, 0])
        cube([length - (2 * rounded_edge_radius), 
                width, 
                height]);
    translate([0, rounded_edge_radius, 0])
        cube([length, 
                width - (2 * rounded_edge_radius), 
                height]);    
}

module shell(inside_length, 
             inside_width, 
             inside_height, 
             thickness, 
             rounded_edge_radius) 
{
    difference () 
    {
        // outside
        translate([-thickness, -thickness, -thickness])
            rounded_box(case_outside_length, 
                case_outside_width, 
                case_outside_height,
                rounded_edge_radius);
    
        // inside, remove top by extending it through the outside
        rounded_box(inside_length, inside_width, case_outside_height+1, rounded_edge_radius);
        
        //NEW
        if (true) {
            offset = 12.4 + gap; // magic number for centre line
            translate([-case_outside_length/8, offset, (standoffs+pz_pcb_thickness/2)])
//                cube([case_outside_length/4, pz_sdcard_width+3, 4]);
                  cube([pz_usb_length+3.5, case_outside_length/8, 7]);
        }
        
        // hole for camera
        if (true) {
            offset = 12.4 + gap;
            translate([case_outside_length/1.25, offset, (standoffs+pz_pcb_thickness)])
                //#cube([case_outside_length/4, pz_camera_width-2, 1.2]);
                //cube([pz_usb_length+3.5, case_outside_length/4, 7]);
                cube([case_outside_length/4, case_outside_length/8, 7]);
        }
        
        
        if (sdcard_hole) {
            offset = 10.4 + gap; // magic number for centre line
            translate([-case_outside_length/8, offset, (standoffs+pz_pcb_thickness/2)+10])
                cube([case_outside_length/4, pz_sdcard_width+3, 4]);
        }
        
        if (usb_hole) {
            offset = 37.9 + gap;
            translate([offset, -case_outside_width/4, standoffs-0.6+10])
                cube([pz_usb_length+3.5, case_outside_length/4, 7]);
        }

        if (power_hole) {
            offset = 50.5 + gap;
            translate([offset, -case_outside_width/4, standoffs-0.6+10])
                cube([pz_usb_length+3.5, case_outside_length/4, 7]);
        }
        
        // hole for camera
        if (camera_hole) {
            offset = 8.5 + gap;
            translate([case_outside_length/1.25, offset, (standoffs+pz_pcb_thickness)+10])
                cube([case_outside_length/4, pz_camera_width-2, 1.2]);
        }
        if (hdmi_hole) {
            offset = 7.3 + gap;
            translate([offset, -case_outside_width/4, (standoffs+pz_pcb_thickness/2) +10])
                cube([pz_hdmi_length+3.5, case_outside_length/4, 5]);
        }
    }
}

module bottom_shell() {
    translate([-case_inside_length/2, -case_inside_width/2, 0])
        shell(case_inside_length, 
              case_inside_width, 
              case_inside_height, 
              shell_thickness, 
              pz_rounded_edge_offset);

    // mounting standoffs and pins for pizero
    translate([pz_camera_protrusion+pz_camera_protrusion-pz_max_length/2,
                pz_usb_protrusion-pz_max_width/2, 0]) 
    {
        x_pins = [pz_mount_hole_offset, (pz_length - pz_mount_hole_offset)];
        y_pins = [pz_mount_hole_offset, (pz_width - pz_mount_hole_offset)];
        for (x = x_pins, y = y_pins)
            translate([x, y, 0])
            {
                $fn = 40;
                difference(){
                cylinder(d=pz_mount_hole_dia_clearance+3, h=standoffs+1);
                //bottom hex cutouts
                bolt_cutout();
                }
                translate([0, 0, standoffs])
                    if (pins) 
                    {
                        // allow for some slack in the hole diameter, 0.9
                        // pins longer then pcb is thick so pcb can't slip out
                        ///////MOUNTING GOHOLES
                        //cylinder(d=(pz_mount_hole_dia*0.9), h=3*pz_pcb_thickness);
                    }
            }
    }  
    
    // for reference we can add a dummy pizero
    if (dummy_pizero) {
        color("yellow")
            translate([0, 0, standoffs]) // add 20 for outside box
                pzw(true, true);
    }
}


module bottom() {
    difference() 
    {
        bottom_shell();
        // holes right through instead of pins
        if (!pins) 
        {
            translate([pz_camera_protrusion+pz_camera_protrusion-pz_max_length/2,
                    pz_usb_protrusion-pz_max_width/2, 0]) 
            {
                x_pins = [pz_mount_hole_offset, (pz_length - pz_mount_hole_offset)];
                y_pins = [pz_mount_hole_offset, (pz_width - pz_mount_hole_offset)];
                for (x = x_pins, y = y_pins)
                    translate([x, y, 0])
                    {
                        $fn = 40;
                        translate([0, 0, -2*shell_thickness])
                            #cylinder(d=(pz_mount_hole_dia*1.1), h=2*case_inside_height);
                    }
            }
        }
    }
}

//bolt for base
module bolt_cutout() {
    cylinder(r=bolt_head_d/2+.02, h=bolt_thickness+10, $fn=6);
}

module top_with_rim() {
    difference(){
    // add an extra layer on top to cover the gpio hole
    union(){
        translate([0,0,0]){
    lid_thickness = (gpio_hole)?(shell_thickness):(shell_thickness+1);
    rounded_box(case_outside_length, case_outside_width, lid_thickness, pz_rounded_edge_offset);
        }    
    // need to make a rim/gland
    translate([shell_thickness, shell_thickness, -2*shell_thickness]) 
    {

        // translate to make sure that rim is part of the top
        translate([0,0,0.5]) 
//difference(){
        difference() 
        {
            rounded_box(case_outside_length - 2*shell_thickness, 
                         case_outside_width - 2*shell_thickness, 
                         2*shell_thickness, 
                         pz_rounded_edge_offset);
            



            // make a gland type rim by extending through the inside box
            translate([shell_thickness, shell_thickness, -shell_thickness])
                rounded_box(case_inside_length - 2*shell_thickness, 
                            case_inside_width - 2*shell_thickness, 
                            3*shell_thickness, 
                            pz_rounded_edge_offset);
        
       }
   }
   }
//camera slit
translate([5,5,10]){
rotate([0,90,0]){
cube([pz_camera_length+10, pz_camera_width+9, pz_camera_height]);
}
}

/*
//camera slit
translate([-1,5,10]){
rotate([0,90,0]){
cube([pz_camera_length+10, pz_camera_width+9, pz_camera_height]);
}
}
*/
}
}







module top () {
    color("orange")
    
    translate([-case_inside_length/2-shell_thickness, 
                -case_inside_width/2-shell_thickness, 
                case_outside_height+shell_thickness]) 
        difference () 
        {
            top_with_rim();
            //difference(){
            //translate([-30,-10,32]){
//}
         /*
            // always cut out for gpio pins
            offset_x = 9.9 + gap; // magic numbers
            offset_y = 25.4 + gap;
            translate([offset_x, offset_y, -3*shell_thickness])
                #cube([pz_gpio_length+2, 
                       pz_gpio_width+2,
                       4*shell_thickness+0.3]);
            
            // a notch to make taking top of easier
             translate([0, 10+gap, -0.1])
                cube([shell_thickness, 
                       15,
                       shell_thickness*0.6]);
            */
            // text, really deep text if we have no gpio cutout
            if(add_text) 
            {
                translate([case_outside_length/2,case_outside_width*0.5,shell_thickness*0.5]) 
                    linear_extrude(5, convexity=4) 
                        text(lid_text, font=text_font, valign="center", halign="center");
            }
        }
/*   
    if (pins)
    {
        // add locking pins to lid
        // values iteratively found 
        translate([pz_camera_protrusion+pz_camera_protrusion-pz_max_length/2, 
                    pz_usb_protrusion-pz_max_width/2,
                    case_outside_height - 2.9*shell_thickness]) 
        {
            x_pins = [pz_mount_hole_offset, (pz_length - pz_mount_hole_offset)];
            y_pins = [pz_mount_hole_offset, (pz_width - pz_mount_hole_offset)];

            for (x = x_pins, y = y_pins)
                translate([x, y, 0])
                {
                    //translate([0, 0, -2*shell_thickness])
                    difference ()
                    {
                        $fn = 40;
                        length = 6.6; //magic
                        #cylinder(d=pz_mount_hole_dia_clearance*0.9, h=length);
                        #cylinder(d=pz_mount_hole_dia*1.1, h=length);
                    }
                }
        }
            
    } */ 
}


/*
// something doesn't add up, measured prints do not equate
echo("inside length ", case_inside_length);
echo("inside width  ", case_inside_width);
echo("inside height  ", case_inside_height);

echo("outside length ", case_outside_length);
echo("outside width  ", case_outside_width);
echo("outside height ", case_outside_height);
*/

if (make_bottom) bottom();
if (make_top) { top();



// A Raspberry Pi camera mount.

$fs = .2;
$fa = 5;

// Dimensions of the camera board.
cameraWidth = 25;
//cameraHeight = 23;
cameraHeight = 38;
aperatureWidth = 8;
aperatureYOffset = 5.5;
cameraBoardThickness = 1;

holeYOffset = 9.5;
holeXSpacing = 21;
holeYSpacing = 12.5;
holeDiameter = 2;

mountMargin = 4;
mountBottomMargin = 7; // To accommodate the cable.
mountWidth = cameraWidth + 2*mountMargin;
mountHeight = cameraHeight + mountMargin + mountBottomMargin;

mountThickness = 3;

baseWidth = 15;
mountingHoleSpacing = 15;
mountingHoleDiameter = 3;

aperatureMargin = 1;

maxModelSize = 30;
/*
// The camera board.
%translate([mountBottomMargin, -cameraWidth/2, mountThickness])
cube(size=[cameraHeight, cameraWidth, cameraBoardThickness]);

// The mount base.
rotate([0, -90, 0])
difference() {
  translate([0, -mountWidth/2, 0])
  cube(size=[baseWidth + mountThickness, mountWidth, mountThickness]);
  
  translate([baseWidth/2 + mountThickness, -mountingHoleSpacing/2, 0])
  cylinder(d=mountingHoleDiameter, h=2*maxModelSize, center=true);
  
  translate([baseWidth/2 + mountThickness, mountingHoleSpacing/2, 0])
  cylinder(d=mountingHoleDiameter, h=2*maxModelSize, center=true);
}
*/

///////////////////////////////////////////////
/*
translate([-30,-10,32]){
rotate([0,90,0]){
cube([pz_camera_length, pz_camera_width, pz_camera_height]);
}
}
*/



// The main part of the mount.
translate([-33.8,0,30]){
rotate([0,-90,0]){
difference() {
  translate([0, -mountWidth/2, 0])
  cube(size=[cameraHeight + mountMargin + mountBottomMargin,
             cameraWidth + 2*mountMargin,
             mountThickness]);

translate([17,0,0]) {
  
  translate([holeYOffset + mountBottomMargin, -holeXSpacing/2, 0])
  cylinder(d=holeDiameter, h=2*maxModelSize, center=true);
  
  translate([holeYOffset + mountBottomMargin, holeXSpacing/2, 0])
  cylinder(d=holeDiameter, h=2*maxModelSize, center=true);
  
  translate([holeYOffset + holeYSpacing + mountBottomMargin, -holeXSpacing/2, 0])
  cylinder(d=holeDiameter, h=2*maxModelSize, center=true);
  
  translate([holeYOffset + holeYSpacing + mountBottomMargin, holeXSpacing/2, 0])
  cylinder(d=holeDiameter, h=2*maxModelSize, center=true);
  
  translate([mountBottomMargin + aperatureYOffset,
              -aperatureWidth/2 - aperatureMargin,
              -maxModelSize])
  cube(size=[aperatureWidth + 2*aperatureMargin,
             aperatureWidth + 2*aperatureMargin,
             2*maxModelSize]);
}
}
}
}
}
