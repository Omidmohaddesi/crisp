'''simulation_builder provides utility classes to build games'''

import simulator.simulation as sim
import simulator.agent as agent
import simulator.network as network
import simulator.simulation_runner as sim_runner
import simulator.decision_maker as dmaker
import simulator.patient_model as pmodel


class ReturnValue(object):
    def __init__(self, simulation, runner):
        self.simulation = simulation
        self.runner = runner


def build_simulation():
    ''' return a new instance of the simulation '''
    simulation = sim.Simulation()

    mn1 = agent.Manufacturer()
    mn1.id = 0
    mn1.num_of_lines = 20
    mn1.line_capacity = 20
    mn1.num_active_lines = 20

    mn2 = agent.Manufacturer()
    mn2.id = 1
    mn2.num_of_lines = 20
    mn2.line_capacity = 20
    mn2.num_active_lines = 20

    ds1 = agent.Distributor()
    ds1.id = 2

    ds2 = agent.Distributor()
    ds2.id = 3

    hc1 = agent.HealthCenter()
    hc1.id = 4

    hc2 = agent.HealthCenter()
    hc2.id = 5

    hc1.upstream_nodes.extend([ds1, ds2])
    hc2.upstream_nodes.extend([ds2])
    ds1.upstream_nodes.extend([mn2])
    ds1.downstream_nodes.extend([hc1])
    ds2.upstream_nodes.extend([mn1, mn2])
    ds2.downstream_nodes.extend([hc1, hc2])
    mn1.downstream_nodes.extend([ds2])
    mn2.downstream_nodes.extend([ds1, ds2])

    # hc1.upstream_nodes.extend([ds1, ds2])
    # hc2.upstream_nodes.extend([ds1, ds2])
    # ds1.upstream_nodes.extend([mn1, mn2])
    # ds1.downstream_nodes.extend([hc1, hc2])
    # ds2.upstream_nodes.extend([mn1, mn2])
    # ds2.downstream_nodes.extend([hc1, hc2])
    # mn1.downstream_nodes.extend([ds1, ds2])
    # mn2.downstream_nodes.extend([ds1, ds2])

    simulation.manufacturers.extend([mn1, mn2])
    simulation.distributors.extend([ds1, ds2])
    simulation.health_centers.extend([hc1, hc2])

    net = network.Network(6)
    info_net = network.Network(6)
    for i in range(6):
        for j in range(6):
            net.connectivity[i, j] = 1
            info_net.connectivity[i, j] = 0
    simulation.network = net
    simulation.info_network = info_net

    decision_maker = dmaker.PerAgentDecisionMaker()

    hc1_dmaker = dmaker.UrgentFirstHCDecisionMaker(hc1)
    decision_maker.add_decision_maker(hc1_dmaker)

    hc2_dmaker = dmaker.UrgentFirstHCDecisionMaker(hc2)
    decision_maker.add_decision_maker(hc2_dmaker)

    ds1_dmaker = dmaker.SimpleDSDecisionMaker(ds1)
    decision_maker.add_decision_maker(ds1_dmaker)

    ds2_dmaker = dmaker.SimpleDSDecisionMaker(ds2)
    decision_maker.add_decision_maker(ds2_dmaker)

    mn1_dmaker = dmaker.SimpleMNDecisionMaker(mn1)
    decision_maker.add_decision_maker(mn1_dmaker)

    mn2_dmaker = dmaker.SimpleMNDecisionMaker(mn2)
    decision_maker.add_decision_maker(mn2_dmaker)

    hc1.up_to_level = 279
    hc2.up_to_level = 279
    ds1.up_to_level = 140
    ds2.up_to_level = 404
    mn1.up_to_level = 202
    mn2.up_to_level = 329

    patient_model = pmodel.NormalDistPatientModel([hc1, hc2])
    simulation.patient_model = patient_model

    runner = sim_runner.SimulationRunner(simulation, decision_maker)

    return ReturnValue(simulation, runner)


