"""Off-screen checks for playback, input handling, resizing, and export."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame
from PIL import Image
from modules.dashboard import Dashboard, WIDTH, HEIGHT
from modules.simulation import Simulation


class DashboardTests(unittest.TestCase):
    def make_dashboard(self):
        return Dashboard(Simulation())

    def test_controls(self):
        app = self.make_dashboard()
        app.action('play')
        self.assertTrue(app.playing)
        app.action('step')
        self.assertEqual(app.turn,1)
        self.assertFalse(app.playing)
        app.action('reset')
        self.assertEqual(app.turn,0)
        app.action('scenario_buffer')
        self.assertEqual((app.seed,app.q), (67,.3))
        app.action('scenario_risk')
        self.assertEqual((app.seed,app.q), (15,.3))
        app.action('scenario_adapt')
        self.assertEqual((app.seed,app.q), (23,.22))
        app.action('new')
        self.assertEqual(app.seed,24)
        for _ in range(30):
            app.action('qup')
            app.action('faster')
        self.assertEqual((app.q,app.speed),(1,12))
        app.action('overlay')
        self.assertFalse(app.overlays)
        for _ in range(30):
            app.action('qdown')
            app.action('slower')
        self.assertEqual((app.q,app.speed),(0,1))

    def test_render_initial_and_final(self):
        app = self.make_dashboard()
        self.assertEqual(app.render().get_size(), (WIDTH,HEIGHT))
        for _ in range(100):
            app.step()
        self.assertTrue(app.finished)
        app.action('play')
        self.assertTrue(app.playing)
        self.assertEqual(app.turn,0)
        self.assertEqual(app.render().get_size(), (WIDTH,HEIGHT))

    def test_keyboard_event_loop(self):
        app = self.make_dashboard()
        events = [[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RIGHT)],
                  [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE)]]
        with patch('pygame.event.get', side_effect=events):
            app.run()
        self.assertEqual(app.turn,1)

    def test_mouse_on_native_resized_window(self):
        app = self.make_dashboard()
        app.render(size=(1100,760))
        pygame.display.init()
        screen = pygame.display.set_mode((1100,760))
        rect = app.buttons['step']
        events = [[pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                      pos=rect.center)],
                  [pygame.event.Event(pygame.QUIT)]]
        with patch('pygame.display.set_mode', return_value=screen), patch('pygame.event.get', side_effect=events):
            app.run()
        self.assertEqual(app.turn,1)

    def test_rewind_preserves_future(self):
        app = self.make_dashboard()
        for _ in range(12):
            app.step()
        expected = [(b.position,b.status,b.route[:]) for b in app.bots]
        app.seek(3)
        for _ in range(9):
            app.step()
        self.assertEqual([(b.position,b.status,b.route) for b in app.bots],expected)
        self.assertEqual(len(app.history),13)

    def test_cell_inspection_and_view_selection(self):
        app = self.make_dashboard()
        app.render()
        area,cell = app.maps[3]
        app.click((area.x+cell//2,area.y+cell//2))
        self.assertEqual(app.pinned,(3,(0,0)))
        app.action('compare')
        app.render()
        self.assertEqual(len(app.maps),4)
        app.action('bot_1')
        self.assertEqual(app.selected,1)
        self.assertIsNone(app.pinned)
        app.action('focus')
        app.render()
        self.assertEqual(list(app.maps),[1])

    def test_drag_timeline(self):
        app = self.make_dashboard()
        for _ in range(10):
            app.step()
        app.render()
        app.click(app.timeline.midleft)
        self.assertEqual(app.turn,0)
        self.assertEqual(app.dragging,'timeline')
        app.scrub(app.timeline.right)
        self.assertEqual(app.turn,10)

    def test_export_decodes_and_limits_steps(self):
        app = self.make_dashboard()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'demo.gif'
            app.export(path, max_steps=3)
            with Image.open(path) as gif:
                self.assertEqual(gif.n_frames,4)
                self.assertEqual(gif.size,(WIDTH,HEIGHT))
                gif.seek(3)
                gif.load()
            self.assertTrue(path.with_suffix('.png').exists())
        self.assertEqual(app.turn,3)


if __name__ == '__main__':
    unittest.main()
