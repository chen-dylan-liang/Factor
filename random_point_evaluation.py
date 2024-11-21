import os, glob, time
import numpy as np
from collect_data import initialize_arm, set_to_init_pos, turn_on_force_sensor, enable_online_mode, safe_exit, keyboard_position_control
from deploy_model import process_argv, load_model, deploy_model
import keyboard
from threading import Thread


def generate_point(min_val, max_val):
    point = np.random.rand(3)
    point = min_val + point * (max_val - min_val)
    return point


def evaluate(arm, n, dur, tol, range_tract=0.7):
    # compute pos range
    data_dir = "./data"
    all_file_paths = sorted(glob.glob(f"{data_dir}/*.traj"))
    min_pos = np.array([np.inf, np.inf, np.inf])
    max_pos = -min_pos
    for path in all_file_paths:
        data = np.load(path, allow_pickle=True)
        pos = np.array(data['pos_data'])[:, :3]
        min_pos = np.minimum(min_pos, pos.min(axis=0))
        max_pos = np.maximum(max_pos, pos.max(axis=0))
    min_pos *= range_tract
    max_pos *= range_tract

    # evaluate
    for i in range(n):
        point = generate_point(min_pos, max_pos)
        print(f"Point {i + 1}: {point}")
        os.system(f'say "Start point {i + 1}"')
        time.sleep(0.5)
        flag = False
        start = time.time()
        while time.time() - start < dur:
            code, pos = arm.get_position()
            pos = np.array(pos[:3])
            diff = point - pos
            if np.abs(diff).max() < tol:
                flag = True
                break
            axis = np.abs(diff).argmax()
            if axis == 0:
                if diff[0] > 0:
                    os.system(f'say "Outward!"')
                else:
                    os.system(f'say "Inward!"')
            elif axis == 1:
                if diff[1] > 0:
                    os.system(f'say "Door!"')
                else:
                    os.system(f'say "Window!"')
            else:
                if diff[2] > 0:
                    os.system(f'say "Up!"')
                else:
                    os.system(f'say "Down!"')
            time.sleep(0.5)
        if not flag:
            os.system(f'say "Point {i + 1} fails. Reach time limit."')
        else:
            os.system(f'say "Finish point {i + 1}"')


if __name__ == "__main__":
    ip, model_name = process_argv()
    model = load_model(model_name)
    robot = initialize_arm(ip, 0)
    robot.set_collision_sensitivity(0)
    set_to_init_pos(robot, speed=300)
    turn_on_force_sensor(robot)
    enable_online_mode(robot)
    npt = 10
    duration = 20
    use_model = False
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
            if use_model:
                t_daemon = Thread(target=lambda: deploy_model(robot,model, duration*npt+5, 10, False))
            else:
                t_daemon = Thread(target=lambda: keyboard_position_control(robot, 10, 80))
            t_eval = Thread(target=lambda:  evaluate(robot, npt, duration, 1e-1))
            t_daemon.start()
            t_eval.start()
            t_daemon.join()
            t_eval.join()
            evaluate(robot, model, 10, 20, 1e-1)
        if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
            safe_exit(robot, 0)
