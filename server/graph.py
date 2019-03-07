import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import pchip
# from game import build_game
matplotlib.use('agg')


def beer_game_graph(data, chart_path, user_id):

    if not os.path.exists(os.path.join(chart_path + "/" + user_id)):
        os.makedirs(os.path.join(chart_path + "/" + user_id))

    data = data.drop_duplicates()
    data = data[data['time'] > 0]
    data = data[data['time'] < 21]
    data = data.drop(['unit'], axis=1)
    inv_data = data[data['item'] == 'inventory']
    order_data = data[data['item'] == 'order'].drop_duplicates()
    demand = data[data['item'] == 'demand']
    production = data[data['item'] == 'in_production']
    x_new = np.asarray(map(int, order_data[order_data['agent'] == 'MN'].time.values), dtype=np.float32)
    x_smooth = np.linspace(min(x_new), max(x_new), 300)

    '''----------------------------------------INVENTORY_CHART--------------------------------------------'''

    with plt.xkcd():
        y_new1 = np.asarray(map(float, inv_data[inv_data['agent'] == 'MN'].value.values), dtype=np.float32)
        y_new2 = np.asarray(map(float, inv_data[inv_data['agent'] == 'DS'].value.values), dtype=np.float32)
        y_new3 = np.asarray(map(float, inv_data[inv_data['agent'] == 'WS'].value.values), dtype=np.float32)
        y_new4 = np.asarray(map(float, inv_data[inv_data['agent'] == 'HC'].value.values), dtype=np.float32)
        pch1 = pchip(x_new, y_new1)
        pch2 = pchip(x_new, y_new2)
        pch3 = pchip(x_new, y_new3)
        pch4 = pchip(x_new, y_new4)
        plt.figure(figsize=(8, 5))
        ax1 = plt.plot(x_smooth, pch1(x_smooth), label='Manufacturer')
        ax2 = plt.plot(x_smooth, pch2(x_smooth), label='Distributor')
        ax3 = plt.plot(x_smooth, pch3(x_smooth), label='Wholesaler (You)')
        ax4 = plt.plot(x_smooth, pch4(x_smooth), label='Health-center')
        plt.legend(loc='lower right', numpoints=1, prop={'size': 10})
        plt.xlabel('Time (Week)')
        plt.ylabel('Quantity')
        plt.title('Inventory level vs. Time')
        plt.xticks(np.arange(min(x_new), max(x_new) + 1, 1.0))
        plt.margins(x=0)
        plt.grid(True, lw=0.15, zorder=0)
        plt.savefig(os.path.join(chart_path + "/" + user_id + "/beer_game_inventory_chart.png"),
                    bbox_inches='tight', dpi=300)
        plt.clf()

        '''----------------------------------------ORDER_QUANTITY--------------------------------------------'''

        y_new1 = np.asarray(map(float, production[production['agent'] == 'MN'].value.values), dtype=np.float32)
        y_new2 = np.asarray(map(float, order_data[order_data['agent'] == 'DS'].value.values), dtype=np.float32)
        y_new3 = np.asarray(map(float, order_data[order_data['agent'] == 'WS'].value.values), dtype=np.float32)
        y_new4 = np.asarray(map(float, order_data[order_data['agent'] == 'HC'].value.values), dtype=np.float32)
        y_new5 = np.asarray(map(float, demand[demand['agent'] == 'HC'].value.values), dtype=np.float32)
        pch1 = pchip(x_new, y_new1)
        pch2 = pchip(x_new, y_new2)
        pch3 = pchip(x_new, y_new3)
        pch4 = pchip(x_new, y_new4)
        pch5 = pchip(x_new, y_new5)
        plt.figure(figsize=(8, 5))
        ax1 = plt.plot(x_smooth, pch1(x_smooth), label='Manufacturer')
        ax2 = plt.plot(x_smooth, pch2(x_smooth), label='Distributor')
        ax3 = plt.plot(x_smooth, pch3(x_smooth), label='Wholesaler (You)')
        ax4 = plt.plot(x_smooth, pch4(x_smooth), label='Health-center')
        ax5 = plt.plot(x_smooth, pch5(x_smooth), label='Demand')
        plt.legend(loc='upper left', numpoints=1, prop={'size': 10})
        plt.xlabel('Time (Week)')
        plt.ylabel('Quantity')
        plt.title('Order/Production Quantity vs. Time')
        plt.xticks(np.arange(min(x_new), max(x_new) + 1, 1.0))
        plt.ylim(bottom=0)
        plt.grid(True, lw=0.15, zorder=0)
        plt.margins(x=0)
        plt.savefig(os.path.join(chart_path + "/" + user_id + "/beer_game_order_quantity.png"),
                    bbox_inches='tight', dpi=300)
        plt.clf()

        '''----------------------------------------CUMULATIVE_COST--------------------------------------------'''

        inv_data.loc[inv_data['value'] > 0, 'cost'] = inv_data.loc[inv_data['value'] > 0, 'value'] / 2
        inv_data.loc[inv_data['value'] <= 0, 'cost'] = abs(inv_data.loc[inv_data['value'] <= 0, 'value'])
        inv_data['cost'] = inv_data['cost'].astype(float)
        inv_data['cum_cost'] = inv_data.groupby('agent')['cost'].cumsum()
        y_new1 = np.asarray(map(float, inv_data[inv_data['agent'] == 'MN'].cum_cost.values), dtype=np.float32)
        y_new2 = np.asarray(map(float, inv_data[inv_data['agent'] == 'DS'].cum_cost.values), dtype=np.float32)
        y_new3 = np.asarray(map(float, inv_data[inv_data['agent'] == 'WS'].cum_cost.values), dtype=np.float32)
        y_new4 = np.asarray(map(float, inv_data[inv_data['agent'] == 'HC'].cum_cost.values), dtype=np.float32)
        pch1 = pchip(x_new, y_new1)
        pch2 = pchip(x_new, y_new2)
        pch3 = pchip(x_new, y_new3)
        pch4 = pchip(x_new, y_new4)
        plt.figure(figsize=(8, 5))
        ax1 = plt.plot(x_smooth, pch1(x_smooth), label='Manufacturer')
        ax2 = plt.plot(x_smooth, pch2(x_smooth), label='Distributor')
        ax3 = plt.plot(x_smooth, pch3(x_smooth), label='Wholesaler (You)')
        ax4 = plt.plot(x_smooth, pch4(x_smooth), label='Health-center')
        plt.legend(loc='upper left', numpoints=1, prop={'size': 10})
        plt.xlabel('Time (Week)')
        plt.ylabel('Cumulative Cost ($)')
        plt.title('Cumulative Cost vs. Time')
        plt.xticks(np.arange(min(x_new), max(x_new) + 1, 1.0))
        plt.margins(x=0)
        plt.grid(True, lw=0.15, zorder=0)
        plt.savefig(os.path.join(chart_path + "/" + user_id + "/beer_game_cum_cost.png"),
                    bbox_inches='tight', dpi=300)
        plt.clf()


def graph(game_data, chart_path, user_id, agent):

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

    if not os.path.exists(os.path.join(chart_path + "/" + user_id)):
        os.makedirs(os.path.join(chart_path + "/" + user_id))

    data = game_data[game_data['agent'] == agent]

    hc1_inv = data[data['item'] == 'inventory']
    hc1_up = data[data['item'] == 'urgent']
    hc1_nup = data[data['item'] == 'non_urgent']
    hc1_order = data[data['item'] == 'order']
    hc1_order_ds1 = data[data['item'] == 'order_ds1']
    hc1_order_ds2 = data[data['item'] == 'order_ds2']
    hc1_on_order_ds1 = data[data['item'] == 'on_order_ds1']
    hc1_on_order_ds2 = data[data['item'] == 'on_order_ds2']
    hc1_rec_ds1 = data[data['item'] == 'rec_ds1']
    hc1_rec_ds2 = data[data['item'] == 'rec_ds2']
    hc1_rec = hc1_rec_ds1.copy()
    hc1_rec['value'] = hc1_rec_ds1['value'].values + hc1_rec_ds2['value'].values
    hc1_on_order = hc1_on_order_ds1.copy()
    hc1_on_order['value'] = hc1_on_order_ds1['value'].values + hc1_on_order_ds2['value'].values

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
    plt.savefig(os.path.join(chart_path + "/" + user_id + "/drug_shortage_inventory_chart_1.png"), bbox_inches='tight')
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
    # plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Number of Patients')
    plt.title('Patients History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.3)
    plt.xticks(np.arange(min(hc1_up.time.values), max(hc1_up.time.values) + 1, 1.0))
    # plt.savefig(os.path.join(chart_path + "/patient_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/" + user_id + "/drug_shortage_patient_history_1.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------DS1_ORDER_HISTORY--------------------------------------------'''

    plt.figure(3)
    ax1 = plt.bar(hc1_order_ds1.time.values-width/2, hc1_order_ds1.value.values, label='Ordered', color='c', zorder=5,
                  width=width, edgecolor='black')
    ax2 = plt.bar(hc1_rec_ds1.time.values+width/2, hc1_rec_ds1.value.values, label='Received', color='r', zorder=5,
                  width=width, edgecolor='black')
    ax3 = plt.plot(hc1_on_order_ds1.time.values, hc1_on_order_ds1.value.values, label='On-Order', color='orange',
                   zorder=5)
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 1 Order and Shipment History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(hc1_order_ds1.time.values), max(hc1_order_ds1.time.values) + 2, 1.0))
    # plt.savefig(os.path.join(chart_path + "/ds1_order_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/" + user_id + "/drug_shortage_ds_order_history_1.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------DS2_ORDER_HISTORY--------------------------------------------'''

    plt.figure(4)
    ax1 = plt.bar(hc1_order_ds2.time.values-width/2, hc1_order_ds2.value.values, label='Ordered', color='c', zorder=5,
                  width=width, edgecolor='black')
    ax2 = plt.bar(hc1_rec_ds2.time.values+width/2, hc1_rec_ds2.value.values, label='Received', color='r', zorder=5,
                  width=width, edgecolor='black')
    ax3 = plt.plot(hc1_on_order_ds2.time.values, hc1_on_order_ds2.value.values, label='On-Order', color='orange',
                   zorder=5)
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 2 Order and Shipment History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(hc1_order_ds2.time.values), max(hc1_order_ds2.time.values) + 2, 1.0))
    # plt.savefig(os.path.join(chart_path + "/ds2_order_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/" + user_id + "/drug_shortage_ds_order_history_2.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------TOTAL_ORDER_HISTORY--------------------------------------------'''

    plt.figure(5)
    ax1 = plt.bar(hc1_order.time.values-width/2, hc1_order.value.values, label='Total Ordered', color='c', zorder=5,
                  width=width, edgecolor='black')
    ax2 = plt.bar(hc1_rec.time.values+width/2, hc1_rec.value.values, label='Total Received', color='r', zorder=5,
                  width=width, edgecolor='black')
    ax3 = plt.plot(hc1_on_order.time.values, hc1_on_order.value.values, label='Total On-Order', color='orange',
                   zorder=5)
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Order and Shipment History')
    plt.grid(True, lw=0.5, zorder=0, color='w')
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(hc1_order.time.values), max(hc1_order.time.values) + 2, 1.0))
    # plt.savefig(os.path.join(chart_path + "/order_history_" + user_id + ".png"), bbox_inches='tight')
    plt.savefig(os.path.join(chart_path + "/" + user_id + "/drug_shortage_order_history_1.png"), bbox_inches='tight')
    plt.clf()


# path2 = os.path.join(os.path.abspath('..'), 'client/charts')
# game = build_game()
# graph(game, path2, user_id="0f27ae9d-31fa-48cf-bbe1-33d0301af699")
