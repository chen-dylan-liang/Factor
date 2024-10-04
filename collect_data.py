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
arm = XArmAPI(ip, is_radian=True)
arm.motion_enable(enable=True)
arm.ft_sensor_enable(0)
arm.set_mode(0)
arm.set_state(state=0)
arm.set_position(x=496.2, y=-28.8, z=469.4, roll=51.7, pitch=-85.9, yaw=125.6, wait=True)
time.sleep(0.5)

# turn on the force sensor
arm.ft_sensor_enable(1)
arm.ft_sensor_set_zero()
arm.ft_sensor_app_set(0)
time.sleep(0.5)

# turn on teach mode
arm.set_mode(2)
arm.set_state(0)
time.sleep(0.5)

# collect data
freq = 10
sleep_time = 1.0 / freq
print_out = False
data = {'pos_data': [], 'pos_aa_data': [], 'joint_state_data': [], 'ext_f_data': [], 'raw_f_data': []}
while arm.connected and arm.error_code == 0:
    code, pos = arm.get_position()
    if code == 0:
        data['pos_data'].append(pos)
    else:
        print("Error in position data!!!")
        break

    code, pos_aa = arm.get_position_aa()
    if code == 0:
        data['pos_aa_data'].append(pos_aa)
    else:
        print("Error in position axis angle data!!!")
        break

    code, js = arm.get_joint_states()
    if code == 0:
        data['joint_state_data'].append(js)
    else:
        print("Error in joint state data!!!")
        break

    code, ext_force = arm.get_ft_sensor_data()
    if code == 0:
        data['ext_f_data'].append(ext_force)
    else:
        print("Error in force data!!!")
        break

    raw_force = arm.ft_raw_force
    data['raw_f_data'].append(raw_force)

    if print_out:
        print(
            "Iteration {}: pos={}, pos_aa={}, joint_states={}, ext_force={}, raw_force={}".format(len(data['pos_data']),
                                                                                                  pos,
                                                                                                  pos_aa, js, ext_force,
                                                                                                  raw_force))
    # save traj
    with open(traj_name + ".traj", 'wb') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    time.sleep(sleep_time)

# save traj
with open(traj_name + ".traj", 'wb') as file:
    pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
time.sleep(1)

# turn off manual mode after recording
arm.set_mode(0)
arm.set_state(0)

# turn off force sensor
arm.ft_sensor_enable(0)

# disconnect after use
arm.disconnect()
