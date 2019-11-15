#!/usr/bin/env python2
	
# Power
power = {'self_off_voltage':2.0,
	 'self_on_voltage':2.5}

# main	
main = {'sleep_time':5,
	'max_data':200}

# ADC pins
ADC_pins = {'CO_PIN':0,
	    'VOC_PIN':1,
	    'OZ_PIN':2,
	    'ADC_Vin':3}

# Convert from ADC readings to concentration
ADC_conversion = {'v_factor':(4.096 / 32767), # 4.096V = reading of 32767 on ADC
		  'Vc':5,		      # the voltatge everything is powered with
		  'CO_RL':10000, 	      # 10k resistor connected to the CO sensor
		  'OZ_RL':10000, 	      # 39k resistor connected to the OZ sensor
		  'VOC_RL':10000} 	      # 10k resistor on the VOC sensor board

# Resistances at known conditions. CALIBRATION REQUIRED
Ro = {'CO_Ro':200000,
      'OZ_Ro':2000,
      'VOC_Ro':100000} # between 100 and 1500 kOhm
