# FACTOR: Force-Assisted Collaborative Object Repositioning
### A Course Project for Yale CPSC 473/573, Intelligent Robotics Laboratory
***Alan Chirong Li, Chen (Dylan) Liang, TJ Vitchuripop***

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
 
Slides:
1. Pitch: https://docs.google.com/presentation/d/1ew2qczEkUWNBvHf2gIASGTlScKLhjqRN/edit?usp=sharing&ouid=108918866099544253796&rtpof=true&sd=true
2. Update1: https://docs.google.com/presentation/d/15hTjuTn6_IQF5O99f0Rat0rTZYORpf7C1IgPh5Vp3G4/edit?usp=sharing
3. Update2: https://docs.google.com/presentation/d/1H_bBKOC1Eru_7OlysFbIc_v624sBtbVqLbhWCltflHI/edit?usp=drive_link
4. Final: https://docs.google.com/presentation/d/1xgP0vpHrbR2VrGPNNkmWnGuI4OL8EI5B9hXTSuXlzY8/edit?usp=drive_link

Videos: 
1. 1d jerky (update2): https://drive.google.com/file/d/1MPyzr9_BYOL0JsL2iViJxrORU7s88cNg/view?usp=sharing
2. Final evaluation in 3d: https://drive.google.com/file/d/1V8x6jX6jQt6Bj6unplMdYftWUCn4y4Rk/view?usp=drive_link
