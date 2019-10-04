# SSBM GYM

OpenAI gym type environment for Super Smash Bros. Melee

It's based the great work of xpilot/vladfi1. Most of the credit goes to him. (https://github.com/vladfi1)

## Installation

You need Python 3 for this to work (use pip or pip3 depending on your setup).

`pip install -e .`

Then also you need to build a specific Dolphin executable from the sources located here https://github.com/Gurvan/dolphin (see instructions below).
The compilation has only be tested on Ubuntu 18.04 at the moment.
It should also work on Ubuntu 16.

You also need an ISO of Super Smash Bros. Melee NTSC v1.02 that you put or link in the ISOs folder. The default name should be SSBM.iso

## Usage

There is a basic usage example in `test_env.py`.
You can look in `ssbm_env.py` to see the abstract BaseEnv class and a simple implementation of it with the SSBMEnv class.
This shows how to define an action space, compute a reward, and so on so you can implement your own environment.

The structure of observations monitored in the game and the definition of actions are visible in `ssbm.py` (it's a bit messy at the moment).

## Tips

You can use `pkill dolphin` __twice__ to kill any instance of Dolphin that didn't close properly.

## Compile Dolphin on Ubuntu 18.04

First you need to install some dependency,

```sh
sudo apt install build-essential cmake libevdev-dev libudev-dev libgl1-mesa-dev libusb-1.0.0-dev libao-dev libpulse-dev libxrandr-dev libopenal-dev libasound2-dev libzmq3-dev libgtk2.0-dev libpng-dev
```

then clone the repository,

```sh
git clone --depth 1 https://github.com/Gurvan/dolphin.git
```

Go inside the directory you just cloned and execute the following steps,

1. `mkdir Build`
2. `cd Build`
3. `cmake ..`
4. `make` (you can use the argument `-j N`, where N is the number of CPU cores you want to assign to speed up the compilation)
5. `ln -s ../Data/Sys {ssbm_gym directory}/dolphin-exe/`
6. `ln -s $PWD/Binaries/dolphin-emu-nogui {ssbm_gym directory}/dolphin-exe/`

This compiles and links the headless version of Dolphin use for training an agent. If you want to be able to render and play the game, you can also compile the regular version of Dolphin with, from the Build directory,

1. `cmake .. -DENABLE_HEADLESS=false`
2. `make`
3. `ln -s $PWD/Binaries/dolphin-emu {ssbm_gym directory}/dolphin-exe/`


## TODO

- [ ] Document all the options
- [ ] Make and test build instruction for other OS
- [ ] Clean most of the code to make it as simple as possible (since the basis of this work is vladfi1/phillip, there is still a lot of stuff that is not used and can be removed)
- [ ] Make an example for self-play environment

