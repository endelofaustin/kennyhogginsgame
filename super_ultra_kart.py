"""Standalone cinematic Ultra Super Kart. Does not patch Mode 7/N64 modes."""
from __future__ import annotations
import math, random
import pyglet
from engineglobals import EngineGlobals
from super_ultra_content import CUPS, DRIVERS, TRACKS
from super_ultra_race import SuperUltraRaceMixin


class SuperUltraKart(SuperUltraRaceMixin):
    HOME, DRIVER, TRACK, CUP, COUNTDOWN, RACE, PAUSE, FINISH = "home driver track cup countdown race pause finish".split()
    SEGMENT_LENGTH, DRAW_SEGMENTS, TOTAL_LAPS, TOTAL_RACERS = 48.0, 64, 3, 12

    def __init__(self, on_exit_to_menu=None):
        self.on_exit_to_menu, self.active, self.state, self.mode = on_exit_to_menu, False, self.HOME, "quick"
        self.selected_home = self.selected_driver = self.selected_track = self.selected_cup = self.gp_race = 0
        self.keys, self.buttons, self.axes, self.controllers = set(), set(), {}, []
        self.nav_wait, self.mounted = 0.0, False
        self.rng = random.Random(1997)
        self.batch = pyglet.graphics.Batch()
        self.bg = pyglet.graphics.Group(0); self.world = pyglet.graphics.Group(1); self.roadg = pyglet.graphics.Group(2)
        self.fx = pyglet.graphics.Group(3); self.carg = pyglet.graphics.Group(4); self.ui = pyglet.graphics.Group(5)
        self.menu_items, self.race_items, self.rival_items, self.particles = [], [], [], []
        self.track, self.rivals, self.road_pool = [], [], []
        self.track_def, self.track_length = TRACKS[0], 1.0
        self.distance = self.speed = self.player_lane = 0.0; self.lap = 0; self.energy = 100.0
        self.boost = self.hit = self.cooldown = self.hop = self.drift_charge = self.msg_timer = 0.0
        self.overdrive = self.drifting = False; self.countdown = 180.0; self.race_time = 0.0; self.steer_vis = 0.0
        self._build_home()

    @staticmethod
    def _mix(a,b,t):
        t=max(0,min(1,t)); return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
    @staticmethod
    def _light(c,n): return tuple(min(255,int(x+n)) for x in c)
    @staticmethod
    def _dark(c,n): return tuple(max(0,int(x-n)) for x in c)
    def _delete(self, items):
        for x in items:
            try: x.delete()
            except Exception: pass
        items.clear()
    def _clear_menu(self): self._delete(self.menu_items)
    def _clear_race(self):
        self._delete(self.race_items)
        for bundle in self.rival_items:
            for x in bundle:
                try: x.delete()
                except Exception: pass
        self.rival_items.clear(); self.rivals.clear()
        for p in self.particles:
            try: p["s"].delete()
            except Exception: pass
        self.particles.clear()

    def _clock(self, dt): self.update(float(dt)*60.0)
    def attach_controllers(self):
        if self.controllers: return
        try:
            for j in pyglet.input.get_joysticks():
                try: j.open(); j.push_handlers(self); self.controllers.append(j)
                except Exception: pass
        except Exception: pass
    def start(self):
        self.active=True; self.keys.clear(); self.buttons.clear(); self.attach_controllers(); self._clear_race(); self._build_home()
        if not self.mounted:
            EngineGlobals.window.push_handlers(self); pyglet.clock.schedule_interval(self._clock,1/60.0); self.mounted=True
    def stop(self):
        self.active=False; self.keys.clear(); self.buttons.clear(); self._clear_menu(); self._clear_race()
        if self.mounted:
            pyglet.clock.unschedule(self._clock)
            try: EngineGlobals.window.remove_handlers(self)
            except Exception: pass
            self.mounted=False

    def _space_bg(self):
        w,h=EngineGlobals.width,EngineGlobals.height
        for i in range(10):
            r=pyglet.shapes.Rectangle(0,i*h/10,w,h/10+2,color=self._mix((43,24,76),(5,8,28),i/9),batch=self.batch,group=self.bg); self.menu_items.append(r)
        r=random.Random(741)
        for _ in range(55):
            s=pyglet.shapes.Circle(r.randrange(w),r.randrange(70,h),r.choice((1,1,2)),color=r.choice(((155,194,255),(255,255,255),(229,144,255))),batch=self.batch,group=self.world); s.opacity=r.randrange(100,255); self.menu_items.append(s)
        p=pyglet.shapes.Circle(w-105,h-112,68,color=(77,91,160),batch=self.batch,group=self.world); p.opacity=215; self.menu_items.append(p)
    def _label(self,text,x,y,size=12,color=(255,255,255,255),bold=False):
        l=pyglet.text.Label(text,x=x,y=y,anchor_x="center",font_size=size,weight=pyglet.text.Weight.BOLD if bold else pyglet.text.Weight.NORMAL,color=color,batch=self.batch,group=self.ui); self.menu_items.append(l); return l
    def _panel(self,x,y,w,h,sel=False):
        p=pyglet.shapes.BorderedRectangle(x,y,w,h,border=2,color=(31,42,72) if sel else (16,24,47),border_color=(91,232,255) if sel else (66,79,112),batch=self.batch,group=self.world); p.opacity=240; self.menu_items.append(p); return p
    def _head(self,subtitle):
        self._label("ULTRA SUPER KART",EngineGlobals.width//2,EngineGlobals.height-66,34,(247,249,255,255),True)
        self._label(subtitle,EngineGlobals.width//2,EngineGlobals.height-96,11,(103,232,255,255),True)
    def _foot(self,text="ARROWS / STICK choose   •   ENTER / A confirm   •   ESC / B back"): self._label(text,EngineGlobals.width//2,26,9,(190,207,235,255))
    def _build_home(self):
        self._clear_menu(); self.state=self.HOME; self._space_bg(); self._head("CINEMATIC CHAMPIONSHIP EDITION")
        self.home_panels=[]
        for i,t in enumerate(("QUICK RACE","GRAND PRIX — 10 CUPS","BACK TO KENNY HOGGINS")):
            y=352-i*86; self.home_panels.append(self._panel(205,y,390,60,i==self.selected_home)); self._label(t,400,y+29,17,bold=True)
        self._label("50 TRACKS  •  24 DRIVERS  •  12 RACERS  •  OVERDRIVE",400,112,10,(255,178,229,255),True); self._foot()
    def _refresh_home(self): self._build_home()
    def _build_driver(self):
        self._clear_menu(); self.state=self.DRIVER; self._space_bg(); self._head("SELECT DRIVER — 24 RACERS")
        for i,d in enumerate(DRIVERS):
            row,col=divmod(i,6); x=31+col*126; y=392-row*92; self._panel(x,y,112,76,i==self.selected_driver)
            c=pyglet.shapes.Circle(x+56,y+46,17,color=d["color"],batch=self.batch,group=self.fx); self.menu_items.append(c); self._label(d["name"].upper(),x+56,y+14,7,bold=True)
        d=DRIVERS[self.selected_driver]; self._label(f"{d['name'].upper()}   SPD {d['speed']}   ACC {d['accel']}   HANDLE {d['handling']}   BOOST {d['boost']}   WEIGHT {d['weight']}",400,83,10,(105,235,255,255),True); self._foot()
    def _build_track_menu(self):
        self._clear_menu(); self.state=self.TRACK; self._space_bg(); self._head("SELECT TRACK — 50 CINEMATIC CIRCUITS")
        page=self.selected_track//10; start=page*10
        for slot in range(10):
            i=start+slot
            if i>=50: break
            tr=TRACKS[i]; col,row=slot%2,slot//2; x=52+col*374; y=394-row*70; self._panel(x,y,322,54,i==self.selected_track)
            self._label(f"{i+1:02d}  {tr['name'].upper()}",x+161,y+32,9,bold=True); self._label(tr["tagline"],x+161,y+12,7,(187,205,233,255))
        self._label(f"PAGE {page+1}/5   •   {TRACKS[self.selected_track]['cup']}",400,69,10,(255,177,228,255),True); self._foot("ARROWS choose   •   PAGE UP/DOWN jump page   •   ENTER race   •   ESC back")
    def _build_cup(self):
        self._clear_menu(); self.state=self.CUP; self._space_bg(); self._head("GRAND PRIX — FIVE RACES PER CUP")
        for i,cup in enumerate(CUPS):
            col,row=i%2,i//2; x=76+col*362; y=393-row*69; self._panel(x,y,286,52,i==self.selected_cup); self._label(cup,x+143,y+28,13,bold=True)
        self._foot()
    def _back_menu(self):
        if self.state==self.HOME:
            self.stop(); self.on_exit_to_menu and self.on_exit_to_menu()
        elif self.state==self.DRIVER: self._build_home()
        else: self._build_driver()

    def on_key_press(self,symbol,modifiers):
        if not self.active:return pyglet.event.EVENT_UNHANDLED
        k=pyglet.window.key
        if self.state==self.HOME:
            if symbol in (k.UP,k.LEFT):self.selected_home=(self.selected_home-1)%3;self._refresh_home()
            elif symbol in (k.DOWN,k.RIGHT):self.selected_home=(self.selected_home+1)%3;self._refresh_home()
            elif symbol in (k.ENTER,k.RETURN):
                if self.selected_home==2:self._back_menu()
                else:self.mode="quick" if self.selected_home==0 else "grand_prix";self._build_driver()
            elif symbol==k.ESCAPE:self._back_menu()
            return pyglet.event.EVENT_HANDLED
        if self.state==self.DRIVER:
            if symbol==k.LEFT:self.selected_driver=(self.selected_driver-1)%24
            elif symbol==k.RIGHT:self.selected_driver=(self.selected_driver+1)%24
            elif symbol==k.UP:self.selected_driver=(self.selected_driver-6)%24
            elif symbol==k.DOWN:self.selected_driver=(self.selected_driver+6)%24
            elif symbol in (k.ENTER,k.RETURN):self._build_cup() if self.mode=="grand_prix" else self._build_track_menu();return pyglet.event.EVENT_HANDLED
            elif symbol==k.ESCAPE:self._back_menu();return pyglet.event.EVENT_HANDLED
            self._build_driver();return pyglet.event.EVENT_HANDLED
        if self.state==self.TRACK:
            if symbol==k.LEFT:self.selected_track=(self.selected_track-1)%50
            elif symbol==k.RIGHT:self.selected_track=(self.selected_track+1)%50
            elif symbol==k.UP:self.selected_track=(self.selected_track-2)%50
            elif symbol==k.DOWN:self.selected_track=(self.selected_track+2)%50
            elif symbol==k.PAGEUP:self.selected_track=(self.selected_track-10)%50
            elif symbol==k.PAGEDOWN:self.selected_track=(self.selected_track+10)%50
            elif symbol in (k.ENTER,k.RETURN):self._start_race();return pyglet.event.EVENT_HANDLED
            elif symbol==k.ESCAPE:self._back_menu();return pyglet.event.EVENT_HANDLED
            self._build_track_menu();return pyglet.event.EVENT_HANDLED
        if self.state==self.CUP:
            if symbol in (k.LEFT,k.UP):self.selected_cup=(self.selected_cup-1)%10
            elif symbol in (k.RIGHT,k.DOWN):self.selected_cup=(self.selected_cup+1)%10
            elif symbol in (k.ENTER,k.RETURN):self.gp_race=0;self.selected_track=self.selected_cup*5;self._start_race();return pyglet.event.EVENT_HANDLED
            elif symbol==k.ESCAPE:self._back_menu();return pyglet.event.EVENT_HANDLED
            self._build_cup();return pyglet.event.EVENT_HANDLED
        if self.state==self.PAUSE:
            if symbol in (k.ESCAPE,k.ENTER,k.RETURN):self.state=self.RACE;self.pausebox.visible=False;self.pauselab.visible=self.pauseprompt.visible=False
            elif symbol==k.Q:self._clear_race();self._build_home()
            return pyglet.event.EVENT_HANDLED
        if self.state==self.FINISH:
            if symbol in (k.ENTER,k.RETURN):
                if self.mode=="grand_prix" and self.gp_race<4:self.gp_race+=1;self.selected_track=self.selected_cup*5+self.gp_race;self._start_race()
                elif self.mode=="grand_prix":self.gp_race=0;self._clear_race();self._build_home()
                else:self._start_race()
            elif symbol==k.ESCAPE:self._clear_race();self._build_home()
            return pyglet.event.EVENT_HANDLED
        if symbol==k.ESCAPE:self.state=self.PAUSE;self.pausebox.visible=True;self.pauselab.visible=self.pauseprompt.visible=True;return pyglet.event.EVENT_HANDLED
        self.keys.add(symbol);return pyglet.event.EVENT_HANDLED
    def on_key_release(self,symbol,modifiers):self.keys.discard(symbol);return pyglet.event.EVENT_HANDLED if self.active else pyglet.event.EVENT_UNHANDLED
    def on_joyaxis_motion(self,j,axis,value):
        if not self.active:return
        self.axes[str(axis).lower()]=float(value)
        if self.state in (self.HOME,self.DRIVER,self.TRACK,self.CUP) and self.nav_wait<=0 and str(axis).lower() in ("x","y") and abs(value)>.65:
            k=pyglet.window.key; self.on_key_press((k.RIGHT if value>0 else k.LEFT) if str(axis).lower()=="x" else (k.DOWN if value>0 else k.UP),0);self.nav_wait=12
    def on_joyhat_motion(self,j,x,y):
        if not self.active or self.nav_wait>0:return
        k=pyglet.window.key
        if x:self.on_key_press(k.RIGHT if x>0 else k.LEFT,0)
        elif y:self.on_key_press(k.UP if y>0 else k.DOWN,0)
        self.nav_wait=10
    def on_joybutton_press(self,j,b):
        if not self.active:return
        self.buttons.add(int(b));k=pyglet.window.key
        if self.state in (self.HOME,self.DRIVER,self.TRACK,self.CUP,self.FINISH):
            if b in (0,1):self.on_key_press(k.ENTER,0)
            elif b in (6,7,8,9):self.on_key_press(k.ESCAPE,0)
        elif b in (7,9):self.on_key_press(k.ESCAPE,0)
    def on_joybutton_release(self,j,b):self.buttons.discard(int(b))

    def update(self,dt):
        if not self.active:return
        dt=float(dt);self.nav_wait=max(0,self.nav_wait-dt)
        if self.state in (self.HOME,self.DRIVER,self.TRACK,self.CUP,self.PAUSE):return
        if self.state==self.COUNTDOWN:
            self.countdown-=dt;self.countlab.text="3" if self.countdown>120 else "2" if self.countdown>60 else "1" if self.countdown>20 else "GO!"
            if self.countdown<=0:self.state=self.RACE;self.countlab.visible=False;self.speed=self._physics()["max"]*.42
        elif self.state==self.RACE:
            self.race_time+=dt;self._player(dt)
            if self.state==self.FINISH:return
            self._ai(dt)
        elif self.state==self.FINISH:self._ai(dt)
        c,w,y=self._project();self._rival_visuals(c,w,y);self._kart_visual();self._particles(dt)
        if self.state==self.RACE:
            self.laplab.text=f"LAP {min(3,self.lap+1)}/3";self.placelab.text=f"PLACE {self._place()}/12";self.ebar.width=210*max(0,min(1,self.energy/100));self.ebar.color=(79,237,199) if self.energy>55 else (246,190,76) if self.energy>25 else (244,78,83);self.speedlab.text=f"{int(abs(self.speed)*29)} KM/H"
            if self.drifting:self.msglab.text=f"DRIFT {int(self.drift_charge)}%"
            elif self.overdrive:self.msglab.text="OVERDRIVE"
    def on_draw(self):
        if not self.active:return pyglet.event.EVENT_UNHANDLED
        EngineGlobals.window.clear();self.batch.draw();return pyglet.event.EVENT_HANDLED
    def draw(self):
        if self.active:self.batch.draw()
