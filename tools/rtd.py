# #Raspberry Pi LM75A I2C temperature sample code.
# #Author: Leon Anavi <leon@anavi.org>

# import sys
# import smbus
# import time
# # By default the address of LM75A is set to 0x48
# # aka A0, A1, and A2 are set to GND (0v).
# address = 0x48

# # Check if another address has been specified
# # if 1 < len(sys.argv):
# # 	address = int(sys.argv[1], 16)

# # Read I2C data and calculate temperature
# bus = smbus.SMBus(1)
# raw = bus.read_word_data(address, 0) & 0xFFFF
# # while True:
# #     print('Temperature: *C',raw)
# #     time.sleep(1)
# raw = ((raw << 8) & 0xFF00) + (raw >> 8)
# temperature = (raw / 32.0) / 8.0
# # Print temperature
# while True:
#     print('Temperature: {0:0.2f} *C'.format(raw))
#     time.sleep(1)

# import board
# import busio
# import Adafruit_ADS1x15.ADS1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn

# i2c = busio.I2C(board.SCL, board.SDA)
# ads = ADS.ADS1115(i2c)

# channel = AnalogIn(ads, ADS.P0)
# r0 = 100.0  # PT100의 저항값 (0도 섭씨에서)
# vref = ads.voltage  # ADS1115의 참조전압
# r = ((vref - channel.voltage) * r0) / channel.voltage
# temperature = (r / 100.0) - 273.15  # 섭씨 온도 계산

# print("Temperature: {:.2f} degrees Celsius".format(temperature))

# import Adafruit_ADS1x15

# # Create an ADS1115 ADC (16-bit) instance.
# adc = Adafruit_ADS1x15.ADS1115()

# # Set the gain to 1 for reading voltages up to 4.096V.
# # You can also adjust this value depending on the voltage range of your sensor.
# GAIN = 1

# # Read the analog input value from A0 pin (PT100 sensor's positive/negative terminals).
# value = adc.read_adc(0, gain=GAIN)

# # Convert the raw analog input value to temperature value in Celsius using PT100's characteristic curve.
# temperature = adc.compute_temperature(value, rtd_nominal=100, ref_resistor=430, ref_temperature=0)

# print("Temperature: {} degrees Celsius".format(temperature))

# import time
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn
# import adafruit_max31865

# # I2C 인터페이스 설정
# i2c = busio.I2C(board.SCL, board.SDA)

# # ADS1115 설정
# ads = ADS.ADS1115(i2c)
# chan = AnalogIn(ads, ADS.P0)

# # MAX31865 설정
# max31865 = adafruit_max31865.PT100(i2c, rtd_nominal=100, ref_resistor=430.0, wires=3)

# # 온도 센서값 읽기 함수
# def read_temp():
#     rtd = max31865.temperature
#     return rtd

# while True:
#     # RTD 온도 센서값 읽기
#     temp_rtd = read_temp()
#     print("RTD Temperature: {:.2f} C".format(temp_rtd))

#     # 1초 대기
#     time.sleep(1.0)

# import time
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn
# import adafruit_max31865

# # RTD PT100 센서를 연결하는 핀
# RTD_PIN = board.D5

# # ADS1115 ADC 모듈 초기화
# i2c = busio.I2C(board.SCL, board.SDA)
# ads = ADS.ADS1115(i2c)

# # 아날로그 입력 채널 설정
# chan = AnalogIn(ads, ADS.P0)

# # PT100 센서 초기화
# rtd = adafruit_max31865.MAX31865(chan, RTD_PIN)

# # 루프에서 온도를 읽고 출력
# while True:
#     print("Temperature: ", rtd.temperature)
#     time.sleep(1)

# import time
# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn
# import adafruit_max31865

# # PT100 센서를 연결하는 핀
# PT100_PIN = board.D5

# # ADS1115 ADC 모듈 초기화
# i2c = busio.I2C(board.SCL, board.SDA)
# adc = ADS.ADS1115(i2c, address=0x48)

# # ADC 게인 설정
# GAIN = 1

# # PT100 센서 초기화
# chan = AnalogIn(adc, ADS.P0)
# rtd = adafruit_max31865.MAX31865(chan, PT100_PIN)

# # 루프에서 온도를 읽고 출력
# while True:
#     print("Temperature: ", rtd.temperature)
#     time.sleep(1)

# import Adafruit_ADS1x15  # ADS1115 라이브러리
# import math
# import time

# # ADC 초기화
# adc = Adafruit_ADS1x15.ADS1115()
# GAIN = 1
# # PT100 RTD 저항 값
# R_REF = 430.0
# # PT100 RTD 알파값
# ALPHA = 0.00385

# temperature = 25.0
# # 측정 횟수
# NUM_SAMPLES = 100

# # PT100 온도 계산 함수
# def pt100_temperature(R,T):
#     R_0 = 100.0
#     A = 3.9083e-3
#     B = -5.775e-7
#     return (-R_0 * A + math.sqrt(R_0**2 * A**2 - 4 * R_0 * B * (R_0 - R))) / (2 * R_0 * B) - T

# # 메인 루프
# while True:
#     # ADC 값을 읽어옴
#     adc_value = adc.read_adc(0, gain=GAIN)

#     # ADC 값을 PT100의 저항 값으로 변환
#     rtd_resistance = R_REF * adc_value / 32767.0

#     # PT100의 온도 값 계산
#     temperature = pt100_temperature(rtd_resistance / (1 + ALPHA * temperature),temperature)

#     # 온도 값 출력
#     print('Temperature: {:.2f} C'.format(temperature))

#     # 잠시 대기
#     time.sleep(0.1)

import smbus
import struct

# bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

DEVICE_ADDRESS = 0x48  # 7 bit address (will be left shifted to add the read write bit)

RTD_TEMPERATURE_ADD = 0
RTD_RESISTANCE_ADD = 59


def get(stack, channel):
    if stack < 0 or stack > 7:
        raise ValueError('Invalid stack level')
    if channel < 1 or channel > 8:
        raise ValueError('Invalid channel number')
    val = (-273.15)
    bus = smbus.SMBus(1)
    try:
        buff = bus.read_i2c_block_data(DEVICE_ADDRESS + stack, RTD_TEMPERATURE_ADD + (4 * (channel - 1)), 4)
        val = struct.unpack('f', bytearray(buff))
    except Exception as e:
        bus.close()
        raise ValueError('Fail to communicate with the RTD card with message: \"' + str(e) + '\"')
    bus.close()
    return val[0]


def getRes(stack, channel):
    if stack < 0 or stack > 7:
        raise ValueError('Invalid stack level')
    if channel < 1 or channel > 8:
        raise ValueError('Invalid channel number')
    val = (-273.15)
    bus = smbus.SMBus(1)
    try:
        buff = bus.read_i2c_block_data(DEVICE_ADDRESS + stack, RTD_RESISTANCE_ADD + (4 * (channel - 1)), 4)
        val = struct.unpack('f', bytearray(buff))
    except Exception as e:
        bus.close()
        raise ValueError('Fail to communicate with the RTD card with message: \"' + str(e) + '\"')
    bus.close()
    return val[0]

print(get(0,1))