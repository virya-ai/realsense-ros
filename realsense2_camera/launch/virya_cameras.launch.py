"""Start one RealSense camera per camera config installed for this build's vehicle.

Sensors_ws builds for one vehicle (src/build.sh <vehicle>). Each RealSense sensor in
that vehicle's sensors.yaml picks a config file (e.g. config/depth_cam_0_AMR50_Canopy.yaml);
sensor_configs installs it as share/sensor_configs/vehicle/realsense2_camera/<sensor name>.yaml.
This includes rs_launch.py once per installed file, with camera_name = the sensor name
and config_file = that file, so its settings apply on top of rs_launch.py's defaults.
"""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def vehicle_camera_configs():
    try:
        share = Path(get_package_share_directory('sensor_configs'))
    except PackageNotFoundError:
        raise RuntimeError('sensor_configs is not installed: build Sensors_ws with '
                           'src/build.sh <vehicle>')
    configs = sorted((share / 'vehicle' / 'realsense2_camera').glob('*.yaml'))
    if not configs:
        raise RuntimeError(
            f'no RealSense config installed for vehicle {(share / "vehicle_name").read_text().strip()} '
            f'({share / "vehicle" / "realsense2_camera"}): check its sensors.yaml')
    return configs


def generate_launch_description():
    rs_launch = str(Path(get_package_share_directory('realsense2_camera')) / 'launch' / 'rs_launch.py')
    return LaunchDescription([
        # GroupAction scopes each include's arguments to that camera.
        GroupAction([IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rs_launch),
            launch_arguments={'camera_name': config.stem, 'config_file': str(config)}.items())])
        for config in vehicle_camera_configs()
    ])
