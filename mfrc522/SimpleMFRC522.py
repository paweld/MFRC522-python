# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import RPi.GPIO as GPIO
  
class SimpleMFRC522:

  READER = None
  
  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  BLOCK_ADDRS = [4,8,12,16]
  BLOCK_ADDRS_TEST = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

  def __init__(self):
    self.READER = MFRC522()
  
  def read(self):
      id, text = self.read_no_block()
      while not id:
          id, text = self.read_no_block()
      return id, text

  def readtest(self):
      id, text = self.read_test_no_block()
      while not id:
          id, text = self.read_test_no_block()
      return id, text

  def read_id(self):
    id = self.read_id_no_block()
    while not id:
      id = self.read_id_no_block()
    return id

  def read_id_no_block(self):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None
      return self.uid_to_num(uid)
  
  def read_no_block(self):
    (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
    if status != self.READER.MI_OK:
        return None, None
    (status, uid) = self.READER.MFRC522_Anticoll()
    if status != self.READER.MI_OK:
        return None, None
    id = ''.join(format(x, '02x') for x in uid)
    self.READER.MFRC522_SelectTag(uid)
    text_read = ''
    status = self.READER.MI_OK #self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1B, 0, self.KEY, uid)
    data = []
    if status == self.READER.MI_OK:
        for block_num in self.BLOCK_ADDRS:
            block = self.READER.MFRC522_Read(block_num) 
            if block:
                data += block
        if data:
             text_read += ''.join(chr(i) if i > 31 else '' for i in data)
    self.READER.MFRC522_StopCrypto1()
    return id, text_read
	
  def read_test_no_block(self):
    (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
    if status != self.READER.MI_OK:
        return None, None
    (status, uid) = self.READER.MFRC522_Anticoll()
    if status != self.READER.MI_OK:
        return None, None
    id = ''.join(format(x, '02x') for x in uid)
    self.READER.MFRC522_SelectTag(uid)
    text_read = ''
	status = self.READER.MI_OK #self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1B, 1, self.KEY, uid)
    data = []
    if status == self.READER.MI_OK:
        for block_num in self.BLOCK_ADDRS_TEST:
            block = self.READER.MFRC522_Read(block_num) 
            if block:
                data = block
            if data:
                text_read += str(block_num) + ': ' + ''.join(chr(i) for i in data) + chr(10)

    self.READER.MFRC522_StopCrypto1()
    return id, text_read
    
  def write(self, text):
      id, text_in = self.write_no_block(text)
      while not id:
          id, text_in = self.write_no_block(text)
      return id, text_in

  def write_no_block(self, text):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1B, 0, self.KEY, uid)
      self.READER.MFRC522_Read(11)
      if status == self.READER.MI_OK:
          data = bytearray()
          data.extend(bytearray(text.ljust(len(self.BLOCK_ADDRS) * 16).encode('ascii')))
          i = 0
          for block_num in self.BLOCK_ADDRS:
            self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
            i += 1
      self.READER.MFRC522_StopCrypto1()
      return id, text[0:(len(self.BLOCK_ADDRS) * 16)]
      
  def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n

  def free_rfid(self):
      self.READER.Close_MFRC522()
