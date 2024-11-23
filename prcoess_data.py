import os
import numpy as np
import glob
import pickle
import matplotlib.pyplot as plt

keys = ["targets", "drop", "within_time_limit", "time_elapsed", "hardware_error", "pos"]
names = ["TJ_box", "TJ_short_rod", "TJ_long_rod", "TJ_sponge",
         "visionTJ_box", "visionTJ_short_rod", "visionTJ_long_rod", "visionTJ_sponge",
         "Alan_box", "Alan_short_rod", "Alan_long_rod", "Alan_sponge",
         "visionAlan_box", "visionAlan_short_rod", "visionAlan_long_rod", "visionAlan_sponge",
         "Dylan_box", "Dylan_short_rod", "Dylan_long_rod", "Dylan_sponge",
         "visionDylan_box", "visionDylan_short_rod", "visionDylan_long_rod", "visionDylan_sponge",
         ]


def concat_data(base_name, output_name):
    all_paths = sorted(glob.glob(f"./raw_data/{base_name}*.dict"))
    if len(all_paths) == 1:
        with open("./data/" + output_name + ".dict", 'wb') as file:
            pickle.dump(np.load(all_paths[0], allow_pickle=True), file, protocol=pickle.HIGHEST_PROTOCOL)
    base_dict = np.load(all_paths[0], allow_pickle=True)
    for key in keys:
        base_dict[key] = base_dict[key][:len(base_dict['time_elapsed'])]
    for path in all_paths[1:]:
        d = np.load(path, allow_pickle=True)
        for key in keys:
            base_dict[key] += d[key][:len(d['time_elapsed'])]
    while len(base_dict['time_elapsed']) > 10:
        mean = np.mean(base_dict['time_elapsed'])
        deviations = np.abs(np.array(base_dict['time_elapsed']) - mean)
        max_deviation_index = np.argmax(deviations)
        for key in keys:
            base_dict[key].pop(max_deviation_index)
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
        avg_time = 0
        succ_rate = 0
        for t in d['time_elapsed']:
            avg_time += t
        for flag in d['within_time_limit']:
            if flag:
                succ_rate += 1
        std_time = np.std(np.array(d['time_elapsed']))
        avg_time /= len(d['time_elapsed'])
        print(f"{avg_time},{std_time}")
        succ_rate /= len(d['within_time_limit'])
        info[name + "_avg_time"] = avg_time
        info[name + "_std_time"] = std_time
        info[name + "_success_rate"] = succ_rate
    return info


def bar_chart():
    info = extract_info()
    persons = ["Alan", "Dylan", "TJ"]
    objects = ["long_rod", "short_rod", "box", "sponge"]
    object_names = ["Long Rod", "Short Rod", "Box", "Sponge Bob"]
    sr_b = [[0] * 3 for _ in range(4)]
    sr_v = [[0] * 3 for _ in range(4)]
    at_b = [[0] * 3 for _ in range(4)]
    at_v = [[0] * 3 for _ in range(4)]
    std_t_b = [[0] * 3 for _ in range(4)]
    std_t_v = [[0] * 3 for _ in range(4)]
    for k in info.keys():
        # sr
        if k.find("success_rate") != -1:
            if k.find("vision") != -1:
                idx1 = -1
                idx2 = -1
                for i in range(3):
                    if k.find(persons[i]) != -1:
                        idx2 = i
                        break
                for j in range(4):
                    if k.find(objects[j]) != -1:
                        idx1 = j
                        break
                sr_v[idx1][idx2] = info[k]
            else:
                idx1 = -1
                idx2 = -1
                for i in range(3):
                    if k.find(persons[i]) != -1:
                        idx2 = i
                        break
                for j in range(4):
                    if k.find(objects[j]) != -1:
                        idx1 = j
                        break
                sr_b[idx1][idx2] = info[k]
        # at
        elif k.find("avg_time") != -1:
            if k.find("vision") != -1:
                idx1 = -1
                idx2 = -1
                for i in range(3):
                    if k.find(persons[i]) != -1:
                        idx2 = i
                        break
                for j in range(4):
                    if k.find(objects[j]) != -1:
                        idx1 = j
                        break
                at_v[idx1][idx2] = info[k]
            else:
                idx1 = -1
                idx2 = -1
                for i in range(3):
                    if k.find(persons[i]) != -1:
                        idx2 = i
                        break
                for j in range(4):
                    if k.find(objects[j]) != -1:
                        idx1 = j
                        break
                at_b[idx1][idx2] = info[k]
        elif k.find("std_time") != -1:
            if k.find("vision") != -1:
                idx1 = -1
                idx2 = -1
                for i in range(3):
                    if k.find(persons[i]) != -1:
                        idx2 = i
                        break
                for j in range(4):
                    if k.find(objects[j]) != -1:
                        idx1 = j
                        break
                std_t_v[idx1][idx2] = info[k]
            else:
                idx1 = -1
                idx2 = -1
                for i in range(3):
                    if k.find(persons[i]) != -1:
                        idx2 = i
                        break
                for j in range(4):
                    if k.find(objects[j]) != -1:
                        idx1 = j
                        break
                std_t_b[idx1][idx2] = info[k]

    width = 0.4
    x = np.arange(len(persons))
    plt.figure(dpi=300)
    for i in range(4):
        plt.clf()
        plt.title(object_names[i])
        plt.ylabel("Success Rate")
        plt.bar(x - width / 2, sr_b[i], width, label='No Vision', color='orange')
        plt.bar(x + width / 2, sr_v[i], width, label='With Vision', color='blue')
        plt.xticks(x, persons)
        plt.legend(loc='upper right')
        plt.savefig(f"./pics/{object_names[i]} Success.png")

    for i in range(4):
        plt.clf()
        plt.title(object_names[i])
        plt.ylabel("Average Time")
        plt.bar(x - width / 2, at_b[i], width, label='No Vision', color='orange', yerr=std_t_b[i],
                capsize=4, edgecolor='black')
        plt.bar(x + width / 2, at_v[i], width, label='With Vision', color='blue', yerr=std_t_v[i],
                capsize=4, edgecolor='black')
        print(f"{at_v[i]}, {std_t_v[i]}")
        print(f"{at_b[i]}, {std_t_b[i]}")
        plt.xticks(x, persons)
        plt.legend(loc='upper right')
        plt.savefig(f"./pics/{object_names[i]} Time.png")


if __name__ == "__main__":
    concat_all()
    debug()
    bar_chart()
