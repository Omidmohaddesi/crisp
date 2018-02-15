import json
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


# def graph(jsonfile, dec_file, output_dir, chart_path, week_no, player_id):           # jsonfile = simulator_output.json
def graph(game, dec_file, output_dir, chart_path, week_no, player_id):  # jsonfile = simulator_output.json


    simjsonfile = open(jsonfile)
    decision = open(dec_file)

    simdata = json.load(simjsonfile)["health_centers"][0]  # This id has to be set to the Hospital we want!!
                                                                # 0: id == 4
                                                                # 1: id == 5

    inv = [0 for i in range(10)]
    up = [0 for i in range(10)]
    nup = [0 for i in range(10)]
    tp = [0 for i in range(10)]
    order = [0 for i in range(10)]
    order_MN1 = [0 for i in range(10)]
    order_DS1 = [0 for i in range(10)]
    order_DS2 = [0 for i in range(10)]
    rec = [0 for i in range(10)]
    rec_MN1 = [0 for i in range(10)]
    rec_DS1 = [0 for i in range(10)]
    rec_DS2 = [0 for i in range(10)]

    t = np.arange(week_no - 9, week_no, 1)

    for i in range(week_no - 10, week_no - 1):
        order_amount = 0
        if 'order' in game.get_current_history_item(i + 1):
            order_amount = sum(order.amount for order in game.get_current_history_item(i + 1)['order'])






    for i in range(1, 10):












    dec_data1 = json.load(decision)
    for i in range(len(dec_data1)):
        if dec_data1[i]['id'] == player_id:
            dec_data = dec_data1[i].copy()

    # minimum = min(time["time"] for time in simdata["history"])
    minimum = 81
    maximum = max(time["time"] for time in simdata["history"])

    inv = [0 for i in range(maximum-minimum+1)]
    up = [0 for i in range(maximum-minimum+1)]
    nup = [0 for i in range(maximum-minimum+1)]
    tp = [0 for i in range(maximum-minimum+1)]
    order = [0 for i in range(maximum-minimum+1)]
    order_MN1 = [0 for i in range(maximum-minimum+1)]
    order_DS1 = [0 for i in range(maximum-minimum+1)]
    order_DS2 = [0 for i in range(maximum-minimum+1)]
    rec = [0 for i in range(maximum-minimum+1)]
    rec_MN1 = [0 for i in range(maximum-minimum+1)]
    rec_DS1 = [0 for i in range(maximum-minimum+1)]
    rec_DS2 = [0 for i in range(maximum-minimum+1)]

    t = np.arange(minimum, maximum + 1, 1)

    for i in t:
        for k in simdata["history"]:
            if i == k["time"]:
                inv[i - minimum] = int(k["Inventory"])
                up[i - minimum] = int(k["patient"][0])
                nup[i - minimum] = int(k["patient"][1])
                # tp[i-1] = sum(k["patient"])
                if "delivery" in k:
                    rec[i - minimum] = int(sum(j["item"]["amount"] for j in k["delivery"]))
                    # rec_MN1[i - minimum] = int(sum(j["item"]["amount"] for j in k["delivery"] if j["src"] == 0))
                    rec_DS1[i - minimum] = int(sum(j["item"]["amount"] for j in k["delivery"] if j["src"] == 2))
                    rec_DS2[i - minimum] = int(sum(j["item"]["amount"] for j in k["delivery"] if j["src"] == 3))

    for i in np.arange(minimum, minimum + 10):
        for k in simdata["history"]:
            if i == k["time"]:
                if "order" in k:
                    order[i - minimum] = int(sum(l["amount"] for l in k["order"]))
                    # order_MN1[i - minimum] = int(sum(l["amount"] for l in k["order"] if l["destination"] == 0))
                    order_DS1[i - minimum] = int(sum(l["amount"] for l in k["order"] if l["destination"] == 2))
                    order_DS2[i - minimum] = int(sum(l["amount"] for l in k["order"] if l["destination"] == 3))

    for i in range(10, 20):
        order_DS1[i] = dec_data["history"][i - 10]['order_DS1']
        order_DS2[i] = dec_data["history"][i - 10]['order_DS2']
        order[i] = dec_data["history"][i - 10]['order_total']
        if order_DS1[i - 1] == 0:
            rec_DS1[i] = 0
        if order_DS2[i - 1] == 0:
            rec_DS2[i] = 0
        if order[i - 1] == 0:
            rec[i] = 0

    on_order_DS1 = (order_DS1[week_no - 2] + order_DS1[week_no - 3] + order_DS1[week_no - 4]) - \
                   (rec_DS1[week_no - 1] + rec_DS1[week_no - 2] + rec_DS1[week_no - 3])
    if on_order_DS1 < 0:
        on_order_DS1 = 0

    on_order_DS2 = (order_DS2[week_no - 2] + order_DS2[week_no - 3] + order_DS2[week_no - 4]) - \
                   (rec_DS2[week_no - 1] + rec_DS2[week_no - 2] + rec_DS2[week_no - 3])
    if on_order_DS2 < 0:
        on_order_DS2 = 0

    with open(os.path.join(output_dir + '/parameters.json'), "w") as jsonfile:
        json.dump({"week": week_no, "inv": inv[week_no - 1], "up": up[week_no - 1], "nup": nup[week_no - 1],
                   "on_order_DS1": on_order_DS1, "on_order_DS2": on_order_DS2,
                   "rec_DS1": rec_DS1[week_no - 1], "rec_DS2": rec_DS2[week_no - 1]}, jsonfile, indent=3)

    # print("time:\t\t", t)
    # print("Urgent:\t\t", up)
    # print("Non-Urgent:\t", nup)
    # print("Inv:\t\t", inv)
    # print("Order_DS1:\t", order_DS1)
    # print("Order_DS2:\t", order_DS2)
    # print("Order_Total:\t", order)
    # print("rec_DS1:\t", rec_DS1)
    # print("rec_DS2:\t", rec_DS2)

    t2 = np.arange(week_no - 10, week_no, 1)
    inv = inv[week_no - 11:week_no - 1]
    up = up[week_no - 11:week_no - 1]
    nup = nup[week_no - 11:week_no - 1]
    order = order[week_no - 11:week_no - 1]
    order_DS1 = order_DS1[week_no - 11:week_no - 1]
    order_DS2 = order_DS2[week_no - 11:week_no - 1]
    rec = rec[week_no - 11:week_no - 1]
    rec_DS1 = rec_DS1[week_no - 11:week_no - 1]
    rec_DS2 = rec_DS2[week_no - 11:week_no - 1]

    if week_no >= 12:
        inv[-1] = dec_data["history"][dec_data["current_week"]-12]['inv']
        # order_DS1[-1] = dec_data['order_DS1']
        # order_DS2[-1] = dec_data['order_DS2']
        # order[-1] = dec_data['order_total']

    width = 0.35

    '''----------------------------------------INVENTORY_CHART--------------------------------------------'''
    plt.xkcd()
    plt.figure(1)
    plt.plot(t2, inv)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Inventory Level')
    plt.grid(True, lw=0.5, zorder=0)
    plt.xticks(np.arange(min(t2), max(t2) + 1, 1.0))
    plt.savefig(os.path.join(chart_path + "/Inventory_Chart.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------PATIENT_HISTORY--------------------------------------------'''

    plt.figure(3)
    ax1 = plt.bar(t2, nup, label='Non-Urgent', color='b', zorder=5, edgecolor='black', width=1.5*width)
    ax2 = plt.bar(t2, up, bottom=nup, label='Urgent', color='r', zorder=5, edgecolor='black', width=1.5*width)
    # plt.plot(t2, nup, label='Non-Urgent', color='b')
    # plt.plot(t2, up, label='Urgent', color='r')
    # plt.plot(t, tp, label='Total')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Number of Patients')
    plt.title('Patients History')
    plt.grid(True, lw=0.5, zorder=0)
    plt.margins(y=0.3)
    plt.xticks(np.arange(min(t2), max(t2) + 1, 1.0))
    plt.savefig(os.path.join(chart_path + "/Patient_History.png"), bbox_inches='tight')
    plt.clf()

    '''----------------------------------------TOTAL_ORDER_HISTORY--------------------------------------------'''

    plt.figure(4)
    # plt.subplot(211)
    # plt.plot(t2, order, label='Total Ordered')
    # plt.legend(loc='upper left')
    # plt.ylabel('Quantity')
    # plt.title('Order History')
    # plt.grid(True, lw=0.5, zorder=0)
    #
    # plt.subplot(212)
    # plt.plot(t2, rec, label='Total Received', color='r')
    # plt.legend(loc='upper left')
    # plt.xlabel('time (Week)')
    # plt.ylabel('Quantity')
    # plt.grid(True, lw=0.5, zorder=0)

    ax1 = plt.bar(t2-width/2, order, label='Total Ordered', color='c', zorder=5, width=width, edgecolor='black')
    ax2 = plt.bar(t2+width/2, rec, label='Total Received', color='r', zorder=5, width=width, edgecolor='black')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Order History')
    plt.grid(True, lw=0.5, zorder=0)
    plt.xticks(np.arange(min(t2), max(t2) + 1, 1.0))
    # autolabel(ax1)
    # autolabel(ax2)
    plt.margins(y=0.2)
    plt.savefig(os.path.join(chart_path + "/Order_History.png"), bbox_inches='tight')
    plt.clf()

    '''

    y = np.row_stack((order, rec))
    fig, ax = plt.subplots()
    stack_coll = ax.stackplot(t, y, zorder=5)
    label_list = ['Total Received', 'Total Ordered']
    proxy_rects = [Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in stack_coll]
    ax.legend(proxy_rects, label_list, loc='upper left')
    plt.xlabel('time (Week)')
    plt.ylabel('Quantity')
    plt.title('Order History')
    plt.grid(True, lw=0.5, zorder=0, linestyle='dashed')
    plt.savefig(os.path.join(chart_path + "/Order_History.png"), bbox_inches='tight')
    '''

    '''----------------------------------------MN1_ORDER_HISTORY--------------------------------------------'''

    # plt.figure(6)
    # ax1 = plt.bar(t2, order_MN1, label='Ordered', color='c', zorder=5)
    # ax2 = plt.bar(t2, rec_MN1, bottom=order_MN1, label='Received', color='r', zorder=5)
    # plt.legend(loc='upper left', numpoints=1)
    # plt.xlabel('time (Week)')
    # plt.ylabel('Quantity')
    # plt.title('Manufacturer 1 Order History')
    # plt.grid(True, lw=0.5, zorder=0)

    '''
    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        plt.text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1, ha="center", va="center", color="black",
                 fontsize=9)
        plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2, ha="center", va="center", color="black",
                 fontsize=9)
    '''
    '''
    y = np.row_stack((order_MN1, rec_MN1))
    fig, ax = plt.subplots()
    stack_coll = ax.stackplot(t, y, zorder=5)
    label_list = ['Received', 'Ordered']
    proxy_rects = [Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in stack_coll]
    ax.legend(proxy_rects, label_list, loc='upper left')
    plt.xlabel('time (Week)')
    plt.ylabel('Quantity')
    plt.title('Manufacturer 1 Order History')
    plt.grid(True, lw=0.5, zorder=0, linestyle='dashed')
    '''

    # plt.savefig(os.path.join(chart_path + "/MN1_Order_History.png"), bbox_inches='tight')


    '''----------------------------------------DS1_ORDER_HISTORY--------------------------------------------'''

    plt.figure(7)
    ax1 = plt.bar(t2-width/2, order_DS1, label='Ordered', color='c', zorder=5, width=width, edgecolor='black')
    ax2 = plt.bar(t2+width/2, rec_DS1, label='Received', color='r', zorder=5, width=width, edgecolor='black')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 1 Order History')
    plt.grid(True, lw=0.5, zorder=0)
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(t2), max(t2) + 1, 1.0))

    '''
    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        plt.text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1, ha="center", va="center", color="black",
                 fontsize=9)
        plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2, ha="center", va="center", color="black",
                 fontsize=9)
    '''
    plt.savefig(os.path.join(chart_path + "/DS1_Order_History.png"), bbox_inches='tight')
    plt.clf()

    '''
    y = np.row_stack((order_DS1, rec_DS1))
    fig, ax = plt.subplots()
    stack_coll = ax.stackplot(t, y, zorder=5)
    label_list = ['Received', 'Ordered']
    proxy_rects = [Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in stack_coll]
    ax.legend(proxy_rects, label_list, loc='upper left')
    plt.xlabel('time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 1 Order History')
    plt.grid(True, lw=0.5, zorder=0, linestyle='dashed')
    plt.savefig(os.path.join(chart_path + "/DS1_Order_History.png"), bbox_inches='tight')
    '''

    '''----------------------------------------DS2_ORDER_HISTORY--------------------------------------------'''


    plt.figure(8)
    ax1 = plt.bar(t2-width/2, order_DS2, label='Ordered', color='c', zorder=5, width=width, edgecolor='black')
    ax2 = plt.bar(t2+width/2, rec_DS2, label='Received', color='r', zorder=5, width=width, edgecolor='black')
    plt.legend(loc='upper left', numpoints=1)
    plt.xlabel('Time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 2 Order History')
    plt.grid(True, lw=0.5, zorder=0)
    plt.margins(y=0.2)
    plt.xticks(np.arange(min(t2), max(t2) + 1, 1.0))

    '''
    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        plt.text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1, ha="center", va="center", color="black",
                 fontsize=9)
        plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2, ha="center", va="center", color="black",
                 fontsize=9)
    '''
    plt.savefig(os.path.join(chart_path + "/DS2_Order_History.png"), bbox_inches='tight')
    plt.clf()

    '''
    y = np.row_stack((order_DS2, rec_DS2))
    fig, ax = plt.subplots()
    stack_coll = ax.stackplot(t, y, zorder=5)
    label_list = ['Received', 'Ordered']
    proxy_rects = [Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in stack_coll]
    ax.legend(proxy_rects, label_list, loc='upper left')
    plt.xlabel('time (Week)')
    plt.ylabel('Quantity')
    plt.title('Distributor 2 Order History')
    plt.grid(True, lw=0.5, zorder=0, linestyle='dashed')
    plt.savefig(os.path.join(chart_path + "/DS2_Order_History.png"), bbox_inches='tight')
    '''

    # IN ORDER TO ADD DATA LABELS IN THE MIDDLE OF THE BAR GRAPH:
    '''
    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        plt.text(r1.get_x() + r1.get_width() / 2., h1 / 2., "%d" % h1, ha="center", va="center", color="black",
                 fontsize=9)
        plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., "%d" % h2, ha="center", va="center", color="black",
                 fontsize=9)
    '''
    '''
    plt.xkcd()
    plt.figure(2)
    plt.plot(t, inv)
    plt.xlabel('time (Week)')
    plt.ylabel('Inventory')
    plt.title('Hospital Inventory')
    plt.grid(True, lw=0.5, zorder=0)
    plt.savefig(os.path.join(chart_path + "/Inventory_Chart_Sketchy.png"), bbox_inches='tight')
    '''

    par_data = open(os.path.join(output_dir + '/parameters.json'))
    data = json.load(par_data)

    return data
