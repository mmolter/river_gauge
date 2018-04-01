import logging
import os
import re
import time
import urllib2

def get_river_level():
    ''' Return river level (ft) at PIAI2 river gauage. '''

    url = 'https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=piai2&output=tabular'
    
    response = urllib2.urlopen(url)

    for line in response:
        match = re.search(r'<td nowrap>(\d+\.?\d+)ft</td>', line)
        if match:
            return float(match.group(1))
    else:
        raise AttributeError('Invalid response from NOAA')

def mapit(x, in_min, in_max, out_min, out_max):
    ''' Scale range of input x. '''

    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def set_gauge(level):
    ''' Set gauge dial to specified level (ft). '''
    
    pin = 0
    freq = 50
    
    min_level = 1
    max_level = 30
    
    min_pwm = 1
    max_pwm = 77
    
    pwm = mapit(level, min_level, max_level, min_pwm, max_pwm)
        
    os.system('fast-gpio pwm %s %s %s' % (pin, freq, pwm))
    

if __name__ == '__main__':
    logging.basicConfig(filename='river_gauge.log', level=logging.DEBUG,
                       format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    
    level = 0
    logging.debug('Attempting to retrieve new river data...')
        
    try:
        level = get_river_level()
        logging.info('PIAI2 river level at %.2f ft.' % level)
        
    except urllib2.URLError:
        logging.error('Network error, could not reach NOAA site.')
        
    except AttributeError:
        logging.error('NOAA returned an invalid response, try again later.')
        
    except Exception as e:
        logging.error('Onion encountered an unknown error (%s) while retrieving data. '
                      'It has recovered and will try again in 30 minutes' % e)
            
    try:
        set_gauge(level):
    except Exception as e:
        logging.error('Onion encountered an unknown error (%s) while setting the'
                      ' gauage. It has recovered and will try again in 30 minutes.' % e)
