import os

import yaml
import json

folder_path = "ALL_DOCKER_COMPOSE"


def create_camera(name, source, fight_engine, pray_engine, city, gpu_id, port):
    # Select image according to engine
    ai_image = None
    vod_image = None
    if fight_engine:
        ai_image = "sp_ai_fight"
        vod_image = "sp_ai_fight"
    elif pray_engine:
        ai_image = "sp_ai_pray"
        vod_image = "sp_ai_pray"

    try:
        # Create docker-compose.yaml for camera
        if json_to_docker_compose(ai_image, vod_image, name, source, gpu_id, port):
            # Execute docker-compose.yaml
            os.system(f"sudo docker-compose -f {folder_path}/{name}-docker-compose.yaml up -d")
            return True

        return False
    except:
        return False


def json_to_docker_compose(ai_image, vod_image, name, source, gpu_id, port):
    docker_compose_json = {
        "version": "3",
        "services": {
            f"{name}_sp_ai_fight": {
                "image": f"{ai_image}",
                "container_name": f"{name}_sp_ai_fight",
                "volumes": [
                    {
                        "type": "bind",
                        "source": "/home/valid/PycharmProjects/microservice_smart_prison/SAMPLE",
                        "target": "/app/sample"
                    },
                    {
                        "type": "bind",
                        "source": "/home/valid/PycharmProjects/microservice_smart_prison/MODEL/FIGHT",
                        "target": "/app/model/fight"
                    },
                    {
                        "type": "bind",
                        "source": "/home/valid/PycharmProjects/microservice_smart_prison/MODEL/YOLO",
                        "target": "/app/model/yolo"
                    }
                ],
                "ports": [f"{port}:80"],
                "networks": [f"{name}"],
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
                        "source": "/home/valid/PycharmProjects/microservice_smart_prison/PERSISTENT_VOD",
                        "target": "/app/vod"
                    }
                ],
                "networks": [f"{name}"],
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
            }
        },
        "networks": {
            f"{name}": {
                "ipam": {
                    "driver": "default"
                }
            }
        }
    }

    try:
        with open(f'{folder_path}/{name}-docker-compose.yaml', 'w') as yaml_file:
            yaml.dump(docker_compose_json, yaml_file, default_flow_style=False)
        return True
    except:
        return False


def delete_camera(camera_name):
    for filename in os.listdir(folder_path):
        if camera_name == filename.split("-")[0]:
            os.system(f"sudo docker-compose -f {folder_path}/{filename} down")
            os.system(f"rm {folder_path}/{filename}")
            return True
    else:
        return False


def delete_all_camera():
    try:
        for filename in os.listdir(folder_path):
            os.system(f"sudo docker-compose -f {folder_path}/{filename} down")
            os.system(f"rm {folder_path}/{filename}")
        else:
            return True
    except:
        return False


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
