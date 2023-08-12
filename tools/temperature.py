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

        self.prev_temp = 0.0

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        # print(lines)
        # print("-"*10)
        try:
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1].strip()[equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                # temp_f = temp_c * 9.0 / 5.0 + 32.0
                self.prev_temp = temp_c
                return temp_c
        except:
            return self.prev_temp

if __name__=="__main__":
    temp_sensor1 =TempSensor(sensor_name = "28-0000000364a0")
    #temp_sensor2 =TempSensor(sensor_name = "28-00000003e755")
    from w1thermsensor import W1ThermSensor,Sensor
    import time
    sensor = W1ThermSensor(Sensor.DS18B20, "00000003e755")
    while True:
        # print(f"[{temp_sensor1.read_temp()}]")
        temp = sensor.get_temperature()
        print(temp)
        time.sleep(1)