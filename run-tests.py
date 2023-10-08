
import glob
import os
import subprocess
import sys
import tempfile

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

skip = [
  '_Pragma-dependency.c',
  '_Pragma-dependency2.c',
  '_Pragma-location.c',
  '_Pragma-physloc.c',
  'assembler-with-cpp.c',
  'builtin_line.c',
  'c99-6_10_3_4_p5.c',
  'c99-6_10_3_4_p6.c',
  'clang_headers.c',
  'comment_save.c',
  'expr_usual_conversions.c',
  'has_attribute.c',
  'has_attribute.cpp',
  'hash_line.c',
  'hash_space.c',
  'header_lookup1.c',

  'macro_backslash.c', # crashes

  'macro_expand.c',
  'macro_fn_comma_swallow.c',
  'macro_fn_comma_swallow2.c',
  'macro_fn_disable_expand.c',
  'macro_misc.c',
  'macro_not_define.c',
  'macro_paste_commaext.c',
  'macro_paste_hard.c',
  'macro_redefined.c',
  'macro_rescan_varargs.c',
  'microsoft-ext.c',
  'optimize.c',
  'pragma-pushpop-macro.c',
  'stdint.c',
  'stringize_misc.c',
  'warn-disabled-macro-expansion.c',
  'warn-macro-unused.c',
]

numberOfSkipped = 0

for cmd in commands:
  fname = cmd[cmd.rfind('\\')+1:]
  print(fname)
  if fname in skip:
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
    print('FAILED ' + cmd)
    if simplecpp_ec:
      print('simplecpp failed - ' + simplecpp_err)
    print(f'opening diff in beyond comapre (clang on left, simplecpp on right)')
    bcomapre = '"C:\\Program Files\\Beyond Compare 4\\BCompare.exe"'
    
    temp1 = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    temp1.write(simplecpp_output.encode())
    name1 = temp1.name
    temp1.close()

    temp2 = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
    temp2.write(clang_output.encode())
    name2 = temp2.name
    temp2.close()

    print(bcomapre + " " + "\"" + name2 + "\"" + " " + "\"" + name1 + "\"")
    subprocess.run(bcomapre + " " + "\"" + name2 + "\"" + " " + "\"" +name1+ "\"")
    
    sys.exit(1)

print('Number of tests: ' + str(len(commands)))
print('Number of skipped: ' + str(numberOfSkipped))

sys.exit(0)
