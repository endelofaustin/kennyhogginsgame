"""Rendering and race simulation for standalone Ultra Super Kart."""
import math
import random
import pyglet
from engineglobals import EngineGlobals
from super_ultra_content import DRIVERS, TRACKS


class Rival:
    def __init__(self, driver, lane, distance, speed, seed):
        self.driver, self.lane, self.distance, self.speed = driver, float(lane), float(distance), float(speed)
        self.base_speed, self.lap, self.finished = float(speed), 0, False
        self.wobble, self.boost, self.hit = random.Random(seed).random()*math.tau, 0.0, 0.0


class SuperUltraRaceMixin:
    def _selected(self): return DRIVERS[self.selected_driver]
    def _physics(self):
        d=self._selected(); return {"max":(8.2+d["speed"]*.22)*self.track_def["max_speed"],"boost":(10.8+d["boost"]*.22)*self.track_def["max_speed"],"over":(12.6+d["speed"]*.2+d["boost"]*.12)*self.track_def["max_speed"],"acc":.105+d["accel"]*.014,"brake":.17+d["accel"]*.009,"steer":(.018+d["handling"]*.0032)*self.track_def["grip"],"drift":(.031+d["handling"]*.004)*self.track_def["grip"],"weight":d["weight"]}
    def _track_data(self):
        self.track_def=TRACKS[self.selected_track]; self.track=[]; i=0
        for n,c,h in self.track_def["sections"]:
            for _ in range(n): self.track.append({"curve":c,"hill":h,"boost":i in self.track_def["boosts"],"ramp":i in self.track_def["ramps"],"hazard":i in self.track_def["hazards"],"energy":i in self.track_def["energy"],"side":-1 if i%19==0 else (1 if i%19==9 else 0)}); i+=1
        self.track_length=len(self.track)*self.SEGMENT_LENGTH
    def _seg(self,d): return self.track[int(d//self.SEGMENT_LENGTH)%len(self.track)]
    def _tri(self,color):
        t=pyglet.shapes.Triangle(-900,-900,-900,-900,-900,-900,color=color,batch=self.batch,group=self.roadg); self.race_items.append(t); return t
    @staticmethod
    def _settri(t,a,b,c): t.x,t.y=a; t.x2,t.y2=b; t.x3,t.y3=c
    def _scene(self):
        w,h=EngineGlobals.width,EngineGlobals.height; th=self.track_def["theme"]; hz=int(h*.455)
        for i in range(10):
            r=pyglet.shapes.Rectangle(0,hz+i*(h-hz)/10,w,(h-hz)/10+2,color=self._mix(th["sky_bottom"],th["sky_top"],i/9),batch=self.batch,group=self.bg); self.race_items.append(r)
        self.race_items.append(pyglet.shapes.Rectangle(0,0,w,hz+5,color=th["ground"],batch=self.batch,group=self.bg))
        for i in range(9):
            bw=45+(i%3)*18; bh=55+(i*37+self.selected_track*11)%145; b=pyglet.shapes.Rectangle(i*94-15,hz,bw,bh,color=self._dark(th["sky_bottom"],35),batch=self.batch,group=self.world); self.race_items.append(b)
        fog=pyglet.shapes.Rectangle(0,hz-16,w,58,color=th["fog"],batch=self.batch,group=self.world); fog.opacity=70; self.race_items.append(fog)
        self.road_pool=[]
        for i in range(self.DRAW_SEGMENTS):
            road=self._dark(th["road"],5 if i%2 else 0); edge=th["edge"] if i%2==0 else self._dark(th["edge"],35); grass=self._dark(th["ground"],8 if i%2 else 0)
            tris=tuple(self._tri(c) for c in (grass,grass,grass,grass,road,road,edge,edge,edge,edge))
            lane=pyglet.shapes.Rectangle(-900,-900,1,1,color=(225,230,238),batch=self.batch,group=self.fx); boost=pyglet.shapes.Rectangle(-900,-900,1,1,color=th["accent"],batch=self.batch,group=self.fx); ramp=pyglet.shapes.Rectangle(-900,-900,1,1,color=(232,170,70),batch=self.batch,group=self.fx); hazard=pyglet.shapes.Circle(-900,-900,1,color=(35,27,38),batch=self.batch,group=self.fx); energy=pyglet.shapes.Circle(-900,-900,1,color=(88,246,210),batch=self.batch,group=self.fx); prop=pyglet.shapes.Rectangle(-900,-900,1,1,color=self._dark(th["ground"],25),batch=self.batch,group=self.world)
            lane.opacity=150; boost.opacity=170; self.race_items += [lane,boost,ramp,hazard,energy,prop]; self.road_pool.append((tris,lane,boost,ramp,hazard,energy,prop))
    def _player_kart(self):
        cx=EngineGlobals.width/2; c=self._selected()["color"]
        sh=pyglet.shapes.Ellipse(cx,61,82,20,color=(4,5,9),batch=self.batch,group=self.carg); sh.opacity=150
        rear=pyglet.shapes.Rectangle(cx-61,61,122,34,color=(24,29,40),batch=self.batch,group=self.carg); body=pyglet.shapes.Rectangle(cx-47,72,94,47,color=c,batch=self.batch,group=self.carg); gloss=pyglet.shapes.Rectangle(cx-38,98,76,9,color=self._light(c,55),batch=self.batch,group=self.carg); gloss.opacity=160; nose=pyglet.shapes.Triangle(cx-45,78,cx+45,78,cx,144,color=self._light(c,20),batch=self.batch,group=self.carg); cockpit=pyglet.shapes.Ellipse(cx,103,27,19,color=(43,65,86),batch=self.batch,group=self.carg)
        self.player_shapes=[sh,rear,body,gloss,nose,cockpit]; self.race_items += self.player_shapes
        for ox in (-55,-31,31,55):
            wh=pyglet.shapes.Circle(cx+ox,66,11,color=(9,11,15),batch=self.batch,group=self.carg); self.player_shapes.append(wh); self.race_items.append(wh)
        self.flames=[]
        for ox in (-15,15):
            f=pyglet.shapes.Triangle(cx+ox-7,61,cx+ox+7,61,cx+ox,30,color=(75,231,255),batch=self.batch,group=self.fx); f.visible=False; self.flames.append(f); self.race_items.append(f)
        self.player_base=[]
        for s in self.player_shapes+self.flames:
            if isinstance(s,pyglet.shapes.Triangle): self.player_base.append((s,(s.x,s.y,s.x2,s.y2,s.x3,s.y3)))
            else: self.player_base.append((s,(getattr(s,"x",0),getattr(s,"y",0))))
    def _rival_setup(self):
        pool=[d for i,d in enumerate(DRIVERS) if i!=self.selected_driver]; self.rng.shuffle(pool); lanes=(-.78,-.26,.26,.78)
        for i,d in enumerate(pool[:11]):
            r=Rival(d,lanes[i%4],115+(i//4)*82+(i%4)*12,7+d["speed"]*.22+(i%3)*.06,900+i); self.rivals.append(r)
            sh=pyglet.shapes.Ellipse(-900,-900,20,7,color=(3,4,8),batch=self.batch,group=self.world); b=pyglet.shapes.Rectangle(-900,-900,28,16,color=d["color"],batch=self.batch,group=self.fx); g=pyglet.shapes.Rectangle(-900,-900,20,4,color=self._light(d["color"],50),batch=self.batch,group=self.fx); h=pyglet.shapes.Circle(-900,-900,5,color=d["color"],batch=self.batch,group=self.fx); self.rival_items.append((sh,b,g,h))
    def _hud(self):
        w,h=EngineGlobals.width,EngineGlobals.height
        glass=pyglet.shapes.BorderedRectangle(10,h-83,250,69,border=2,color=(8,14,29),border_color=(80,105,139),batch=self.batch,group=self.ui); glass.opacity=215; self.race_items.append(glass)
        self.ebg=pyglet.shapes.Rectangle(22,h-72,210,10,color=(31,37,50),batch=self.batch,group=self.ui); self.ebar=pyglet.shapes.Rectangle(22,h-72,210,10,color=(79,237,199),batch=self.batch,group=self.ui); self.race_items += [self.ebg,self.ebar]
        def lab(t,x,y,size=10,ax="left",col=(255,255,255,255),bold=False):
            l=pyglet.text.Label(t,x=x,y=y,anchor_x=ax,font_size=size,weight=pyglet.text.Weight.BOLD if bold else pyglet.text.Weight.NORMAL,color=col,batch=self.batch,group=self.ui); self.race_items.append(l); return l
        self.tracklab=lab(self.track_def["name"].upper(),w//2,h-25,12,"center",bold=True); self.laplab=lab("LAP 1/3",20,h-36,12,bold=True); self.placelab=lab("PLACE 12/12",20,h-56,11,col=(255,196,227,255)); self.speedlab=lab("0 KM/H",w-18,28,18,"right",bold=True); self.msglab=lab("",w-18,54,11,"right",(95,235,255,255),True); lab("↑ accelerate  ↓ brake  ←→ steer  SPACE drift  SHIFT overdrive  ESC pause",w//2,12,8,"center",(184,201,226,255))
        self.countlab=lab("3",w//2,h//2+70,78,"center",(255,242,148,255),True)
        self.pausebox=pyglet.shapes.BorderedRectangle(220,185,360,215,border=2,color=(10,16,31),border_color=(88,228,255),batch=self.batch,group=self.ui); self.pausebox.opacity=240; self.pausebox.visible=False; self.race_items.append(self.pausebox)
        self.pauselab=lab("PAUSED",w//2,350,30,"center",bold=True); self.pauseprompt=lab("ESC resume   •   Q Ultra menu",w//2,275,11,"center",(192,214,240,255)); self.pauselab.visible=self.pauseprompt.visible=False
        self.finishbox=pyglet.shapes.BorderedRectangle(145,145,510,300,border=2,color=(10,16,31),border_color=(255,105,199),batch=self.batch,group=self.ui); self.finishbox.opacity=242; self.finishbox.visible=False; self.race_items.append(self.finishbox)
        self.fintitle=lab("",w//2,385,30,"center",(255,246,174,255),True); self.finresult=lab("",w//2,325,16,"center"); self.findetail=lab("",w//2,285,10,"center",(127,228,255,255)); self.finprompt=lab("",w//2,215,11,"center",(213,222,239,255))
        for x in (self.fintitle,self.finresult,self.findetail,self.finprompt): x.visible=False
        for _ in range(40):
            s=pyglet.shapes.Circle(-900,-900,2,color=(160,210,235),batch=self.batch,group=self.fx); s.visible=False; self.particles.append({"s":s,"vx":0.,"vy":0.,"life":0.,"max":1.}); self.race_items.append(s)
    def _start_race(self):
        self._clear_menu(); self._clear_race(); self._track_data(); self._scene(); self._rival_setup(); self._player_kart(); self._hud(); self.state=self.COUNTDOWN
        self.distance=self.speed=self.player_lane=0.; self.lap=0; self.energy=100.; self.boost=self.hit=self.cooldown=self.hop=self.drift_charge=self.msg_timer=0.; self.overdrive=self.drifting=False; self.countdown=180.; self.race_time=0.; self.keys.clear()
    def _project(self):
        w,h=float(EngineGlobals.width),float(EngineGlobals.height); hz=h*.455; centers=[]; widths=[]; ys=[]; ca=ha=0.
        for i in range(self.DRAW_SEGMENTS+1):
            t=i/self.DRAW_SEGMENTS; p=t**1.62; seg=self._seg(self.distance+(self.DRAW_SEGMENTS-i)*self.SEGMENT_LENGTH); ca+=seg["curve"]*(.48+p*2.4); ha+=seg["hill"]*(.18+p*.95); ys.append(hz+p*(h-hz+56)+ha*110*p); widths.append(18+p*405); centers.append(w*.5-self.player_lane*255*p+ca*455*p)
        for i,(tris,lane,boost,ramp,hazard,energy,prop) in enumerate(self.road_pool):
            c1,c2=centers[i],centers[i+1]; r1,r2=widths[i],widths[i+1]; y1,y2=ys[i],ys[i+1]; l1,rr1,l2,rr2=c1-r1,c1+r1,c2-r2,c2+r2; e1,e2=max(2.5,r1*.055),max(3,r2*.055); a,b,c,d,ro1,ro2,el1,el2,er1,er2=tris
            self._settri(a,(0,y1),(l1,y1),(0,y2)); self._settri(b,(0,y2),(l1,y1),(l2,y2)); self._settri(c,(rr1,y1),(w,y1),(rr2,y2)); self._settri(d,(w,y1),(w,y2),(rr2,y2)); self._settri(ro1,(l1,y1),(rr1,y1),(l2,y2)); self._settri(ro2,(rr1,y1),(rr2,y2),(l2,y2)); self._settri(el1,(l1,y1),(l1+e1,y1),(l2,y2)); self._settri(el2,(l1+e1,y1),(l2+e2,y2),(l2,y2)); self._settri(er1,(rr1-e1,y1),(rr1,y1),(rr2-e2,y2)); self._settri(er2,(rr1,y1),(rr2,y2),(rr2-e2,y2))
            seg=self._seg(self.distance+(self.DRAW_SEGMENTS-i)*self.SEGMENT_LENGTH); p=max(.03,min(1,(i+1)/self.DRAW_SEGMENTS)); sc=p**1.55
            lane.visible=i%5==0 and i>3
            if lane.visible: lane.width=max(1,5*sc); lane.height=max(1,13*sc); lane.x=c2-lane.width/2; lane.y=y2
            boost.visible=seg["boost"]; ramp.visible=seg["ramp"]; hazard.visible=seg["hazard"]; energy.visible=seg["energy"]; prop.visible=bool(seg["side"])
            if boost.visible: boost.width=max(4,r2*.82); boost.height=max(2,12*sc); boost.x=c2-boost.width/2; boost.y=y2
            if ramp.visible: ramp.width=max(4,r2*.62); ramp.height=max(2,22*sc); ramp.x=c2-ramp.width/2; ramp.y=y2
            if hazard.visible: hazard.radius=max(2,22*sc); hazard.position=(c2+r2*.18,y2)
            if energy.visible: energy.radius=max(2,11*sc); energy.position=(c2-r2*.15,y2+4)
            if prop.visible: prop.width=max(3,24*sc); prop.height=max(6,85*sc); prop.x=c2+seg["side"]*(r2+38*sc); prop.y=y2
        return centers,widths,ys
    def _rival_visuals(self,c,w,y):
        md=self.DRAW_SEGMENTS*self.SEGMENT_LENGTH
        for bundle,r in zip(self.rival_items,self.rivals):
            rel=(r.distance-self.distance)%self.track_length
            if rel<=18 or rel>=md:
                for q in bundle:q.visible=False
                continue
            idx=int(max(0,min(1,(md-rel)/md))*(self.DRAW_SEGMENTS-1)); p=(idx+1)/self.DRAW_SEGMENTS; sc=max(.13,p**1.4); x=c[idx]+r.lane*w[idx]*.70; yy=y[idx]
            sh,b,g,hd=bundle
            for q in bundle:q.visible=True
            sh.width=38*sc; sh.height=10*sc; sh.position=(x,yy+2); b.width=38*sc; b.height=19*sc; b.position=(x-b.width/2,yy+4); g.width=24*sc; g.height=max(1,5*sc); g.position=(x-g.width/2,yy+15*sc); hd.radius=max(2,6*sc); hd.position=(x,yy+20*sc)
    def _emit(self,x,y,color):
        for p in self.particles:
            if p["life"]<=0:
                p["s"].visible=True; p["s"].position=(x,y); p["s"].radius=self.rng.choice((2,3,4)); p["s"].color=color; p["s"].opacity=220; p["vx"]=self.rng.uniform(-.6,.6); p["vy"]=self.rng.uniform(-1.8,.6); p["life"]=p["max"]=self.rng.uniform(14,28); return
    def _particles(self,dt):
        for p in self.particles:
            if p["life"]<=0: continue
            p["life"]-=dt; p["s"].x+=p["vx"]*dt; p["s"].y+=p["vy"]*dt; p["s"].opacity=max(0,int(220*p["life"]/p["max"])); p["vx"]*=.985**dt; p["vy"]*=.98**dt
            if p["life"]<=0:p["s"].visible=False
    def _kart_visual(self):
        hop=math.sin(max(0,min(math.pi,(1-self.hop/46)*math.pi)))*18 if self.hop>0 else 0; lean=self.steer_vis*8
        for s,b in self.player_base:
            if isinstance(s,pyglet.shapes.Triangle): s.x=b[0]+lean;s.y=b[1]+hop;s.x2=b[2]+lean;s.y2=b[3]+hop;s.x3=b[4]+lean;s.y3=b[5]+hop
            else:
                try:s.x=b[0]+lean;s.y=b[1]+hop
                except Exception:pass
        fire=self.boost>0 or self.overdrive
        for f in self.flames:f.visible=fire
        if (fire and self.rng.random()<.42) or (self.drifting and self.rng.random()<.25): self._emit(EngineGlobals.width/2+lean+self.rng.uniform(-45,45),60+hop,self.track_def["theme"]["accent"] if fire else (178,188,198))
    def _msg(self,text,t=45): self.msglab.text=text; self.msg_timer=max(self.msg_timer,t)
    def _axis(self):
        k=pyglet.window.key; s=(-1 if k.LEFT in self.keys or k.A in self.keys else 0)+(1 if k.RIGHT in self.keys or k.D in self.keys else 0); ax=float(self.axes.get("x",0)); return max(-1,min(1,ax if abs(ax)>.18 else s))
    def _player(self,dt):
        p=self._physics(); k=pyglet.window.key; up=k.UP in self.keys or k.W in self.keys or 0 in self.buttons; down=k.DOWN in self.keys or k.S in self.keys or 1 in self.buttons; drift=k.SPACE in self.keys or 2 in self.buttons; od=k.LSHIFT in self.keys or k.RSHIFT in self.keys or 3 in self.buttons; steer=self._axis(); self.steer_vis+=(steer-self.steer_vis)*min(1,.12*dt)
        self.speed += (p["acc"] if up else (-p["brake"] if down else 0))*dt
        if not up and not down:self.speed*=.982**dt
        self.overdrive=bool(od and self.lap>=1 and self.energy>5 and self.hit<=0)
        mx=p["max"]
        if self.boost>0:self.boost-=dt;mx=max(mx,p["boost"]);self.speed+=.025*dt
        if self.overdrive:self.energy=max(0,self.energy-.12*dt);self.speed+=.035*dt;mx=max(mx,p["over"]);self._msg("OVERDRIVE — ENERGY BURN",5)
        self.speed=max(-2.2,min(mx,self.speed)); self.drifting=bool(drift and abs(steer)>.15 and abs(self.speed)>2.8); rate=p["drift"] if self.drifting else p["steer"]
        if abs(steer)>.05 and abs(self.speed)>.2:self.player_lane+=steer*rate*(.52+abs(self.speed)/max(8,p["max"]))*dt
        if self.drifting:self.drift_charge=min(100,self.drift_charge+(.55)*dt)
        elif self.drift_charge>0:
            if self.drift_charge>=70:self.boost=max(self.boost,64);self._msg("ULTRA DRIFT TURBO!",52)
            elif self.drift_charge>=35:self.boost=max(self.boost,36);self._msg("DRIFT BOOST!",38)
            self.drift_charge=0
        self.player_lane-=self._seg(self.distance+90)["curve"]*max(0,self.speed)*(.24-self._selected()["handling"]*.008)*dt
        if abs(self.player_lane)>1.02:self.speed*=.89**dt;self.energy=max(0,self.energy-.018*dt)
        self.player_lane=max(-1.38,min(1.38,self.player_lane)); self.hop=max(0,self.hop-dt); self.hit=max(0,self.hit-dt); self.cooldown=max(0,self.cooldown-dt)
        if self.msg_timer>0:self.msg_timer-=dt
        elif hasattr(self,"msglab"):self.msglab.text=""
        self.distance+=self.speed*dt
        while self.distance>=self.track_length:
            self.distance-=self.track_length;self.lap+=1;self.energy=min(100,self.energy+8)
            if self.lap>=3:self._finish();return
        while self.distance<0:self.distance+=self.track_length
        if self.cooldown<=0:
            seg=self._seg(self.distance+10)
            if seg["boost"] and abs(self.player_lane)<.82:self.boost=max(self.boost,55);self._msg("NEON BOOST!",38);self.cooldown=18
            elif seg["ramp"] and abs(self.player_lane)<.88:self.hop=46;self.boost=max(self.boost,22);self._msg("BIG AIR!",44);self.cooldown=35
            elif seg["hazard"] and abs(self.player_lane-.18)<.34:self.speed*=.67;self.energy=max(0,self.energy-7);self.player_lane+=self.rng.choice((-.3,.3));self.hit=40;self._msg("HARD HIT!  ENERGY -7",48);self.cooldown=40
            elif seg["energy"] and abs(self.player_lane+.15)<.34:self.energy=min(100,self.energy+16);self._msg("ENERGY RING +16",42);self.cooldown=40
        for r in self.rivals:
            if self.hit<=0 and (r.distance-self.distance)%self.track_length<33 and abs(r.lane-self.player_lane)<.23:self.speed*=.76;self.energy=max(0,self.energy-3);self.player_lane+=-.16 if r.lane>self.player_lane else .16;r.speed*=.82;r.hit=28;self.hit=24;self._msg("KART CONTACT!",28);break
    def _ai(self,dt):
        for r in self.rivals:
            if r.finished:continue
            seg=self._seg(r.distance); target=r.base_speed*self.track_def["max_speed"]*(1-min(1,abs(seg["curve"])*14)*.13); gap=(self.lap-r.lap)*self.track_length+self.distance-r.distance
            if gap>850:target+=min(.9,gap/2300)
            elif gap<-950:target-=min(.5,abs(gap)/4300)
            if seg["boost"]:r.boost=max(r.boost,26)
            if r.boost>0:r.boost-=dt;target+=.85
            if r.hit>0:r.hit-=dt;target*=.91
            r.speed+=(target-r.speed)*min(1,.038*dt);r.wobble+=.012*dt;r.lane+=math.sin(r.wobble)*.0018*dt-seg["curve"]*.62*dt;r.lane=max(-.88,min(.88,r.lane));r.distance+=max(0,r.speed)*dt
            while r.distance>=self.track_length:r.distance-=self.track_length;r.lap+=1;r.finished=r.lap>=3
    def _place(self):
        p=self.lap*self.track_length+self.distance; return min(12,1+sum(1 for r in self.rivals if r.finished or r.lap*self.track_length+r.distance>p))
    def _finish(self):
        self.state=self.FINISH;self.speed=0;place=self._place();self.finishbox.visible=True
        for x in (self.fintitle,self.finresult,self.findetail,self.finprompt):x.visible=True
        self.fintitle.text="ULTRA FINISH!";self.finresult.text=f"{self._selected()['name']} finished {place} of 12";self.findetail.text=f"{self.track_def['name']}  •  {self.race_time/60:.1f}s  •  energy {int(self.energy)}%";self.finprompt.text="ENTER next/rematch   •   ESC Ultra menu"
