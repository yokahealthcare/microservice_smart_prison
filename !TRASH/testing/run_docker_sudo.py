import subprocess


def run_docker_command(command):
    subprocess.run(['sudo', 'docker', command], check=True)


# Example usage
run_docker_command('ps')
