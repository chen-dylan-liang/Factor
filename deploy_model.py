import sys, os
from collect_data import initialize_arm, set_to_init_pos, turn_on_force_sensor, safe_exit
import torch as th
from model import FeedForwardModel
import time
import keyboard


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


def deploy_model(_arm, _model, _dur=10, _look_ahead=5, _print_out=False):
    _model.eval()
    if _look_ahead < 1:
        _look_ahead = 1
    if _look_ahead > 10:
        _look_ahead = 10
    with th.no_grad():
        itr = 0
        print("=====START TESTING THE MODEL=====")
        os.system('say "Start testing the model"')
        start = time.time()
        while True:
            _code_p, _pos = _arm.get_position()
            _code_f, _force = _arm.get_ft_sensor_data()
            _future_pos = [float(x) for x in _model(th.tensor(_pos + _force, dtype=th.float32))]  # 10*6
            _arm.set_position(*_future_pos[6*(_look_ahead-1):6*_look_ahead], speed=50, wait=True)
            end = time.time()
            if _print_out:
                print("iter:{}, time:{}, control:{}".format(itr, end - start,
                                         dict(zip(["x", "y", "z", "roll", "pitch", "yaw"], _future_pos[-6:]))))
            itr = itr + 1
            if end - start >= _dur:
                print("Reached time limit.")
                break


if __name__ == "__main__":
    ip, model_name = process_argv()
    model = load_model("model.ckpt")
    arm = initialize_arm(ip, 0)  # use position control mode
    set_to_init_pos(arm, speed=300)
    turn_on_force_sensor(arm)
    while True:
        event = keyboard.read_event()
        print_out = True
        if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
            dur = 10
            deploy_model(arm, model, dur, 5, print_out)
        if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
            safe_exit(arm, 0)
