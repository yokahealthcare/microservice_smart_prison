import subprocess
import json
import ipaddress


def get_docker_networks():
    # Get a list of Docker network names
    network_names = subprocess.check_output(
        ["sudo", "docker", "network", "ls", "--format", "{{.Name}}"]).decode().splitlines()

    # Initialize an empty dictionary to store network names and their subnets
    network_subnets = {}

    for name in network_names:
        # Get network details in JSON format
        network_info = subprocess.check_output(["sudo", "docker", "network", "inspect", name]).decode()
        network_data = json.loads(network_info)

        driver = network_data[0]["Driver"]
        if driver == "bridge":
            # Extract the subnet information
            subnet = network_data[0]["IPAM"]["Config"][0]["Subnet"]
            network_subnets[name] = subnet

    return network_subnets


def allocate_available_subnet(docker_subnets):
    n2d = 17
    choosen_subnet = f"172.{n2d}.0.0/16"

    for i in range(17, 256):
        if choosen_subnet not in docker_subnets.values():
            break
        n2d += 1
        choosen_subnet = f"172.{n2d}.0.0/16"
    return choosen_subnet


if __name__ == "__main__":
    existing_subnets = get_docker_networks()
    print(existing_subnets)
    print(allocate_available_subnet(existing_subnets))
