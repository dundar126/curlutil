# Simple cURL utility
# By Stephen Campbell
# Requires Python 3 and PycURL

import sys

# Test for Python 3 and quit at this stage if not found.
if not sys.version_info[0] > 2:
	print('Python 3 required!')
	quit()

import time, os, pycurl
from urllib.parse import urlencode

args = sys.argv[1:] # Strip filename from arguments list

# Class used to store downloaded HTML
class Loader:
	def __init__(self):
		self.content = ''.encode('ascii')

	# Used to append lines to the Loader's content
	def append_lines(self, lines):
		self.content = self.content + lines

def show_usage():
	print('Usage:')
	print('-f <url> <form data file>')
	print('\tFill out and submit a form at specified URL. Form data should be')
	print('\tstored in a local text file, in the same directory as this script')
	print('\tand use the following format: \'<field>:<value>\' with each field')
	print('\ton its own line.')
	print('-l <url>')
	print('\tDownload HTML of specified URL.')
	print('-m <url> <runs>')
	print('\tRun download multiple times.')
	print('-r')
	print('\tFollow redirects.')
	print('-c')
	print('\tDownload cookies.')
	print('-o')
	print('\tPrint downloaded HTML.')

# Method to download a specified URL
def download(url, output = False, redirect = False, cookies = False, repetitions = 1, ssl = False):
	try:
		if repetitions < 1:
			print('File download must complete at least 1 repetition.')
			quit()

		if not output:
			print('Iteration,Timing (ms)'.format(repetitions, url))

		for run in range(0, repetitions):
			l = Loader() # Loader may not seem necessary here, but prevents pycurl spamming prints
			c = pycurl.Curl()
			c.setopt(c.URL, url) # Access URL specified by user
			c.setopt(c.WRITEFUNCTION, l.append_lines) # Write to Loader

			if not ssl:
				# Skip SSL
				c.setopt(pycurl.SSL_VERIFYPEER, 0)
				c.setopt(pycurl.SSL_VERIFYHOST, 0)

			if redirect:
				c.setopt(c.FOLLOWLOCATION, True) # Follow redirects

			if cookies:
				# Save cookies to local file
				c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
				c.setopt(pycurl.COOKIEJAR, 'cookies.txt')

			t1 = time.clock() # Take time before
			c.perform() # Download page
			t2 = time.clock() # Take time after
			c.close()

			if output:
				print(l.content)

			# Convert to milliseconds
			t1 = t1 * 1000
			t2 = t2 * 1000

			# Print time taken
			ttotal = round(t2 - t1, 4) # Calculate total time and round off
			if output:
				print('Download completed in {}ms.'.format(ttotal))
			else:
				print('{},{}'.format(str(run + 1).zfill(len(str(repetitions))), ttotal))
	except:
		print('Valid URL not provided.')

def fill_form(url, form_file, cookies = False, ssl = False):
	if os.path.exists(form_file):
		# Open, read and parse file
		f = open(form_file, 'r') # Open specified file for reading
		form_data = {}
		for line in f:
			line_list = line.split(':') # Split line using : delimiter
			form_data[line_list[0]] = line_list[1] # Add data to dictionary
		f.close()
	else:
		print('Valid filename not provided.')
		quit()

	try:
		# Setup
		c = pycurl.Curl()
		c.setopt(c.URL, url) # Access URL specified by user
		postfields = urlencode(form_data)
		c.setopt(c.POSTFIELDS, postfields)

		if not ssl:
			# Skip SSL
			c.setopt(pycurl.SSL_VERIFYPEER, 0)
			c.setopt(pycurl.SSL_VERIFYHOST, 0)

		if cookies:
			# Save cookies to local file
			c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
			c.setopt(pycurl.COOKIEJAR, 'cookies.txt')

		# Perform form submission
		t1 = time.clock() # Take time before
		c.perform() # Fill form
		t2 = time.clock() # Take time after
		c.close()

		# Convert to milliseconds
		t1 = t1 * 1000
		t2 = t2 * 1000

		ttotal = round(t2 - t1, 4) # Calculate total time and round off
		print('Form submitted in {}ms.'.format(ttotal))
	except:
		print('Valid URL not provided.')

# Command line interface
if len(args) == 0: # If no arguments provided, show list of arguments
	show_usage()

else: # Main program logic
	mode = ''
	cookies = False
	redirects = False
	output = False

	# for index, arg in enumerate(args): # Iterate through arguments
	if args[0][:1] == '-':
		for flag in args[0][1:]:
			if flag == 'l':
				mode = 'download'
			elif flag == 'm':
				mode = 'multi'
			elif flag == 'f':
				mode = 'form'
			elif flag == 'c':
				cookies = True
			elif flag == 'r':
				redirects = True
			elif flag == 'o':
				output = True
			else:
				mode = ''
				break

	if mode == 'download':
		download(args[1], output, redirects, cookies)
	elif mode == 'multi':
		download(args[1], output, redirects, cookies, int(args[2]))
	elif mode == 'form':
		fill_form(args[1], args[2])
	else:
		show_usage()
