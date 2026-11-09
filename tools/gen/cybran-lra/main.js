// Cybran Arsenal - artillery visuals for the Long Range Artillery shells.
//  * ground shadow that separates from the shell at mid-flight (shows the ballistic arc)
//  * pulsing impact marker at the landing point while the shell is in the air
//  * incoming-shell whistle at the landing point ~1.2 s before impact
// Purely visual/audio, client-side. If anything here fails it disables itself and the mod keeps working.
// If your Mindustry build has problems with scripts, simply delete the scripts folder from the mod.

var lra = null;
var types = null;
var failed = false;
var red = Color.valueOf("ff3355");
var whistle = null;
var played = {};
var cleanTimer = 0;

try{
    whistle = Vars.tree.loadSound("cybran-lra-whistle");
}catch(e){
    whistle = null;
}

Events.run(Trigger.draw, function(){
    if(failed) return;
    try{
        if(types == null){
            lra = Vars.content.block("cybran-arsenal-cybran-lra");
            if(lra == null) return;
            types = lra.ammoTypes.values().toSeq();
        }
        Groups.bullet.each(function(b){
            if(!types.contains(b.type())) return;
            var s = b.fslope();
            var h = s * 16;
            var x = b.x(), y = b.y();

            // shadow on the ground, drifts away from the shell while it is high up
            Draw.z(Layer.groundUnit - 1);
            Draw.color(0, 0, 0, 0.28 + 0.3 * s);
            Fill.circle(x - h * 0.9, y - h, 2.2 + s * 2.8);

            var rem = b.lifetime() - b.time();
            if(rem > 1){
                var v = b.vel();
                var ix = x + v.x * rem, iy = y + v.y * rem;

                // impact marker
                var r = Math.max(8, b.type().splashDamageRadius) * (0.4 + 0.6 * b.fout());
                Draw.z(Layer.effect);
                Draw.color(red, 0.35 + 0.45 * Mathf.absin(Time.time, 3, 1));
                Lines.stroke(1.3);
                Lines.circle(ix, iy, r);
                for(var i = 0; i < 4; i++){
                    var a = i * 90 + 45;
                    Lines.lineAngle(ix + Angles.trnsx(a, r * 0.55), iy + Angles.trnsy(a, r * 0.55), a, r * 0.3);
                }
                Draw.color(red, 0.7);
                Fill.circle(ix, iy, 1.3);

                // whistle of the incoming shell
                if(whistle != null && rem < 75){
                    var id = b.id();
                    if(played[id] === undefined){
                        played[id] = Time.time;
                        whistle.at(ix, iy, 1);
                    }
                }
            }
        });
        Draw.reset();

        cleanTimer += 1;
        if(cleanTimer > 600){
            cleanTimer = 0;
            for(var k in played){
                if(Time.time - played[k] > 600) delete played[k];
            }
        }
    }catch(e){
        failed = true;
        Draw.reset();
        Log.err("[cybran-arsenal] artillery visuals disabled: " + e);
    }
});
