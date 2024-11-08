### The Course Project for Yale CPSC 473/573, Intelligent Robotics Laboratory

- ***sudo python3 collect_data.py ip_address traj_name***
    - Go to System Preferences -> Security & Privacy -> Accessibility to allow the terminal or the IDE to control your computer if there's segfault.
    - Press "enter" to start collecting data.
    - Press "esc" to exit. When you are in the keyboard control mode, you need to press "esc" twice. First to exit keyboard control, second to exit the script.
    - Press a/d/s/w/up/down to move the end effector along x, y, and z axis.
    - Start moving the arm when you hear the system has finished the sentence "Start collecting data", and stop moving as soon as you hear the system starts to say the sentence "Finish collecting data".

- ***sudo python3 deploy_model.py ip_address model_name***
    - Go to System Preferences -> Security & Privacy -> Accessibility to allow the terminal or the IDE to control your computer if there's segfault.
    - Set "dur" to your desirable trajectory length (in seconds)
    - Setting "_look_ahead" too low (such as 1) may result in jerky and slow movements. Recommended value is 10 if not unstable motions are observed.
    - Press "enter" to start testing the model
    - Press "esc" after "dur" seconds to set the arm back to the initial position
