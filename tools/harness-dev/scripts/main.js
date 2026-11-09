// Vanguard Arsenal in-game test stand (NOT shipped with the mod).
// Builds a flat test world with every vg block, a firing range with enemy targets,
// takes screenshots from the real renderer and exits. Output: <data>/vgtest/*.png + manifest.json
var OUT = Core.settings.getDataDirectory().child("vgtest");
var W = 230, H = 160;
var CAT_ORDER = ["turret", "defense", "effect", "crafting", "production", "power", "units", "distribution", "liquid", "logic"];
var manifest = { blocks: [], shots: [], errors: [] };
var shots = [], shotIdx = 0, armedFrame = -1, t0 = -1, done = false, feedTick = 0, waveTick = 0;
var turrets = [], targets = [];

function L(m){ Log.info("[vgtest] " + m); }
function E(m){ Log.err("[vgtest] " + m); manifest.errors.push(String(m)); }

function vgBlocks(){
    var out = [];
    Vars.content.blocks().each(function(b){
        if(b.minfo != null && b.minfo.mod != null && b.minfo.mod.name == "vg") out.push(b);
    });
    return out;
}

function off(size){ return Math.floor((size - 1) / 2); }

function place(block, bx, by, team, rot){
    var t = Vars.world.tile(bx + off(block.size), by + off(block.size));
    if(t == null) return null;
    t.setBlock(block, team, rot || 0);
    return t.build;
}

function addShot(name, at, cx, cy, scale, gif){
    shots.push({ name: name, at: at, cx: cx, cy: cy, scale: scale, gif: !!gif });
}

function setup(){
    try{
        Vars.world.loadGenerator(W, H, function(tiles){
            tiles.each(function(x, y){
                var floor = (y >= 88) ? Blocks.darksand : Blocks.stone;
                tiles.set(x, y, new Tile(x, y, floor, Blocks.air, Blocks.air));
            });
        });
        var r = new Rules();
        r.infiniteResources = true;
        r.waves = false;
        r.fog = false;
        r.lighting = false;
        r.teams.get(Team.sharded).cheat = true;
        r.teams.get(Team.crux).cheat = true;
        Vars.state.rules = r;
        Vars.logic.play();
        Vars.renderer.minZoom = 0.5;
        Vars.ui.hudfrag.shown = false;
        place(Blocks.coreShard, 2, H - 6, Team.sharded, 0);

        layoutShowcase();
        layoutRange();
        layoutMech();
        planShots();
        t0 = Time.time;
        L("setup done: " + manifest.blocks.length + " blocks, " + shots.length + " shots");
    }catch(e){
        E("setup failed: " + e);
        finish();
    }
}

function layoutShowcase(){
    var list = vgBlocks();
    list.sort(function(a, b){
        var ca = CAT_ORDER.indexOf(String(a.category)), cb = CAT_ORDER.indexOf(String(b.category));
        if(a instanceof OreBlock) ca = 99;
        if(b instanceof OreBlock) cb = 99;
        if(ca != cb) return ca - cb;
        return a.size - b.size;
    });
    var x = 6, y = 6, rowH = 0, gap = 2, maxX = W - 6, prevCat = null;
    for(var i = 0; i < list.length; i++){
        var b = list[i];
        var cat = (b instanceof OreBlock) ? "ore" : String(b.category);
        var s = (b instanceof OreBlock) ? 3 : b.size;
        if(prevCat != null && cat != prevCat){ x += 3; }
        if(x + s > maxX){ x = 6; y += rowH + gap; rowH = 0; }
        try{
            if(b instanceof OreBlock){
                for(var dx = 0; dx < 3; dx++) for(var dy = 0; dy < 3; dy++){
                    Vars.world.tile(x + dx, y + dy).setOverlay(b);
                }
            }else{
                var bd = place(b, x, y, Team.sharded, 0);
                if(bd == null) E("place returned null: " + b.name);
            }
            manifest.blocks.push({ name: String(b.name), x: x, y: y, size: s, cat: cat });
        }catch(e){ E("place " + b.name + ": " + e); }
        x += s + gap;
        rowH = Math.max(rowH, s);
        prevCat = cat;
    }
    // units next to the showcase
    var ux = 8;
    var uy = y + rowH + 4;
    ["vg-acu-uef", "vg-acu-cybran", "vg-engineer"].forEach(function(n){
        var u = Vars.content.unit(n);
        if(u == null){ E("missing unit " + n); return; }
        try{ u.spawn(Team.sharded, ux * 8, uy * 8); manifest.blocks.push({ name: n, x: ux, y: uy, size: 2, cat: "unit" }); }catch(e){ E("spawn " + n + ": " + e); }
        ux += 6;
    });
    manifest.showcaseTop = uy + 4;
}

function layoutRange(){
    var row = 96, x = 8;
    vgBlocks().forEach(function(b){
        if(String(b.category) != "turret") return;
        var bd = place(b, x, row, Team.sharded, 1);
        if(bd != null) turrets.push(bd);
        if(b.heatRequirement > 0){
            // heat source directly below, facing up into the turret
            var hb = Vars.content.block("vg-plasma-heater");
            if(hb != null) place(hb, x + Math.floor((b.size - 3) / 2), row - 3, Team.sharded, 1);
        }
        manifest.blocks.push({ name: String(b.name), x: x, y: row, size: b.size, cat: "range" });
        x += b.size + 4;
    });
    ["vg-spotter-beacon", "vg-recon-radar"].forEach(function(n){
        var b = Vars.content.block(n);
        if(b == null){ E("missing " + n); return; }
        place(b, x, row, Team.sharded, 0);
        manifest.blocks.push({ name: n, x: x, y: row, size: b.size, cat: "range" });
        x += b.size + 4;
    });
    manifest.rangeEnd = x;
    buildTargets();
}

function buildTargets(){
    var walls = [[106, 110], [134, 142]];
    for(var w = 0; w < walls.length; w++){
        for(var y = walls[w][0]; y < walls[w][1]; y += 3){
            for(var x = 6; x < manifest.rangeEnd + 4; x += 3){
                var t = Vars.world.tile(x, y);
                if(t != null && t.build == null) t.setBlock(Blocks.thoriumWallLarge, Team.crux, 0);
            }
        }
    }
}

function spawnEnemies(){
    var types = [UnitTypes.dagger, UnitTypes.mace, UnitTypes.flare, UnitTypes.horizon];
    for(var i = 0; i < 8; i++){
        var t = types[i % types.length];
        t.spawn(Team.crux, (10 + Math.random() * (manifest.rangeEnd - 10)) * 8, (112 + Math.random() * 18) * 8);
    }
}

function feed(){
    for(var i = 0; i < turrets.length; i++){
        var b = turrets[i];
        if(b == null || !b.isValid()) continue;
        var am = b.block.ammoTypes;
        if(am == null || am.keys == undefined) continue;
        var keys = am.keys().toSeq();
        if(keys.size == 0) continue;
        var phase = Math.floor((Time.time - t0) / 400);
        var it = keys.get((i + phase) % keys.size);
        for(var n = 0; n < 12 && b.acceptItem(b, it); n++) b.handleItem(b, it);
    }
}

function planShots(){
    var top = manifest.showcaseTop;
    addShot("00-showcase-overview", t0 + 60, W / 2, top / 2, 0.6);
    var i = 1;
    for(var cy = 18; cy < top + 4; cy += 30){
        for(var cx = 30; cx < W + 20; cx += 50){
            addShot("0" + (i++) + "-showcase-" + cx + "-" + cy, t0 + 70 + i * 4, cx, cy, 3);
        }
    }
    var rc = manifest.rangeEnd / 2;
    addShot("20-range-overview-a", t0 + 300, rc, 118, 0.9);
    addShot("25-mech-area", t0 + 560, 185, 128, 1.6);
    addShot("21-range-overview-b", t0 + 520, rc, 118, 0.9);
    for(var cx = 26, k = 0; cx < manifest.rangeEnd + 20; cx += 52, k++){
        addShot("3" + k + "-range-turrets-" + cx, t0 + 600 + k * 30, cx, 104, 2.6);
    }
    for(var f = 0; f < 36; f++){
        addShot("gif-" + (f < 10 ? "0" : "") + f, t0 + 760 + f * 5, rc, 112, 1.4, true);
    }
}

var probes = [];
function statusByName(n){ return Vars.content.getByName(ContentType.status, n); }
function probe(){
    var sp = statusByName("vg-spotted"), ds = statusByName("vg-disarmed");
    var c = { t: Math.round(Time.time - t0), enemyUnits: 0, spotted: 0, disarmed: 0, slowedEnemyBuildings: 0, bullets: Groups.bullet.size() };
    Groups.unit.each(function(u){
        if(u.team != Team.crux) return;
        c.enemyUnits++;
        if(sp != null && u.hasEffect(sp)) c.spotted++;
        if(ds != null && u.hasEffect(ds)) c.disarmed++;
    });
    Groups.build.each(function(b){ if(b.team == Team.crux && b.timeScale < 0.99) c.slowedEnemyBuildings++; });
    probes.push(c);
    L("probe " + JSON.stringify(c));
}
// ---- deterministic mechanics tests (pinned, unkillable enemy dummies)
var dummies = [], mech = { spottedMax: 0, disarmedMax: 0, empSlowMax: 0, monolithSlowMax: 0, acuWallsBefore: -1, acuWallsAfter: -1, acuKilled: false };
var acuWalls = [], acuUnit = null, poly = null, eng = null;
function wallRing(cx, cy, rad){
    for(var dx = -rad; dx <= rad; dx += 2) for(var dy = -rad; dy <= rad; dy += 2){
        if(Math.abs(dx) < rad && Math.abs(dy) < rad) continue;
        var t = Vars.world.tile(cx + dx, cy + dy);
        var corner = Math.abs(dx) == rad && Math.abs(dy) == rad;
        if(t != null && t.build == null) t.setBlock(corner ? Blocks.duo : Blocks.thoriumWall, Team.crux, 0);
    }
}
function dummy(x, y){
    var u = UnitTypes.dagger.spawn(Team.crux, x * 8, y * 8);
    dummies.push({ u: u, x: x * 8, y: y * 8 });
    wallRing(x, y, 3);
}
function layoutMech(){
    place(Vars.content.block("vg-spotter-beacon"), 150, 140, Team.sharded, 0);
    dummy(153, 140); dummy(150, 145);
    place(Vars.content.block("vg-suppressor"), 162, 130, Team.sharded, 0);
    dummy(168, 131); dummy(163, 137);
    var m = place(Vars.content.block("vg-mantis"), 176, 102, Team.sharded, 1);
    var mo = place(Vars.content.block("vg-monolith"), 196, 102, Team.sharded, 1);
    place(Vars.content.block("vg-plasma-heater"), 197, 99, Team.sharded, 1);
    mech.mantis = m; mech.monolith = mo;
    dummy(180, 128); dummy(200, 142);
    // ACU blast test: isolated corner
    for(var dx = -4; dx <= 4; dx += 2) for(var dy = -4; dy <= 4; dy += 2){
        if(dx == 0 && dy == 0) continue;
        var t = Vars.world.tile(216 + dx, 150 + dy);
        if(t != null){ t.setBlock(Blocks.thoriumWall, Team.crux, 0); acuWalls.push(t.build); }
    }
    acuUnit = Vars.content.unit("vg-acu-uef").spawn(Team.sharded, 216 * 8, 150 * 8);
    // SupCom build rule test
    place(Vars.content.block("vg-core-uef"), 112, 146, Team.green, 0);
    poly = UnitTypes.poly.spawn(Team.green, 130 * 8, 152 * 8);
    // plans are added in the render phase (like player input), see the postDraw handler
    eng = Vars.content.unit("vg-engineer").spawn(Team.green, 134 * 8, 152 * 8);
    eng.addBuild(new BuildPlan(134, 155, 0, Blocks.copperWall));
}
function feedOnly(b, name){
    var it = Vars.content.item(name);
    if(b == null || !b.isValid() || it == null) return;
    for(var n = 0; n < 12 && b.acceptItem(b, it); n++) b.handleItem(b, it);
}
function wallHp(){ var s = 0; for(var i = 0; i < acuWalls.length; i++){ var w = acuWalls[i]; s += (w != null && w.isValid()) ? w.health : 0; } return s; }
function mechUpdate(){
    for(var i = 0; i < dummies.length; i++){
        var d = dummies[i];
        if(d.u == null || !d.u.isValid()){ d.u = UnitTypes.dagger.spawn(Team.crux, d.x, d.y); }
        d.u.set(d.x, d.y); d.u.vel.setZero(); d.u.health = d.u.maxHealth;
    }
    feedOnly(mech.mantis, "vg-magnet");
    feedOnly(mech.monolith, "vg-magnet");
    var sp = statusByName("vg-spotted"), ds = statusByName("vg-disarmed"), ns = 0, nd = 0;
    for(var j = 0; j < dummies.length; j++){
        var du = dummies[j].u;
        if(sp != null && du.hasEffect(sp)) ns++;
        if(ds != null && du.hasEffect(ds)) nd++;
    }
    mech.spottedMax = Math.max(mech.spottedMax, ns);
    mech.disarmedMax = Math.max(mech.disarmedMax, nd);
    var s35 = 0, s30 = 0;
    Groups.build.each(function(b){ if(b.team != Team.crux) return; var ts = b.timeScale(); if(Math.abs(ts - 0.35) < 0.01) s35++; if(Math.abs(ts - 0.3) < 0.01) s30++; });
    mech.empSlowMax = Math.max(mech.empSlowMax, s35); mech.monolithSlowMax = Math.max(mech.monolithSlowMax, s30);
    var t = Time.time - t0;
    if(!mech.acuKilled && t > 400){ mech.acuWallsBefore = wallHp(); acuUnit.kill(); mech.acuKilled = true; }
    if(mech.acuKilled && t > 460 && mech.acuWallsAfter < 0) mech.acuWallsAfter = wallHp();
}
function mechReport(){
    var slow35 = 0, slow30 = 0;
    Groups.build.each(function(b){
        if(b.team != Team.crux) return;
        if(Math.abs(b.timeScale - 0.35) < 0.01) slow35++;
        if(Math.abs(b.timeScale - 0.3) < 0.01) slow30++;
    });
    mech.empSlowedWalls = slow35;
    mech.monolithSlowedWalls = slow30;
    mech.monolithHeat = mech.monolith != null ? mech.monolith.heatReq : -1;
    mech.polyPlans = poly.plans.size;
    mech.polyBuilt = Vars.world.tile(130, 155).block().name;
    mech.engPlans = eng.plans.size;
    mech.engBuilt = Vars.world.tile(134, 155).block().name;
    delete mech.mantis; delete mech.monolith;
    manifest.mech = mech;
    L("mech " + JSON.stringify(mech));
}
var dbg = { magBullets: {}, magEnd: 0, directSlow: -1, duoProbe: null };
function dbgUpdate(){
    var mag = Vars.content.item("vg-magnet");
    var mt = Vars.content.block("vg-mantis").ammoTypes.get(mag), mo = Vars.content.block("vg-monolith").ammoTypes.get(mag);
    Groups.bullet.each(function(b){
        if(b.type != mt && b.type != mo) return;
        dbg.magBullets[b.id] = 1;
        if(b.time + Time.delta * 1.5 >= b.lifetime) dbg.magEnd++;
    });
    if(dbg.duoProbe == null){
        Groups.build.each(function(b){ if(dbg.duoProbe == null && b.team == Team.crux && b.block == Blocks.duo) dbg.duoProbe = b; });
        if(dbg.duoProbe != null) dbg.duoProbe.applySlowdown(0.5, 600);
    }else if(dbg.directSlow < 0){
        dbg.directSlow = dbg.duoProbe.timeScale();
    }
}
var typesLogged = false;
function logTypes(){
    if(typesLogged) return;
    var bl = null, un = null, bd = null, fb = null;
    Groups.bullet.each(function(b){ if(bl == null) bl = b; });
    Groups.unit.each(function(u){ if(un == null) un = u; });
    Groups.build.each(function(b){ if(bd == null && b.block == Blocks.duo) bd = b; if(fb == null && b.block.name == "vg-shield-emitter") fb = b; });
    if(bl == null || un == null || bd == null) return;
    typesLogged = true;
    var o = {};
    ["id", "type", "team", "x", "y", "time", "lifetime", "vel", "data"].forEach(function(k){ o["bullet." + k] = typeof bl[k]; });
    ["id", "type", "team", "x", "y", "hitSize", "plans", "health", "maxHealth"].forEach(function(k){ o["unit." + k] = typeof un[k]; });
    ["block", "team", "timeScale", "efficiency", "x", "y", "health", "tile"].forEach(function(k){ o["build." + k] = typeof bd[k]; });
    if(fb != null) ["hit", "broken", "buildup"].forEach(function(k){ o["force." + k] = typeof fb[k]; });
    var tds = Vars.state.teams.present.get(0);
    ["cores", "team"].forEach(function(k){ o["teamdata." + k] = typeof tds[k]; });
    L("types " + JSON.stringify(o));
}
var polyTrace = [];
function polyDbg(){
    if(poly == null || polyTrace.length >= 12) return;
    var t = Vars.world.tile(130, 155);
    polyTrace.push(poly.plans.size + ":" + t.block().name + (t.build != null && t.build.progress !== undefined ? "@" + Math.round(t.build.progress * 100) : ""));
    if(polyTrace.length == 12){
        var names = [];
        Vars.state.teams.get(Team.green).cores.each(function(c){ names.push(String(c.block.name)); });
        L("poly trace " + polyTrace.join(" ") + " | sharded cores: " + names.join(","));
    }
}
function finish(){
    if(done) return;
    done = true;
    manifest.probes = probes;
    try{ mechReport(); }catch(e){ E("mechReport: " + e); }
    L("dbg magBullets=" + Object.keys(dbg.magBullets).length + " magEnd=" + dbg.magEnd + " directSlow=" + dbg.directSlow);
    try{ OUT.child("manifest.json").writeString(JSON.stringify(manifest, null, 1)); }catch(e){ Log.err(e); }
    L("finished, errors: " + manifest.errors.length);
    Time.run(5, function(){ Core.app.exit(); });
}

Events.on(ClientLoadEvent, function(){
    OUT.mkdirs();
    Time.run(30, setup);
});

Events.run(Trigger.update, function(){
    if(t0 < 0 || done) return;
    try{
        if(Vars.control.input.panning !== undefined) Vars.control.input.panning = true;
        if(++feedTick >= 15){ feedTick = 0; feed(); }
        mechUpdate();
        dbgUpdate();
        logTypes();
        polyDbg();
        if(Time.time - t0 > 200 && ++waveTick >= 240){ waveTick = 0; spawnEnemies(); buildTargets(); probe(); }
        if(shotIdx >= shots.length){ finish(); return; }
        var s = shots[shotIdx];
        Core.camera.position.set(s.cx * 8, s.cy * 8);
        Vars.renderer.setScale(s.scale);
        if(armedFrame < 0 && Time.time >= s.at) armedFrame = Core.graphics.getFrameId() + 2;
    }catch(e){ E("update: " + e); finish(); }
});

var polyPending = true;
Events.run(Trigger.postDraw, function(){
    if(polyPending && poly != null && Time.time - t0 > 120){ polyPending = false; polyTrace = []; poly.addBuild(new BuildPlan(130, 155, 0, Blocks.copperWall)); }
    if(armedFrame < 0 || done || Core.graphics.getFrameId() < armedFrame) return;
    var s = shots[shotIdx];
    try{
        ScreenUtils.saveScreenshot(OUT.child(s.name + ".png"));
        manifest.shots.push({ name: s.name, cx: s.cx, cy: s.cy, scale: s.scale, w: Core.graphics.getWidth(), h: Core.graphics.getHeight(), t: Time.time - t0 });
    }catch(e){ E("screenshot " + s.name + ": " + e); }
    shotIdx++;
    armedFrame = -1;
});
