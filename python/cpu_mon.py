import json, psutil, os, dbus
from gpiozero import Button, LED, RGBLED
from colorzero import Color
from time import sleep

def monitorCpu():
	cpu = psutil.cpu_percent()

	#print('CPU Usage: %s' % (cpu))

	red = cpu / 100
	green = (100 - cpu) / 100
	blue = 0
	
	#print('Red %f, Green %f, Blue %f, ' % (red, green, blue))
	cpuLed.color = (red, green, blue)

def monitorMem():
	mem = psutil.virtual_memory()
	
	total = mem.total
	available = mem.available
	used = total - available
	percent = used / total * 100
	#print('Memory Usage: %s' % (percent))
	
	red = percent / 100
	green = (100 - percent) / 100
	blue = 0
	
	#print('Red %f, Green %f, Blue %f, ' % (red, green, blue))
	memLed.color = (red, green, blue)

def monitorDisk():
	disk = psutil.disk_usage('/')
	
	total = disk.total
	used = disk.used
	percent = used / total * 100
	#print('Disk Usage: %s' % (percent))

	red = percent / 100
	green = (100 - percent) / 100
	blue = 0
	
	#print('Red %f, Green %f, Blue %f, ' % (red, green, blue))
	diskLed.color = (red, green, blue)

def monitorDiskIo():
	global disksBefore
	diskIo = psutil.disk_io_counters()
	disksAfter = diskIo.read_bytes + diskIo.write_bytes

#	print('Disk IO: was %s - is %s' % (disksBefore, disksAfter))

	if disksAfter > disksBefore:
		diskIoLed.on()
	else:
		diskIoLed.off()
	
	disksBefore = disksAfter

def monitorNetIo():
	global netBefore
	netIo = psutil.net_io_counters()
	netAfter = netIo.packets_recv + netIo.packets_sent

#	print('Network IO: was %s - is %s' % (netBefore, netAfter))

	if netAfter > netBefore:
		netIoLed.on()
	else:
		netIoLed.off()
	
	netBefore = netAfter

def setupBt():
	global bus, man
	try:
		bus = dbus.SystemBus()
		man = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
	except dbus.exceptions.DBusException as error:
		print(str(error) + "\n")

def monitorBt():
	global pairedBefore
	global connectedBefore
	paired = False
	connected = False

	try:
		objects = man.GetManagedObjects()
		
		for path, interfaces in objects.items():
			if "org.bluez.Device1" in interfaces:
				dev = interfaces["org.bluez.Device1"]

				if "Address" not in dev:
					continue

				if "Name" not in dev:
					continue

				props = dbus.Interface(bus.get_object("org.bluez", path), "org.freedesktop.DBus.Properties")

				if props.Get("org.bluez.Device1", "Paired"):
					paired = True

				if props.Get("org.bluez.Device1", "Connected"):
					connected = True

	except dbus.exceptions.DBusException as error:
		print(str(error) + "\n")

	if connected:
		if connected != connectedBefore:
			btLed.on()
	elif paired:
		if paired != pairedBefore or connectedBefore:
			btLed.blink()
	else:
		btLed.off()

	pairedBefore = paired
	connectedBefore = connected

def reboot():
	print('Rebooting...')
	os.system("sudo reboot")

def shutdown():
	print('Shutting down...')
	os.system("sudo shutdown now")

def testLeds():
	diskIoLed.blink()
	netIoLed.blink()
	btLed.blink()
	for counter in range (3):
		for rainbowcolour in range (7):
			if (rainbowcolour == 0):
				colour = Color("red")
			elif (rainbowcolour == 1):
				colour = Color("orange")
			elif (rainbowcolour == 2):
				colour = Color("yellow")
			elif (rainbowcolour == 3):
				colour = Color("green")
			elif (rainbowcolour == 4):
				colour = Color("blue")
			elif (rainbowcolour == 5):
				colour = Color("indigo")
			elif (rainbowcolour == 6):
				colour = Color("darkviolet")
			cpuLed.color = colour
			memLed.color = colour
			diskLed.color = colour
			sleep(0.1)

def main():
	testLeds()
	setupBt()
	counter = 0
	while True:
		monitorCpu()
		monitorNetIo()
		if counter % 2 == 0:
			monitorDiskIo()
			monitorBt()
			monitorMem()
		if counter % 4 == 0:
			monitorDisk()
			counter = 0
		sleep(0.5)
		counter += 1

configFile = open('cpu_mon.config', 'r')
config = json.loads(configFile.read())

#config = {'cpuLed':{'r':24,'g':25,'b':7}, 'memLed':{'r':10,'g':9,'b':11}, 'diskIoLed':16, 'diskLed':{'r':26,'g':13,'b':19}, 'netIoLed':20, 'btLed':21, 'rebootButton':14}
#configFile = open('cpu_mon.config', 'w')
#configFile.write(json.dumps(config))
configFile.close()

cpuLed = RGBLED(config.get('cpuLed').get('r'),config.get('cpuLed').get('g'),config.get('cpuLed').get('b'))
memLed = RGBLED(config.get('memLed').get('r'),config.get('memLed').get('g'),config.get('memLed').get('b'))
diskIoLed = LED(config.get('diskIoLed'))
diskLed = RGBLED(config.get('diskLed').get('r'),config.get('diskLed').get('g'),config.get('diskLed').get('b'))
netIoLed = LED(config.get('netIoLed'))
btLed = LED(config.get('btLed'))

rebootButton = Button(config.get('rebootButton'))
rebootButton.hold_time = 2
rebootButton.when_held = shutdown
rebootButton.when_released = reboot

disksBefore = 0
netBefore = 0

pairedBefore = False
connectedBefore = False

main()
