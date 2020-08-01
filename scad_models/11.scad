seed = 10;
seeds = rands(0,1000000,10,seed);
head_size = rands(25,50,1,seeds[1])[0];
bolt_length = rands(head_size*2,200,1,seeds[3])[0];
bolt_radius = rands(head_size/3, head_size/2,1,seeds[0])[0];

union(){
    sphere(head_size);
    cylinder(bolt_length,bolt_radius,bolt_radius);
}