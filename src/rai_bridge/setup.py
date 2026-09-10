"""Install the rai_bridge package and its documentation."""

from glob import glob
from os.path import join

from setuptools import find_packages, setup

package_name = 'rai_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            [join('resource', package_name)],
        ),
        (join('share', package_name), ['package.xml', 'README.md', 'README.en.md']),
        (
            join('share', package_name, 'config'),
            glob(join('config', '*.yaml')),
        ),
        (
            join('share', package_name, 'launch'),
            glob(join('launch', '*.launch.py')),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Sample Maintainers',
    maintainer_email='dev@example.com',
    description=(
        "Bridge free-form natural-language text commands to ROS 2 Twist commands, "
        "in the spirit of RobotecAI's RAI agent framework."
    ),
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'nl_command_node = rai_bridge.nl_command_node:main',
            'nl_demo_publisher = rai_bridge.nl_demo_publisher:main',
        ],
    },
)
