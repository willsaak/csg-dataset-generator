seed = 18;
seeds = rands(0,1000000,10,seed);
head_size = rands(25,50,1,seeds[1])[0];
head_radius = rands(25,50,1,seeds[2])[0];
bolt_length = rands(head_size*2,200,1,seeds[3])[0];
bolt_radius = rands(head_size/3, head_size/2,1,seeds[0])[0];
cube_size = rands(bolt_radius*2, head_radius*1.6,1, seeds[4])[0];
hole_size = rands(cube_size/10, cube_size/7,1,seeds[5])[0];

difference(){
    union(){
        intersection(){
            cylinder(head_size,head_radius,head_radius);
            cube([cube_size,head_radius*2,head_size], center=true);
        }
        cylinder(bolt_length,bolt_radius,bolt_radius);
    }
    rotate([90, 0, 0]){
        cylinder(head_radius*2,hole_size,hole_size, true);
    }
}