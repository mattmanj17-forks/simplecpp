
import glob
import os
import subprocess
import sys

def cleanup(out):
  ret = ''
  for s in out.decode('utf-8').split('\n'):
    if len(s) > 1 and s[0] == '#':
      continue
    s = "".join(s.split())
    ret = ret + s
  return ret

commands = []

for f in sorted(glob.glob(os.path.expanduser('testsuite/clang-preprocessor-tests/*.c*'))):
  for line in open(f, 'rt', encoding="utf-8"):
    if line.startswith('// RUN: %clang_cc1 '):
      cmd = ''
      for arg in line[19:].split():
        if arg == '-E' or (len(arg) >= 3 and arg[:2] == '-D'):
          cmd = cmd + ' ' + arg
      if len(cmd) > 1:
        newcmd = cmd[1:] + ' ' + f
        if not newcmd in commands:
          commands.append(cmd[1:] + ' ' + f)

skip = []
todo = []

numberOfSkipped = 0
numberOfFailed = 0
numberOfFixed = 0

usedTodos = []

for cmd in commands:
  if cmd[cmd.rfind('/')+1:] in skip:
    numberOfSkipped = numberOfSkipped + 1
    continue

  clang_cmd = ["C:\\Users\\drape\\OneDrive\\Desktop\\build\\Release\\bin\\clang.exe"]
  clang_cmd.extend(cmd.split(' '))
  p = subprocess.Popen(clang_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  comm = p.communicate()
  clang_output = cleanup(comm[0])

  simplecpp_cmd = ['..\\simplecpp.build\\\Debug\\\simplecpp.exe']
  # -E is not supported and we bail out on unknown options
  simplecpp_cmd.extend(cmd.replace('-E ', '', 1).split(' '))
  p = subprocess.Popen(simplecpp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  comm = p.communicate()
  simplecpp_ec = p.returncode
  simplecpp_output = cleanup(comm[0])
  simplecpp_err = comm[0].decode('utf-8').strip()

  if simplecpp_output != clang_output:
    filename = cmd[cmd.rfind('/')+1:]
    if filename in todo:
      print('TODO ' + cmd)
      usedTodos.append(filename)
    else:
      print('FAILED ' + cmd)
      if simplecpp_ec:
          print('simplecpp failed - ' + simplecpp_err)
      numberOfFailed = numberOfFailed + 1
    

for filename in todo:
    if not filename in usedTodos:
        print('FIXED ' + filename)
        numberOfFixed = numberOfFixed + 1

print('Number of tests: ' + str(len(commands)))
print('Number of skipped: ' + str(numberOfSkipped))
print('Number of todos (fixed): ' + str(len(usedTodos)) + ' (' + str(numberOfFixed) + ')')
print('Number of failed: ' + str(numberOfFailed))

if numberOfFailed or numberOfFixed:
    sys.exit(1)

sys.exit(0)
