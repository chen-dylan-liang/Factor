import sys, os
from collect_data import initialize_arm, set_to_init_pos, turn_on_force_sensor, safe_exit, enable_online_mode
import torch as th
from model import FeedForwardModel
import time
import keyboard
import numpy as np


def process_argv():
    if len(sys.argv) >= 2:
        _ip = sys.argv[1]
    else:
        try:
            from configparser import ConfigParser

            parser = ConfigParser()
            parser.read('../robot.conf')
            _ip = parser.get('xArm', 'ip')
        except:
            _ip = input('Please input the xArm ip address:')
            if not _ip:
                print('input error, exit')
                sys.exit(1)
    if len(sys.argv) >= 3:
        _model_name = sys.argv[2]
    else:
        _model_name = "model.ckpt"
    return _ip, _model_name


def load_model(_model_name):
    _model = FeedForwardModel.load_from_checkpoint(_model_name)
    return _model


def step_model(_arm, _model, _look_ahead):
    _code_p, _pos = _arm.get_position()
    _pos = _pos[:3]
    _code_f, _force = _arm.get_ft_sensor_data()
    _future_pos = [float(x) for x in _model(th.tensor(_force, dtype=th.float32))]  # 10*3
    _new_signal = np.array(_future_pos[0:3 * _look_ahead]).reshape(-1, 3)
    _new_signal = np.mean(_new_signal, axis=0)
    _control_signal = _new_signal + np.array(_pos)
    _arm.set_position(*list(_control_signal), speed=50, wait=False)
    return _pos, _force, _control_signal


def deploy_model(_arm, _model, _dur=10, _look_ahead=5, _print_out=False):
    _model.eval()
    if _look_ahead < 1:
        _look_ahead = 1
    if _look_ahead > 10:
        _look_ahead = 10
    with th.no_grad():
        itr = 0
        start = time.time()
        while True:
            _, _force, _control_signal = step_model(_arm, _model, _look_ahead)
            end = time.time()
            if _print_out:
                print("iter:{}, time:{}, control:{}".format(itr, end - start,
                                                            dict(zip(["x", "y", "z", "roll", "pitch", "yaw"],
                                                                     _control_signal))))
                print("force:{}".format(_force))
            itr = itr + 1
            if end - start >= _dur:
                print("Reached time limit.")
                break


if __name__ == "__main__":
    ip, model_name = process_argv()
    model = load_model("model_delta_final.ckpt")
    arm = initialize_arm(ip, 0)  # use position control mode
    # set collision sensitivity to 0
    arm.set_collision_sensitivity(0)
    set_to_init_pos(arm, speed=60)
    turn_on_force_sensor(arm)
    enable_online_mode(arm)
    while True:
        # event = keyboard.read_event()
        print_out = True
        # if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
        dur = 10000000
        print("=====START TESTING THE MODEL=====")
        os.system('say "Start testing the model"')
        deploy_model(arm, model, dur, 10, print_out)
        # if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
        # safe_exit(arm, 0)
