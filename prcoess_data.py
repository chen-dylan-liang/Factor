import os
import numpy as np
import glob
import pickle


def concat_data(base_name, output_name):
    all_paths = sorted(glob.glob(f"./data/{base_name}*.dict"))
    if len(all_paths) == 1:
        with open("./data/" + output_name + ".dict", 'wb') as file:
            pickle.dump(np.load(all_paths[0], allow_pickle=True), file, protocol=pickle.HIGHEST_PROTOCOL)
    base_dict = np.load(all_paths[0], allow_pickle=True)
    keys = ["targets", "drop", "within_time_limit", "time_elapsed", "hardware_error", "pos"]
    for key in keys:
        base_dict[key] = base_dict[key][:len(base_dict['time_elapsed'])]
    for path in all_paths[1:]:
        d = np.load(path, allow_pickle=True)
        for key in keys:
            base_dict[key] += d['pos'][:len(d['time_elapsed'])]
    with open("./data/" + output_name + ".dict", 'wb') as file:
        pickle.dump(base_dict, file, protocol=pickle.HIGHEST_PROTOCOL)


def concat_all():
    # without vision
    concat_data("TJ_and_Box", "tj_box")
    concat_data("TJ_and_Fat_Rod", "tj_short_rod")
    concat_data("TJ_and_Rod", "tj_rod")
    concat_data("TJ_and_Sponge", "tj_sponge")

    concat_data("Alan_and_Box", "alan_box")
    concat_data("Alan_and_Fat_Rod", "alan_short_rod")
    concat_data("Alan_and_Rod", "alan_rod")
    concat_data("Alan_and_Sponge", "alan_sponge")

    concat_data("Dylan_and_box", "dylan_box")
    concat_data("Dylan_and_fatrod", "dylan_short_rod")
    concat_data("Dylan_and_rod", "dylan_rod")
    concat_data("Dylan_and_sponge", "dylan_sponge")
    # with vision
    concat_data("VTJ_and_Box", "vtj_box")
    concat_data("VTJ_and_Fat_Rod", "vtj_short_rod")
    concat_data("VTJ_and_Rod", "vtj_rod")
    concat_data("VTJ_and_Sponge", "vtj_sponge")

    concat_data("VAlan_and_Box", "valan_box")
    concat_data("VAlan_and_Fat_Rod", "valan_short_rod")
    concat_data("VAlan_and_Rod", "valan_rod")
    concat_data("VAlan_and_Sponge", "valan_sponge")

    concat_data("VDylan_and_box", "vdylan_box")
    concat_data("VDylan_and_fatrod", "vdylan_short_rod")
    concat_data("VDylan_and_rod", "vdylan_rod")
    concat_data("VDylan_and_sponge", "vdylan_sponge")


def debug():
    keys = ["targets", "drop", "within_time_limit", "time_elapsed", "hardware_error", "pos"]
    names = ["tj_box", "tj_short_rod", "tj_rod", "tj_sponge",
             "vtj_box", "vtj_short_rod", "vtj_rod", "vtj_sponge",
             "alan_box", "alan_short_rod", "alan_rod", "alan_sponge",
             "valan_box", "valan_short_rod", "valan_rod", "valan_sponge",
             "dylan_box", "dylan_short_rod", "dylan_rod", "dylan_sponge",
             "vdylan_box", "vdylan_short_rod", "vdylan_rod", "vdylan_sponge",
             ]
    for name in names:
        print(name)
        d = np.load("./data/"+name+".dict", allow_pickle=True)
        for key in keys:
            print(f"{key}: {len(d[key])}")


if __name__ == "__main__":
    concat_all()
    debug()
