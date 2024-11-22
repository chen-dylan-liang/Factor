import os
import sys
import time
import pickle
import keyboard
from threading import Thread
# from multiprocess import Process
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
        _traj_name = "test.traj"
    return _ip, _traj_name


def initialize_arm(_ip, _mode=0):
    _arm = XArmAPI(_ip)
    _arm.motion_enable(enable=True)
    _arm.ft_sensor_enable(0)
    _arm.set_mode(_mode)
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
    time.sleep(0.5)
    _arm.ft_sensor_set_zero()
    time.sleep(0.5)
    _arm.ft_sensor_app_set(0)
    time.sleep(0.5)
    _arm.set_state(0)
    time.sleep(0.5)
    if _see_ft_sensor_config:
        _code, config = _arm.get_ft_senfor_config()
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


def enable_online_mode(_arm):
    _arm.set_mode(7)
    _arm.set_state(0)
    time.sleep(0.5)


def save_traj(_data, _traj_name):
    os.makedirs("./data", exist_ok=True)
    with open("./data/" + _traj_name, 'wb') as file:
        pickle.dump(_data, file, protocol=pickle.HIGHEST_PROTOCOL)


def load_traj(_traj_name):
    with open("./data/" + _traj_name, 'rb') as file:
        _data = pickle.load(file)
    return _data


def move_x(_arm, _delta=10, _speed=50):
    _code, _pos = _arm.get_position()
    return _arm.set_position(x=_pos[0] + _delta, wait=False, speed=_speed)


def move_y(_arm, _delta=10, _speed=50):
    _code, _pos = _arm.get_position()
    return _arm.set_position(y=_pos[1] + _delta, wait=False, speed=_speed)


def move_z(_arm, _delta=10, _speed=50):
    _code, _pos = _arm.get_position()
    return _arm.set_position(z=_pos[2] + _delta, wait=False, speed=_speed)


def collect_data(_arm, _traj_name, _dur=10, _freq=50, _print_out=False, _save_data=False):
    """
    This is a clock interruption in essence.
    """
    # collect data
    _n = _freq * _dur
    _sleep_time = 1.0 / _freq
    _data = {'pos_data': [], 'pos_aa_data': [], 'joint_state_data': [], 'ext_f_data': [], 'raw_f_data': []}
    print("=====START DATA COLLECTION=====")
    os.system('say "Start collecting data"')
    for _i in range(_n):
        _code, _pos = _arm.get_position()
        if _code == 0:
            _data['pos_data'].append(_pos)
        else:
            print("Error in position data!!!")
            if _save_data:
                save_traj(_data, _traj_name)
            safe_exit(_arm, _code)
        _code, _pos_aa = _arm.get_position_aa()
        if _code == 0:
            _data['pos_aa_data'].append(_pos_aa)
        else:
            print("Error in position axis angle data!!!")
            if _save_data:
                save_traj(_data, _traj_name)
            safe_exit(_arm, _code)

        _code, _js = _arm.get_joint_states()
        if _code == 0:
            _data['joint_state_data'].append(_js)
        else:
            print("Error in joint state data!!!")
            if _save_data:
                save_traj(_data, _traj_name)
            safe_exit(_arm, _code)

        _code, _ext_force = _arm.get_ft_sensor_data()
        if _code == 0:
            _data['ext_f_data'].append(_ext_force)
        else:
            print("Error in force data!!!")
            if _save_data:
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
    os.system('say "Finish collecting data"')
    print("=====FINISH DATA COLLECTION=====")
    if _save_data:
        save_traj(_data, _traj_name)


def keyboard_position_control(_arm, _delta=20, _speed=100):
    """
        This is a keyboard interruption in essence. We want it to be real-time.
        It can achieve smooth linear motion when mode == 7
    """
    print("=====START KEYBOARD CONTROL=====")
    press_down = False
    _max_delta = 50  # to prevent jerky motion in the first call to set_position when pressing down a/d/s/w/up/down
    while True:
        _event = keyboard.read_event()
        if _event.event_type == keyboard.KEY_UP and (_event.name == "s" or _event.name == "w" or
                                                     _event.name == "a" or _event.name == "d" or
                                                     _event.name == "up" or _event.name == "down"):
            press_down = False
            # print("Stop")
            # _arm.set_state(4)  # as suggested by the support team
            # time.sleep(0.2)
        """    
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "s":
            if not press_down:
                press_down = True
                _arm.clean_conf()
                _arm.set_state(0)  # as suggested by the support team
                time.sleep(0.2)
                move_x(_arm, _delta=_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "w":
            if not press_down:
                press_down = True
                _arm.clean_conf()sssssw
                _arm.set_state(0)  # as suggested by the support team
                time.sleep(0.2)
                move_x(_arm, _delta=-_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "a":
            if not press_down:
                press_down = True
                _arm.clean_conf()
                _arm.set_state(0)  # as suggested by the support team
                time.sleep(0.2)
                move_y(_arm, _delta=-_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "d":
            if not press_down:
                press_down = True
                _arm.clean_conf()
                _arm.set_state(0)  # as suggested by the support team
                time.sleep(0.2)
                move_y(_arm, _delta=_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "up":
            if not press_down:
                press_down = True
                _arm.clean_conf()
                _arm.set_state(0)  # as suggested by the support team
                time.sleep(0.2)
                move_z(_arm, _delta=_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "down":
            if not press_down:
                press_down = True
                _arm.clean_conf()
                _arm.set_state(0)  # as suggested by the support team
                time.sleep(0.2)
                move_z(_arm, _delta=-_delta, _speed=_speed)
        """
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "a":
            if press_down:
                move_x(_arm, _delta=_delta, _speed=_speed)
            else:
                press_down = True
                move_x(_arm, _delta=_max_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "d":
            if press_down:
                move_x(_arm, _delta=-_delta, _speed=_speed)
            else:
                press_down = True
                move_x(_arm, _delta=-_max_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "w":
            if press_down:
                move_y(_arm, _delta=-_delta, _speed=_speed)
            else:
                press_down = True
                move_y(_arm, _delta=-_max_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "s":
            if press_down:
                move_y(_arm, _delta=_delta, _speed=_speed)
            else:
                press_down = True
                move_y(_arm, _delta=_max_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "q":
            if press_down:
                move_z(_arm, _delta=_delta, _speed=_speed)
            else:
                press_down = True
                move_z(_arm, _delta=_max_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == "e":
            if press_down:
                move_z(_arm, _delta=-_delta, _speed=_speed)
            else:
                press_down = True
                move_z(_arm, _delta=-_max_delta, _speed=_speed)
        if _event.event_type == keyboard.KEY_DOWN and _event.name == 'esc':
            print("=====FINISH KEYBOARD CONTROL=====")
            return


if __name__ == "__main__":
    ip, traj_name = process_argv()
    collect = True
    if collect:
        arm = initialize_arm(ip)
        set_to_init_pos(arm, speed=300)
        turn_on_force_sensor(arm)
        dur = 60
        freq = 50
        print_out = False
        save_data = True
        teach = False
        if not teach:
            enable_online_mode(arm)
            speed = 80
            delta = 10  # as suggested by the support team
            while True:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
                    t_manipulate = Thread(target=lambda: keyboard_position_control(arm, delta, speed))
                    t_collect = Thread(target=lambda: collect_data(arm, traj_name, dur, freq, print_out, save_data))
                    t_manipulate.start()
                    t_collect.start()
                    t_manipulate.join()
                    t_collect.join()
                if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
                    safe_exit(arm, 0)
        else:
            enable_teach_mode(arm)
            while True:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN and event.name == 'enter':
                    collect_data(arm, traj_name, dur, freq, print_out, save_data)
                if event.event_type == keyboard.KEY_DOWN and event.name == 'esc':
                    safe_exit(arm, 0)
    else:
        data = load_traj(traj_name)
        for k, v in zip(data.keys(), data.values()):
            print("{}:{}".format(k, v))
