"""
Responsible for interfacing with Dolphin to interface with SSBM, and handles things like:
* character selection
* stage selection
* running Phillip within SSBM

"""


import ssbm, state_manager, util, movie
from dolphin import DolphinRunner, Player
import memory_watcher as mw
from state import *
from menu_manager import *
import os
from pad import *
import time
import ctype_util as ct
from numpy import random
from default import *
import functools

class SSBMEnv(Default):
  _options = [
    Option('zmq', type=int, default=0, help="use zmq for memory watcher"),
    Option('tcp', type=int, default=0, help="use zmq over tcp for memory watcher and pipe input"),
  #  Option('stage', type=str, default="final_destination", choices=movie.stages.keys(), help="which stage to play on"),
    Option('start', type=int, default=1, help="start game in endless time mode"),
    Option('debug', type=int, default=0),
  ]
  # ] + [
  #   Option('p%d' % i, type=str, choices=['human', 'cpu', 'ai'], default='ai',
  #       help="Player type in port %d.") for i in [1, 2]
  # ] + [
  #   Option('char%d' % i, type=str, choices=characters.keys(), default="falcon",
  #       help="character for player %d" % i) for i in [1, 2]
  # ] + [
  #   Option('cpu%d' % i, type=int, help="cpu level %d" % i) for i in [1, 2]
  # ]
  
  _members = [
    ('dolphin', DolphinRunner),
  ]
  
  def __init__(self, **kwargs):
    Default.__init__(self, **kwargs)

    self.toggle = 0

    #self.user = os.path.expanduser(self.user)
    self.user = self.dolphin.user
    
    # set up players
    self.pids = []
    self.players = {}
    # self.levels = {}
    # self.characters = {}
    for i in range(2):
      j = i + 1
    #   cpu = getattr(self, 'cpu%d' % j)
    #   self.levels[i] = cpu
    #   if cpu:
    #     player = Player.CPU
    #   else:
    #     player = str_to_player[getattr(self, 'p%d' % j)]
      player = getattr(self.dolphin, 'player%d' % j)
      print(player)
      self.players[i] = player
      if player == 'ai':
        self.pids.append(i)
    #   self.characters[i] = getattr(self, 'char%d' % j)

    self.state = ssbm.GameMemory()
    # track players 1 and 2 (pids 0 and 1)
    self.sm = state_manager.StateManager([0, 1])
    self.write_locations()
    
    print('Creating MemoryWatcher.')
    self.tcp = self.tcp or self.dolphin.windows
    if self.tcp:
      self.mw = mw.MemoryWatcherZMQ(port=5555)
    else:
      mwType = mw.MemoryWatcherZMQ if self.zmq else mw.MemoryWatcher
      self.mw = mwType(path=self.user + '/MemoryWatcher/MemoryWatcher')
    
    # pipe_dir = os.path.join(self.user, 'Pipes')
    # print('Creating Pads at %s.' % pipe_dir)
    # util.makedirs(pipe_dir)
    
    # pad_ids = self.pids
    # if self.dolphin.netplay:
    #   pad_ids = [0]
    
    # pipe_paths = [os.path.join(pipe_dir, 'p%d' % i) for i in pad_ids]
    # print(pipe_paths)
    # self.pads = [Pad(path, tcp=self.tcp) for path in pipe_paths]


    # self.dolphin = dolphin.DolphinRunner(p1=self.p1, p2=self.p2, char1=self.char1, char2=self.char2, cpu1=self.cpu1, cpu2=self.cpu2)
    # self.dolphin = dolphin.DolphinRunner(*kwargs)
    self.dolphin_process = None
    self.last_frame = 0


  def reset(self):
    if self.dolphin_process is not None:
      self.close()
      #self.dolphin_process.terminate()
    self.init_stats()
    self.state = ssbm.GameMemory()
    print('Running dolphin.')
    self.dolphin_process = self.dolphin()


    pipe_dir = os.path.join(self.user, 'Pipes')
    print('Creating Pads at %s.' % pipe_dir)
    util.makedirs(pipe_dir)

    pad_ids = self.pids
    if self.dolphin.netplay:
      pad_ids = [0]
    
    pipe_paths = [os.path.join(pipe_dir, 'p%d' % i) for i in pad_ids]
    print(pipe_paths)
    self.pads = [Pad(path, tcp=self.tcp) for path in pipe_paths]

    
    print("Pipes initialized.")

    self.start_time = time.time()


  def close(self):
    self.dolphin_process.terminate()
    self.dolphin_process.terminate()
    self.print_stats()

  def init_stats(self):
    self.game_frame = 0
    self.total_frames = 1
    self.skip_frames = 0

  def print_stats(self):
    total_time = time.time() - self.start_time
    frac_skipped = self.skip_frames / self.total_frames
    print('Total Time:', total_time)
    print('Total Frames:', self.total_frames)
    print('Average FPS:', self.total_frames / total_time)
    print('Fraction Skipped: {:.6f}'.format(frac_skipped))

  def write_locations(self):
    path = os.path.join(self.dolphin.user, 'MemoryWatcher')
    util.makedirs(path)
    print('Writing locations to:', path)
    with open(os.path.join(path, 'Locations.txt'), 'w') as f:
      f.write('\n'.join(self.sm.locations()))


  def update_state(self):
    messages = self.mw.get_messages()
    for message in messages:
      self.sm.handle(self.state, *message)
  
  def spam(self, button, period=120):
    self.toggle = (self.toggle + 1) % period
    if self.toggle == 0:
      self.pads[0].press_button(button)
    elif self.toggle == 1:
      self.pads[0].release_button(button)
  
  def step(self, controllers):
    for pid, pad in zip(self.pids, self.pads):
      assert(self.players[pid] == 'ai')
      pad.send_controller(controllers[pid])
    while self.state.frame == self.last_frame:
      #print(self.state.frame)
      try:
        self.update_state()
        self.mw.advance()
      except Exception as e:
        print('couldnt advance')
        #self.mw.get_messages()
      #print(self.state.frame, self.state.players[0].percent)


    self.last_frame = self.state.frame

    # TODO: if not in game, wait
    """
    for pid, pad in zip(self.pids, self.pads):
      if pid not in controllers:
        assert(self.players[pid] != Player.AI)
      assert(self.players[pid] == Player.AI)
      pad.send_controller(controllers[pid])
    
    while self.state.frame == self.last_frame:
      self.mw.advance()
      self.update_state()

    skipped_frames = self.last_frame - self.state.frame - 1
    if skipped_frames > 1:
      print("skipped %d frames") % skipped_frames
      self.skip_frames += skipped_frames

    self.last_frame = self.state.frame
    return self.state
    """

  # def step(self, controllers):
  #     # print("advance_frame")
  #     last_frame = self.state.frame
      
  #     self.update_state()
  #     # if self.menu == Menu.Game:
  #     if True:
  #       if self.game_frame < 10:
  #         # let the slippi frame counter initialize
  #         self.game_frame += 1
  #         print(self.game_frame)
  #         if self.game_frame == 10:
  #           self.start_time = time.time()
  #       elif self.state.frame > last_frame:
  #         print(self.game_frame)
  #         skipped_frames = self.state.frame - last_frame - 1
  #         if skipped_frames > 0:
  #             self.skip_frames += skipped_frames
  #             print("Skipped frames ", skipped_frames)
  #         self.total_frames += self.state.frame - last_frame
  #         last_frame = self.state.frame

  #         start = time.time()
  #         self.make_action()
  #         self.thinking_time += time.time() - start

  #         if self.agent.verbose and self.state.frame % (15 * 60) == 0:
  #             self.print_stats()
  #     else:
  #       self.make_action()

  #     #time.sleep(0.05)
  #     self.mw.advance()

  # def make_action(self):
  #   player = self.state.players[1]
  #   print('a: ', player)
  #   if True:
  #     self.game_frame += 1
      
  #     if self.game_frame % 60 == 0:
  #       print('action_frame', self.state.players[0].action_frame)
  #       items = list(util.deepItems(ct.toDict(self.state.players)))
  #       print('max value', max(items, key=lambda x: abs(x[1])))
      
  #     if self.game_frame <= 120:
  #       return # wait for game to properly load
