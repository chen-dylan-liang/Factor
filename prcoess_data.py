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
        print(name)
        d = np.load("./data/" + name + ".dict", allow_pickle=True)
        succ_rate = 0
        for flag in d['within_time_limit']:
            if flag:
                succ_rate += 1
        ttime = []
        length=[]
        for i in range(len(d['time_elapsed'])):
            if d['within_time_limit'][i]:
                ttime.append(d['time_elapsed'][i])
                length.append(np.linalg.norm(np.array(d['targets'][i]-d['pos'][i][0])))



        std_time = np.std(np.array(ttime))
        avg_time = np.mean(np.array(ttime))
        avg_speed = np.mean(np.array(length)) / np.mean(np.array(ttime))
        succ_rate /= len(d['within_time_limit'])

        info[name + "_avg_speed"] = avg_speed
        info[name + "_avg_time"] = avg_time
        info[name + "_std_time"] = std_time
        info[name + "_success_rate"] = succ_rate

    return info


def bar_chart():
    info = extract_info()
    persons = ["Alan", "Dylan", "TJ"]
    objects = ["long_rod", "short_rod", "box", "sponge"]
    object_names = ["Long Rod", "Short Rod", "Box", "Ball"]
    sr_b = [[0] * 3 for _ in range(4)]
    sr_v = [[0] * 3 for _ in range(4)]
    at_b = [[0] * 3 for _ in range(4)]
    at_v = [[0] * 3 for _ in range(4)]
    st_b = [[0] * 3 for _ in range(4)]
    st_v = [[0] * 3 for _ in range(4)]
    as_b = [[0] * 3 for _ in range(4)]
    as_v = [[0] * 3 for _ in range(4)]

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

    def collect_info(vd, bd, _info, _key):
        if _key.find("vision") != -1:
            idx1, idx2 = find_indices(_key)
            vd[idx1][idx2]=_info[_key]
        else:
            idx1, idx2 = find_indices(_key)
            bd[idx1][idx2] = _info[_key]

    for k in info.keys():
        # sr
        if k.find("success_rate") != -1:
            collect_info(sr_v, sr_b, info, k)
        # at
        elif k.find("avg_time") != -1:
            collect_info(at_v, at_b, info, k)
        elif k.find("std_time") != -1:
            collect_info(st_v, st_b, info, k)
        elif k.find("avg_speed")!=-1:
            collect_info(as_v, as_b, info, k)

    width = 0.4
    x = np.arange(len(persons))
    plt.figure(dpi=300)

    def plot_std_bar(ylabel, file_name,avg_v, avg_b, std_v, std_b):
        for _i in range(4):
            plt.clf()
            plt.title(object_names[_i])
            plt.ylabel(ylabel)
            plt.bar(x - width / 2, avg_b[_i], width, label='No Vision', color='orange', yerr=std_b[_i],
                    capsize=4, edgecolor='black')
            plt.bar(x + width / 2, avg_v[_i], width, label='With Vision', color='blue', yerr=std_v[_i],
                    capsize=4, edgecolor='black')
            plt.xticks(x, persons)
            plt.legend(loc='upper right')
            plt.savefig(f"./pics/{object_names[_i]} {file_name}.png")

    plot_std_bar("Average Time", "Time", at_v, at_b, st_v, st_b)
    plot_std_bar("Performance", "Performance", as_v, as_b, [None]*4, [None]*4)
    plot_std_bar("Success Rate", "Success", sr_v, sr_b, [None] * 4, [None] * 4)



if __name__ == "__main__":
    concat_all()
    debug()
    bar_chart()
