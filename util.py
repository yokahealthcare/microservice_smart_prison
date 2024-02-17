import os

import yaml
import subprocess
import json

folder_path = "ALL_DOCKER_COMPOSE"


def get_docker_subnets():
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


def create_camera(name, source, fight_engine, pray_engine, city, gpu_id, port):
    # Select image according to engine
    ai_image = None
    vod_image = None
    if fight_engine:
        ai_image = "sp_ai_fight"
        vod_image = "sp_ai_fight"  # later change
    elif pray_engine:
        ai_image = "sp_ai_pray"
        vod_image = "sp_ai_pray"  # later change

    try:
        # Create docker-compose.yaml for camera
        if json_to_docker_compose(ai_image, vod_image, name, source, gpu_id, port):
            # Execute docker-compose.yaml
            os.system(f"sudo docker compose -f {folder_path}/{name}-docker-compose.yaml up -d")
            return True, "Successfully created camera and running"

        return False, "Failed to create docker compose"
    except:
        return False, "Caught exception"


def json_to_docker_compose(ai_image, vod_image, name, source, gpu_id, port):
    # Select subnet
    subnet = allocate_available_subnet(get_docker_subnets())

    docker_compose_json = {
        "version": "3",
        "services": {
            f"{name}_sp_ai_fight": {
                "image": f"{ai_image}",
                "container_name": f"{name}_sp_ai_fight",
                "volumes": [
                    {
                        "type": "bind",
                        "source": "/home/erwinyonata/PycharmProjects/microservice_smart_prison/SAMPLE",
                        "target": "/app/sample"
                    },
                    {
                        "type": "bind",
                        "source": "/home/erwinyonata/PycharmProjects/microservice_smart_prison/MODEL/FIGHT",
                        "target": "/app/model/fight"
                    },
                    {
                        "type": "bind",
                        "source": "/home/erwinyonata/PycharmProjects/microservice_smart_prison/MODEL/YOLO",
                        "target": "/app/model/yolo"
                    }
                ],
                "ports": [f"{port}:80"],
                "networks": {
                    f"{name}": {
                        "ipv4_address": f"{'.'.join(subnet.split('.')[:-1])}.2"
                    }
                },
                "deploy": {
                    "resources": {
                        "reservations": {
                            "devices": [
                                {
                                    "driver": "nvidia",
                                    "device_ids": [f"{gpu_id}"],
                                    "capabilities": ["gpu"]
                                }
                            ]
                        }
                    }
                }
            },
            f"{name}_sp_vod_fight": {
                "image": f"{vod_image}",
                "container_name": f"{name}_sp_vod_fight",
                "volumes": [
                    {
                        "type": "bind",
                        "source": "/home/erwinyonata/PycharmProjects/microservice_smart_prison/PERSISTENT_VOD",
                        "target": "/app/vod"
                    }
                ],
                "networks": {
                    f"{name}": {
                        "ipv4_address": f"{'.'.join(subnet.split('.')[:-1])}.3"
                    }
                }
            }
        },
        "volumes": {
            f"{name}_volume": {}
        },
        "networks": {
            f"{name}": {
                "ipam": {
                    "driver": "default",
                    "config": [
                        {
                            "subnet": subnet
                        }
                    ]
                }
            }
        }
    }

    try:
        with open(f'{folder_path}/{name}-docker-compose.yaml', 'w') as yaml_file:
            yaml.dump(docker_compose_json, yaml_file, default_flow_style=False)
        return True, "Success creating docker-compose.yaml"
    except:
        return False, "Failed to create docker-compose.yaml"


def delete_camera(camera_name):
    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml") and camera_name == filename.split("-")[0]:
            os.system(f"sudo docker compose -f {folder_path}/{filename} down")
            os.system(f"rm {folder_path}/{filename}")
            return True, "Success deleting camera"
    else:
        return False, "Camera does not exist"


def delete_all_camera():
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".yaml"):
                os.system(f"sudo docker compose -f {folder_path}/{filename} down")
                os.system(f"rm {folder_path}/{filename}")
        return True, "All camera configurations deleted"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


def extract_yaml_to_json(filename):
    # Read YAML from file
    with open(f"{filename}", 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

        # Convert YAML to JSON
        json_data = json.dumps(yaml_data, indent=2)

        return json_data


def get_info_camera(camera_name):
    for filename in os.listdir(folder_path):
        if camera_name == filename.split("-")[0]:
            json_camera_data = extract_yaml_to_json(f"{folder_path}/{filename}")

            return True, json_camera_data
    else:
        return False, None


def get_info_all_camera():
    list_camera_info = []
    try:
        for filename in os.listdir(folder_path):
            json_data_camera = extract_yaml_to_json(f"{folder_path}/{filename}")
            list_camera_info.append(json_data_camera)
        else:
            return True, list_camera_info
    except:
        return False, None


if __name__ == '__main__':
    name = "camera4"
    source = "a"
    fight_engine = True
    pray_engine = False
    city = "San Francisco"
    gpu_id = 0
    port = 5558

    response, message = create_camera(name, source, fight_engine, pray_engine, city, gpu_id, port)
    print(response)
    print(message)
