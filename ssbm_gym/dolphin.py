import os
import enum
import subprocess

from .import util
from .default import *
from . import gen_code

path = os.path.dirname(__file__)
datapath = os.path.join(path, 'data')

pipeConfig = """
Buttons/A = `Button A`
Buttons/B = `Button B`
Buttons/X = `Button X`
Buttons/Y = `Button Y`
Buttons/Z = `Button Z`
Main Stick/Up = `Axis MAIN Y +`
Main Stick/Down = `Axis MAIN Y -`
Main Stick/Left = `Axis MAIN X -`
Main Stick/Right = `Axis MAIN X +`
Triggers/L = `Button L`
Triggers/R = `Button R`
D-Pad/Up = `Button D_UP`
D-Pad/Down = `Button D_DOWN`
D-Pad/Left = `Button D_LEFT`
D-Pad/Right = `Button D_RIGHT`
Buttons/Start = `Button START`
C-Stick/Up = `Axis C Y +`
C-Stick/Down = `Axis C Y -`
C-Stick/Left = `Axis C X -`
C-Stick/Right = `Axis C X +`
"""
#Triggers/L-Analog = `Axis L -+`
#Triggers/R-Analog = `Axis R -+`

def generatePipeConfig(player, count):
  config = "[GCPad%d]\n" % (player+1)
  config += "Device = Pipe/%d/p%d\n" % (count, player)
  config += pipeConfig
  return config

def generateGCPadNew(pids=[1], pipe_count=True):
  config = ""
  count = 0
  for p in sorted(pids):
    config += generatePipeConfig(p, count if pipe_count else 0)
    count += 1
  return config

with open(datapath + '/Dolphin.ini', 'r') as f:
  dolphin_ini = f.read()

gale01_ini = """
[Gecko]
$Boot To Match [UnclePunch]
041A45A0 3800000E

$Skip Memcard Prompt [UnclePunch]
C21AF6F4 00000004
2C1D000F 40820014
3D80801B 618C01AC
7D8903A6 4E800420
2C1D0000 00000000

$DMA Read Before Poll [Fizzi, xpilot]
*Does a DMA read on the EXI device in slot B before polling controllers.
C20055F0 00000027 #Codes/EXITransferBuffer.asm
7C0802A6 90010004
9421FFB0 BE810008
7C7E1B78 7C9D2378
7CBF2B78 7FC3F378
7C9EEA14 2C1F0000
4182001C 7C0018AC
38630020 7C032000
4180FFF4 7C0004AC
4C00012C 38600001
38800000 3D808034
618C64C0 7D8903A6
4E800421 38600001
3D808034 618C6D80
7D8903A6 4E800421
38600001 38800000
38A00005 3D808034
618C6688 7D8903A6
4E800421 38600001
7FC4F378 7FA5EB78
7FE6FB78 38E00000
3D808034 618C5E60
7D8903A6 4E800421
38600001 3D808034
618C5F4C 7D8903A6
4E800421 38600001
3D808034 618C67B4
7D8903A6 4E800421
38600001 3D808034
618C6E74 7D8903A6
4E800421 38600001
3D808034 618C65CC
7D8903A6 4E800421
2C1F0000 4082001C
7C001BAC 38630020
7C032000 4180FFEC
7C0004AC 4C00012C
BA810008 80010054
38210050 7C0803A6
4E800020 00000000
C216D294 00000006 #Codes/IncrementFrameIndex.asm
987F0008 3C608048
80639D58 2C030000
40820010 3860FF85
906DB654 48000010
806DB654 38630001
906DB654 00000000
C2019608 00000005 #Codes/ReadAfterPoll.asm
9421FFF8 7C230B78
38800000 38A00000
3D808000 618C55F0
7D8903A6 4E800421
38600000 00000000

{match_setup}

[Gecko_Enabled]
$DMA Read Before Poll
$Skip Memcard Prompt
{speed_hack}
$Boot To Match
#$Fox vs Fox-9
$Match Setup
"""

lcancel_ini = """
$Flash White on Successful L-Cancel
"""
#$Flash Red on Unsuccessful L-Cancel



class Player(enum.Enum):
  HUMAN = 0
  CPU = 1
  AI = 2
  
  def player_status(self):
    if self is Player.CPU:
      return gen_code.PlayerStatus.CPU
    return gen_code.PlayerStatus.HUMAN

str_to_player = {p.name.lower(): p for p in Player}

class DolphinRunner(Default):
  _options = [
    # Option('gfx', type=str, default="Null", help="graphics backend"),
    # Option('audio', type=str, default="No audio backend", help="audio backend"),
    Option('speed', type=int, default=1, help='framerate - 1=normal, 0=unlimited'),
    # Option('pipe_count', type=int, default=0, help="Count pipes alphabetically. Turn on for older dolphins."),
    Option('fullscreen', action="store_true", default=False, help="run dolphin with fullscreen"),
    Option('lcancel_flash', action="store_true", help="flash on lcancel"),
    # Option('speedhack', action="store_true", help="enable speed hack"),

    Option('exe', type=str, default=None, help="dolphin executable"),
    Option('user', type=str, help="path to dolphin user directory"),
    Option('iso', type=str, default=None, help="path to SSBM iso"),
    Option('render', action="store_true", default=False, help="run with graphics and sound at normal speed"),
    Option('windows', action="store_true", default=False, help="to be define if the plateform is Windows"),
    
    Option('stage', type=str, choices=gen_code.stage_ids.keys(),
           default='final_destination', help='stage'),
  ] + [
    Option('player%d' % i, type=str, choices=str_to_player.keys(), default='ai',
           help='player type for port %d' % i) for i in [1, 2]
  ] + [
    Option('char%d' % i, type=str, choices=gen_code.char_ids.keys(), default='falcon',
           help='character for port %d' % i) for i in [1, 2]
  ] + [
    Option('cpu%d' % i, type=int, choices=range(1, 10), default=9,
           help='cpu level for port %d' % i) for i in [1, 2]
  ]

  def __init__(self, **kwargs):
    Default.__init__(self, **kwargs)
    
    if self.user is None:
      import tempfile
      self.user = tempfile.mkdtemp() + '/'
    
    # print("Dolphin user dir", self.user)

    if self.iso is None:
      dir_path = os.path.dirname(os.path.realpath(__file__)[:-1])
      self.iso = os.path.join(dir_path[:-8], "ISOs", "SSBM.iso")

    if self.exe is None:
      dir_path = os.path.dirname(os.path.realpath(__file__)[:-1])
      if self.windows:
        self.exe = os.path.join(dir_path[:-8], "dolphin-exe", "Dolphin.exe")
      else:
        self.exe = os.path.join(dir_path[:-8], "dolphin-exe", "dolphin-emu-nogui")
    
    self.audio = 'No audio backend'  # 'Pulse'
    if self.render:
      self.speed = 1
      self.gfx = 'OGL'
    else:
      self.gfx = 'Null'

    self.setup_user_dir()

  def setup_user_dir(self):
    user = self.user
    configDir = user + '/Config'
    util.makedirs(configDir)

    with open(configDir + '/GCPadNew.ini', 'w') as f:
      # print("generate pad: ", [i for i, e in enumerate([self.player1, self.player2]) if e == 'ai'])
      # f.write(generateGCPadNew([i for i, e in enumerate([self.player1, self.player2]) if e == 'ai'], not self.windows))
      f.write(generateGCPadNew([i for i, e in enumerate([self.player1, self.player2]) if e == 'ai'], 0))

    with open(configDir + '/Dolphin.ini', 'w') as f:
      config_args = dict(
        user=user,
        gfx=self.gfx,
        audio=self.audio,
        speed=self.speed,
        fullscreen=self.fullscreen,
        port1 = 12 if self.player1 == 'human' else 6,
        port2 = 12 if self.player2 == 'human' else 6,
      )
      f.write(dolphin_ini.format(**config_args))

    gameSettings = user + '/GameSettings'
    util.makedirs(gameSettings)
    with open(gameSettings + '/GALE01.ini', 'w') as f:      
      keys = ['stage', 'char1', 'char2', 'cpu1', 'cpu2']
      kwargs = {k: getattr(self, k) for k in keys}
      
      for i in [1, 2]:
        k = 'player%d' % i
        kwargs[k] = str_to_player[getattr(self, k)].player_status()

      # print(kwargs)
      match_setup_code = gen_code.setup_match_code(**kwargs)
      
      speed_hack = ''
      if not self.render:
        speed_hack = '$Speed Hack'
        if self.gfx != 'Null':
          speed_hack += ' Render'
      ini = gale01_ini.format(match_setup=match_setup_code, speed_hack=speed_hack)
      if self.lcancel_flash:
        ini += lcancel_ini
      f.write(ini)

  def __call__(self):
    args = [self.exe, "--user", self.user]
    args += ["--exec", self.iso]
    if self.windows:
      args += ["--batch"]
    else:
      if not self.render:
        args += ["--platform", "headless"]
      else:
        args += ["--platform", "x11"]


    # print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return process

def main():
  import argparse
  
  parser = argparse.ArgumentParser()
  
  for opt in DolphinRunner.full_opts():
    opt.update_parser(parser)
  
  args = parser.parse_args()
  
  runner = DolphinRunner(**args.__dict__)
  runner()


if __name__ == "__main__":
  main()
