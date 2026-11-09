
// ---------------- Vanguard Arsenal 2.5 - T4 scripts
//  * Monolith shells get the ballistic shadow / impact marker / incoming whistle (shared ARTY system)
//  * 'disarmed' status (weapons offline, -40% speed) for Suppressor EMP and Monolith magnet shells
//  * Monolith magnet shell: on impact enemy buildings in 9 tiles are slowed to 30% for 5 s (server-side) + red shock ring
ARTY["vg-monolith"] = { col: Color.valueOf("7fd4ff"), whistle: "scorpion-whistle", h: 26 };

var disarmed = null;
try{
    disarmed = new StatusEffect("disarmed");
    disarmed.disarm = true;
    disarmed.speedMultiplier = 0.6;
    disarmed.color = Color.valueOf("ff3355");
    disarmed.effect = Fx.none;
}catch(e){ Log.err("[vg] disarmed status failed: " + e); }

var dsFx = new Effect(48, function(e){
    Draw.color(Color.valueOf("ffd6dd"), Color.valueOf("ff3355"), e.fin());
    Lines.stroke(3 * e.fout());
    Lines.circle(e.x, e.y, e.rotation * e.finpow());
    Lines.stroke(1.4 * e.fout());
    Lines.circle(e.x, e.y, e.rotation * 0.6 * e.finpow());
    Angles.randLenVectors(e.id, 14, e.rotation * e.finpow(), function(x, y){
        Lines.lineAngle(e.x + x, e.y + y, Mathf.angle(x, y), 1 + 6 * e.fout());
    });
    Draw.reset();
});
var dsT = null, dsFail = false, dsDone = false;
function dsInit(){
    dsT = new ObjectMap();
    var sup = Vars.content.block("vg-suppressor");
    var mon = Vars.content.block("vg-monolith");
    var mag = Vars.content.item("vg-magnet");
    if(disarmed != null && sup != null && sup.shootType != null){
        sup.shootType.status = disarmed; sup.shootType.statusDuration = 240;
    }
    if(mon != null && mag != null){
        var bt = mon.ammoTypes.get(mag);
        if(bt != null){
            if(disarmed != null){ bt.status = disarmed; bt.statusDuration = 240; }
            dsT.put(bt, 72);
        }
    }
    dsDone = true;
}
try{ Events.on(ContentInitEvent, function(){ try{ dsInit(); }catch(e){ Log.err("[vg] T4 init: " + e); } }); }catch(e){}
Events.run(Trigger.update, function(){
    if(dsFail || !Vars.state.isPlaying()) return;
    try{
        if(!dsDone) dsInit();
        if(dsT.size == 0) return;
        Groups.bullet.each(function(b){
            var r = dsT.get(b.type());
            if(r == null || b.data() === "ds") return;
            if(b.time() + Time.delta * 1.5 < b.lifetime()) return;
            b.data("ds");
            var x = b.x(), y = b.y(), tm = b.team();
            dsFx.at(x, y, r);
            if(Vars.net.client()) return;
            Vars.indexer.eachBlock(null, x, y, r, function(bd){ return bd.team != tm; }, function(bd){
                try{ bd.applySlowdown(0.3, 300); }catch(e2){}
            });
        });
    }catch(e){ dsFail = true; Log.err("[vg] T4 script disabled: " + e); }
});
