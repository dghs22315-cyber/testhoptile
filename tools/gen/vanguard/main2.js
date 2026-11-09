
// ===================== Stage 2: BKM cores, engineers, SupCom build rule, ACU death blast, mech steps, spotter marking
// Gameplay parts (build rule, death blast, status) run on the server/host; visuals and sounds run on clients.
var ACU = { "vg-acu-uef": true, "vg-acu-cybran": true };
var BUILDERS = { "vg-acu-uef": true, "vg-acu-cybran": true, "vg-engineer": true };
var VGCORE = { "vg-core-uef": true, "vg-core-cybran": true };
function F(o, n){ var v = o[n]; return (typeof v === "function") ? o[n]() : v; }

// status "spotted" (vg-spotted): marked by a powered spotter beacon, takes +25% damage
var spotted = null;
try{
    spotted = new StatusEffect("spotted");
    spotted.healthMultiplier = 0.8;
    spotted.color = Color.valueOf("6ab8ff");
    spotted.effect = Fx.none;
}catch(e){ spotted = null; Log.err("[vg] spotted status disabled: " + e); }

// engineers start in "assist" mode: they follow and help any construction nearby
Events.on(ContentInitEvent, function(){
    try{
        var eng = Vars.content.unit("vg-engineer");
        if(eng != null) eng.defaultCommand = UnitCommand.assistCommand;
    }catch(e){ Log.err("[vg] engineer default command: " + e); }
});

// SupCom rule: a team that owns a BKM core can only build with ACUs and engineers
var failC = false, ruleTick = 0, toastAt = -9999;
Events.run(Trigger.update, function(){
    if(failC || !Vars.state.isGame()) return;
    if(++ruleTick < 20) return;
    ruleTick = 0;
    try{
        var rt = {}, any = false;
        var tds = Vars.state.teams.present;
        for(var i = 0; i < tds.size; i++){
            var td = tds.get(i), cs = F(td, "cores");
            for(var j = 0; j < cs.size; j++){
                if(VGCORE[cs.get(j).block().name]){ rt[F(td, "team").id] = true; any = true; break; }
            }
        }
        if(!any) return;
        Groups.unit.each(function(u){
            if(!rt[u.team().id] || BUILDERS[u.type().name]) return;
            var q = u.plans();
            if(q == null || q.size == 0) return;
            u.clearBuilding();
            if(!Vars.headless && u == Vars.player.unit() && Time.time - toastAt > 300){
                toastAt = Time.time;
                Vars.ui.showInfoToast(Core.bundle.get("vg.buildrule"), 3);
            }
        });
    }catch(e){
        failC = true;
        Log.err("[vg] build rule disabled: " + e);
    }
});

// ACU death: overload blast hits enemies only (visual + sound come from the unit's deathExplosionEffect/deathSound)
Events.on(UnitDestroyEvent, function(ev){
    try{
        var u = ev.unit;
        if(u == null || !ACU[u.type().name]) return;
        if(!Vars.headless) Effect.shake(7, 70, u.x, u.y);
        if(!Vars.net.client()) Damage.damage(u.team(), u.x, u.y, 64, 1200);
    }catch(e){ Log.err("[vg] ACU death blast: " + e); }
});

// heavy mech footsteps: sound + light shake when a foot lands
var failD = false, steps = {}, stepClean = 0;
Events.run(Trigger.update, function(){
    if(failD || Vars.headless || !Vars.state.isGame()) return;
    try{
        Groups.unit.each(function(u){
            if(!ACU[u.type().name] || u.isFlying()) return;
            var q = Math.floor(u.walkExtend(true)), id = u.id, p = steps[id];
            if(p !== undefined && q != p && (q == 1 || q == 3)){
                var sn = S("acu-step");
                if(sn != null) sn.at(u.x, u.y, Mathf.random(0.9, 1.1), 0.7);
                Effect.shake(0.7, 8, u.x, u.y);
            }
            steps[id] = q;
        });
        if(++stepClean > 1800){ stepClean = 0; steps = {}; }
    }catch(e){
        failD = true;
        Log.err("[vg] mech steps disabled: " + e);
    }
});

// spotter beacon: powered beacons mark enemies within 25 tiles (status applied by the server/host)
var failE = false, spotTick = 0, beacon = null, pingAt = {};
Events.on(WorldLoadEvent, function(){ pingAt = {}; steps = {}; });
Events.run(Trigger.update, function(){
    if(failE || spotted == null || !Vars.state.isGame()) return;
    if(++spotTick < 30) return;
    spotTick = 0;
    try{
        if(beacon == null){
            beacon = Vars.content.block("vg-spotter-beacon");
            if(beacon == null){ failE = true; return; }
        }
        Groups.build.each(function(b){
            if(b.block() != beacon) return;
            var ef = F(b, "efficiency");
            if(!(ef > 0.01)) return;
            var n = 0, bx = b.x, by = b.y;
            Units.nearbyEnemies(b.team(), bx, by, 200, function(u){
                n++;
                if(!Vars.net.client()) u.apply(spotted, 75);
            });
            if(n > 0 && !Vars.headless){
                var k = b.pos(), last = pingAt[k];
                if(last === undefined || Time.time - last > 360){
                    pingAt[k] = Time.time;
                    var ps = S("spot-ping");
                    if(ps != null) ps.at(bx, by, 1, 0.5);
                }
            }
        });
    }catch(e){
        failE = true;
        Log.err("[vg] spotter marking disabled: " + e);
    }
});

// rotating blue target brackets over spotted units
var failF = false;
Events.run(Trigger.draw, function(){
    if(failF || spotted == null) return;
    try{
        Draw.z(Layer.effect + 1);
        Groups.unit.each(function(u){
            if(!u.hasEffect(spotted)) return;
            var r = u.hitSize * 0.75 + 3, x = u.x, y = u.y;
            Draw.color(spotted.color, 0.5 + 0.35 * Mathf.absin(Time.time, 4, 1));
            Lines.stroke(1.1);
            for(var i = 0; i < 4; i++){
                var a = 45 + i * 90 + Time.time * 0.8;
                Lines.lineAngle(x + Angles.trnsx(a, r), y + Angles.trnsy(a, r), a + 180, 3);
            }
        });
        Draw.reset();
    }catch(e){
        failF = true; Draw.reset();
        Log.err("[vg] spotted markers disabled: " + e);
    }
});
