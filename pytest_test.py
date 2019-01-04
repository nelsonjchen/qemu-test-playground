"""
Spin up the VM.
Poll until a connection can be made
Make a directory
Check if the directory exists


"""
import logging
import time

import pytest
import winrm
from smb.SMBConnection import SMBConnection

import qemu


@pytest.fixture()
def vm():
    logging.info("Making VM Fixture")
    with qemu.QEMUMachine(
        binary='qemu-system-x86_64',
        test_dir='./test_dir',
) as vm:
        vm.add_args("-m", "2048")
        vm.add_args("-vga", "std")
        vm.add_args("-snapshot")
        vm.add_args("-device", 'usb-tablet')
        vm.add_args("-netdev", 'user,id=n1,hostfwd=tcp:127.0.0.1:5995-:5985,hostfwd=tcp:127.0.0.1:8445-:445')
        vm.add_args("-device", 'virtio-net-pci,netdev=n1,mac=52:54:98:76:54:32')
        vm.add_args("-machine", 'usb=on')
        vm.add_args("-accel", 'kvm')
        vm.add_args("-cpu", 'host,hv_relaxed,hv_spinlocks=0x1fff,hv_time,hv_vapic,hv_vendor_id=0xDEADBEEFFF')
        vm.add_args("-vnc", ':1')
        vm.add_args("-drive", r"file=/home/nelson/code/packer-windows-docker/output-qemu/packer-qemu,format=raw,if=virtio")
        logging.info("Launching VM")
        vm.launch()
        logging.info("Running Version Info Check")
        vm.command('human-monitor-command',
                         command_line='info version')
        seconds_to_sleep = 1 * 60
        logging.info(f"Sleeping {seconds_to_sleep} seconds for initial boot")
        time.sleep(seconds_to_sleep)

        s = winrm.Session('localhost:5995', ('vagrant', 'vagrant'), read_timeout_sec=20, operation_timeout_sec=10)
        # Poll the VM
        while True:
            try:
                logging.info("Trying dir")
                s.run_cmd('dir')
                logging.info("dir success")
                break
            except:
                logging.info("dir failed")
                time.sleep(10)
                pass
        # Once command has run, wait 10 seconds.
        logging.debug("sharing desktop")
        s.run_cmd('net', ['share', r'Desktop=C:\Users\vagrant\Desktop', '/grant:everyone,FULL'])
        logging.info("Yielding VM Fixture")
        yield vm
    logging.info("Tearing down VM Fixture")

def test_install(vm):
    s = winrm.Session('localhost:5995', ('vagrant', 'vagrant'), read_timeout_sec=20, operation_timeout_sec=10)

    logging.info("uploading installer.msi")
    c = SMBConnection('vagrant', 'vagrant', 'PYTHON', 'vagrant-10', is_direct_tcp=True)
    c.connect('127.0.0.1', port=8445)
    with open('installer/installer.msi', 'rb') as f:
        c.storeFile('Desktop', 'installer.msi', f)
    c.close()
    logging.info("closed smb")
    logging.info("Sleeping 600 seconds")
    time.sleep(60*10)
    assert True
