# 此代码仅适用于Ubuntu，其他系统正在开发
sudo apt-get update && sudo apt-get install openjdk-17-jdk git wget mysql-server redis python3 python3-pip -y && mkdir Bot && git clone https://github.com/daizihan233/KuoHuBit && cd KuoHuBit && pip3 install pdm && pdm install && pdm run python3 main.py && echo 请使用mysql -u root -p配置数据库!
