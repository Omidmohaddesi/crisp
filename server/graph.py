import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# from game import build_game


def graph(game_data, chart_path, user_id):

    # data_columns = ['time', 'agent', 'item', 'value', 'unit']
    # data = pd.DataFrame(columns=data_columns)
    # for i in range(1, 10):
    #     game.runner.next_cycle()
    #
    #     data = data.append(pd.DataFrame([
    #         [i, 'hc1', 'inventory', game.simulation.health_centers[0].inventory_level(), ''],
    #         [i, 'hc1', 'urgent', game.simulation.health_centers[0].urgent, ''],
    #         [i, 'hc1', 'non_urgent', game.simulation.health_centers[0].non_urgent, ''],
    #         [i, 'hc1', 'patients', game.simulation.health_centers[0].urgent +
    #          game.simulation.health_centers[0].non_urgent, ''],
    #         [i, 'hc1', 'order', sum(
    #             order.amount for order in game.simulation.health_centers[0].get_history_item(i)['order']), ''],
    #         [i, 'hc1', 'order_ds1', sum(
    #             order.amount for order in game.simulation.health_centers[0].get_history_item(i)['order']
    #             if order.dst.id == 2), ''],
    #         [i, 'hc1', 'order_ds2', sum(
    #             order.amount for order in game.simulation.health_centers[0].get_history_item(i)['order']
    #             if order.dst.id == 3), ''],
    #         [i, 'hc1', 'on_order_ds1', sum(game.simulation.health_centers[0].on_order[j].amount
    #                                        for j in range(0, len(game.simulation.health_centers[0].on_order))
    #                                        if game.simulation.health_centers[0].on_order[j].dst.id == 2), ''],
    #         [i, 'hc1', 'on_order_ds2', sum(game.simulation.health_centers[0].on_order[j].amount
    #                                        for j in range(0, len(game.simulation.health_centers[0].on_order))
    #                                        if game.simulation.health_centers[0].on_order[j].dst.id == 3), ''],
    #         [i, 'hc1', 'rec_ds1',
    #          sum(game.simulation.health_centers[0].get_history_item(i)['delivery'][j]["item"].amount
    #              for j in range(0, len(game.simulation.health_centers[0].get_history_item(i)
    #                                    ['delivery']))
    #              if game.simulation.health_centers[0].get_history_item(i)
    #              ['delivery'][j]["src"].id == 2), ''],
    #         [i, 'hc1', 'rec_ds2',
    #          sum(game.simulation.health_centers[0].get_history_item(i)['delivery'][j]["item"].amount
    #              for j in range(0, len(game.simulation.health_centers[0].get_history_item(i)
    #                                    ['delivery']))
    #              if game.simulation.health_centers[0].get_history_item(i)
    #              ['delivery'][j]["src"].id == 3), ''],
    #     ], columns=data_columns))

    data = game_data[game_data['agent'] == 'hc_4']

    hc1_inv = data[data['item'] == 'inventory']
    hc1_up = data[data['item'] == 'urgent']
    hc1_nup = data[data['item'] == 'non_urgent']
    # hc1_order = data[data['item'] == 'on_order']
    hc1_order_ds1 = data[data['item'] == 'on_order_ds1']
    hc1_order_ds2 = data[data['item'] == 'on_order_ds2']
    hc1_rec_ds1 = data[data['item'] == 'rec_ds1']
    hc1_rec_ds2 = data[data['item'] == 'rec_ds2']
    hc1_rec = hc1_rec_ds1.copy()
    hc1_rec['value'] = hc1_rec_ds1['value'].values + hc1_rec_ds2['value'].values
    hc1_order = hc1_order_ds1.copy()
    hc1_order['value'] = hc1_order_ds1['value'].values + hc1_order_ds1['value'].values

    width = 0.35

    '''----------------------------------------INVENTORY_CHART--------------------------------------------'''

    plt.xkcd()
    plt.figure(1)
    plt.plot(hc1_inv.time.values, hc1_inv.value.values)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Inventory Level')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.xticks(np.arange(min(hc1_inv.time.values), max(hc1_inv.time.values) + 1, 1.0))
    # plt.savefig(os.path.join(chart_path + "/inventory_chart_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/Inventory_Chart.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------PATIENT_HISTORY--------------------------------------------'''

    plt.figure(2)
    ax1 = plt.bar(hc1_nup.time.values, hc1_nup.value.values, label='Non-Urgent', color='b', zorder=5, edgecolor='black',
                  width=1.5*width)
    ax2 = plt.bar(hc1_up.time.values, hc1_up.value.values, bottom=hc1_nup.value.values, label='Urgent', color='r', zorder=5,
                  edgecolor='black', width=1.5*width)
    # plt.plot(t2, nup, label='Non-Urgent', color='b')
    # plt.plot(t2, up, label='Urgent', color='r')
    # plt.plot(t, tp, label='Total')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Number of Patients')
    plt.title('Patients History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.3)
    plt.xticks(np.arange(min(hc1_up.time.values), max(hc1_up.time.values) + 1, 1.0))
    # plt.savefig(os.path.join(chart_path + "/patient_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/Patient_History.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------DS1_ORDER_HISTORY--------------------------------------------'''

    plt.figure(3)
    ax1 = plt.bar(hc1_order_ds1.time.values-width/2, hc1_order_ds1.value.values, label='On-Order', color='c', zorder=5,
                  width=width, edgecolor='black')
    ax2 = plt.bar(hc1_rec_ds1.time.values+width/2, hc1_rec_ds1.value.values, label='Received', color='r', zorder=5,
                  width=width, edgecolor='black')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 1 Order History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(hc1_order_ds1.time.values), max(hc1_order_ds1.time.values) + 1, 1.0))
    # plt.savefig(os.path.join(chart_path + "/ds1_order_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/DS1_Order_History.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------DS2_ORDER_HISTORY--------------------------------------------'''

    plt.figure(4)
    ax1 = plt.bar(hc1_order_ds2.time.values-width/2, hc1_order_ds2.value.values, label='On-Order', color='c', zorder=5,
                  width=width, edgecolor='black')
    ax2 = plt.bar(hc1_rec_ds2.time.values+width/2, hc1_rec_ds2.value.values, label='Received', color='r', zorder=5,
                  width=width, edgecolor='black')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 2 Order History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(hc1_order_ds2.time.values), max(hc1_order_ds2.time.values) + 1, 1.0))
    # plt.savefig(os.path.join(chart_path + "/ds2_order_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/DS2_Order_History.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------TOTAL_ORDER_HISTORY--------------------------------------------'''

    plt.figure(5)
    ax1 = plt.bar(hc1_order.time.values-width/2, hc1_order.value.values, label='Total On-Order', color='c', zorder=5,
                  width=width, edgecolor='black')
    ax2 = plt.bar(hc1_rec.time.values+width/2, hc1_rec.value.values, label='Total Received', color='r', zorder=5,
                  width=width, edgecolor='black')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Order History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(hc1_order.time.values), max(hc1_order.time.values) + 1, 1.0))
    # plt.savefig(os.path.join(chart_path + "/order_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/Order_History.png"), bbox_inches='tight')
    plt.clf()


# path2 = os.path.join(os.path.abspath('..'), 'client/charts')
# game = build_game()
# graph(game, path2, user_id="0f27ae9d-31fa-48cf-bbe1-33d0301af699")
