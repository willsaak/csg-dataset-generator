seed = 6;
seeds = rands(0,1000000,10,seed);
head_size = rands(50,100,1,seeds[1])[0];
head_length = rands(10,40,1,seeds[2])[0];
bolt_length = rands(head_length*2,200,1,seeds[3])[0];
bolt_radius = rands(head_size/5, head_size/3,1,seeds[0])[0];
cube_size = rands(head_size/3, head_length*1.5,1, seeds[4])[0];

difference(){
    union(){
        cube([head_size,head_size,head_length], center=true);
        cylinder(bolt_length,bolt_radius,bolt_radius);
    }
    translate([0,0,-head_length/2]){
        cube(cube_size, true);
    }
}