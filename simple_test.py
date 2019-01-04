import qemu

with qemu.QEMUMachine(binary='qemu-system-x86_64'
) as vm:
    vm.launch()
    res = vm.command('human-monitor-command',
                     command_line='info version')
    print(res)
