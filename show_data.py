import pickle

traj_name =  "x-axis-1"
with open(traj_name + ".traj", 'rb') as file:
    data=pickle.load(file)

print(data)