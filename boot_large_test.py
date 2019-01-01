import sys
import time
import winrm
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
from smb.SMBConnection import SMBConnection

import qemu

with qemu.QEMUMachine(
        r"C:\Program Files\qemu\qemu-system-x86_64.exe",
        test_dir="test_dir",
        monitor_address=("127.0.0.1", 8008)
) as vm:
    vm.add_args("-m", "2048")
    vm.add_args("-vnc", ":0")
    vm.add_args("-vga", "std")
    vm.add_args("-snapshot")
    vm.add_args("-device", 'usb-tablet')
    vm.add_args("-netdev", 'user,id=n1,hostfwd=tcp:127.0.0.1:5995-:5985,hostfwd=tcp:127.0.0.1:8445-:445')
    vm.add_args("-device", 'e1000,netdev=n1,mac=52:54:98:76:54:32')
    vm.add_args("-machine", 'usb=on')
    vm.add_args("-accel", 'whpx')
    vm.add_args("-vnc", ':1')
    vm.add_args("--drive", r"file=C:\Users\Nelson\Documents\packer-windows-docker\output-qemu\packer-qemu")
    vm.launch()
    res = vm.command('human-monitor-command',
                     command_line='info version')
    s = winrm.Session('localhost:5995', ('vagrant', 'vagrant'))
    # Poll the crap out of the VM until a directory is shared.

    while True:
        try:
            logging.debug("polling for systeminfo")
            s.run_cmd('systeminfo')
            break
        except:
            pass
    # Once booted, wait 10 seconds.
    time.sleep(10)
    logging.debug("sharing desktop")
    r = s.run_cmd('net', ['share', r'Desktop=C:\Users\vagrant\Desktop', '/grant:everyone,FULL'])
    logging.debug("uploading readme.md")
    c = SMBConnection('vagrant', 'vagrant', 'PYTHON', 'vagrant-10', is_direct_tcp=True)
    c.connect('127.0.0.1', port=8445)
    with open('README.md', 'rb') as f:
        c.storeFile('Desktop', 'README.md', f)
    c.close()
    logging.debug("closed smb")
    time.sleep(5*60)
    logging.debug("slept")

