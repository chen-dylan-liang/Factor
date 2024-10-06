# import os
import sys
import time
import pickle

# sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from xarm.wrapper import XArmAPI

if len(sys.argv) >= 2:
    ip = sys.argv[1]
else:
    try:
        from configparser import ConfigParser

        parser = ConfigParser()
        parser.read('../robot.conf')
        ip = parser.get('xArm', 'ip')
    except:
        ip = input('Please input the xArm ip address:')
        if not ip:
            print('input error, exit')
            sys.exit(1)
if len(sys.argv) >= 3:
    traj_name = sys.argv[2]
else:
    traj_name = "test"

# initialize robot arm
arm = XArmAPI(ip)
arm.motion_enable(enable=True)
arm.ft_sensor_enable(0)
arm.set_mode(0)
arm.set_state(state=0)
time.sleep(0.5)
arm.reset(wait=True)
arm.set_position(x=496.2, y=-28.8, z=469.4, roll=180, pitch=0, yaw=0, speed=100, wait=True)
arm.set_position(x=496.2, y=-28.8, z=469.4, roll=51.7, pitch=-85.9, yaw=0, speed=100, wait=True)
arm.set_position(x=496.2, y=-28.8, z=469.4, roll=51.7, pitch=-85.9, yaw=125.6, speed=100, wait=True)


# arm.set_position(x=496.2, y=-28.8, z=469.4, roll=51.7, pitch=-85.9, yaw=125.6, speed=100, wait=True)
# arm.set_position(x=300, y=0, z=150, roll=-180, pitch=0, yaw=0, speed=100, wait=True)

def safe_exit(code):
    # turn off manual mode after recording
    arm.set_mode(0)
    arm.set_state(0)

    # turn off force sensor
    arm.ft_sensor_enable(0)

    # disconnect after use
    arm.disconnect()
    if code == 0:
        exit(0)
    else:
        exit(1)


# turn on the force sensor
arm.ft_sensor_enable(1)
arm.ft_sensor_set_zero()
arm.ft_sensor_app_set(0)
time.sleep(0.5)
see_ft_sensor_config = True
if see_ft_sensor_config:
    code, config = arm.get_ft_senfor_config()
    if code == 0:
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
        safe_exit(code)

# turn on teach mode
#arm.set_mode(2)
#arm.set_state(0)
time.sleep(5)

# collect data
freq = 50
dur = 10
n = freq * dur
sleep_time = 1.0 / freq
print_out = False
save_data = True
data = {'pos_data': [], 'pos_aa_data': [], 'joint_state_data': [], 'ext_f_data': [], 'raw_f_data': []}
print("START!!!!!!!!!!!!!!!!!!")
for i in range(n):
    code, pos = arm.get_position()
    if code == 0:
        data['pos_data'].append(pos)
    else:
        print("Error in position data!!!")
        safe_exit(code)

    code, pos_aa = arm.get_position_aa()
    if code == 0:
        data['pos_aa_data'].append(pos_aa)
    else:
        print("Error in position axis angle data!!!")
        safe_exit(code)

    code, js = arm.get_joint_states()
    if code == 0:
        data['joint_state_data'].append(js)
    else:
        print("Error in joint state data!!!")
        safe_exit(code)

    code, ext_force = arm.get_ft_sensor_data()
    if code == 0:
        data['ext_f_data'].append(ext_force)
    else:
        print("Error in force data!!!")
        safe_exit(code)

    raw_force = arm.ft_raw_force
    data['raw_f_data'].append(raw_force)

    if print_out:
        print(
            "Iteration {}: ext_force={}, raw_force={}".format(len(data['pos_data']),
                                                              ext_force,
                                                              raw_force))
    if save_data:  # save traj
        with open(traj_name + ".traj", 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    time.sleep(sleep_time)

if save_data:
    # save traj
    with open(traj_name + ".traj", 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    time.sleep(1)

safe_exit(0)
