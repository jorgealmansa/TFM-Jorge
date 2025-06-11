FROM ubuntu:20.04

# Instalar dependencias básicas
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends --fix-missing install \
    sudo \
    curl \
    git \
    ca-certificates \
    openssh-server

# Instalar libglib
COPY libglib2.0-0_2.64.6-1~ubuntu20.04.7_amd64.deb /tmp/
RUN dpkg -i /tmp/libglib2.0-0_2.64.6-1~ubuntu20.04.7_amd64.deb

# Instalar OpenJDK 11
RUN DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends --fix-missing install \
    openjdk-11-jdk

# Crear usuario p4
RUN sudo useradd -m -d /home/p4 -s /bin/bash p4 && \
    echo "p4:p4" | chpasswd && \
    echo "p4 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

USER p4
WORKDIR /home/p4

# Instalar herramientas de red
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends --fix-missing install \
    tmux \
    iperf \
    iperf3 \
    net-tools \
    iputils-ping \
    iputils-tracepath \
    mtr \
    htop \
    tcpdump \
    tshark \
    wget \
    unzip \
    vim \
    joe \
    nano \
    patch \
    lsb-release

# Instalar Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - && \
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends --fix-missing install nodejs

# Clonar repositorios
RUN git clone https://github.com/jafingerhut/p4-guide && \
    p4-guide/bin/install-p4dev-v5.sh

# Instalar dependencias de Python
RUN sudo pip3 install --upgrade pip && \
    sudo pip3 install pyyaml && \
    sudo pip3 install influxdb && \
    sudo pip3 install confluent_kafka

# Instalar kopf, protobuf y demás librerías necesarias
RUN sudo pip3 install kopf && \
    sudo pip3 uninstall -y protobuf && \
    sudo pip3 install --no-cache-dir protobuf==3.19.1 && \
    sudo pip3 install --no-cache-dir grpcio==1.46.3 grpcio-tools==1.46.3 googleapis-common-protos==1.56.4 && \
    sudo pip3 install --no-cache-dir google-auth==2.20.0 kubernetes==30.1.0

# Clonar repositorio de P4
RUN git clone https://github.com/p4lang/tutorials

# Limpiar caché
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get -y clean

# Instalar InfluxDB
RUN wget https://dl.influxdata.com/influxdb/releases/influxdb_1.8.10_amd64.deb && \
    sudo dpkg -i influxdb_1.8.10_amd64.deb

# Configurar directorio de trabajo
RUN mkdir pot
WORKDIR /home/p4/pot

CMD ["/bin/bash"]
