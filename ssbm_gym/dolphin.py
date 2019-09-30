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

gfx_ini = """
[Settings]
DumpFramesAsImages = {dump_ppm}
DumpFramesToPPM = {dump_ppm}
DumpFramesCounter = False
Crop = True
DumpFormat = {dump_format}
DumpCodec = {dump_codec}
DumpEncoder = {dump_encoder}
DumpPath = {dump_path}
"""

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


gale01_ini_fm = """
[Core]
CPUThread = True
GPUDeterminismMode = fake-completion
PollingMethod = OnSIRead
[Gecko_Enabled]
$Faster Melee Netplay Settings
$Lag Reduction
$Game Music ON
"""


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
    Option('gfx', type=str, default="Null", help="graphics backend"),
    Option('dual_core', type=int, default=1, help="Use separate gpu and cpu threads."),
    Option('cpus', type=int, nargs='+', default=[1], help="Which players are cpu-controlled."),
    Option('audio', type=str, default="No audio backend", help="audio backend"),
    Option('speed', type=int, default=0, help='framerate - 1=normal, 0=unlimited'),
    Option('dump_frames', action="store_true", default=False, help="dump frames from dolphin to disk"),
    Option('dump_ppm', action="store_true", help="dump frames as ppm images"),
    Option('pipe_count', type=int, default=0, help="Count pipes alphabetically. Turn on for older dolphins."),
    Option('netplay', type=str),
    Option('direct', action="store_true", default=False, help="netplay direct connect"),
    Option('fullscreen', action="store_true", default=False, help="run dolphin with fullscreen"),
    Option('iso_path', type=str, default="", help="directory where you keep your isos"),
    Option('human', action="store_true", help="set p1 to human"),
    Option('fm', action="store_true", help="set up config for Faster Melee"),
    Option('dump_format', type=str, default='mp4'),
    Option('dump_codec', type=str, default='h264'),
    Option('dump_encoder', type=str, default=''),
    Option('dump_path', type=str, default=''),
    Option('lcancel_flash', action="store_true", help="flash on lcancel"),
    Option('speedhack', action="store_true", help="enable speed hack"),

    Option('exe', type=str, default='dolphin-emu-headless', help="dolphin executable"),
    Option('user', type=str, help="path to dolphin user directory"),
    Option('iso', type=str, default="SSBM.iso", help="path to SSBM iso"),
    Option('movie', type=str, help="path to dolphin movie file to play at startup"),
    Option('setup', type=int, default=1, help="setup custom dolphin directory"),
    Option('gui', action="store_true", default=False, help="run with graphics and sound at normal speed"),
    Option('mute', action="store_true", default=False, help="mute game audio"),
    Option('windows', action='store_true', help="set defaults for windows"),
    Option('netplay', type=str, help="join traversal server"),
    
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
    
    print("Dolphin user dir", self.user)
    
    #if self.netplay: # need gui version to netplay
    #  index = self.exe.rfind('dolphin-emu') + len('dolphin-emu')
    #  self.exe = self.exe[:index]
    
    if self.gui or self.windows:
      # switch from headless to gui
      if self.exe.endswith("-headless"):
        #self.exe = self.exe[:-9]
        self.exe = self.exe[:-9] + "-nogui"
      
      # Note: newer dolphins use 'DX11', but win-mw is an old fork.
      self.speed = 1
      self.gfx = 'D3D' if self.windows else 'OGL'
      
      if self.mute:
        self.audio = 'No audio backend'
      else:
        self.audio = 'XAudio2' if self.windows else 'Pulse'

    if self.setup:
      self.setup_user_dir()

  def setup_user_dir(self):
    user = self.user
    configDir = user + '/Config'
    util.makedirs(configDir)
    
    if self.dump_ppm:
      self.dump_frames = True

    with open(configDir + '/GCPadNew.ini', 'w') as f:
      print("generate pad: ", [i for i, e in enumerate([self.player1, self.player2]) if e == 'ai'])
      f.write(generateGCPadNew([0] if self.netplay else [i for i, e in enumerate([self.player1, self.player2]) if e == 'ai'], self.pipe_count))

    with open(configDir + '/Dolphin.ini', 'w') as f:
      config_args = dict(
        user=user,
        gfx=self.gfx,
        cpu_thread=bool(self.dual_core),
        dump_frames=self.dump_frames,
        audio=self.audio,
        speed=self.speed,
        netplay=self.netplay,
        traversal='direct' if self.direct else 'traversal',
        fullscreen=self.fullscreen,
        iso_path=self.iso_path,
        port1 = 12 if self.human else 6,
      )
      f.write(dolphin_ini.format(**config_args))
    
    with open(configDir + '/GFX.ini', 'w') as f:
      f.write(gfx_ini.format(
        dump_ppm=self.dump_ppm,
        dump_path=self.dump_path,
        dump_codec=self.dump_codec,
        dump_encoder=self.dump_encoder,
        dump_format=self.dump_format))

    gameSettings = user + '/GameSettings'
    util.makedirs(gameSettings)
    with open(gameSettings + '/GALE01.ini', 'w') as f:
      assert not self.fm  # only custom exi build is supported
      
      keys = ['stage', 'char1', 'char2', 'cpu1', 'cpu2']
      kwargs = {k: getattr(self, k) for k in keys}
      
      for i in [1, 2]:
        k = 'player%d' % i
        kwargs[k] = str_to_player[getattr(self, k)].player_status()

      print(kwargs)
      match_setup_code = gen_code.setup_match_code(**kwargs)
      
      speed_hack = ''
      if self.speedhack:
        speed_hack = '$Speed Hack'
        if self.gfx != 'Null':
          speed_hack += ' Render'
      ini = gale01_ini.format(match_setup=match_setup_code, speed_hack=speed_hack)
      if self.lcancel_flash:
        ini += lcancel_ini
      f.write(ini)

    util.makedirs(user + '/Dump/Frames')

  def __call__(self):
    args = [self.exe, "--user", self.user]
    if not self.netplay:
      args += ["--exec", self.iso]
      if self.gfx == 'Null':
        args += ['--platform', 'headless']
    if self.movie is not None:
      args += ["--movie", self.movie]
    
    print(args)
    process = subprocess.Popen(args)
    
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
