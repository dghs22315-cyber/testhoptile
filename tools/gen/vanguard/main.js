// Vanguard Arsenal 2.0 - stage 1 client scripts. Visual/audio only: safe on servers and in multiplayer.
//  * artillery: ground shadow of the shell (ballistic arc), pulsing impact marker, incoming-shell whistle
//  * shield emitter: hit and break sounds
// Each part disables itself on error; the mod keeps working without scripts.

var ARTY = {
    "vg-howl": { col: Color.valueOf("ffc94a"), whistle: "vg-shell-whistle", h: 10 },
    "vg-scorpion": { col: Color.valueOf("ff3355"), whistle: "scorpion-whistle", h: 16 }
};
var snd = {};
function S(n){
    if(snd[n] === undefined){
        try{ snd[n] = Vars.tree.loadSound(n); }catch(e){ snd[n] = null; }
    }
    return snd[n];
}

var types = null, failA = false, played = {}, clean = 0;
function initTypes(){
    types = new ObjectMap();
    for(var k in ARTY){
        var bl = Vars.content.block(k);
        if(bl == null) continue;
        var seq = bl.ammoTypes.values().toSeq();
        for(var i = 0; i < seq.size; i++) types.put(seq.get(i), ARTY[k]);
    }
}

Events.run(Trigger.draw, function(){
    if(failA) return;
    try{
        if(types == null) initTypes();
        Groups.bullet.each(function(b){
            var cfg = types.get(b.type());
            if(cfg == null) return;
            var s = b.fslope(), h = s * cfg.h, x = b.x(), y = b.y();
            Draw.z(Layer.groundUnit - 1);
            Draw.color(0, 0, 0, 0.25 + 0.3 * s);
            Fill.circle(x - h * 0.9, y - h, 1.8 + s * 2.6);

            var rem = b.lifetime() - b.time();
            if(rem > 1){
                var v = b.vel();
                var ix = x + v.x * rem, iy = y + v.y * rem;
                var r = Math.max(8, b.type().splashDamageRadius) * (0.4 + 0.6 * b.fout());
                Draw.z(Layer.effect);
                Draw.color(cfg.col, 0.3 + 0.4 * Mathf.absin(Time.time, 3, 1));
                Lines.stroke(1.2);
                Lines.circle(ix, iy, r);
                for(var i = 0; i < 4; i++){
                    var a = i * 90 + 45;
                    Lines.lineAngle(ix + Angles.trnsx(a, r * 0.55), iy + Angles.trnsy(a, r * 0.55), a, r * 0.3);
                }
                Draw.color(cfg.col, 0.7);
                Fill.circle(ix, iy, 1.2);
                if(rem < 70){
                    var id = b.id();
                    if(played[id] === undefined){
                        played[id] = Time.time;
                        var w = S(cfg.whistle);
                        if(w != null) w.at(ix, iy, Mathf.random(0.94, 1.06));
                    }
                }
            }
        });
        Draw.reset();
        if(++clean > 600){
            clean = 0;
            for(var k in played){ if(Time.time - played[k] > 600) delete played[k]; }
        }
    }catch(e){
        failA = true; Draw.reset();
        Log.err("[vg] artillery visuals disabled: " + e);
    }
});

var failB = false, emitter = null, shields = {}, tick = 0;
Events.on(WorldLoadEvent, function(){ shields = {}; });
Events.run(Trigger.update, function(){
    if(failB || Vars.headless || !Vars.state.isGame()) return;
    if(++tick < 4) return;
    tick = 0;
    try{
        if(emitter == null){
            emitter = Vars.content.block("vg-shield-emitter");
            if(emitter == null){ failB = true; return; }
        }
        Groups.build.each(function(b){
            if(b.block() != emitter) return;
            var k = b.pos(), p = shields[k], hit = b.hit, br = b.broken;
            if(p !== undefined){
                if(br && !p.br){
                    var s1 = S("shield-break"); if(s1 != null) s1.at(b.x(), b.y(), 1);
                }else if(!br && hit > p.hit + 0.3){
                    var s2 = S("shield-hit"); if(s2 != null) s2.at(b.x(), b.y(), Mathf.random(0.9, 1.1), 0.6);
                }
            }
            shields[k] = { hit: hit, br: br };
        });
    }catch(e){
        failB = true;
        Log.err("[vg] shield sounds disabled: " + e);
    }
});
