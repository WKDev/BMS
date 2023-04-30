import os
import time


# 28-0000000364a0  28-00000003e755
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class TempSensor:
    def __init__(self,
                 sensor_name : str) -> None:
        base_dir = '/sys/bus/w1/devices/'
        device_folder = base_dir + sensor_name
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            # temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c

if __name__=="__main__":
    temp_sensor2 =TempSensor(sensor_name = "28-00000003e755")
    import time
    while True:
        print(f"[{temp_sensor2.read_temp()}]")
        time.sleep(1)