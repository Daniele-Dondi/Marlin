diam_M3=3.5;
servo_t=19.8;
servo_w1=40.6;
servo_w2=48.4;
servo_w3=53.4;
servo_d=17.3;
servo_a=20;
servo_fixingscrew_diam=4.5;
servo_fixingscrew_distance=10.2;

//variables for driving disk
$fn=100;
R=20;
spess_y=3.3;
spess_z=5;
lung=26.8;
diam_horn_screws=2.3;

translate([-20/2+11/2+3,-7+11/2,-7.5
]){//basement+pillars
    
    translate([-35+15/2,0,0]){
    translate([40,0,0])cube([80,20,5],true);        
        difference(){
        union(){
        cube([10,30,5],true);
        translate([0,10,45/2+5/2])cube([10,10,45],true);
translate([0,-10,45/2+5/2])cube([10,10,45],true);     
translate([80-5,0,45/2+5/2])cube([10,10,45],true);}
//M3 holes
translate([0,0,45+5/2-5]){        
translate([0,10,0])rotate([0,90,0])cylinder(d=diam_M3,h=20,center=true,$fn=30);        
translate([0,-10,0])rotate([0,90,0])cylinder(d=diam_M3,h=20,center=true,$fn=30);            
translate([80-10/2,0,0])rotate([0,90,0])cylinder(d=diam_M3,h=20,center=true,$fn=30);                
} }
    }
    }
mirror([0,1,0])
difference(){
cube([20,14,10],center=true);
    //corpo centrale
    translate([-20/2+11/2+3,7-11/2,3])cylinder(d=11,h=8,$fn=50,center=true);
        translate([-30/2,7-11/2,(6+10)/2-3])rotate([0,90,0])cylinder(d=6,h=30,$fn=50,center=true);
       rotate([0,0,90]) translate([-30/2,7-11/2,(6+10)/2-3])rotate([0,90,0])cylinder(d=6,h=100,$fn=50,center=true);    
           
}

//driving disk
   translate([-20/2+11/2+3,-7+11/2,20])rotate([0,0,-45]){
difference () {
cylinder(h=spess_z+3 , r=22);
translate([0,0,-1])cylinder(h=spess_z+1 , r=5);
translate([0,0,spess_z/2-1]) cube([lung,spess_y,spess_z+2],true) ;
translate([0,spess_y+1,spess_z/2-1]) cube([spess_y,18,spess_z+2],true) ;
translate([0,1.5,-1]) cylinder(h=spess_z+1 , r=5+1,$fn=4);    
//hole for servo central screw    
cylinder(h=spess_z+4 , r=3.5);//holes for fixing servo horn    
rotate([0,0,45]){
translate([0,16,-1])cylinder(h=spess_z+6 , d=diam_horn_screws);
translate([0,-16,-1])cylinder(h=spess_z+6 , d=diam_horn_screws);
}

rotate([0,0,-45]){
translate([0,15,-1])cylinder(h=spess_z+6 , d=diam_horn_screws);
translate([0,-15,-1])cylinder(h=spess_z+6 , d=diam_horn_screws);
}    
}

    
}




translate([0,0,57])
{difference(){
    translate([8.5,-1.5,0]){cube([95,30,5],true);
    translate([95/2-5/2,0,-15/2])cube([5,30,15],true);        
    translate([-95/2+5/2,0,-15/2])cube([5,30,15],true);        
        
    }
    //difference
translate([-20/2+11/2+3+11,-7+11/2,0]){    
//hole for servo
cube([servo_w1+2,servo_t+2,5*2],center=true);    
//servo screw holes
translate([-servo_w2/2,-servo_fixingscrew_distance/2,0])cylinder(d=servo_fixingscrew_diam,h=20,$fn=20,center=true);
translate([-servo_w2/2,+servo_fixingscrew_distance/2,0])cylinder(d=servo_fixingscrew_diam,h=20,$fn=20,center=true);    
translate([servo_w2/2,-servo_fixingscrew_distance/2,0])cylinder(d=servo_fixingscrew_diam,h=20,$fn=20,center=true);
translate([servo_w2/2,+servo_fixingscrew_distance/2,0])cylinder(d=servo_fixingscrew_diam,h=20,$fn=20,center=true);    }
//M3 holes
translate([-35,-1.5,-5/2-5]){        
translate([0,10,0])rotate([0,90,0])cylinder(d=diam_M3,h=20,center=true,$fn=30);        
translate([0,-10,0])rotate([0,90,0])cylinder(d=diam_M3,h=20,center=true,$fn=30);            
translate([90-5/2,0,0])rotate([0,90,0])cylinder(d=diam_M3,h=20,center=true,$fn=30);                
}


}

}
