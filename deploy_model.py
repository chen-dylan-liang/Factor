import sys
from collect_data import initialize_arm, set_to_init_pos, turn_on_force_sensor, safe_exit
import torch as th


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


def deploy_model(_arm, _model, _dur=10, _freq=50, _print_out=False):
    pass


if __name__ == "__main__":
    ip, model_name = process_argv()
    model = th.load(model_name)
    arm = initialize_arm(ip, 0)  # use position control mode
    set_to_init_pos(arm, speed=300)
    turn_on_force_sensor(arm)
    dur = 10
    freq = 50
    print_out = False
    deploy_model(arm, model, dur, freq, print_out)
    safe_exit(arm, 0)
