import qemu

with qemu.QEMUMachine(
        "C:\Program Files\qemu\qemu-system-x86_64.exe",
        test_dir="test_dir",
        monitor_address=("127.0.0.1", 8008)
) as vm:
    vm.launch()
    res = vm.command('human-monitor-command',
                          command_line='info version')
    print(res)
