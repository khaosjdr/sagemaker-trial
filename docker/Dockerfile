FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

RUN apt-get update
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone
RUN apt-get install -yq --no-install-recommends python3-pip \
    python3-dev \
    python3-opencv \
    vim \
    wget \
    git \
    tzdata && apt-get upgrade -y && apt-get clean

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
RUN pip install --no-cache-dir pytorch-lightning matplotlib
