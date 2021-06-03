# syntax=docker/dockerfile:1
FROM ubuntu:20.04

# For display forwarding purposes
ENV LIBGL_ALWAYS_INDIRECT=1

# We need to specify TZ so tkinter doesn't ask for it later
ENV TZ=America/Los_Angeles
ENV DEBIAN_FRONTEND="noninteractive"

COPY . /root/thesis/
RUN apt-get update && apt-get install -y \
    tzdata \
    wget \
    libgfortran4 \
    libgl1-mesa-glx \
    libglu1-mesa \ 
    python3 \
    python3-pip \
    python3-pyaudio \
    python3-tk \
    libxi6 \
    libxmu6 \
    tetgen \
 && cd  /tmp \
 && wget http://www.dhondt.de/cgx_2.17.1.bz2 \ 
 && wget http://www.dhondt.de/ccx_2.17.tar.bz2 \
 && tar -xf ccx_2.17.tar.bz2  \ 
 && bzip2 -d cgx_2.17.1.bz2 \
 && chmod 777 cgx_2.17.1 \
 && mv cgx_2.17.1 /usr/bin/cgx \ 
 && mv CalculiX/ccx_2.17/src/ccx_2.17 /usr/bin/ccx \
 && rm -r * \
 && cd ~/thesis \
 && pip install -r requirements.txt \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get remove -y wget python3-pip \
 && apt-get -y autoremove 
CMD /bin/bash