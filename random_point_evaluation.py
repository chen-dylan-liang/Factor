import os, glob, time
import numpy as np
from collect_data import initialize_arm, set_to_init_pos, turn_on_force_sensor, enable_online_mode, safe_exit, \
    keyboard_position_control
from deploy_model import process_argv, load_model, deploy_model
import keyboard
from threading import Thread
import pickle


def generate_point(min_val, max_val):
    point = np.random.rand(3)
    point = min_val + point * (max_val - min_val)
    return point


def evaluate(name, arm, n, dur, tol, range_tract=0.7):
    # compute pos range
    data_dir = "./data"
    all_file_paths = sorted(glob.glob(f"{data_dir}/*.traj"))
    min_pos = np.array([np.inf, np.inf, np.inf])
    max_pos = -min_pos
    init_pos = np.array([496.2, -28.8, 469.4])
    for path in all_file_paths:
        data = np.load(path, allow_pickle=True)
        pos = np.array(data['pos_data'])[:, :3]
        min_pos = np.minimum(min_pos, pos.min(axis=0))
        max_pos = np.maximum(max_pos, pos.max(axis=0))
    min_pos = init_pos + (min_pos - init_pos) * range_tract
    max_pos = init_pos + (max_pos - init_pos) * range_tract
    print(min_pos)
    print(max_pos)
    vol = 1
    for i in range(3):
        vol *= (max_pos[i] - min_pos[i]) * 0.001
    print(vol)
    data_to_store = {'min_pos': min_pos, 'max_pos': max_pos,
                     'targets': [], 'drop': [], 'within_time_limit': [], 'time_elapsed': [],
                     'hardware_error': [],
                     'pos': [[]] * n }  # wrong design for pos
    # evaluate
    for i in range(n):
        point = generate_point(min_pos, max_pos)
        data_to_store['targets'].append(point)
        print(f"Point {i + 1}: {point}")
        os.system(f'say "Start point {i + 1}"')
        time.sleep(0.5)
        within_time_limit = False
        drop = False
        start = time.time()
        hardware_error = False
        while time.time() - start < dur:
            code, pos = arm.get_position()
            if arm.error_code != 0:
                hardware_error = True
                break
            pos = np.array(pos[:3])
            data_to_store['pos'][i].append(pos)
            diff = point - pos
            if np.abs(diff).max() < tol:
                within_time_limit = True
                break
            axis = np.abs(diff).argmax()
            if axis == 0:
                if diff[0] > 0:
                    os.system(f'say "Right"')
                else:
                    os.system(f'say "Left"')
            elif axis == 1:
                if diff[1] > 0:
                    os.system(f'say "Outward"')
                else:
                    os.system(f'say "Inward"')
            else:
                if diff[2] > 0:
                    os.system(f'say "Up"')
                else:
                    os.system(f'say "Down"')
            if keyboard.is_pressed('f'):
                drop = True
                break
            time.sleep(1)
        time_elapsed = time.time() - start
        data_to_store['within_time_limit'].append(within_time_limit)
        data_to_store['drop'].append(drop)
        data_to_store['time_elapsed'].append(time_elapsed)
        data_to_store['hardware_error'].append(hardware_error)
        os.makedirs("./data", exist_ok=True)
        with open("./data/" + name, 'wb') as file:
            pickle.dump(data_to_store, file, protocol=pickle.HIGHEST_PROTOCOL)
        if drop:
            os.system(f'say "Point {i + 1} drops."')
            continue
        if hardware_error:
            os.system(f'say "Point {i + 1} has hardware errors."')
            time.sleep(15)
            continue
        if not within_time_limit:
            os.system(f'say "Point {i + 1} reaches time limit."')
        else:
            os.system(f'say "Finish point {i + 1}"')


if __name__ == "__main__":
    np.random.seed(int(time.time()))
    use_model = True
    ip, _ = process_argv()
    model_name = "model_final.ckpt"
    if use_model:
        model = load_model(model_name)
    robot = initialize_arm(ip, 0)
    robot.set_collision_sensitivity(0)
    set_to_init_pos(robot, speed=300)
    turn_on_force_sensor(robot)
    enable_online_mode(robot)
    npt = 10
    duration = 30
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
            if use_model:
                t_daemon = Thread(target=lambda: deploy_model(robot, model, duration * npt + 5, 10, False))
            else:
                t_daemon = Thread(target=lambda: keyboard_position_control(robot, 10, 80))
            t_eval = Thread(target=lambda: evaluate("play"
                                                    ".dict", robot, npt, duration, 50, 0.4))
            t_daemon.start()
            t_eval.start()
            t_daemon.join()
            t_eval.join()
        if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
            safe_exit(robot, 0)
