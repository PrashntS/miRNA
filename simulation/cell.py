#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import networkx as nx

number_of_nodes = 100
G = nx.complete_graph(number_of_nodes)

import random
from nxsim import BaseNetworkAgent, BaseLoggingAgent

class ZombieOutbreak(BaseNetworkAgent):
    def __init__(self, environment=None, agent_id=0, state=()):
        super().__init__(environment=environment, agent_id=agent_id, state=state)
        self.bite_prob = 0.1
        self.cure_prob = 0.001
        self.cure_lim  = 1

    def run(self):
        while True:
            if self.state['id'] == 1:
                self.zombify()
                yield self.env.timeout(20)
            else:
                if random.random() < 0.3:
                    self.cure()
                else:
                    self.kill()
                yield self.env.timeout(1)
                # yield self.env.event()

    def zombify(self):
        normal_neighbors = self.get_neighboring_agents(state_id=0)
        for neighbor in normal_neighbors:
            if random.random() < self.bite_prob:
                neighbor.state['id'] = 1  # zombie
                print("BITEN", self.env.now, self.id, neighbor.id, sep='\t')
                break

    def cure(self):
        zombified_neighbours = self.get_neighboring_agents(state_id=1)
        lim = self.cure_lim
        for neighbor in zombified_neighbours:
            if random.random() < self.cure_prob:
                neighbor.state['id'] = 0
                print("CURED", self.env.now, self.id, neighbor.id, sep='\t')
                lim -= 1
            if lim == 0:
                break
    def kill(self):
        zombified_neighbours = self.get_neighboring_agents(state_id=1)
        ammos = 4
        for neighbor in zombified_neighbours:
            if random.random() < 0.05:
                neighbor.state['id'] = 2
                print("KILLD", self.env.now, self.id, neighbor.id, sep='\t')
                ammos -= 1
            if ammos == 0:
                break


from nxsim import NetworkSimulation

# Initialize agent states. Let's assume everyone is normal.
# Add keys as as necessary, but "id" must always refer to that state category
init_states = [{'id': 0, } for _ in range(number_of_nodes)]

# Seed a zombie
init_states[5] = {'id': 1}
sim = NetworkSimulation(topology=G, states=init_states, agent_type=ZombieOutbreak,
                        max_time=3000, dir_path='sim_01', num_trials=1, logging_interval=1.0)

sim.run_simulation()

trial = BaseLoggingAgent.open_trial_state_history(dir_path='sim_01', trial_id=0)

from matplotlib import pyplot as plt
plt.yscale('log')
zombie_census = [sum([1 for node_id, state in g.items() if state['id'] == 1]) for t,g in trial.items()]
plt.plot(zombie_census)
plt.show()
