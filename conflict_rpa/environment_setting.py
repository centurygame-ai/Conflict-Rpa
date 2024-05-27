import os
import platform
import subprocess
import sys
from shutil import copyfile

from setuptools import setup, find_packages, Command
from setuptools.command.develop import develop
from setuptools.command.install import install


def cmd_install():
    home_dir = os.path.expanduser("~")
    profile_path = os.path.join(home_dir, 'Documents', 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1')
    script_source = os.path.join(home_dir, 'record_last_command.psm1')
    cmd_auto_run_path = os.path.join(home_dir, 'record_last_command.cmd')

    script = '''function crpa
{
    param (
        [string[]]$Args
    )

    # Get the last command from the history
    $lastCommand = (Get-History | Select-Object -Last 1).CommandLine
    if ($lastCommand) {
        # Call rpa_main with last command and additional arguments
        conflict_rpa $lastCommand $Args
    } else {
        conflict_rpa $Args
    }

}'''

    # Copy the module to the home directory
    with open(script_source, 'w') as f:
        f.write(script)

    # Ensure the profile path exists
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)

    # Update the profile to import the module
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as file:
            content = file.read()
        import_module_cmd = 'Import-Module "$HOME\\record_last_command.psm1"'
        if import_module_cmd not in content:
            with open(profile_path, "a") as profile_file:
                profile_file.write('\n' + import_module_cmd + '\n')
                print(f"Added module import command to PowerShell profile")
        else:
            print(f"Module import command already exists in PowerShell profile")
    else:
        with open(profile_path, "w") as profile_file:
            profile_file.write(f'import-module "$HOME\\record_last_command.psm1"\n')
            print(f"Created PowerShell profile and added module import command")

    print('done')

    # CMD script
    cmd_script = '''
    @echo off
    :: This command captures the last command in the history and runs the user-defined action
    doskey /history > "%TEMP%\\cmd_history.txt"
    for /f "delims=" %%a in (%TEMP%\\cmd_history.txt) do set "last_cmd=%%a"
    set last_cmd=%last_cmd:~0,-1%
    set new_cmd=conflict_rpa %last_cmd%
    echo Executing: %new_cmd%
    :: Call your function here
    :: %new_cmd%
    '''

    # Write the CMD autorun script
    with open(cmd_auto_run_path, 'w') as f:
        f.write(cmd_script)

    # Set AutoRun environment variable for CMD
    os.system(
        f'reg add "HKCU\\Software\\Microsoft\\Command Processor" /v AutoRun /t REG_SZ /d "{cmd_auto_run_path}" /f')
    print(f"Added CMD AutoRun command to registry")

    print('done')


def add_bashrc_content():
    shell = os.getenv('SHELL')
    if shell:
        shellrc_content = """
crpa() {
    local last_command=$(fc -ln -1)
    conflict_rpa "${last_command}"  "$@"
}"""
        home_dir = os.path.expanduser("~")
        shell_files = ['.bashrc', '.zshrc']

        if 'bash' in shell:
            shellrc_path = os.path.join(home_dir, '.bashrc')
            shell_file = '.bashrc'
        elif 'zsh' in shell:
            shellrc_path = os.path.join(home_dir, '.zshrc')
            shell_file = '.zshrc'
        else:
            return
        if os.path.exists(shellrc_path):
            with open(shellrc_path, 'r') as file:
                content = file.read()
            if "crpa()" not in content:
                with open(shellrc_path, "a") as shellrc_file:
                    shellrc_file.write(shellrc_content)
                    print(f"Added custom command to {shell_file}")
                # Source the updated shell configuration
                source_command = f"source {shellrc_path}"
                subprocess.run(source_command, shell=True)
                print(f"Sourced {shell_file} to apply changes")
            else:
                print(f"Custom command already exists in {shell_file}")
        else:
            print(f"{shell_file} not found")
    else:
        return


def environment_setting():
    shell = os.getenv('SHELL')
    if shell:
        add_bashrc_content()
    if platform.system() == 'Windows':
        comspec = os.getenv('ComSpec')
        if comspec:
            if 'cmd.exe' in comspec.lower():
                cmd_install()
