"""Regression checks for the assignment rules and reproducible comparisons."""
import unittest
import numpy as np

from modules.simulation import Simulation, generate_ship, neighbors
import random


def scenario(bot=2, q=0, start=(4,0), goal=(4,4), fire=(0,0), opened=None):
    sim = Simulation(5, q, 2, bot)
    sim.opened = np.ones((5,5), dtype=bool) if opened is None else opened.copy()
    sim.start = sim.position = start
    sim.goal = goal
    sim.fire[:] = False
    sim.fire[fire] = True
    sim.trail = [start]
    sim.route = []
    sim.status = 'RUNNING'
    sim.steps = sim.plans = sim.expanded = sim.reroutes = 0
    sim.visits, sim.actions, sim.risk = {}, {}, {}
    sim.plan()
    return sim


class SimulationTests(unittest.TestCase):
    def test_generated_layout_is_connected(self):
        for size in (5, 25, 40):
            opened = generate_ship(size, random.Random(23))
            first = tuple(np.argwhere(opened)[0])
            reached, pending = {first}, [first]
            while pending:
                for child in neighbors(pending.pop(), size):
                    if opened[child] and child not in reached:
                        reached.add(child)
                        pending.append(child)
            self.assertEqual(len(reached), int(opened.sum()))

    def test_distinct_placements_and_matched_conditions(self):
        bots = [Simulation(bot=b) for b in range(1,5)]
        for bot in bots:
            fire = tuple(np.argwhere(bot.fire)[0])
            self.assertEqual(len({bot.start, bot.goal, fire}), 3)
            np.testing.assert_array_equal(bot.opened, bots[0].opened)
            np.testing.assert_array_equal(bot.fire, bots[0].fire)
            self.assertEqual((bot.start, bot.goal), (bots[0].start, bots[0].goal))

    def test_fire_spreads_simultaneously(self):
        sim = scenario(q=1)
        sim.step()
        self.assertEqual(set(map(tuple,np.argwhere(sim.fire))), {(0,0),(1,0),(0,1)})
        self.assertEqual(sim.position, (4,1))

    def test_zero_flammability_and_success(self):
        for bot in range(1,5):
            sim = scenario(bot=bot)
            for _ in range(30):
                if sim.status == 'RUNNING':
                    self.assertEqual(int(sim.fire.sum()), 1)
                sim.step()
            self.assertEqual(sim.status, 'SUCCESS')
            self.assertFalse(sim.fire.any())

    def test_success_precedes_fire_spread(self):
        sim = scenario(q=1, start=(2,1), goal=(2,2), fire=(1,2))
        sim.step()
        self.assertEqual(sim.status, 'SUCCESS')
        self.assertEqual(sim.steps, 1)

    def test_bot_burns_after_moving(self):
        sim = scenario(q=1, start=(2,0), goal=(2,4), fire=(1,1))
        sim.step()
        self.assertEqual(sim.position, (2,1))
        self.assertEqual(sim.status, 'BOT LOST')

    def test_fixed_bot_enters_new_fire(self):
        sim = scenario(bot=1)
        sim.fire[sim.route[0]] = True
        sim.step()
        self.assertEqual(sim.status, 'BOT LOST')
        self.assertEqual(sim.plans, 1)

    def test_bot2_replans_every_turn(self):
        sim = scenario(bot=2)
        sim.step()
        sim.step()
        self.assertEqual(sim.plans, 3)
        self.assertEqual(sim.steps, 2)

    def test_buffer_is_not_real_fire(self):
        sim = scenario(bot=3, start=(2,0), goal=(2,4), fire=(1,2))
        original = sim.fire.copy()
        self.assertTrue(sim.route)
        self.assertTrue(all(sim.fire_neighbors()[cell] == 0 for cell in sim.route))
        sim.plan()
        np.testing.assert_array_equal(sim.fire, original)

    def test_buffer_falls_back(self):
        opened = np.zeros((5,5), dtype=bool)
        opened[2,:] = True
        opened[1,2] = True
        sim = scenario(bot=3, start=(2,0), goal=(2,4), fire=(1,2), opened=opened)
        self.assertEqual(len(sim.route), 4)
        self.assertIn('Falling back', sim.note)

    def test_no_route_is_terminal(self):
        opened = np.zeros((5,5), dtype=bool)
        opened[4,0] = opened[4,4] = opened[0,0] = True
        sim = scenario(opened=opened)
        self.assertEqual(sim.status, 'NO ROUTE')
        sim.step()
        self.assertEqual(sim.steps, 0)

    def test_shared_fire_progression(self):
        bots = [Simulation(bot=b) for b in range(1,5)]
        for _ in range(50):
            for bot in bots:
                bot.step()
            active = [b for b in bots if b.status == 'RUNNING']
            for bot in active[1:]:
                np.testing.assert_array_equal(bot.fire, active[0].fire)

    def test_replay_is_identical(self):
        a, b = Simulation(bot=4), Simulation(bot=4)
        for _ in range(60):
            self.assertEqual((a.position,a.route,a.status), (b.position,b.route,b.status))
            np.testing.assert_array_equal(a.fire,b.fire)
            a.step()
            b.step()

    def test_forecast_respects_walls_and_simultaneous_spread(self):
        sim = scenario(bot=4, q=1)
        sim.opened[0,1] = False
        forecasts = sim.forecast(2)
        self.assertEqual(forecasts[1][1,0], 1)
        self.assertEqual(forecasts[1][2,0], 0)
        self.assertEqual(forecasts[2][2,0], 1)
        self.assertEqual(forecasts[2][0,1], 0)

    def test_predictive_bot_uses_no_future_random_draws(self):
        sim = Simulation(bot=4)
        state = str(sim.rng.bit_generator.state)
        sim.plan()
        self.assertEqual(str(sim.rng.bit_generator.state), state)

    def test_predictive_button_arrival_precedes_spread(self):
        sim = scenario(bot=4, q=1, start=(2,1), goal=(2,2), fire=(1,2))
        sim.step()
        self.assertEqual(sim.status, 'SUCCESS')

    def test_curated_scenarios(self):
        cases = [(23,.22,['BOT LOST','SUCCESS','SUCCESS','SUCCESS']),
                 (67,.3,['BOT LOST','BOT LOST','SUCCESS','SUCCESS']),
                 (15,.3,['BOT LOST','SUCCESS','BUTTON LOST','SUCCESS'])]
        for seed,q,expected in cases:
            bots = [Simulation(25,q,seed,b) for b in range(1,5)]
            for _ in range(100):
                for bot in bots:
                    previous = bot.position
                    was_running = bot.status == 'RUNNING'
                    bot.step()
                    if was_running:
                        self.assertEqual(sum(abs(x-y) for x,y in zip(previous,bot.position)), 1)
                        self.assertTrue(bot.opened[bot.position])
            self.assertEqual([b.status for b in bots],expected)

    def test_invalid_parameters(self):
        for kwargs in ({'size':4}, {'size':81}, {'q':-0.1}, {'q':1.1}, {'q':float('nan')}, {'bot':5}):
            with self.assertRaises(ValueError):
                Simulation(**kwargs)


if __name__ == '__main__':
    unittest.main()
