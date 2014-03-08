"""
GCC output parser
Copyright (c) 2013 Kim Blomqvist, kblomqvist.github.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os, subprocess
import string, re

def predefs(location = None, flags = [], gcc = "gcc"):
	""" Returns GCC predefined macros """
	gcc = os.path.join(location, gcc)
	flags.extend(["-dM", "-E", "-", "<", os.devnull])
	p = subprocess.Popen(
		" ".join([gcc] + flags),
		shell = True,
		# cwd = location, This ain't working on OSX
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE
	)
	out, err = p.communicate()

	if err:
		raise Exception("In gcc.predefs(): " + err.decode())

	dump = []
	for line in out.decode().split(os.linesep):
		identifier = None
		replacement = None
		try:
			m = re.search(r"#define ([\w()]+) (.+)", line)
			identifier = m.group(1)
			replacement = m.group(2)
		except:
			try:
				m = re.search(r"#define (\w+)", line)
				identifier = m.group(1)
			except:
				pass
		if identifier:
			dump.append((identifier, replacement))

	if not dump:
		return None

	return dump

def def2opt(define, undef = False):
	""" Returns C preprocessor define converted to GCC option flag """
	if isinstance(define, tuple):
		define = [define]
	if not isinstance(define, list):
		return None

	dump = []
	for d in define:
		if not isinstance(d, tuple):
			continue
		if undef:
			dump.append("-U%s" % re.sub(r"\((.+)\)$", '', d[0]))
		if d[1]:
			dump.append("-D%s=%s" % d)
		else:
			dump.append("-D%s" % d[0])

	if not dump:
		return None

	return dump

def version(location = None, gcc = "gcc"):
	""" Returns GCC version """
	for p in predefs(location=location, gcc=gcc):
		if p[0] == "__VERSION__":
			return p[1][1:-1]
	return ""