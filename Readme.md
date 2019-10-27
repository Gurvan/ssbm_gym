# SSBM GYM

OpenAI gym type environment for Super Smash Bros. Melee

It's based the great work of xpilot/vladfi1. Most of the credit goes to him. (https://github.com/vladfi1)

## Installation

You need Python 3 for this to work (use pip or pip3 depending on your setup).

`pip install -e .`

For Linux also you need to build a specific Dolphin executable from the sources located here https://github.com/Gurvan/dolphin (see instructions below).
The compilation has only be tested on Ubuntu 18.04 at the moment.
It should also work on Ubuntu 16.

For Windows, you should download this [compiled version of Dolphin](https://github.com/vladfi1/dolphin/releases/download/v5.2-alpha/win-mw-push.zip), and put the content of the x64 folder inside `dolphin-exe`.
Windows is supported only for playing or visualizing a bot, it is not recommended for training.

You also need an ISO of Super Smash Bros. Melee NTSC v1.02 that you put or link in the ISOs folder. The default name should be SSBM.iso

## Usage

There is a basic usage example in `test_env.py`.
You can look in `ssbm_env.py` to see the abstract BaseEnv class and a simple implementation of it with the SSBMEnv class.
This shows how to define an action space, compute a reward, and so on so you can implement your own environment.

The structure of observations monitored in the game and the definition of actions are visible in `ssbm.py` (it's a bit messy at the moment).

## Options

Here is a documentation of the different options.

- exe: string, specifies wich dolphin executable to use (should be good by default if you followed the installation guide).
- iso: string, what melee iso to use. Useful if you want to use a 20XX iso.
- render: boolean, if True, show game window and set the fps as 60.
- windows: boolean, required if you use the program on windows.
- stage: string, what stage to be played on. ['final_destination', 'battlefield'] have been tested, the others stages should work to (you can look in ssbm_gym/gen_code.py for a list).
- player1: string, player1 type. ['ai', 'human', 'cpu']. 'ai' allows to send command through env.step, 'human' allows to play with a controller on the respective port, 'cpu' is game cpu.
- player2: string, player1 type. ['ai', 'human', 'cpu']. 'ai' allows to send command through env.step, 'human' allows to play with a controller on the respective port, 'cpu' is game cpu.
-char1: string, player1 character. You can find the list in ssbm_gym/gen_code.py.
-char2: string, player2 character. You can find the list in ssbm_gym/gen_code.py.
-cpu1: int, player1 cpu level, if player1 is set to 'cpu'. [1-9]
-cpu2: int, player2 cpu level, if player2 is set to 'cpu'. [1-9]


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
5. `cp -R ../Data/Sys Binaries/`
6. `ln -s $PWD/Binaries/dolphin-emu-nogui {ssbm_gym directory}/dolphin-exe/`

This compiles and links the headless version of Dolphin use for training an agent. If you want to be able to render and play the game, you can also compile the regular version of Dolphin with, from the Build directory,

1. `cmake .. -DENABLE_HEADLESS=false -DENABLE_NOGUI=false`
2. `make`
3. `ln -s $PWD/Binaries/dolphin-emu {ssbm_gym directory}/dolphin-exe/`


## TODO

- [x] Credit all the people that made this possible
- [x] Document all the options
- [x] Make and test build instruction for other OS
- [ ] Clean most of the code to make it as simple as possible (since the basis of this work is vladfi1/phillip, there is still a lot of stuff that is not used and can be removed)
- [x] Make an example for self-play environment

## Issues

- Sometimes Dolphin doesn't shut down properly, especially when a keyboard interrupt occures.

## Credits

- [vladfi1/xpilot](https://github.com/vladfi1/) for [phillip](https://github.com/vladfi1/phillip), the main basis of this work and the [zmq version of Dolphin](https://github.com/vladfi1/dolphin/tree/new-zmq-exi).
- UnclePunch, tauKhan, Savestate, for most of the gecko codes codes and melee knowledge.
- Fizzi, and the people mentioned above for [Project Slippi](https://github.com/project-slippi)
- [Dolphin emulator](https://github.com/dolphin-emu)
- ... probably missing a lot of people, tell me!
