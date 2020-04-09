import os
import sqlite3
import signal
import datetime
import shutil
import re
import xml.etree.ElementTree as ET

import numpy as np

from . import sensor_core
from .logger import loader_tcx
from .logger import logger_csv
from .logger import logger_fit

#ambient 
# online uploading service in Japan
# https://ambidata.io
_IMPORT_AMBIENT = False
try:
  #disable
  #import ambient
  #_IMPORT_AMBIENT = True
  pass
except:
  pass


class LoggerCore():
  
  config = None
  sensor = None

  #for DB
  con = None
  cur = None
  
  #for timer
  count = 0
  count_lap = 0
  lap = 0
  record_stats = {
    "pre_lap_avg":{},
    "lap_avg":{},
    "entire_avg":{},
    "pre_lap_max":{},
    "lap_max":{},
    "entire_max":{}
  }
  lap_keys = [
    "heart_rate",
    "cadence",
    "distance",
    "speed",
    "power",
    "accumulated_power",
    "total_ascent",
    "total_descent",
  ]
  #for power and cadence (including / not including zero)
  average = {
    "lap":{
      "cadence":{"count":0,"sum":0},
      "power":{"count":0,"sum":0}},
    "entire":{
      "cadence":{"count":0,"sum":0},
      "power":{"count":0,"sum":0}}
  }

  #for update_track
  pre_lon = None
  pre_lat = None

  #send online
  send_time = None
  send_online_interval_sec = 30
  am = None

  #for debug
  position_log = np.array([])

  def __init__(self, config):
    print("\tlogger_core : init...")
    super().__init__()
    self.config = config
    self.sensor = sensor_core.SensorCore(self.config)
    self.course = loader_tcx.LoaderTcx(self.config, self.sensor)
    self.logger_csv = logger_csv.LoggerCsv(self.config)
    self.logger_fit = logger_fit.LoggerFit(self.config)

    if _IMPORT_AMBIENT:
      #need to get ambient account
      #self.am = ambient.Ambient(channel_ID, write_key)
      self.send_time = datetime.datetime.now()
      print("\tlogger_core : setup ambient...: done", (datetime.datetime.utcnow()-t).total_seconds(), "sec")
    
    t = datetime.datetime.utcnow()
    print("\tlogger_core : loading course...")
    self.course.load()
    print("\tlogger_core : loading course...: done", (datetime.datetime.utcnow()-t).total_seconds(), "sec")
    
    for k in self.lap_keys:
      self.record_stats['pre_lap_avg'][k] = 0
      self.record_stats['lap_avg'][k] = 0
      self.record_stats['entire_avg'][k] = 0
      self.record_stats['pre_lap_max'][k] = 0
      self.record_stats['lap_max'][k] = 0
      self.record_stats['entire_max'][k] = 0

    #sqlite3
    self.init_db()
    con = sqlite3.connect(self.config.G_LOG_DB)
    cur = con.cursor()    
    cur.execute("SELECT timestamp FROM BIKECOMPUTER_LOG LIMIT 1")
    first_row = cur.fetchone()
    if first_row == None:
      self.init_value() 
    else: self.resume(cur)
    cur.close()
    con.close()

    try:
      signal.signal(signal.SIGALRM, self.do_countup)
      signal.setitimer(signal.ITIMER_REAL, self.config.G_LOGGING_INTERVAL, self.config.G_LOGGING_INTERVAL)
    except:
      #for windows
      pass

  def init_db(self):
    con = sqlite3.connect(self.config.G_LOG_DB)
    cur = con.cursor()
    cur.execute("SELECT * FROM sqlite_master WHERE type='table' and name='BIKECOMPUTER_LOG'")
    if cur.fetchone() == None:
      con.execute("""CREATE TABLE BIKECOMPUTER_LOG(
        timestamp DATETIME,
        lap INTEGER, 
        timer INTEGER,
        total_timer_time,
        position_lat FLOAT,
        position_long FLOAT,
        gps_altitude FLOAT,
        gps_distance FLOAT,
        gps_mode INTEGER,
        gps_used_sats INTEGER,
        gps_total_sats INTEGER,
        gps_track INTEGER,
        heart_rate INTEGER,
        cadence INTEGER,
        distance FLOAT,
        speed FLOAT,
        power INTEGER,
        accumulated_power INTEGER,
        temperature FLOAT,
        pressure FLOAT,
        altitude FLOAT,
        heading INTEGER,
        motion FLOAT,
        acc_x FLOAT,
        acc_y FLOAT,
        acc_z FLOAT,
        voltage_battery FLOAT,
        voltage_in FLOAT,
        current_in FLOAT,
        voltage_out FLOAT,
        current_out FLOAT,
        capacity_in FLOAT,
        capacity_out FLOAT,
        battery_percentage FLOAT,
        total_ascent FLOAT,
        total_descent FLOAT,
        lap_heart_rate INTEGER,
        lap_cadence INTEGER,
        lap_distance FLOAT,
        lap_speed FLOAT,
        lap_power INTEGER,
        lap_accumulated_power INTEGER,
        lap_total_ascent FLOAT,
        lap_total_descent FLOAT,
        avg_heart_rate INTEGER,
        avg_cadence INTEGER,
        avg_speed FLOAT,
        avg_power INTEGER,
        lap_cad_count INTEGER,
        lap_cad_sum INTEGER,
        avg_cad_count INTEGER,
        avg_cad_sum INTEGER,
        lap_power_count INTEGER,
        lap_power_sum INTEGER,
        avg_power_count INTEGER,
        avg_power_sum INTEGER
      )""")
      cur.execute("CREATE INDEX lap_index ON BIKECOMPUTER_LOG(lap)")
      cur.execute("CREATE INDEX total_timer_time_index ON BIKECOMPUTER_LOG(total_timer_time)")
      cur.execute("CREATE INDEX timestamp_index ON BIKECOMPUTER_LOG(timestamp)")
      con.commit()
    cur.close()
    con.close()
      
  def do_countup(self, arg1, arg2):
    if self.config.G_STOPWATCH_STATUS != "START":
      return
    self.count += 1
    self.count_lap += 1
    self.record_log()

  def start_and_stop_manual(self):
    self.sensor.sensor_spi.screen_flash_short()
    if self.config.G_MANUAL_STATUS != "START":
      print("->M START\t", datetime.datetime.now())
      self.start_and_stop("STOP")
      self.config.G_MANUAL_STATUS = "START"
      self.config.gui.change_start_stop_button(self.config.G_MANUAL_STATUS)
    elif self.config.G_MANUAL_STATUS == "START":
      print("->M STOP\t", datetime.datetime.now())
      self.start_and_stop("START")
      self.config.G_MANUAL_STATUS = "STOP"
      self.config.gui.change_start_stop_button(self.config.G_MANUAL_STATUS)
 
  def start_and_stop(self, status=None):
    if status != None:
      self.config.G_STOPWATCH_STATUS = status
    if self.config.G_STOPWATCH_STATUS != "START":
      #self.signal_start.emit()
      self.config.G_STOPWATCH_STATUS = "START"
      print("->START\t", datetime.datetime.now())
    elif self.config.G_STOPWATCH_STATUS == "START":
      #self.signal_stop.emit()
      self.config.G_STOPWATCH_STATUS = "STOP"
      print("->STOP\t", datetime.datetime.now())
  
  def count_laps(self):
    if self.count == 0: return
    self.sensor.sensor_spi.screen_flash_short()
    self.lap += 1
    self.count_lap = 0
    for k in self.lap_keys:
      self.record_stats['pre_lap_avg'][k] = self.record_stats['lap_avg'][k]
      self.record_stats['pre_lap_max'][k] = self.record_stats['lap_max'][k]
      self.record_stats['lap_max'][k] = 0
      self.record_stats['lap_avg'][k] = 0
    for k2 in ["cadence","power"]:
      self.average["lap"][k2]["count"] = 0
      self.average["lap"][k2]["sum"] = 0
    self.record_log()

  def reset_count(self):
    if self.config.G_MANUAL_STATUS == "START" or self.count == 0:
      return

    #reset
    self.sensor.sensor_spi.screen_flash_long()
    if self.config.G_LOG_WRITE_CSV:
      t = datetime.datetime.now()
      if not self.logger_csv.write_log():
        return
      print("Write csv :", (datetime.datetime.now()-t).total_seconds(),"sec")
    if self.config.G_LOG_WRITE_FIT:
      t = datetime.datetime.now()
      if not self.logger_fit.write_log():
        return
      print("Write Fit :", (datetime.datetime.now()-t).total_seconds(),"sec")
    
    # backup and reset database
    t = datetime.datetime.now()
    self.init_value()
    shutil.move(self.config.G_LOG_DB, self.config.G_LOG_DB+"-"+self.config.G_LOG_START_DATE)
    self.init_db()
    print("DELETE :", (datetime.datetime.now()-t).total_seconds(),"sec")

  def init_value(self):
    #clear lap
    self.count = 0
    self.count_lap = 0
    self.lap = 0
    for k in self.lap_keys:
      self.record_stats['pre_lap_avg'][k] = 0
      self.record_stats['lap_avg'][k] = 0
      self.record_stats['entire_avg'][k] = 0
      self.record_stats['pre_lap_max'][k] = 0
      self.record_stats['lap_max'][k] = 0
      self.record_stats['entire_max'][k] = 0
    for k1 in self.average.keys():
      for k2 in ["cadence","power"]:
        self.average[k1][k2]["count"] = 0
        self.average[k1][k2]["sum"] = 0
    #reset accumulated values
    self.sensor.reset()

  def record_log(self):
    #need to detect location delta for smart recording
    
    #get present value
    value = {
      "heart_rate":self.sensor.values['integrated']['hr'],
      "cadence":self.sensor.values['integrated']['cadence'],
      "distance":self.sensor.values['integrated']['distance'],
      "speed":self.sensor.values['integrated']['speed'],
      "power":self.sensor.values['integrated']['power'],
      "accumulated_power":self.sensor.values['integrated']['accumulated_power'],
      "total_ascent":self.sensor.values['I2C']['total_ascent'],
      "total_descent":self.sensor.values['I2C']['total_descent']
    }
     
    #update lap stats if value is not Null
    for k,v in value.items():
      #skip when null value(np.nan)
      if v in [self.config.G_GPS_NULLVALUE, self.config.G_ANT_NULLVALUE]:
        continue
      #get average
      if k in ['heart_rate', 'cadence', 'speed', 'power']:
        x1 = t1 = 0 #for lap_avg = x1 / t1
        x2 = t2 = 0 #for entire_ave = x2 / t2
        if k in ['heart_rate', 'speed']:
          lap_avg = self.record_stats['lap_avg'][k]
          x1 = lap_avg * (self.count_lap - 1) + v
          t1 = self.count_lap
          avg = self.record_stats['entire_avg'][k]
          x2 = avg * (self.count - 1) + v
          t2 = self.count
        #average including/excluding zero (cadence, power)
        elif k in ['cadence', 'power']:
          if v == 0 and not self.config.G_AVERAGE_INCLUDING_ZERO[k]:
            continue
          for l_e in ['lap','entire']:
            self.average[l_e][k]['sum'] += v
            self.average[l_e][k]['count'] += 1
          x1 = self.average['lap'][k]['sum']
          x2 = self.average['entire'][k]['sum']
          t1 = self.average['lap'][k]['count']
          t2 = self.average['entire'][k]['count']
        #update lap average
        if t1 == 0: continue
        if t2 == 0: continue
        self.record_stats['lap_avg'][k] = x1 / t1
        self.record_stats['entire_avg'][k] = x2 / t2
      #get lap distance, accumulated_power, total_ascent, total_descent
      elif k in ['distance', 'accumulated_power', 'total_ascent', 'total_descent']:
        # v is valid value
        x1 = self.record_stats['pre_lap_max'][k]
        if np.isnan(x1): x1 = 0
        self.record_stats['lap_avg'][k]  = v - x1
      
      #update max
      if k in ['heart_rate', 'cadence', 'speed', 'power']:
        if self.record_stats['lap_max'][k] < v:
          self.record_stats['lap_max'][k] = v
        if self.record_stats['entire_max'][k] < v:
          self.record_stats['entire_max'][k] = v
      elif k in ['distance', 'accumulated_power', 'total_ascent', 'total_descent']:
        self.record_stats['lap_max'][k] = v
   
    ## SQLite
    con = sqlite3.connect(self.config.G_LOG_DB)
    cur = con.cursor()
    now_time = datetime.datetime.utcnow()
    cur.execute("""\
      INSERT INTO BIKECOMPUTER_LOG VALUES(\
        ?,?,?,?,\
        ?,?,?,?,?,?,?,?,\
        ?,?,?,?,?,?,\
        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
        ?,?,?,?,?,?,?,?,\
        ?,?,?,?,\
        ?,?,?,?,?,?,?,?\
      )""",
      (now_time,
       self.lap,
       self.count_lap,
       self.count,
       ###
       self.sensor.values['GPS']['lat'],
       self.sensor.values['GPS']['lon'],
       self.sensor.values['GPS']['alt'],
       self.sensor.values['GPS']['distance'],
       self.sensor.values['GPS']['mode'],
       self.sensor.values['GPS']['used_sats'],
       self.sensor.values['GPS']['total_sats'],
       self.sensor.values['GPS']['track'],
       ###
       value['heart_rate'],
       value['cadence'],
       value['distance'],
       value['speed'],
       value['power'],
       value['accumulated_power'],
       ###
       self.sensor.values['I2C']['temperature'],
       self.sensor.values['I2C']['pressure'],
       self.sensor.values['I2C']['altitude'],
       self.sensor.values['I2C']['heading'],
       self.sensor.values['I2C']['motion'],
       self.sensor.values['I2C']['acc'][0],
       self.sensor.values['I2C']['acc'][1],
       self.sensor.values['I2C']['acc'][2],
       self.sensor.values['I2C']['voltage_battery'],
       self.sensor.values['I2C']['voltage_in'],
       self.sensor.values['I2C']['current_in'],
       self.sensor.values['I2C']['voltage_out'],
       self.sensor.values['I2C']['current_out'],
       self.sensor.values['I2C']['capacity_in'],
       self.sensor.values['I2C']['capacity_out'],
       self.sensor.values['I2C']['battery_percentage'],
       value['total_ascent'],
       value['total_descent'],
       ###
       self.record_stats['lap_avg']['heart_rate'],
       self.record_stats['lap_avg']['cadence'],
       self.record_stats['lap_avg']['distance'],
       self.record_stats['lap_avg']['speed'],
       self.record_stats['lap_avg']['power'],
       self.record_stats['lap_avg']['accumulated_power'],
       self.record_stats['lap_avg']['total_ascent'],
       self.record_stats['lap_avg']['total_descent'],
       ###
       self.record_stats['entire_avg']['heart_rate'],
       self.record_stats['entire_avg']['cadence'],
       self.record_stats['entire_avg']['speed'],
       self.record_stats['entire_avg']['power'],
       ###
       self.average['lap']['cadence']['count'],
       self.average['lap']['cadence']['sum'],
       self.average['entire']['cadence']['count'],
       self.average['entire']['cadence']['sum'],
       self.average['lap']['power']['count'],
       self.average['lap']['power']['sum'],
       self.average['entire']['power']['count'],
       self.average['entire']['power']['sum']
       )
    )
    con.commit()
    t2 = (datetime.datetime.utcnow() - now_time).total_seconds()
    if self.count % 1800 == 10:
      print("### DB insert ({}s) : {:.3f}s".format(self.count, t2))
    cur.close()
    con.close()

    #send online
    self.send_ambient()

  def resume(self, cur):
    cur.execute("SELECT count(*) FROM BIKECOMPUTER_LOG")
    v = cur.fetchone()
    if v[0] == 0: return
    
    print("resume existing rides...")
    row_all = "\
      lap,timer,total_timer_time,\
      distance,accumulated_power,total_ascent,total_descent,\
      lap_heart_rate,lap_cadence,lap_distance,lap_speed,lap_power,\
      lap_accumulated_power,lap_total_ascent,lap_total_descent,\
      avg_heart_rate,avg_cadence,avg_speed,avg_power,\
      lap_cad_count,lap_cad_sum,lap_power_count,lap_power_sum,\
      avg_cad_count,avg_cad_sum,avg_power_count,avg_power_sum"
    cur.execute("\
      SELECT %s FROM BIKECOMPUTER_LOG\
      WHERE total_timer_time = (SELECT MAX(total_timer_time) FROM BIKECOMPUTER_LOG)" \
      % (row_all))
    value = list(cur.fetchone())
    (self.lap, self.count_lap,self.count) = value[0:3]

    sn = self.sensor.values['integrated']
    i2c = self.sensor.values['I2C']
    (sn['distance'],sn['accumulated_power'],i2c['total_ascent'],i2c['total_descent']) = value[3:7]
    
    index = 7
    for k in self.lap_keys:
      self.record_stats['lap_avg'][k] = value[index]
      index += 1
    for k in ['heart_rate', 'cadence', 'speed', 'power']:
      self.record_stats['entire_avg'][k] = value[index]
      index += 1
    for k1 in ['lap','entire']:
      for k2 in ['cadence','power']:
        for k3 in ['count','sum']:
          self.average[k1][k2][k3] = value[index]
          index += 1
    #print(self.average)
    
    #get lap
    cur.execute("SELECT MAX(LAP) FROM BIKECOMPUTER_LOG")
    max_lap = (cur.fetchone())[0]
    #get max
    max_row = "MAX(heart_rate), MAX(cadence), MAX(speed), MAX(power)"
    main_item = ['heart_rate', 'cadence', 'speed', 'power']
    cur.execute("SELECT %s FROM BIKECOMPUTER_LOG" % (max_row))
    max_value = list(cur.fetchone())
    for i,k in enumerate(main_item):
      self.record_stats['entire_max'][k] = 0
      if max_value[i] != None:
        self.record_stats['entire_max'][k] = max_value[i]
    #get lap max
    cur.execute("SELECT %s FROM BIKECOMPUTER_LOG WHERE LAP = %s" % (max_row,max_lap))
    max_value = list(cur.fetchone())
    for i,k in enumerate(main_item):
      self.record_stats['lap_max'][k] = 0
      if max_value[i] != None:
        self.record_stats['lap_max'][k] = max_value[i]
    #get pre lap
    if max_lap >= 1:
      cur.execute("\
        SELECT %s FROM BIKECOMPUTER_LOG\
        WHERE LAP = %s AND total_timer_time = (\
          SELECT MAX(total_timer_time) FROM BIKECOMPUTER_LOG\
          WHERE LAP = %s)" \
        % (row_all,max_lap-1,max_lap-1))
      value = list(cur.fetchone())
      
      index = 3
      for k in ['distance', 'accumulated_power', 'total_ascent', 'total_descent']:
        self.record_stats['pre_lap_max'][k] = value[index]
        index +=1
      for k in self.lap_keys:
        self.record_stats['pre_lap_avg'][k] = value[index]
        index += 1
      
      #max
      cur.execute("SELECT %s FROM BIKECOMPUTER_LOG WHERE LAP = %s" % (max_row,max_lap-1))
      max_value = list(cur.fetchone())
      for i,k in enumerate(main_item):
        self.record_stats['pre_lap_max'][k] = max_value[i]
    #print(self.record_stats)
    #print(self.average)

    if not self.config.G_IS_RASPI and self.config.G_DUMMY_OUTPUT:
      select = "SELECT position_lat,position_long FROM BIKECOMPUTER_LOG"
      cur.execute(select)
      self.position_log = np.array(cur.fetchall())
 
  def update_track(self, timestamp):
    lon = np.array([])
    lat = np.array([])
    timestamp_new = timestamp
    cond_base = \
      "FROM BIKECOMPUTER_LOG " + \
      "WHERE position_lat is not null AND position_long is not null "
    select_base = "SELECT distance,position_lat,position_long " + cond_base
    #t = datetime.datetime.utcnow()
    
    #copy db file if loading many records (avoiding for db locking with record_log)
    db_file = self.config.G_LOG_DB
    make_tmp_db = False
    timestamp_delta = None
    if timestamp != None:
      timestamp_delta = (datetime.datetime.utcnow() - self.config.datetime_myparser(timestamp)).total_seconds()
    if timestamp_delta != None and timestamp_delta > 120: #[s]
      db_file = db_file+".tmp"
      make_tmp_db = True
      shutil.copy(self.config.G_LOG_DB, db_file)
      print("##### make_tmp_db")

    con = sqlite3.connect(db_file)
    cur = con.cursor()
    if timestamp is None:
      cur.execute(select_base)
    else:
      cur.execute(select_base + "AND timestamp > '%s'" % timestamp)
    
    test = np.array(cur.fetchall())
    if(test.shape[0] > 0):
      lat_raw = test[:,1].astype('float32')
      lon_raw = test[:,2].astype('float32')
      dist_raw = test[:,0].astype('float32') #[m]
      #downsampling
      valid_points = np.insert(
        #close points are delete
        np.where(np.diff(dist_raw) >= 1, True, False) & \
        (
          #same points are delete
          np.where(np.diff(lat_raw) != 0, True, False) | \
          np.where(np.diff(lon_raw) != 0, True, False)
        ),
        0, True)
      lat_raw = lat_raw[valid_points]
      lon_raw = lon_raw[valid_points]
      dist_raw = dist_raw[valid_points]
      azimuth_diff = np.diff(self.config.calc_azimuth(lat_raw, lon_raw))
      azimuth_cond = np.insert(np.where(abs(azimuth_diff) <= 3, False, True), 0, True)
      dist_diff = np.diff(dist_raw)
      dist_cond = np.where(dist_diff >= self.config.G_GPS_DISPLAY_INTERVAL_DISTANCE, True, False)
      cond = np.insert((dist_cond & azimuth_cond), 0, True)
      cond[-1] = True
      lat = lat_raw[cond]
      lon = lon_raw[cond]

      #timestamp
      cur.execute("SELECT MAX(timestamp) FROM BIKECOMPUTER_LOG")
      timestamp_new = cur.fetchone()
      
      print("length", test.shape[0], "->", np.sum(valid_points), "->", len(lat))
    cur.close()
    con.close()

    if timestamp is None:
      timestamp_new = str(datetime.datetime.utcnow())
    if make_tmp_db:
      os.remove(db_file)
    
    #print("\tlogger_core : update_track(new) ", (datetime.datetime.utcnow()-t).total_seconds(), "sec")

    return timestamp_new, lon, lat

  def send_ambient(self):
    if not _IMPORT_AMBIENT or self.config.G_MANUAL_STATUS != "START":
      return
    t = datetime.datetime.now()
    if (t - self.send_time).total_seconds() < self.send_online_interval_sec:
      return
    self.send_time = t
    try:
      d = {
        'd1': self.sensor.values['integrated']['speed'] * 3.6,
        'd2': self.sensor.values['integrated']['hr'], 
        'd3': self.sensor.values['integrated']['cadence'],
        'd4': self.sensor.values['integrated']['power'],
        'd5': self.sensor.values['I2C']['altitude'],
        'd6': self.sensor.values['integrated']['distance']/1000,
        'd7': self.sensor.values['integrated']['accumulated_power']/1000,
        'd8': self.sensor.values['I2C']['temperature'],
        'lat':self.sensor.values['GPS']['lat'], 
        'lng':self.sensor.values['GPS']['lon']
        }
      d_send = {}
      for k,v in d.items():
        if not np.isnan(v):
          d_send[k] = v
      r = self.am.send(d_send)
      print(r,d_send)
    #except requests.exceptions.RequestException as e:
    #  print('request failed: ', e)
    except:
      pass
