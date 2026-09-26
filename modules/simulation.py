"""Deterministic simulation, separate from rendering and the legacy experiments."""
import heapq
import math
import random
from collections import deque
import numpy as np

STRATEGIES = {
    1: ('Fixed route', 'Plans once, then follows its original route.'),
    2: ('Replanning', 'Finds a shortest safe route at every turn.'),
    3: ('Safety buffer', 'Avoids fire neighbors whenever possible.'),
    4: ('Predictive planner', 'Plans around where fire may spread next.'),
}


def neighbors(cell, size):
    r, c = cell
    for row, col in ((r-1,c), (r,c+1), (r+1,c), (r,c-1)):
        if 0 <= row < size and 0 <= col < size:
            yield row, col


def generate_ship(size, rng):
    opened = np.zeros((size, size), dtype=bool)
    first = (rng.randrange(1, size-1), rng.randrange(1, size-1))
    opened[first] = True
    candidates = set(neighbors(first, size))
    while candidates:
        cell = rng.choice(sorted(candidates))
        candidates.remove(cell)
        if sum(opened[n] for n in neighbors(cell, size)) == 1:
            opened[cell] = True
            candidates.update(n for n in neighbors(cell, size) if not opened[n])
    dead = [tuple(c) for c in np.argwhere(opened)
            if sum(opened[n] for n in neighbors(tuple(c), size)) == 1]
    rng.shuffle(dead)
    for cell in dead[:len(dead)//2]:
        closed = [n for n in neighbors(cell, size) if not opened[n]]
        if closed:
            opened[rng.choice(closed)] = True
    return opened


class Simulation:
    def __init__(self, size=25, q=0.22, seed=23, bot=3):
        if not 5 <= size <= 80:
            raise ValueError('Grid size must be between 5 and 80.')
        if not math.isfinite(q) or not 0 <= q <= 1:
            raise ValueError('Flammability must be between 0 and 1.')
        if bot not in STRATEGIES:
            raise ValueError('Bot must be 1, 2, 3, or 4.')
        self.size, self.q, self.seed, self.bot = size, q, seed, bot
        rng = random.Random(seed)
        self.opened = generate_ship(size, rng)
        cells = [tuple(map(int,c)) for c in np.argwhere(self.opened)]
        self.start, self.goal, initial_fire = rng.sample(cells, 3)
        self.position = self.start
        self.fire = np.zeros_like(self.opened)
        self.fire[initial_fire] = True
        # Fixed-size random draws keep the fire identical across surviving bots.
        self.rng = np.random.default_rng(seed % (2**64))
        self.steps = self.plans = self.expanded = self.reroutes = 0
        self.status = 'RUNNING'
        self.trail = [self.position]
        self.route = []
        self.note = ''
        self.plan()

    def fire_neighbors(self):
        counts = np.zeros(self.fire.shape, dtype=int)
        counts[1:] += self.fire[:-1]
        counts[:-1] += self.fire[1:]
        counts[:,1:] += self.fire[:,:-1]
        counts[:,:-1] += self.fire[:,1:]
        return counts

    def search(self, avoid_adjacent=False):
        blocked = ~self.opened | self.fire
        if avoid_adjacent:
            blocked |= self.fire_neighbors() > 0
        if blocked[self.goal]:
            return []
        frontier = [(0.0, 0.0, self.position)]
        costs = {self.position: 0.0}
        previous = {self.position: None}
        while frontier:
            _, cost, cell = heapq.heappop(frontier)
            if cost != costs[cell]:
                continue
            self.expanded += 1
            if cell == self.goal:
                route = []
                while cell is not None:
                    route.append(cell)
                    cell = previous[cell]
                return list(reversed(route))[1:]
            for child in neighbors(cell, self.size):
                if blocked[child]:
                    continue
                candidate = cost + 1
                if candidate < costs.get(child, math.inf):
                    costs[child] = candidate
                    previous[child] = cell
                    heapq.heappush(frontier, (candidate, candidate, child))
        return []

    def forecast(self, horizon):
        """Estimate fire probabilities; neighboring events are approximated as independent."""
        forecasts = [self.fire.astype(float)]
        for _ in range(horizon):
            current = forecasts[-1]
            safe = np.ones(current.shape)
            safe[1:] *= 1 - self.q * current[:-1]
            safe[:-1] *= 1 - self.q * current[1:]
            safe[:, 1:] *= 1 - self.q * current[:, :-1]
            safe[:, :-1] *= 1 - self.q * current[:, 1:]
            forecasts.append(np.where(self.opened, 1 - (1-current)*safe, 0))
        return forecasts

    def predictive_search(self):
        """Search cell-and-arrival-time states using distance and estimated survival."""
        distances = {self.goal: 0}
        pending = deque([self.goal])
        while pending:
            cell = pending.popleft()
            for child in neighbors(cell, self.size):
                if self.opened[child] and not self.fire[child] and child not in distances:
                    distances[child] = distances[cell] + 1
                    pending.append(child)
        if self.position not in distances or self.fire[self.goal]:
            return []
        horizon = distances[self.position] + max(16, distances[self.position] // 2)
        forecasts = self.forecast(horizon)
        first = (0, self.position)
        costs, previous = {first: 0.0}, {first: None}
        fringe = [(distances[self.position], 0.0, first)]
        while fringe:
            _, cost, state = heapq.heappop(fringe)
            if cost != costs[state]:
                continue
            time, cell = state
            self.expanded += 1
            if cell == self.goal:
                route = []
                while previous[state] is not None:
                    route.append(state[1])
                    state = previous[state]
                return route[::-1]
            for child in neighbors(cell, self.size):
                arrival = time + 1
                if child not in distances or arrival + distances[child] > horizon:
                    continue
                # Reaching the button succeeds before this turn's fire update.
                probability = forecasts[time if child == self.goal else arrival][child]
                if probability >= 1:
                    continue
                candidate = cost + 1 + 12 * -math.log(max(1e-12, 1-probability))
                target = (arrival, child)
                if candidate < costs.get(target, math.inf):
                    costs[target], previous[target] = candidate, state
                    heapq.heappush(fringe, (candidate + distances[child], candidate, target))
        return []

    def plan(self):
        previous = self.route[:]
        self.plans += 1
        self.route = self.predictive_search() if self.bot == 4 else self.search(avoid_adjacent=self.bot == 3)
        forecast_fallback = self.bot == 4 and not self.route
        if forecast_fallback:
            self.route = self.search()
        if self.bot == 3 and not self.route:
            self.route = self.search()
            self.note = 'No buffered route. Falling back to shortest safe path.'
        else:
            self.note = STRATEGIES[self.bot][1]
        if forecast_fallback:
            self.note = 'Forecast found no viable route. Trying the shortest current-safe route.'
        if previous and previous != self.route:
            self.reroutes += 1
            if self.bot != 3:
                self.note = 'Route changed in response to the spreading fire.'
        if not self.route:
            self.status = 'NO ROUTE'
            self.note = 'No route to the button remains without crossing fire.'

    def step(self):
        if self.status != 'RUNNING':
            return
        self.position = self.route.pop(0)
        self.steps += 1
        self.trail.append(self.position)
        if self.fire[self.position]:
            self.status, self.note = 'BOT LOST', 'The original route led into a burning cell.'
        elif self.position == self.goal:
            self.status, self.note = 'SUCCESS', 'Button reached. Fire suppression activated.'
            self.fire[:] = False
        else:
            probability = 1 - (1-self.q)**self.fire_neighbors()
            self.fire |= self.opened & (self.rng.random(self.fire.shape) < probability)
            if self.fire[self.position]:
                self.status, self.note = 'BOT LOST', 'Fire reached the bot immediately after its move.'
            elif self.fire[self.goal]:
                self.status, self.note = 'BUTTON LOST', 'The suppression button is now burning.'
            elif self.bot != 1:
                self.plan()
        if self.status != 'RUNNING':
            self.route = []
