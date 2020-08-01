seed = 13;
seeds = rands(0,1000000,10,seed);
head_size = rands(25,50,1,seeds[1])[0];
bolt_length = rands(head_size*2,200,1,seeds[3])[0];
bolt_radius = rands(head_size/3, head_size/2,1,seeds[0])[0];
cylinder_size = rands(head_size/7, head_size/4,1, seeds[4])[0];


difference(){
    union(){
        sphere(head_size);
        cylinder(bolt_length,bolt_radius,bolt_radius);
    }
    translate([0,0,-head_size]){
        rotate([90, 0, 0]){
            cylinder(head_size*2, cylinder_size, cylinder_size, center=true);
        }
    }
}