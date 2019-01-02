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

import qemu


@pytest.fixture()
def vm():
    logging.info("Making VM Fixture")
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
                logging.exception("dir failed")
                time.sleep(10)
                pass
        # Once command has run, wait 10 seconds.
        logging.info("running dir again")
        s.run_cmd('dir')
        logging.info("ran dir again")
        logging.info("Yielding VM Fixture")
        yield vm
    logging.info("Tearing down VM Fixture")

def test_install(vm):
    assert True
