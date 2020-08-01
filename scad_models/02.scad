seed = 1;
seeds = rands(0,1000000,10,seed);
head_outer_radius = rands(25,50,1,seeds[0])[0];
head_inner_radius = rands(10,head_outer_radius*2/3,1,seeds[1])[0];
head_length = rands(40,80,1,seeds[2])[0];
bolt_length = rands(head_length*2,200,1,seeds[3])[0];
cube_size = rands(head_inner_radius, head_length/2,1, seeds[4])[0];

difference(){
    union(){
        cylinder(head_length,head_outer_radius,0);
        cylinder(bolt_length,head_inner_radius,head_inner_radius);
    }
    cube(cube_size, true);
}