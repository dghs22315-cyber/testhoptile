
// ---------------- Vanguard Arsenal 2.0 - stage 3 scripts
//  * Redoubt / Mantis shells get the same ballistic shadow, impact marker and incoming whistle as Howl / Scorpion
//  * EMP (neodymium magnet) shells: on impact enemy buildings in the blast radius are slowed to 35% for 4 s (server-side only)
//    + blue shock-ring effect for everyone. Units get 'electrified' from the shell itself (JSON status).
ARTY["vg-redoubt"] = { col: Color.valueOf("ffc94a"), whistle: "vg-shell-whistle", h: 12 };
ARTY["vg-mantis"] = { col: Color.valueOf("ff3355"), whistle: "scorpion-whistle", h: 18 };

var empFx = new Effect(42, function(e){
    Draw.color(Color.valueOf("d6f0ff"), Color.valueOf("4aa8ff"), e.fin());
    Lines.stroke(2.6 * e.fout());
    Lines.circle(e.x, e.y, e.rotation * e.finpow());
    Angles.randLenVectors(e.id, 10, e.rotation * e.finpow(), function(x, y){
        Lines.lineAngle(e.x + x, e.y + y, Mathf.angle(x, y), 1 + 5 * e.fout());
    });
    Draw.reset();
});
var empT = null, empFail = false;
function empInit(){
    empT = new ObjectMap();
    var mag = Vars.content.item("vg-magnet");
    var defs = [["vg-mantis", 40], ["vg-hydra", 22]];
    for(var i = 0; i < defs.length; i++){
        var bl = Vars.content.block(defs[i][0]);
        if(bl == null || mag == null) continue;
        var bt = bl.ammoTypes.get(mag);
        if(bt != null) empT.put(bt, defs[i][1]);
    }
}
Events.run(Trigger.update, function(){
    if(empFail || !Vars.state.isPlaying()) return;
    try{
        if(empT == null) empInit();
        if(empT.size == 0) return;
        Groups.bullet.each(function(b){
            var r = empT.get(b.type());
            if(r == null || b.data() === true) return;
            if(b.time() + Time.delta * 1.5 < b.lifetime()) return;
            b.data(true);
            var x = b.x(), y = b.y(), tm = b.team();
            empFx.at(x, y, r);
            if(Vars.net.client()) return;
            Vars.indexer.eachBlock(null, x, y, r, function(bd){ return bd.team != tm; }, function(bd){
                try{ bd.applySlowdown(0.35, 240); }catch(e2){}
            });
        });
    }catch(e){ empFail = true; Log.err("[vg] EMP script disabled: " + e); }
});
