'''simulation_builder provides utility classes to build games'''

import crisp.simulator.simulation as simulations


def build_simulation():
    ''' return a new instance of the simulation '''
    sim = simulations.Simulation()
    return sim
