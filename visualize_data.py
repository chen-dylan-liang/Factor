import pickle 
import matplotlib.pyplot as plt
import numpy as np

def load_traj(_traj_name):
    with open('./dataset/'+_traj_name + ".traj", 'rb') as file:
        _data = pickle.load(file)
    return _data

data = load_traj('traj_15')
print(data.keys())
# print(data['pos_data'])

# Convert data to numpy array
pos_data = np.array(data['ext_f_data'])
print(pos_data.shape)
# [[x1, y1, z1, ...], [x2, y2, z2, ...], ...]
# Plot X values over time
plt.plot(pos_data[:, 0])
# Scale y values to be between -1000 and 1000
plt.ylim(-1000, 1000)
plt.show()
# # Plot Y values over time
# plt.plot(pos_data[:, 1])
# # Scale y values to be between -1000 and 1000
# plt.ylim(-1000, 1000)
# plt.show()
# # Plot Z values over time
# plt.plot(pos_data[:, 2])
# # Scale y values to be between -1000 and 1000
# plt.ylim(-1000, 1000)
# plt.show()

# Convert force data to numpy array
force_data = np.array(data['ext_f_data'])
# # [[x1, y1, z1, ...], [x2, y2, z2, ...], ...]
# # Plot X values over time
# plt.plot(force_data[:, 0])
# # Scale y values to be between -20 and 20
# plt.ylim(-20, 20)
# plt.show()
# # Plot Y values over time
# plt.plot(force_data[:, 1])
# # Scale y values to be between -20 and 20
# plt.ylim(-20, 20)
# plt.show()
# Plot Z values over time
plt.plot(force_data[:, 2])
# Scale y values to be between -20 and 20
plt.ylim(-20, 20)
plt.show()

# Plot both the position X direction and the Z force values over time as subplots
fig, axs = plt.subplots(2)
axs[0].plot(pos_data[:, 0])
axs[0].set_ylim(0, 1000)
axs[1].plot(force_data[:, 2])
axs[1].set_ylim(-10, 10)
plt.show()



# for k, v in zip(data.keys(), data.values()):
#     print("{}:{}".format(k, v))