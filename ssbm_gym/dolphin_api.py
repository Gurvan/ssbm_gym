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
    Option('windows', action="store_true", default=False, help="to be define if the plateform is Windows"),
    # Option('start', type=int, default=1, help="start game in endless time mode"),
    # Option('debug', type=int, default=0),
  ]
  _members = [
    ('dolphin', DolphinRunner),
  ]
  
  def __init__(self, **kwargs):
    Default.__init__(self, **kwargs)

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
      self.players[i] = player
      if player == 'ai':
        self.pids.append(i)

    self.state = ssbm.GameMemory()
    # track players 1 and 2 (pids 0 and 1)
    self.sm = state_manager.StateManager([0, 1])
    self.write_locations()
    
    # print('Creating MemoryWatcher.')
    if self.windows:
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
    self.state = ssbm.GameMemory()

    pipe_dir = os.path.join(self.user, 'Pipes')
    # print('Creating Pads at %s.' % pipe_dir)
    util.makedirs(pipe_dir)
    
    # print('Running dolphin.')
    self.dolphin_process = self.dolphin()

    pad_ids = self.pids
    pipe_paths = [os.path.join(pipe_dir, 'p%d' % i) for i in pad_ids]
    self.pads = [Pad(path, tcp=self.windows) for path in pipe_paths]

    # print("Pipes initialized.")

    self.start_time = time.time()
    self.update_state()
    while(self.state.players[0].action_state != 322 or
          self.state.players[1].action_state != 322):
      self.mw.advance()
      self.update_state()
      # print(self.state)
      # print(self.state.players[0].action_state, self.state.players[1].action_state)
    return self.state


  def close(self):
    for pad in self.pads:
      del pad
    self.dolphin_process.terminate()
    time.sleep(0.1)
    self.dolphin_process.terminate()
    self.dolphin_process = None


  def write_locations(self):
    path = os.path.join(self.dolphin.user, 'MemoryWatcher')
    util.makedirs(path)
    # print('Writing locations to:', path)
    with open(os.path.join(path, 'Locations.txt'), 'w') as f:
      f.write('\n'.join(self.sm.locations()))


  def update_state(self):
    messages = self.mw.get_messages()
    for message in messages:
      self.sm.handle(self.state, *message)
  
  def step(self, controllers):
    for pid, pad in zip(self.pids, self.pads):
      assert(self.players[pid] == 'ai')
      pad.send_controller(controllers[pid])
    while self.state.frame == self.last_frame:
      try:
        self.mw.advance()
        self.update_state()
      except:
        pass

    self.last_frame = self.state.frame
    return self.state

