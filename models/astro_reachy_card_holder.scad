// Astro Reachy: marco para tarjeta QR 100 × 141,7 mm.
// Imprime QR en papel y pégalo en el rebaje: un QR 3D no da contraste/precisión fiables.
$fn=48; card_w=100; card_h=141.7; border=4; base_h=2.4; recess=1.1;
module rounded_rect(w,h,r){hull()for(x=[r,w-r],y=[r,h-r])translate([x,y])circle(r=r);}
difference(){
 linear_extrude(base_h)rounded_rect(card_w+2*border,card_h+2*border,6);
 translate([border,border,base_h-recess])linear_extrude(recess+.1)rounded_rect(card_w,card_h,3);
 translate([border+7,card_h+border+5,-.1])cylinder(h=base_h+.2,r=1.8);
 translate([card_w+border-7,card_h+border+5,-.1])cylinder(h=base_h+.2,r=1.8);
}
