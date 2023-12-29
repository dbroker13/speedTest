import json
import requests
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import time
import json
import os

reportLock = threading.Lock()


API_KEY = os.environ["API_KEY"]
token = API_KEY

class SimpleAppiumRun(threading.Thread):
    def __init__(self, argument, argument2):
        super(SimpleAppiumRun, self).__init__()
        self.argument = argument
        self.argument2 = argument2

    def run(self):
        device_id = self.argument
        host = self.argument2

        nobrowser_devices = []
        captureSession = True
        captureNetwork = False
        appAutomation = device_id in nobrowser_devices
        global token
        
        desired_caps = {}
        selector = "device_id="+device_id

        desired_caps = {
                "automationName": "xcuitest",
                "platformName": "ios",
                "browserName":"Safari",
                "headspin:selector":selector, 
                "headspin:capture.video" : captureSession,
                "headspin:capture.network" : captureNetwork,
                "headspin:newCommandTimeout" : "300",
                "headspin:retryNewSessionFailure" : False,
                "appium:shouldTerminateApp" : True,
                "headspin:network.regionalRouting" : "pbox",
        }
        
        driver = None
        try:
            driver = webdriver.Remote("https://appium-dev.headspin.io/v0/" + token + "/wd/hub", desired_caps)
        except Exception as e:
            print("*---------------------")
            print(e)
            print("DRIVER CONNECTION FAILED FOR DEVICE " + device_id)
            print("---------------------*")
            return
            
        if not appAutomation:
            wait = WebDriverWait(driver, 50)
            try:
                # if printLockSpeeds:
                driver.get('http://www.fast.com')
                # time.sleep(30)
                val = wait.until(EC.presence_of_element_located((By.ID, 'speed-value')))
                units = wait.until(EC.presence_of_element_located((By.ID, 'speed-units')))
                print(val.text + ": " + units.text + " for device UUID " + device_id)

            except Exception as e:
                print("*---------------------")
                print(e)
                print("Couldn't load the web page for device " + device_id + ". Aborting!")
                print("---------------------*")
                
            finally:
                driver.implicitly_wait(10)

                driver.quit()


json_url = "https://api-dev.headspin.io/v0/devices/device_type:ios/information"

headers = {"Authorization": "Bearer " + token}
json_data = requests.get(json_url, headers=headers).json()

holder = json_data['devices'].copy()
for device_obj in holder:
    if device_obj["owner_email"] is not None:
        json_data['devices'].remove(device_obj)
        print("removing " + device_obj['device_id'])

if 'devices' in json_data:
    for device_obj in json_data['devices']:
        if 'hostname' in device_obj:
            hostname = device_obj['hostname']
        else:
            hostname = None

        if 'device_id' in device_obj:
            device_id = device_obj['device_id']
        else:
            device_id = None

        if 'safari' not in device_id and 'chrome' not in device_id and 'opera' not in device_id and 'firefox' not in device_id and 'edge' not in device_id:
            appiumThread = SimpleAppiumRun(device_id, hostname)
            appiumThread.start()
        
else:
    print("'devices' key not found in the JSON data.")
