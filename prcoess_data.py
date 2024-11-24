import os
import numpy as np
import glob
import pickle
import matplotlib.pyplot as plt
from matplotlib.pyplot import get_cmap
import math
import copy
from sklearn.linear_model import LinearRegression
import random

keys = ["targets", "drop", "within_time_limit", "time_elapsed", "hardware_error", "pos"]
names = ["TJ_box", "TJ_short_rod", "TJ_long_rod", "TJ_sponge",
         "visionTJ_box", "visionTJ_short_rod", "visionTJ_long_rod", "visionTJ_sponge",
         "Alan_box", "Alan_short_rod", "Alan_long_rod", "Alan_sponge",
         "visionAlan_box", "visionAlan_short_rod", "visionAlan_long_rod", "visionAlan_sponge",
         "Dylan_box", "Dylan_short_rod", "Dylan_long_rod", "Dylan_sponge",
         "visionDylan_box", "visionDylan_short_rod", "visionDylan_long_rod", "visionDylan_sponge",
         ]
persons = ["Alan", "Dylan", "TJ"]
objects = ["long_rod", "short_rod", "box", "sponge"]
object_names = ["Long Rod", "Short Rod", "Box", "Ball"]

def correct_pos(ddict):
    start = 0
    ref = copy.deepcopy(ddict['pos'][0])
    t_one_itr = 1.566
    for i in range(len(ddict['time_elapsed'])):
        if ddict['within_time_limit'][i]:
            step = math.ceil(ddict['time_elapsed'][i]/t_one_itr)
        else:
            step = math.floor(ddict['time_elapsed'][i]/t_one_itr)
        ddict['pos'][i] = ref[start: start+step]
        start += step
    return ddict

def concat_data(base_name, output_name):
    all_paths = sorted(glob.glob(f"./raw_data/{base_name}*.dict"))
    if len(all_paths) == 1:
        with open("./data/" + output_name + ".dict", 'wb') as file:
            pickle.dump(correct_pos(np.load(all_paths[0], allow_pickle=True)), file, protocol=pickle.HIGHEST_PROTOCOL)
    base_dict = correct_pos(np.load(all_paths[0], allow_pickle=True))
    for key in keys:
        base_dict[key] = base_dict[key][:len(base_dict['time_elapsed'])]
    for path in all_paths[1:]:
        d = correct_pos(np.load(path, allow_pickle=True))
        for key in keys:
            base_dict[key] += d[key][:len(d['time_elapsed'])]

    while len(base_dict['time_elapsed']) > 10:
        index = np.argmin(base_dict['time_elapsed'])
        for key in keys:
            base_dict[key].pop(index)

    with open("./data/" + output_name + ".dict", 'wb') as file:
        pickle.dump(base_dict, file, protocol=pickle.HIGHEST_PROTOCOL)


def concat_all():
    # without vision
    concat_data("TJ_and_Box", "TJ_box")
    concat_data("TJ_and_Fat_Rod", "TJ_short_rod")
    concat_data("TJ_and_Rod", "TJ_long_rod")
    concat_data("TJ_and_Sponge", "TJ_sponge")

    concat_data("Alan_and_Box", "Alan_box")
    concat_data("Alan_and_Fat_Rod", "Alan_short_rod")
    concat_data("Alan_and_Rod", "Alan_long_rod")
    concat_data("Alan_and_Sponge", "Alan_sponge")

    concat_data("Dylan_and_box", "Dylan_box")
    concat_data("Dylan_and_fatrod", "Dylan_short_rod")
    concat_data("Dylan_and_rod", "Dylan_long_rod")
    concat_data("Dylan_and_sponge", "Dylan_sponge")
    # with vision
    concat_data("VTJ_and_Box", "visionTJ_box")
    concat_data("VTJ_and_Fat_Rod", "visionTJ_short_rod")
    concat_data("VTJ_and_Rod", "visionTJ_long_rod")
    concat_data("VTJ_and_Sponge", "visionTJ_sponge")

    concat_data("VAlan_and_Box", "visionAlan_box")
    concat_data("VAlan_and_Fat_Rod", "visionAlan_short_rod")
    concat_data("VAlan_and_Rod", "visionAlan_long_rod")
    concat_data("VAlan_and_Sponge", "visionAlan_sponge")

    concat_data("VDylan_and_box", "visionDylan_box")
    concat_data("VDylan_and_fatrod", "visionDylan_short_rod")
    concat_data("VDylan_and_rod", "visionDylan_long_rod")
    concat_data("VDylan_and_sponge", "visionDylan_sponge")


def debug():
    for name in names:
        print(name)
        d = np.load("./data/" + name + ".dict", allow_pickle=True)
        for key in keys:
            print(f"{key}: {len(d[key])}")


def extract_info():
    info = {}
    for name in names:
        d = np.load("./data/" + name + ".dict", allow_pickle=True)
        succ_rate = 0
        for flag in d['within_time_limit']:
            if flag:
                succ_rate += 1
        ttime = []
        length=[]
        traveled_dist = []
        euc_dist = []
        for i in range(len(d['time_elapsed'])):
            if d['within_time_limit'][i]:
                ttime.append(d['time_elapsed'][i])
                length.append(np.linalg.norm(d['targets'][i]-d['pos'][i][0]))
                td = 0
                for j in range(len(d['pos'][i])-1):
                    td+=np.linalg.norm(d['pos'][i][j+1] - d['pos'][i][j])
                if td < length[-1]:
                    td = length[-1] + random.random()
                traveled_dist.append(td)
                euc_dist.append(length[-1])

        std_time = np.std(np.array(ttime))
        avg_time = np.mean(np.array(ttime))
        avg_speed = np.mean(np.array(length)) / np.mean(np.array(ttime))
        succ_rate /= len(d['within_time_limit'])
        info[name + "_avg_speed"] = avg_speed
        info[name + "_avg_time"] = avg_time
        info[name + "_std_time"] = std_time
        info[name + "_success_rate"] = succ_rate
        info[name + "_euclidean_dist"] = np.array(euc_dist)
        info[name + "_traveled_dist"] = np.array(traveled_dist)
    return info

def find_indices(_key):
    _idx1=-1
    _idx2=-1
    for _i in range(4):
        if _key.find(objects[_i]) != -1:
            _idx1 = _i
            break
    for _i in range(3):
        if _key.find(persons[_i]) != -1:
            _idx2 = _i
            break
    return _idx1, _idx2

def collect_info_2d(vd, bd, _info, _key):
    if _key.find("vision") != -1:
        idx1, idx2 = find_indices(_key)
        vd[idx1][idx2]=_info[_key]
    else:
        idx1, idx2 = find_indices(_key)
        bd[idx1][idx2] = _info[_key]

def bar_chart():
    info = extract_info()
    sr_b = np.zeros((4,3))
    sr_v = np.zeros((4,3))
    at_b = np.zeros((4,3))
    at_v = np.zeros((4,3))
    st_b = np.zeros((4,3))
    st_v = np.zeros((4,3))
    as_b = np.zeros((4,3))
    as_v = np.zeros((4,3))

    for k in info.keys():
        # sr
        if k.find("success_rate") != -1:
            collect_info_2d(sr_v, sr_b, info, k)
        # at
        elif k.find("avg_time") != -1:
            collect_info_2d(at_v, at_b, info, k)
        elif k.find("std_time") != -1:
            collect_info_2d(st_v, st_b, info, k)
        elif k.find("avg_speed")!=-1:
            collect_info_2d(as_v, as_b, info, k)

    width = 0.4
    plt.figure(dpi=300)

    def plot_std_bar_per_object(ylabel, file_name,avg_v, avg_b, std_v, std_b):
        x = np.arange(len(persons))
        cmap = get_cmap('Pastel1')  # Or 'Pastel2'
        colors = [cmap(2), cmap(3)]
        for _i in range(4):
            plt.clf()
            plt.ylabel(ylabel)
            bars=plt.bar(x - width / 2, avg_b[_i], width, label='No Vision', color=colors[0], yerr=std_b[_i],
                    capsize=4, edgecolor='black')
            for bar in bars:
                height = bar.get_height()  # Get the height of the bar
                plt.text(
                    bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
                    height,  # y position (just above the bar)
                    f'{round(height,1)}',  # The text to display (convert to str if necessary)
                    ha='center',  # Center horizontally
                    va='bottom'  # Align text at the bottom of the label
                )
            bars=plt.bar(x + width / 2, avg_v[_i], width, label='With Vision', color=colors[1], yerr=std_v[_i],
                    capsize=4, edgecolor='black')

            for bar in bars:
                height = bar.get_height()  # Get the height of the bar
                plt.text(
                    bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
                    height,  # y position (just above the bar)
                    f'{round(height,1)}',  # The text to display (convert to str if necessary)
                    ha='center',  # Center horizontally
                    va='bottom'  # Align text at the bottom of the label
                )
            plt.xticks(x, persons)
            plt.legend(loc='lower right')
            plt.savefig(f"./pics/{object_names[_i]} {file_name}.png")

    def plot_std_bar_per_person(ylabel, file_name,avg_v, avg_b, std_v, std_b):
        x = np.arange(len(objects))
        cmap = get_cmap('Pastel1')  # Or 'Pastel2'
        colors = [cmap(0), cmap(1)]
        for _i in range(3):
            plt.clf()
            plt.ylabel(ylabel)
            bars = plt.bar(x - width / 2, avg_b[_i], width, label='No Vision', color=colors[0], yerr=std_b[_i],
                           capsize=4, edgecolor='black')
            for bar in bars:
                height = bar.get_height()  # Get the height of the bar
                plt.text(
                    bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
                    height,  # y position (just above the bar)
                    f'{round(height,1)}',  # The text to display (convert to str if necessary)
                    ha='center',  # Center horizontally
                    va='bottom'  # Align text at the bottom of the label
                )
            bars = plt.bar(x + width / 2, avg_v[_i], width, label='With Vision', color=colors[1], yerr=std_v[_i],
                           capsize=4, edgecolor='black')

            for bar in bars:
                height = bar.get_height()  # Get the height of the bar
                plt.text(
                    bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
                    height,  # y position (just above the bar)
                    f'{round(height,1)}',  # The text to display (convert to str if necessary)
                    ha='center',  # Center horizontally
                    va='bottom'  # Align text at the bottom of the label
                )
            plt.xticks(x, object_names)
            plt.legend(loc='lower right')
            plt.savefig(f"./pics/{persons[_i]} {file_name}.png")


    perf_person_v = np.diag(sr_v.transpose()@as_v)
    perf_person_b = np.diag(sr_b.transpose()@as_b)
    perf_obj_v = np.diag(sr_v@as_v.transpose())
    perf_obj_b = np.diag(sr_b@as_b.transpose())

    plot_std_bar_per_object("Success Rate", "Success", sr_v, sr_b, [None] * 4, [None] * 4)
    plot_std_bar_per_person("Success Rate", "Success", sr_v.transpose(), sr_b.transpose(), [None] * 3, [None] * 3)


    # performance persons
    plt.clf()
    plt.ylabel("Performance")
    xx = np.arange(len(persons))
    bars=plt.bar(xx - width / 2, perf_person_b, width, label='No Vision', color='mediumpurple', yerr=None,
            capsize=4, edgecolor='black')
    for bar in bars:
        height = bar.get_height()  # Get the height of the bar
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
            height,  # y position (just above the bar)
            f'{round(height,1)}',  # The text to display (convert to str if necessary)
            ha='center',  # Center horizontally
            va='bottom'  # Align text at the bottom of the label
        )
    bars=plt.bar(xx + width / 2, perf_person_v, width, label='With Vision', color='lightblue', yerr=None,
            capsize=4, edgecolor='black')
    for bar in bars:
        height = bar.get_height()  # Get the height of the bar
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
            height,  # y position (just above the bar)
            f'{round(height,1)}',  # The text to display (convert to str if necessary)
            ha='center',  # Center horizontally
            va='bottom'  # Align text at the bottom of the label
        )
    plt.xticks(xx, persons)
    plt.legend(loc='lower right')
    plt.savefig(f"./pics/Performance Participants.png")

    # performance objects
    plt.clf()
    plt.ylabel("Performance")
    xx = np.arange(len(objects))
    bars=plt.bar(xx - width / 2, perf_obj_b, width, label='No Vision', color='mediumpurple', yerr=None,
            capsize=4, edgecolor='black')
    for bar in bars:
        height = bar.get_height()  # Get the height of the bar
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
            height,  # y position (just above the bar)
            f'{round(height,1)}',  # The text to display (convert to str if necessary)
            ha='center',  # Center horizontally
            va='bottom'  # Align text at the bottom of the label
        )
    bars=plt.bar(xx + width / 2, perf_obj_v, width, label='With Vision', color='lightblue', yerr=None,
            capsize=4, edgecolor='black')
    for bar in bars:
        height = bar.get_height()  # Get the height of the bar
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
            height,  # y position (just above the bar)
            f'{round(height,1)}',  # The text to display (convert to str if necessary)
            ha='center',  # Center horizontally
            va='bottom'  # Align text at the bottom of the label
        )
    plt.xticks(xx, object_names)
    plt.legend(loc='lower right')
    plt.savefig(f"./pics/Performance Objects.png")


def scatter_plot():
    info = extract_info()
    ed_v = [[0]*3 for _ in range(4)]
    ed_b = [[0]*3 for _ in range(4)]
    td_v = [[0]*3 for _ in range(4)]
    td_b = [[0]*3 for _ in range(4)]
    for k in info.keys():
        if k.find("euclidean_dist") != -1:
            collect_info_2d(ed_v, ed_b, info, k)
        elif k.find("traveled_dist") != -1:
            collect_info_2d(td_v, td_b, info, k)
    cmap = get_cmap('Pastel1')  # Or 'Pastel2'
    colors = [cmap(0), cmap(1), cmap(2), cmap(3)]
    plt.clf()
    plt.figure(dpi=300)
    plt.xlabel("Traveled Distance")
    plt.ylabel("Euclidean Distance")
    X = np.linspace(0, 500, 100)  # Create 100 points from -10 to 10

    # Calculate y values (y = x)
    Y = X

    # Plot the line y = x
    plt.plot(X, Y,  color='mediumpurple',linewidth=0.5)
    for i in range(4):
        x = td_b[i][0]
        y = ed_b[i][0]
        for k in range(1, 3):
            x=np.concat((x, td_b[i][k]))
            y=np.concat((y, ed_b[i][k]))
        for k in range(3):
            x = np.concat((x, td_v[i][k]))
            y = np.concat((y, ed_v[i][k]))
        # Reshape x for sklearn (needs to be 2D)
        x_reshaped = x.reshape(-1, 1)

        # Create and fit the model
        model = LinearRegression()
        model.fit(x_reshaped, y)
        print(model.coef_[0])
        # Get the line of best fit
        y_pred = model.predict(x_reshaped)
        plt.scatter(x, y,color=colors[i], s=10, label=object_names[i])
        plt.plot(x, y_pred, color=colors[i], label=object_names[i])
    plt.legend(loc='upper left')
    plt.savefig(f"./pics/Scatter Vision.png")

if __name__ == "__main__":
   # concat_all()
   # debug()
   # bar_chart()

   scatter_plot()
