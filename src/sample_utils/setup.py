"""Install the sample_utils package and its documentation."""

from setuptools import find_packages, setup

setup(
    name='sample_utils', version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/sample_utils']),
        ('share/sample_utils', ['package.xml', 'README.md', 'README.en.md']),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='ROS 2 Sample Maintainers', maintainer_email='dev@example.com',
    description='Shared simulation math and noise utilities.', license='MIT',
    tests_require=['pytest'],
)
