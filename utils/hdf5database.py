import os
import string
import datetime
import h5py
import numpy as np
from threading import Event

class HDF5Database(object):
  database_file:string = None
  write_event:Event = None
  read_event:Event = None
  def __init__(self, file_path:string) -> None:
    self.database_file = file_path
    self.write_event = Event()
    self.read_event = Event()
    self.write_event.set()
    self.read_event.set()
  
  def delete_database(self) -> bool:
    try:
      os.remove(self.database_file)
      return True
    except:
      return False
  
  def set_version(self, version:int) -> None:
    self.read_event.wait()
    self.write_event.clear()
    try:
      with h5py.File(self.database_file, 'a') as db:
        db.database_file.attrs['version'] = version
    finally:
      self.write_event.set()
  
  def get_version(self) -> int:
    self.write_event.wait()
    self.read_event.clear()
    try:
      with h5py.File(self.database_file, 'r') as db:
        return db.database_file.attrs['version']
    finally:
      self.read_event.set()