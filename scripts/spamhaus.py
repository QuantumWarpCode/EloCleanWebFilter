import os, shutil, time, datetime, urllib.request, ipaddress, math, re, sys, traceback

print("Spamhaus DROP and EDROP to Adguard Regex Converter")

# Get datetime in this format: Tuesday, 12 Jan 2020
datetimeString = datetime.datetime.now().strftime("%A, %d %b %Y")

dropText = """[uBlock Origin]
! Title: Spamhaus DROP Adguard Home
! Description: Spamhaus Do Not Route or Peer
! Expires: 7 days
! Updated: """

# Datetime 
dropText += datetimeString

dropText += """
! License: All rights reserved to Spamhaus Project
! Homepage: https://github.com/QuantumWarpCode/EloCleanWebFilter
! GitHub issues: https://github.com/QuantumWarpCode/EloCleanWebFilter/issues
! GitHub pull requests: https://github.com/QuantumWarpCode/EloCleanWebFilter/pulls
! Writing rules: https://github.com/gorhill/uBlock/wiki/Static-filter-syntax
! Source: https://www.spamhaus.org/drop/drop.txt
! Special thanks to https://d-fault.nl/CIDRtoRegex

! """

edropText = """[uBlock Origin]
! Title: Spamhaus EDROP Adguard Home
! Description: Spamhaus Extended Do Not Route or Peer
! Expires: 7 days
! Updated: """

# Datetime in this format: Tuesday, 12 Jan 2020
edropText += datetimeString

edropText += """
! License: All rights reserved to Spamhaus Project
! Homepage: https://github.com/QuantumWarpCode/EloCleanWebFilter
! GitHub issues: https://github.com/QuantumWarpCode/EloCleanWebFilter/issues
! GitHub pull requests: https://github.com/QuantumWarpCode/EloCleanWebFilter/pulls
! Writing rules: https://github.com/gorhill/uBlock/wiki/Static-filter-syntax
! Source: https://www.spamhaus.org/drop/edrop.txt
! Special thanks to https://d-fault.nl/CIDRtoRegex

! """

def netmaskLength(netmask):
	if netmask == "255":
		print(netmask)
		return 0
	elif netmask == "254":
		return 1
	elif netmask == "252":
		return 2
	elif netmask == "248":
		return 3
	elif netmask == "240":
		return 4
	elif netmask == "224":
		return 5
	elif netmask == "192":
		return 6
	elif netmask == "128":
		return 7
	elif netmask == "0":
		return 8
	else:
		return 9



# Converts single-group ranges to regex
def safeRangeToRegex(min, max, last=False):
	regex = ""
	
	# If range contains only one value
	if min == max:
		regex += str(min)
		if math.floor(min / 100) < 1:
			regex += "$"
	else:
		minOnes = min % 10
		minHundreds = math.floor(min / 100)
		minTens = math.floor(min / 10) - (minHundreds * 10)
		maxOnes = max % 10
		maxHundreds = math.floor(max / 100)
		maxTens = math.floor(max / 10) - (maxHundreds * 10)
		
		# If hundreds digit is the same throughout range
		if minHundreds == maxHundreds:
			# If tens digit is the same throughout range
			if minTens == maxTens:
				if minHundreds != 0:
					regex +=str(minHundreds)
				if minTens != 0:
					regex +=str(minTens)
				regex += "["
				regex += str(minOnes)
				regex += "-"
				regex += str(maxOnes)
				regex += "]"
				if math.floor(min / 100) < 1 and last == True:
					regex += "$"
			# Does it include all numbers within the tens range?
			elif minOnes == 0 and maxOnes == 9:
				if minHundreds != 0:
					regex +=str(minHundreds)
				regex += "["
				regex += str(minTens)
				regex += "-"
				regex += str(maxTens)
				regex += "]["
				regex += str(minOnes)
				regex += "-"
				regex += str(maxOnes)
				regex += "]"
				if minHundreds < 1 and last == True:
					regex += "$"
			else:
				print("Regex not safe! Not generating range. Tens")
				print("Range was", min, " - ", max)
				traceback.print_stack()
				sys.exit("Unsafe range...tens")
		else:
			print("Regex not safe! Not generating range. Hundreds")
			print("Range was", min, " - ", max)
			traceback.print_stack()
			sys.exit("Unsafe range...hundreds")
	
	return regex



# Converts range of values between 0-255 to regex groups
def rangeToRegex(min, max, last=False):
	#print("{", min, ",", max, "}")
	
	regex = "("
	
	# Get individual digits of min and max
	minOnes = min % 10
	minTens = math.floor(min / 10)
	minHundreds = math.floor(min / 100)
	maxOnes = max % 10
	maxTens = math.floor(max / 10)
	maxHundreds = math.floor(max / 100)
	
	# Does the range include single digit numbers?
	if min < 10:
		# Is it all single digit numbers greater than min?
		if max > 9:
			regex += safeRangeToRegex(min, 9, last)
			regex += "|"
		else:
			regex += safeRangeToRegex(min, max, last)
	
	# Does the range include two digit numbers?
	if min < 100 and max > 9:
		# Does the min include all two digit numbers?
		if min < 11:
			# Does the max include all two digit numbers?
			if max > 98:
				regex += safeRangeToRegex(10, 99, last)
			else:
				# Is the ones digit of max a 9?
				if maxOnes == 9:
					regex += safeRangeToRegex(10, max, last)
				else:
					regex += safeRangeToRegex(10, maxTens * 10 - 1, last)
					regex +="|"
					regex += safeRangeToRegex(maxTens * 10, max, last)
		else:
			# Does the max include all two digit numbers?
			if max > 98:
				# Is the ones digit of min a 0?
				if minOnes == 0:
					regex += safeRangeToRegex(min, 99, last)
				else:
					regex += safeRangeToRegex(min, minTens * 10, last)
					
					# Are there numbers above the minTens?
					if minTens < 9:
						regex += "|"
						regex += safeRangeToRegex((minTens + 1) * 10, 99, last)
			else:
				# Is the ones digit of min a 0?
				if minOnes == 0 and (minTens != maxTens):
					regex += safeRangeToRegex(min, maxTens * 10 - 1, last)
				elif (minTens != maxTens):
					regex += safeRangeToRegex(min, ((minTens + 1) * 10) - 1, last)
					if maxTens - minTens > 1:
						regex += "|"
						regex += safeRangeToRegex((minTens + 1) * 10, (maxTens * 10) - 1, last)
				if maxOnes != 0:
					if minTens != maxTens:
						regex += "|"
					regex += safeRangeToRegex(maxTens * 10, max, last)
		# Will there be a three digit block?
		if max > 99:
			regex += "|"
	
	# Does range include three digit?
	if max > 99:
		# Does range include values from 100-199?
		if min < 200:
			# Does range go to 199?
			if max > 198:
				# Does range include 100?
				if min < 101:
					regex += safeRangeToRegex(100, 199, last)
				else:
					# Is the ones digit of min a 0?
					if minOnes == 0:
						regex += safeRangeToRegex(min, 199, last)
					else:
						regex += safeRangeToRegex(min, ((minTens + 1) * 10) - 1, last)
						
						# Are there numbers above the minTens?
						if minTens < 19:
							regex += "|"
							regex += safeRangeToRegex((minTens + 1) * 10, 199, last)
			else:
				if min < 100 and max > 109:
					regex += safeRangeToRegex(100, maxTens * 10 -1, last)
				elif minOnes == 0 and (minTens != maxTens):
					regex += safeRangeToRegex(min, maxTens * 10 - 1, last)
				elif (minTens != maxTens):
					regex += safeRangeToRegex(min, ((minTens + 1) * 10) - 1, last)
					if maxTens - minTens > 1:
						regex += "|"
						regex += safeRangeToRegex((minTens + 1) * 10, (maxTens * 10) - 1, last)
				if maxOnes != 0:
					if minTens != maxTens:
						regex += "|"
					regex += safeRangeToRegex(maxTens * 10, max, last)
		if max > 199:
			if min < 200:
				regex += "|"
			
			if min < 201 or minOnes == 0:
				if (minOnes == 0 and maxOnes == 9) or maxTens == 20:
					regex += safeRangeToRegex(200, max, last)
				else:
					regex += safeRangeToRegex(200, max - maxOnes - 1, last)
					regex += "|"
					regex += safeRangeToRegex(max - maxOnes, max, last)
			else:
				if minTens == maxTens:
					regex += safeRangeToRegex(min, max, last)
				else:
					regex += safeRangeToRegex(min, (minTens + 1) * 10 - 1, last)
					regex += "|"
					if maxTens - minTens > 1:
						regex += safeRangeToRegex((minTens + 1) * 10, maxTens * 10 - 1, last)
						regex += "|"
					regex += safeRangeToRegex(maxTens * 10, max, last)
	
	regex += ")"
	
	#print(regex)
	
	return regex



def lineToRegex(line):
	regex = "/("
	
	# Gather the string before the first space
	cidr = line.split(' ', 1)[0]
	#print("Converting CIDR", cidr)
	
	# Split on / to get ip and subnet
	ipStart = cidr.split('/', 1)[0]
	# Split ip to dots
	ipDots = ipStart.split('.', 3)
	subnet = cidr.split('/', 1)[1]
	
	network = ipaddress.IPv4Network(cidr)
	#print(network.netmask)
	netmaskDots = format(network.netmask).split('.', 3)
	
	for i in range(0, 4):
		if netmaskDots[i] == "255":
			regex += ipDots[i]
			if i < 3:
				regex += "\."
		#elif netmaskDots[i] == "0":
			# Regex for all valid ip values
			#regex += "(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
			#if i < 3:
			#	regex += "\."
		else:
			
			#regex += netmaskDots[i]
			nLength = netmaskLength(netmaskDots[i])
			ipMaxDelta = 2**nLength - 1
			ipMin = int(ipDots[i])
			ipMax = ipMin + ipMaxDelta
			
			if i == 3:
				regex += rangeToRegex(ipMin,ipMax, last=True)
			else:
				regex += rangeToRegex(ipMin,ipMax)
			
			if i < 3:
				regex += "\."
	
	regex += ")/"
	
	#print(regex)
	return regex



# File locations
workingdir = os.path.dirname(__file__)
droploc = os.path.join(workingdir, 'downloads', 'drop.txt')
dropoloc = os.path.join(workingdir, 'output', 'drop.txt')
edroploc = os.path.join(workingdir, 'downloads', 'edrop.txt')
edropoloc = os.path.join(workingdir, 'output', 'edrop.txt')

# Spamhaus list urls
dropurl = 'https://www.spamhaus.org/drop/drop.txt'
edropurl = 'https://www.spamhaus.org/drop/edrop.txt'

# Get current time
time = datetime.datetime.fromtimestamp(time.time())
#print("Current time is: ")
#print(time.strftime('%c'))

# Get most recent files (if enough time has elapsed)
print("Downloading lists.")
if os.path.exists(droploc):
	droptime = datetime.datetime.fromtimestamp(os.stat(droploc).st_mtime)
	#print("DROP file modified at: ")
	#print(droptime.strftime('%c'))
	
	dropdays = (time - droptime) / datetime.timedelta(days=1)
	#print ("Time since download...")
	#print(dropdays)
	if dropdays >= 1:
		print("Aquiring new copy of DROP.")
		urllib.request.urlretrieve(dropurl, droploc)
	else:
		print("DROP already up to date.")
else:
	print("Aquiring copy of DROP.")
	urllib.request.urlretrieve(dropurl, droploc)
if os.path.exists(edroploc):
	edroptime = datetime.datetime.fromtimestamp(os.stat(edroploc).st_mtime)
	#print("EDROP file modified at: ")
	#print(edroptime.strftime('%c'))
	
	edropdays = (time - edroptime) / datetime.timedelta(days=1)
	#print("Time since download...")
	#print(edropdays)
	if edropdays >= 1:
		print("Aquiring new copy of EDROP.")
		urllib.request.urlretrieve(edropurl, edroploc)
	else:
		print("EDROP already up to date.")
else:
	print("Aquiring copy of EDROP.")
	urllib.request.urlretrieve(edropurl, edroploc)


# Read input files
print("Reading input files.")
with open(droploc, "r") as f:
	droplines = f.readlines()
with open(edroploc, "r") as f:
	edroplines = f.readlines()


# Convert file to regex
print("Converting lines to regex.")

dropregex = []
for line in droplines:
	if line[:1] == ";":
		if line[:3] == "; S":
			#print("Adding copyright line...")
			print(line[2:])
			dropText += line[2:]
			dropText += "\n\n"
		else:
			print(line, " is comment...ignoring.")
	elif line[:1] == "#":
		print(line, " is comment...ignoring.")
	else:
		dropregex.append(lineToRegex(line))
edropregex = []
for line in edroplines:
	if line[:1] == ";":
		if line[:3] == "; S":
			#print("Adding copyright line...")
			print(line[2:1])
			edropText += line[2:]
			edropText += "\n\n"
		else:
			print(line, " is comment...ignoring.")
	elif line[:1] == "#":
		print(line, " is comment...ignoring.")
	else:
		edropregex.append(lineToRegex(line))



# Write output
with open(dropoloc, "w") as f:
	f.write(dropText)
	for line in dropregex:
		f.write(line)
		f.write("\n")
with open(edropoloc, "w") as f:
	f.write(edropText)
	for line in edropregex:
		f.write(line)
		f.write("\n")
