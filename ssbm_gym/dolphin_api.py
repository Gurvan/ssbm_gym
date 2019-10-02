"""
Responsible for interfacing with Dolphin to interface with SSBM, and handles things like:
* character selection
* stage selection
* running Phillip within SSBM

"""


from . import ssbm, state_manager, util, movie
from .dolphin import DolphinRunner, Player
from . import memory_watcher as mw
from .state import *
from .menu_manager import *
import os
from .pad import *
import time
from . import ctype_util as ct
import random
from .default import *
import functools

class DolphinAPI(Default):
  _options = [
    Option('zmq', type=int, default=1, help="use zmq for memory watcher"),
    Option('tcp', type=int, default=0, help="use zmq over tcp for memory watcher and pipe input"),
    Option('start', type=int, default=1, help="start game in endless time mode"),
    Option('debug', type=int, default=0),
  ]

  
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
      player = getattr(self.dolphin, 'player%d' % j)
      print(player)
      self.players[i] = player
      if player == 'ai':
        self.pids.append(i)

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
    

    self.dolphin_process = None
    self.last_frame = 0


  def reset(self):
    if self.dolphin_process is not None:
      self.close()
      #self.dolphin_process.terminate()
    self.init_stats()
    self.state = ssbm.GameMemory()
    print(self.state.players[0])

  
    pipe_dir = os.path.join(self.user, 'Pipes')
    print('Creating Pads at %s.' % pipe_dir)
    util.makedirs(pipe_dir)

    pad_ids = self.pids
    if self.dolphin.netplay:
      pad_ids = [0]
    
    print('Running dolphin.')
    self.dolphin_process = self.dolphin()


    print(pad_ids)
    pipe_paths = [os.path.join(pipe_dir, 'p%d' % i) for i in pad_ids]
    print(pipe_paths)

    self.pads = [Pad(path, tcp=self.tcp) for path in pipe_paths]

    print("Pipes initialized.")

    self.start_time = time.time()
    self.update_state()
    while(self.state.players[0].action_state != 322 or
          self.state.players[1].action_state != 322):
      self.mw.advance()
      self.update_state()
      # print(self.state.players[1].action_state, self.state.players[1].action_state)
    return self.state


  def close(self):
    for pad in self.pads:
      del pad
    self.dolphin_process.terminate()
    while True:
      try:
        self.mw.advance()
      except:
        pass
      try:
        self.update_state()
      except:
        break
      try:
        self.mw.advance()
      except:
        break
    self.dolphin_process.terminate()

  def init_stats(self):
    self.game_frame = 0
    self.total_frames = 1
    self.skip_frames = 0

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
        self.mw.advance()
        self.update_state()
      except:
        pass
        #print('couldnt advance')
        #self.mw.get_messages()
      #print(self.state.frame, self.state.players[0].percent)

    self.last_frame = self.state.frame
    return self.state

