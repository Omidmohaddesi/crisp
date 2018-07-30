"""simulation_builder provides utility classes to build games"""

import simulator.simulation as sim
import simulator.agent as agent
import simulator.network as network
import simulator.simulation_runner as sim_runner
import simulator.decision_maker as dmaker
import simulator.patient_model as pmodel


def build_simulation():
    """ return a new instance of the simulation """
    simulation = sim.Simulation()

    agent_builder = agent.AgentBuilder()
    agent_builder.lead_time = 2
    agent_builder.review_time = 0
    agent_builder.cycle_service_level = 0.9
    agent_builder.history_preserve_time = 20

    mn1 = agent_builder.build("manufacturer")
    mn1.num_of_lines = 20
    mn1.line_capacity = 20
    mn1.num_active_lines = 20

    mn2 = agent_builder.build("manufacturer")
    mn2.num_of_lines = 20
    mn2.line_capacity = 20
    mn2.num_active_lines = 20

    ds1 = agent_builder.build("distributor")
    ds2 = agent_builder.build("distributor")

    hc1 = agent_builder.build("health_center")
    hc2 = agent_builder.build("health_center")

    hc1.upstream_nodes.extend([ds1, ds2])
    hc2.upstream_nodes.extend([ds1, ds2])
    ds1.upstream_nodes.extend([mn1, mn2])
    ds1.downstream_nodes.extend([hc1, hc2])
    ds2.upstream_nodes.extend([mn1, mn2])
    ds2.downstream_nodes.extend([hc1, hc2])
    mn1.downstream_nodes.extend([ds1, ds2])
    mn2.downstream_nodes.extend([ds1, ds2])

    simulation.add_agent(mn1)
    simulation.add_agent(mn2)
    simulation.add_agent(ds1)
    simulation.add_agent(ds2)
    simulation.add_agent(hc1)
    simulation.add_agent(hc2)

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

    return (simulation, runner)
