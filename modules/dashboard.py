"""Native-resolution Pygame UI with inspection, focus views, and replay scrubbing."""
import copy
import os
from pathlib import Path

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
from modules.simulation import Simulation, STRATEGIES

WIDTH, HEIGHT = 1440, 960
BG, PANEL, BORDER = '#0D1117', '#161D27', '#303C4C'
TEXT, MUTED, FLOOR = '#F1F5FA', '#A5B4C7', '#2C3C50'
FIRE, GOAL = '#FF825B', '#9AE6AC'
FAILURE = '#FF5263'
COLORS = ['#70C5FF', '#BAA1FF', '#71DCC1', '#FFD17F']
EXPLANATIONS = [
    'Commits to its first shortest path. New fire never changes its plan.',
    'Recomputes a shortest path after every fire update. Avoids fire that exists now.',
    'First avoids fire and adjacent cells. Uses a shortest safe path if that buffer blocks every route.',
    'Forecasts fire probabilities, then searches positions and arrival times to balance distance and survival.',
]


def make_app_icon():
    """Draw a small robot with a circuit motif for the application window."""
    icon = pygame.Surface((64,64),pygame.SRCALPHA)
    pygame.draw.rect(icon,'#172737',(0,0,64,64),border_radius=15)
    pygame.draw.line(icon,'#A9EAC5',(32,9),(32,18),3)
    pygame.draw.circle(icon,'#A9EAC5',(32,8),4)
    pygame.draw.rect(icon,'#70C5FF',(10,18,44,34),border_radius=10)
    pygame.draw.rect(icon,'#101B29',(15,24,34,22),border_radius=7)
    for x in (23,41):
        pygame.draw.circle(icon,'#A9EAC5',(x,33),4)
    pygame.draw.lines(icon,'#70C5FF',False,[(27,40),(32,43),(37,40)],2)
    pygame.draw.rect(icon,'#70C5FF',(5,29,4,13),border_radius=2)
    pygame.draw.rect(icon,'#70C5FF',(55,29,4,13),border_radius=2)
    pygame.draw.lines(icon,'#A9EAC5',False,[(19,54),(19,58),(45,58),(45,54)],2)
    return icon


def make_bot_icon(size, color, lost=False):
    """Draw a crisp robot marker at its display size, without bitmap scaling."""
    icon = pygame.Surface((size,size),pygame.SRCALPHA)
    middle = size//2
    pygame.draw.rect(icon,BG,(0,2,size,size-2),border_radius=4)
    pygame.draw.line(icon,color,(middle,1),(middle,5),2)
    pygame.draw.rect(icon,color,(middle-1,0,3,3),border_radius=1)
    pygame.draw.rect(icon,color,(3,4,size-6,size-6),border_radius=3)
    pygame.draw.rect(icon,BG,(5,6,size-10,size-10),border_radius=2)
    pygame.draw.rect(icon,color,(1,size//2,2,4))
    pygame.draw.rect(icon,color,(size-3,size//2,2,4))
    eye_size = max(2,size//8)
    eye_y = max(7,size//2-1)
    for eye_x in (size//3, size-1-size//3-eye_size+1):
        pygame.draw.rect(icon,FAILURE if lost else TEXT,(eye_x,eye_y,eye_size,eye_size))
    if size >= 20:
        pygame.draw.line(icon,color,(middle-2,size-6),(middle+2,size-6),1)
    return icon


class Dashboard:
    def __init__(self, simulation):
        pygame.font.init()
        self.size, self.q, self.seed = simulation.size, simulation.q, simulation.seed
        self.fonts = {}
        self.bot_icons = {}
        self.font_name = next((name for name in ('segoeui', 'inter', 'dejavusans', 'arial')
                               if pygame.font.match_font(name)), None)
        fonts_dir = Path(os.environ.get('WINDIR','C:/Windows')) / 'Fonts'
        self.font_paths = [fonts_dir/'segoeui.ttf',fonts_dir/'segoeuib.ttf']
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.speed, self.overlays = 3, True
        self.selected, self.focus = 3, True
        self.pointer = (-1, -1)
        self.pinned = None
        self.dragging = None
        self.forecast_steps = 0
        self.forecast_cache = None
        self.buttons, self.maps = {}, {}
        self.reset()

    def reset(self):
        self.bots = [Simulation(self.size, self.q, self.seed, bot) for bot in range(1, 5)]
        self.turn, self.playing = 0, False
        self.history = [copy.deepcopy(self.bots)]
        self.pinned = None
        self.forecast_cache = None

    @property
    def finished(self):
        return all(bot.status != 'RUNNING' for bot in self.bots)

    def step(self):
        if self.turn < len(self.history)-1:
            self.seek(self.turn+1)
        elif not self.finished:
            for bot in self.bots:
                bot.step()
            self.turn += 1
            self.history.append(copy.deepcopy(self.bots))
        if self.finished:
            self.playing = False

    def seek(self, turn):
        self.turn = max(0, min(int(turn), len(self.history)-1))
        self.bots = copy.deepcopy(self.history[self.turn])

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            path = self.font_paths[int(bold)]
            self.fonts[key] = pygame.font.Font(str(path),size) if path.exists() else pygame.font.SysFont(self.font_name,size,bold=bold)
        return self.fonts[key]

    def text(self, value, x, y, size=17, color=TEXT, bold=False):
        self.canvas.blit(self.font(size, bold).render(str(value), True, color), (int(x), int(y)))

    def wrap(self, value, x, y, width, size=16, color=MUTED):
        line = ''
        for word in value.split():
            candidate = (line+' '+word).strip()
            if self.font(size).size(candidate)[0] > width and line:
                self.text(line, x, y, size, color)
                y += size+7
                line = word
            else:
                line = candidate
        self.text(line, x, y, size, color)
        return y+size+7

    def box(self, rect, color=PANEL, border=None, radius=10):
        pygame.draw.rect(self.canvas, color, rect, border_radius=radius)
        if border:
            pygame.draw.rect(self.canvas, border, rect, 1, border_radius=radius)

    def button(self, action, label, rect, active=False):
        rect = pygame.Rect(rect)
        self.buttons[action] = rect
        hover = rect.collidepoint(self.pointer)
        fill = '#A9EAC5' if active else '#32445A' if hover else '#243145'
        self.box(rect, fill, '#667F98' if hover else None, 7)
        rendered = self.font(15, active).render(label, True, BG if active else TEXT)
        self.canvas.blit(rendered, rendered.get_rect(center=rect.center))

    def draw_map(self, bot, rect, index):
        cell = max(1, min(rect.width, rect.height)//bot.size)
        side = cell*bot.size
        origin = (rect.centerx-side//2, rect.centery-side//2)
        area = pygame.Rect(*origin, side, side)
        self.maps[index] = (area, cell)
        self.box(area.inflate(12,12), '#090E15', radius=5)
        adjacent = bot.fire_neighbors()
        prediction = None
        if index == 3 and self.forecast_steps:
            key = (self.seed,self.q,self.turn,self.forecast_steps,bot.fire.tobytes())
            if self.forecast_cache is None or self.forecast_cache[0] != key:
                self.forecast_cache = (key,bot.forecast(self.forecast_steps)[-1])
            prediction = self.forecast_cache[1]
        def center(point):
            return origin[0]+point[1]*cell+cell//2, origin[1]+point[0]*cell+cell//2
        for r in range(bot.size):
            for c in range(bot.size):
                if not bot.opened[r,c]:
                    continue
                fill = FIRE if bot.fire[r,c] else '#65523C' if self.overlays and index in (2,3) and adjacent[r,c] else FLOOR
                if prediction is not None and not bot.fire[r,c]:
                    p = float(prediction[r,c])
                    fill = (int(44+174*p),int(60-15*p),int(80-20*p))
                pygame.draw.rect(self.canvas, fill, (origin[0]+c*cell,origin[1]+r*cell,cell-1 if cell>3 else cell,cell-1 if cell>3 else cell))
        if self.overlays:
            if len(bot.trail)>1:
                pygame.draw.lines(self.canvas, '#71849C', False, [center(p) for p in bot.trail], max(1,cell//7))
            route = [bot.position]+bot.route
            if len(route)>1:
                pygame.draw.lines(self.canvas, COLORS[index], False, [center(p) for p in route], max(2,cell//6))
        radius = max(3, cell//3)
        target = center(bot.goal)
        pygame.draw.polygon(self.canvas, FIRE if bot.fire[bot.goal] else GOAL,
                            [(target[0],target[1]-radius-1),(target[0]+radius+1,target[1]),
                             (target[0],target[1]+radius+1),(target[0]-radius-1,target[1])])
        pygame.draw.circle(self.canvas, MUTED, center(bot.start), radius, 1)
        current = center(bot.position)
        # Keep the bot readable even when four maps share the window.
        icon_size = max(20,min(34,cell*2))
        icon_key = (icon_size,index,bot.status == 'BOT LOST')
        if icon_key not in self.bot_icons:
            self.bot_icons[icon_key] = make_bot_icon(icon_size,COLORS[index],icon_key[2])
        icon = self.bot_icons[icon_key]
        self.canvas.blit(icon,icon.get_rect(center=current))
        inspected = self.cell_at(self.pointer)
        if self.pinned and self.pinned[0] == index:
            inspected = self.pinned
        if inspected and inspected[0] == index:
            r,c = inspected[1]
            pygame.draw.rect(self.canvas, TEXT, (origin[0]+c*cell,origin[1]+r*cell,cell,cell), 1)

    def cell_at(self, point):
        for index,(area,cell) in self.maps.items():
            if area.collidepoint(point):
                return index, ((point[1]-area.y)//cell,(point[0]-area.x)//cell)
        return None

    def render(self, export=False, size=None):
        if size and self.canvas.get_size() != size:
            self.canvas = pygame.Surface(size)
        w,h = self.canvas.get_size()
        self.canvas.fill(BG)
        self.buttons, self.maps = {}, {}
        self.text('THIS BOT IS ON FIRE',24,17,29,TEXT,True)
        self.text('Explore the decision. Follow the route. Inspect the risk.',25,57,16,MUTED)
        self.button('reset','Reset',(w-460,25,72,38))
        self.button('new','New ship',(w-380,25,100,38))
        self.button('view','Compare all' if self.focus else 'Focus bot', (w-268,25,116,38))
        self.button('overlay','Overlays on' if self.overlays else 'Overlays off',(w-144,25,120,38))
        tabwidth = (w-60)//4
        for i,bot in enumerate(self.bots):
            x = 24+i*(tabwidth+4)
            self.button(f'bot_{i}',f'Bot {i+1} ({STRATEGIES[i+1][0]})',(x,94,tabwidth,45),i==self.selected)
        content_top, content_bottom = 157,h-156
        leftwidth, sidebar_x = w-366,w-326
        if self.focus:
            bot = self.bots[self.selected]
            card = pygame.Rect(24,content_top,leftwidth,content_bottom-content_top)
            self.box(card,PANEL,BORDER)
            self.text(f'Bot {bot.bot} ({STRATEGIES[bot.bot][0]})',card.x+18,card.y+13,18,COLORS[self.selected],True)
            self.text('Hover to inspect  /  Click to pin a cell',card.x+18,card.bottom-31,14,MUTED)
            self.draw_map(bot,pygame.Rect(card.x+18,card.y+49,card.width-36,card.height-92),self.selected)
        else:
            cw,ch = (leftwidth-12)//2,(content_bottom-content_top-12)//2
            for i,bot in enumerate(self.bots):
                card = pygame.Rect(24+(i%2)*(cw+12),content_top+(i//2)*(ch+12),cw,ch)
                self.box(card,PANEL,COLORS[i] if i==self.selected else BORDER)
                self.text(f'Bot {i+1} ({STRATEGIES[i+1][0]})',card.x+12,card.y+9,16,COLORS[i],True)
                self.draw_map(bot,pygame.Rect(card.x+10,card.y+43,card.width-20,card.height-78),i)
                status_color = GOAL if bot.status == 'SUCCESS' else MUTED if bot.status == 'RUNNING' else FAILURE
                self.text(bot.status,card.x+12,card.bottom-26,14,status_color,bot.status!='RUNNING')
                self.text(f'/  {bot.steps} moves',card.x+140,card.bottom-26,14,MUTED)
        bot = self.bots[self.selected]
        y = content_top
        self.text('DECISION INSPECTOR',sidebar_x,y,14,MUTED,True)
        y += 30
        self.text(STRATEGIES[bot.bot][0],sidebar_x,y,25,COLORS[self.selected],True)
        y = self.wrap(EXPLANATIONS[self.selected],sidebar_x,y+43,296,16) if h >= 820 else y+43
        y += 15
        self.text(bot.status,sidebar_x,y,17,GOAL if bot.status=='SUCCESS' else FAILURE if bot.status!='RUNNING' else TEXT,True)
        y = self.wrap(bot.note,sidebar_x,y+31,296,16,TEXT)
        y += 14
        self.text(f'{bot.steps} moves   /   {bot.plans} plans',sidebar_x,y,16)
        self.text(f'{bot.reroutes} route changes',sidebar_x,y+28,16,MUTED)
        y += 72
        inspected = self.pinned or self.cell_at(self.pointer)
        if inspected:
            index,cell = inspected
            subject = self.bots[index]
            count = int(subject.fire_neighbors()[cell])
            self.text(f'CELL {cell[0]}, {cell[1]} / BOT {index+1}',sidebar_x,y,14,COLORS[index],True)
            state = 'Wall' if not subject.opened[cell] else 'Burning' if subject.fire[cell] else 'Open corridor'
            self.text(state,sidebar_x,y+27,17)
            chance = 1 if subject.fire[cell] else 1-(1-subject.q)**count if subject.opened[cell] else 0
            self.text(f'Next-spread ignition: {chance:.0%}',sidebar_x,y+55,16,MUTED)
            self.text('Click another cell to pin. Esc clears.',sidebar_x,y+83,14,MUTED)
        else:
            self.wrap('Hover over a cell to inspect its fire exposure. Click to pin it while the simulation runs.',sidebar_x,y,296,16)
        if y+250 < content_bottom:
            self.wrap('Same ship and fire draws for every bot. Outcomes depend on the scenario.',sidebar_x,y+142,296,14)
        if self.selected == 3:
            label = f'Forecast +{self.forecast_steps} turns / warmer = risk' if self.forecast_steps else 'Show future fire risk'
            self.button('forecast',label,(sidebar_x,content_bottom-40,302,34))
        controls_y = h-132
        self.button('scenario_adapt','Replanning',(24,controls_y,116,36))
        self.button('scenario_buffer','Safety buffer',(148,controls_y,124,36))
        self.button('scenario_risk','Prediction',(280,controls_y,116,36))
        self.text(f'Seed {self.seed}  /  {self.size} x {self.size}',414,controls_y+7,15,MUTED)
        self.button('qdown','Flammability -',(w-326,controls_y,146,36))
        self.button('qup','Flammability +',(w-172,controls_y,148,36))
        y = h-82
        self.button('back','<',(24,y,38,38))
        self.button('play','Pause' if self.playing else 'Replay' if self.finished else 'Play',(70,y,84,38),True)
        self.button('step','>',(162,y,38,38))
        self.timeline = pygame.Rect(230,y+17,max(100,w-636),5)
        pygame.draw.rect(self.canvas,BORDER,self.timeline,border_radius=2)
        fraction = self.turn/max(1,len(self.history)-1)
        pygame.draw.circle(self.canvas,GOAL,(self.timeline.x+round(fraction*self.timeline.width),self.timeline.centery),7)
        self.text(f'Turn {self.turn:03d}',w-388,y+8,16)
        self.button('slower','-',(w-288,y,34,38))
        self.text(f'{self.speed}x',w-244,y+8,16)
        self.button('faster','+',(w-210,y,34,38))
        self.text(f'Flammability: {self.q:.2f}',w-164,y+9,14,MUTED)
        self.text('Space: play / pause    Arrows: scrub    1-4: select bot    C: compare    F: focus    P: overlays',24,h-30,13,MUTED)
        if export:
            self.text('RECORDED SIMULATION',w-215,h-30,12,GOAL)
        return self.canvas

    def action(self, action):
        if action == 'play':
            if self.finished:
                self.seek(0)
            self.playing = not self.playing
        elif action == 'step':
            self.playing = False
            self.step()
        elif action == 'back':
            self.playing = False
            self.seek(self.turn-1)
        elif action == 'reset':
            self.reset()
        elif action == 'new':
            self.seed += 1
            self.reset()
        elif action == 'slower':
            self.speed = max(1,self.speed-1)
        elif action == 'faster':
            self.speed = min(12,self.speed+1)
        elif action in ('qdown','qup'):
            self.q = round(min(1,max(0,self.q+(0.05 if action=='qup' else -0.05))),2)
            self.reset()
        elif action == 'overlay':
            self.overlays = not self.overlays
        elif action == 'forecast':
            self.forecast_steps = {0:3,3:6,6:0}[self.forecast_steps]
        elif action == 'view':
            self.focus = not self.focus
        elif action in ('focus','compare'):
            self.focus = action == 'focus'
        elif action.startswith('bot_'):
            self.selected = int(action[-1])
            self.pinned = None
        elif action.startswith('scenario_'):
            self.size = 25
            self.seed,self.q = {'scenario_adapt':(23,.22),'scenario_buffer':(67,.3),'scenario_risk':(15,.3)}[action]
            self.reset()

    def scrub(self, x):
        fraction = (x-self.timeline.x)/max(1,self.timeline.width)
        self.seek(round(fraction*(len(self.history)-1)))
        self.playing = False

    def click(self, point):
        for action,rect in self.buttons.items():
            if rect.collidepoint(point):
                self.action(action)
                return
        if self.timeline.inflate(12,26).collidepoint(point):
            self.dragging = 'timeline'
            self.scrub(point[0])
        elif self.cell_at(point):
            self.pinned = self.cell_at(point)
            self.selected = self.pinned[0]

    def run(self):
        # Prevent Windows from stretching an already-rendered bitmap on high-DPI screens.
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (AttributeError,OSError):
                pass
        pygame.display.init()
        pygame.display.set_icon(make_app_icon())
        info = pygame.display.Info()
        initial = (min(WIDTH,info.current_w),min(HEIGHT,max(680,info.current_h-80)))
        screen = pygame.display.set_mode(initial,pygame.RESIZABLE)
        pygame.display.set_caption('This Bot Is on Fire | Interactive Strategy Lab')
        clock,elapsed,running = pygame.time.Clock(),0,True
        keys = {pygame.K_SPACE:'play',pygame.K_RIGHT:'step',pygame.K_LEFT:'back',pygame.K_r:'reset',
                pygame.K_n:'new',pygame.K_MINUS:'slower',pygame.K_EQUALS:'faster',
                pygame.K_LEFTBRACKET:'qdown',pygame.K_RIGHTBRACKET:'qup',pygame.K_p:'overlay',
                pygame.K_c:'compare',pygame.K_f:'focus',pygame.K_1:'bot_0',pygame.K_2:'bot_1',
                pygame.K_3:'bot_2',pygame.K_4:'bot_3'}
        self.render(size=screen.get_size())
        try:
            while running:
                dt = clock.tick(60)/1000
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.VIDEORESIZE:
                        screen = pygame.display.set_mode((max(1000,event.w),max(720,event.h)),pygame.RESIZABLE)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.pinned:
                                self.pinned = None
                            else:
                                running = False
                        elif event.key in keys:
                            self.action(keys[event.key])
                            elapsed = 0
                    elif event.type == pygame.MOUSEMOTION:
                        self.pointer = event.pos
                        if self.dragging:
                            self.scrub(event.pos[0])
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.click(event.pos)
                        elapsed = 0
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.dragging = None
                if self.playing:
                    elapsed += dt
                    if elapsed >= 1/self.speed:
                        self.step()
                        elapsed = 0
                screen.blit(self.render(size=screen.get_size()),(0,0))
                pygame.display.flip()
        finally:
            pygame.quit()

    def export(self, filename, max_steps=180):
        from PIL import Image
        path = Path(filename)
        path.parent.mkdir(parents=True,exist_ok=True)
        self.reset()
        self.focus = False
        frames,durations = [],[]
        cover = None
        for index in range(max_steps+1):
            surface = self.render(export=True,size=(WIDTH,HEIGHT))
            frame = Image.frombytes('RGB',(WIDTH,HEIGHT),pygame.image.tobytes(surface,'RGB'))
            if index == 8 or cover is None:
                cover = frame.copy()
            frames.append(frame.convert('P',palette=Image.Palette.ADAPTIVE,colors=256))
            durations.append(1100 if index==0 else 260)
            if self.finished or index == max_steps:
                break
            self.step()
        durations[-1] = 2300
        frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
        cover.save(path.with_suffix('.png'))
        print(f'Exported {path} ({len(frames)} frames; {"complete" if self.finished else "truncated"})')
        for bot in self.bots:
            print(f'Bot {bot.bot}: {bot.status}, {bot.steps} moves')
        pygame.quit()
