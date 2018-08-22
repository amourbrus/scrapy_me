#coding:utf-8


#from os.path import dirname, join

try:  # pip <= 9.0.1
    from pip.req import parse_requirements
except: # pip >= 10.0.1
    from pip._internal.req import parse_requirements

from setuptools import find_packages, setup


# with open(join(dirname(__file__), './VERSION.txt'), 'rb') as f:
#     version = f.read().decode('ascii').strip()

with open("VERSION.txt", "r") as f:
    version = f.read().strip()
    """
        作为一个合格的模块，应该要有版本号哦。
    """
setup(
    name='scrapy_suger',    # 模块名称
    version=version,        # 安装框架后的版本号
    description='A mini spider framework, like Scrapy',    # 描述
    packages=find_packages(exclude=[]), # 不排除任何文件
    author='amourbrus',
    author_email='your@email.com',
    license='Apache License v2', # 遵循的Linux软件发行协议
    package_data={'': ['*.*']},  # 获取任意文件名任意后缀的文件
    url='#',
    install_requires=[str(ir.req) for ir in parse_requirements("requirements.txt", session=False)],#所需的运行环境，读取requirements文件，自动安装运行环境
    zip_safe=False, # 表示在Windows中可以正常卸载
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

