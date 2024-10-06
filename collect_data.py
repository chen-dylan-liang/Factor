# import os
import sys
import time
import pickle
import keyboard

# sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from xarm.wrapper import XArmAPI


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
        _traj_name = sys.argv[2]
    else:
        _traj_name = "test"
    return _ip, _traj_name


def initialize_arm(_ip):
    _arm = XArmAPI(_ip)
    _arm.motion_enable(enable=True)
    _arm.ft_sensor_enable(0)
    _arm.set_mode(0)
    _arm.set_state(state=0)
    time.sleep(0.5)
    return _arm


def set_to_init_pos(_arm, speed=50):
    _arm.reset(wait=True, speed=speed)
    _arm.set_position(x=496.2, y=-28.8, z=469.4, roll=180, pitch=0, yaw=0, speed=speed, wait=True)
    _arm.set_position(x=496.2, y=-28.8, z=469.4, roll=51.7, pitch=-85.9, yaw=0, speed=speed, wait=True)
    _arm.set_position(x=496.2, y=-28.8, z=469.4, roll=51.7, pitch=-85.9, yaw=125.6, speed=speed, wait=True)


def safe_exit(_arm, _code):
    # turn off manual mode after recording
    _arm.set_mode(0)
    _arm.set_state(0)
    time.sleep(0.5)
    _arm.reset(wait=True, speed=50)
    # time.sleep(10)
    # turn off force sensor
    _arm.ft_sensor_enable(0)
    # disconnect after use
    _arm.disconnect()
    if _code == 0:
        exit(0)
    else:
        exit(1)


def turn_on_force_sensor(_arm, _see_ft_sensor_config=True):
    # turn on the force sensor
    _arm.ft_sensor_enable(1)
    _arm.ft_sensor_set_zero()
    _arm.ft_sensor_app_set(0)
    time.sleep(0.5)
    _arm.set_state(0)
    time.sleep(0.5)
    if _see_ft_sensor_config:
        _code, config = arm.get_ft_senfor_config()
        if _code == 0:
            print('ft_app_status: {}'.format(config[0]))
            print('ft_is_started: {}'.format(config[1]))
            print('ft_type: {}'.format(config[2]))
            print('ft_id: {}'.format(config[3]))
            print('ft_freq: {}'.format(config[4]))
            print('ft_mass: {}'.format(config[5]))
            print('ft_dir_bias: {}'.format(config[6]))
            print('ft_centroid: {}'.format(config[7]))
            print('ft_zero: {}'.format(config[8]))
            print('imp_coord: {}'.format(config[9]))
            print('imp_c_axis: {}'.format(config[10]))
            print('M: {}'.format(config[11]))
            print('K: {}'.format(config[12]))
            print('B: {}'.format(config[13]))
            print('f_coord: {}'.format(config[14]))
            print('f_c_axis: {}'.format(config[15]))
            print('f_ref: {}'.format(config[16]))
            print('f_limits: {}'.format(config[17]))
            print('kp: {}'.format(config[18]))
            print('ki: {}'.format(config[19]))
            print('kd: {}'.format(config[20]))
            print('xe_limit: {}'.format(config[21]))
        else:
            print("Error in checking force sensor config!!!")
            safe_exit(_arm, _code)


def enable_teach_mode(_arm):
    _arm.set_mode(2)
    _arm.set_state(0)
    time.sleep(0.5)


def save_traj(_data, _traj_name):
    with open(_traj_name + ".traj", 'wb') as file:
        pickle.dump(_data, file, protocol=pickle.HIGHEST_PROTOCOL)


def load_traj(_traj_name):
    with open(_traj_name + ".traj", 'rb') as file:
        _data = pickle.load(file)
    return _data


def collect_data(_arm, _traj_name, _dur=10, _freq=50, _print_out=False):
    # collect data
    _n = _freq * _dur
    _sleep_time = 1.0 / _freq
    _data = {'pos_data': [], 'pos_aa_data': [], 'joint_state_data': [], 'ext_f_data': [], 'raw_f_data': []}
    print("=====START DATA COLLECTION=====")
    for _i in range(_n):
        _code, _pos = _arm.get_position()
        if _code == 0:
            _data['pos_data'].append(_pos)
        else:
            print("Error in position data!!!")
            save_traj(_data, _traj_name)
            safe_exit(_arm, _code)

        _code, _pos_aa = _arm.get_position_aa()
        if _code == 0:
            _data['pos_aa_data'].append(_pos_aa)
        else:
            print("Error in position axis angle data!!!")
            save_traj(_data, _traj_name)
            safe_exit(_arm, _code)

        _code, _js = _arm.get_joint_states()
        if _code == 0:
            _data['joint_state_data'].append(_js)
        else:
            print("Error in joint state data!!!")
            save_traj(_data, _traj_name)
            safe_exit(_arm, _code)

        _code, _ext_force = _arm.get_ft_sensor_data()
        if _code == 0:
            _data['ext_f_data'].append(_ext_force)
        else:
            print("Error in force data!!!")
            save_traj(_data, _traj_name)
            safe_exit(_arm, _code)

        _raw_force = _arm.ft_raw_force
        _data['raw_f_data'].append(_raw_force)

        if _print_out:
            print(
                "Iteration {}: ext_force={}, raw_force={}".format(len(_data['pos_data']),
                                                                  _ext_force,
                                                                  _raw_force))
        time.sleep(_sleep_time)
    print("=====FINISH DATA COLLECTION=====")
    return _data


def move_x(_arm, delta=10, speed=50):
    _code, _pos = _arm.get_position()
    _arm.set_position(x=_pos[0] + delta, wait=True,speed=speed)


def move_y(_arm, delta=10,speed=50):
    _code, _pos = _arm.get_position()
    _arm.set_position(y=_pos[1] + delta, wait=True,speed=speed)


def move_z(_arm, delta=10,speed=50):
    _code, _pos = _arm.get_position()
    _arm.set_position(z=_pos[2] + delta, wait=True,speed=speed)


if __name__ == "__main__":
    ip, traj_name = process_argv()
    arm = initialize_arm(ip)
    set_to_init_pos(arm, speed=100)
    turn_on_force_sensor(arm)
    # enable_teach_mode(arm)
    dur = 1
    freq = 50
    print_out = False
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
            data = collect_data(arm, traj_name, dur, freq, print_out)
            save_traj(data, traj_name)
        if event.event_type == keyboard.KEY_DOWN and event.name == "s":
            move_x(arm, delta=20,speed=100)
        if event.event_type == keyboard.KEY_DOWN and event.name == "w":
            move_x(arm, delta=-20,speed=100)
        if event.event_type == keyboard.KEY_DOWN and event.name == "a":
            move_y(arm, delta=-20,speed=100)
        if event.event_type == keyboard.KEY_DOWN and event.name == "d":
            move_y(arm, delta=20,speed=100)
        if event.event_type == keyboard.KEY_DOWN and event.name == "up":
            move_z(arm, delta=20,speed=100)
        if event.event_type == keyboard.KEY_DOWN and event.name == "down":
            move_z(arm, delta=-20,speed=100)
        if event.event_type == keoard.KEY_DOWN and event.name == 'esc':
            safe_exit(arm, 0)
