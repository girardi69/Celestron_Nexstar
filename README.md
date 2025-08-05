## Programming for Celestron Nexstar+

A directory of python programs to start using Nexstar

# Prerequisites
- A Windows PC with admin rights
- A USB to USB mini cable
- A Celestron telescope with Nexstar+ pad

# Activities to do
- Install WSL on the PC (Windows Subsystem for Linux)
- Use the preinstalled Ubuntu 24.04 version included

# Connect the computer to the pad
- open powershell as administrator
- run on WSL your favourite linux environment (mine is Ubuntu 24.04)  
- share from powershell the port to the linux environment:  
  usbipd list  
  usbipd bind --busid 1-1  
  usbipd attach --wsl --busid 1-1  

# Open the linux environment
use vi or another editor to create the pyton program "name.py"
use i to paste the program and exit with :wq
run the python program with 
  python3 name.py
  
