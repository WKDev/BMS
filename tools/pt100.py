
"""
Simple demo of reading Temperature using a Pt100 sensor with the help of a
Raspbbery Pi and the ADS1115 AD controller.
Author: Christos Karapanagiotis
"""

import time
import csv
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import board
import busio
import inspect


GAIN = 8
#The gain defines the voltage range:
#  Gain = 2/3   --> +/-6.144V
#  Gain = 1     --> +/-4.096V
#  Gain = 2     --> +/-2.048V
#  Gain = 4     --> +/-1.024V
#  Gain = 8     --> +/-0.512V
#  Gain = 16    --> +/-0.256V

GAIN_MAP = {
    2/3 : 6.144,
    1 : 4.096,
    2: 2.048,
    4 : 1.024,
    8 : 0.512,
    16 : 0.256
}

class PT100:
    def __init__(self) -> None:
        #Import the conversion table
        self.conv_list = None
        with open("/home/motion/Desktop/flir/tools/pt100/pt100.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            conv_list = list(csv_reader)
            self.conv_list = list(list(map(float,i)) for i in conv_list)

        self.adc = Adafruit_ADS1x15.ADS1115()

        self.temperature = None


    def show_me(self):
        # Print nice channel column headers.
        print(f"[{self.__class__.__name__}] Temperature : {self.temperature}°C")

    def find_nearest(self,list_,ref_resist):
        """
        find the element in a list which is closest to a reference value
        """
        resist = list(list_[i][1] for i in range(len(list_)))
        nearest_value = min(resist, key=lambda x:abs(x-ref_resist))
        list_index = resist.index(nearest_value)
        temperature = list_[list_index][0]

        return temperature

    def read_temp(self):
        # Main loop.
            # Read all the ADC channel values in a list.
        values = [0]*2
        for i in range(2):
            # Read the specified ADC channel using the previously set gain value.
            values[i] = self.adc.read_adc(i, gain=GAIN)/32767 *GAIN_MAP[GAIN] * 1000

            # Note you can also pass in an optional data_rate parameter that controls
            # the ADC conversion time (in samples/second). Each chip has a different
            # set of allowed data rate values, see datasheet Table 9 config register
            # DR bit values.
            #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
            # Each value will be a 12 or 16 bit signed integer value depending on the
            # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).

        # print(f"Voltage in :{values[0]} | voltage out {values[1]}")
        R3 = 100 * (1 / ((values[0]/values[1])-1))
        self.temperature = self.find_nearest(self.conv_list, R3) - 8.5
        return float(self.temperature)


if __name__=="__main__":
    temp = PT100()
    while True:
        print(f"[{temp.read_temp()}]")
        time.sleep(1)