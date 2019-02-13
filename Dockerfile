# ==============================
# Docker Build File
# 
#   This will generate an image that can run the optimization code. It is
#   built ontop of an Ubuntu 18.04 image. Multiple dependancies are then 
#   installed, which includes python3, calculix (cgx and ccx), netgen 
#   (from source via sourceforge).
#
#   Please note, Vim is included, but is only intended for viewing output
#   files when debugging in interactive mode. It is not intended to be
#   used in production. For regular behaviour, it may be left commented.
#
# ==============================


# Start from an Ubuntu image
FROM ubuntu:18.04

# Set no user interaction
ENV DEBIAN_FRONTEND noninteractive

# Install "essentials" (NOTE: there's a lot installed that could and should be trimmed)
RUN echo "locales locales/locales_to_be_generated multiselect en_US.UTF-8 UTF-8" | debconf-set-selections \
	&& echo "locales locales/default_environment_locale select en_US.UTF-8" | debconf-set-selections \
	&& apt-get update \
	&& apt-get --yes --no-install-recommends install \
		locales tzdata ca-certificates sudo \
		bash-completion curl tree \
	&& rm -rf /var/lib/apt/lists/*
ENV LANG en_US.UTF-8

# Install build dependancies
RUN apt-get update \
	&& apt-get install --yes software-properties-common
RUN apt-add-repository universe \
	&& apt-get update --yes

# Install python
RUN apt-get update \
	&& apt-get --yes --no-install-recommends install \
		python3 python3-dev \
		python3-pip python3-venv python3-wheel python3-setuptools \
		build-essential \
		git \
	&& rm -rf /var/lib/apt/lists/*

# Install netgen-mesher from source (via sourceforge)
ENV ngp "/usr/local/netgen_install"
ENV nv "5.3"
ENV nver "${nv}.1"
RUN apt-add-repository universe \
	&& apt-get update --yes \
	&& apt-get install --yes build-essential gfortran gcc g++ cmake \
		cvs mercurial subversion tk-dev tcl-dev automake autoconf perl \
		liblapack-dev libblas-dev libeigen3-dev libopenblas-dev \
		openmpi-bin libopenmpi-dev libxmu-dev libglu1-mesa-dev liblapacke-dev \
	&& rm -rf /var/lib/apt/lists/* \
	&& mkdir "${ngp}" \
	&& curl -L "https://downloads.sourceforge.net/project/netgen-mesher/netgen-mesher/${nv}/netgen-${nver}.tar.gz" > "netgen-${nver}.tar.gz" \
	&& tar -xzvf "netgen-${nver}.tar.gz" \
	&& cp -r "netgen-${nver}" "${ngp}" \
	&& cd "${ngp}/netgen-${nver}" \
	&& ./configure --prefix="${ngp}" --disable-gui \
	&& make \
	&& make install
RUN  cd "${ngp}/bin" \
	&& cp * "/usr/local/bin/" \
	&& rm "/netgen-${nver}.tar.gz"

# Install cgx and ccx
RUN apt-add-repository universe \
	&& apt-get update --yes \
	&& apt-get install --yes calculix-cgx calculix-ccx \
	&& rm -rf /var/lib/apt/lists/*

# Install Vim (please see note above)
# RUN apt-add-repository universe \
# 	&& apt-get update --yes \
# 	&& apt-get install --yes vim \
# 	&& rm -rf /var/lib/apt/lists/*

# Get the package
RUN git clone https://github.com/arinconl/thesis.git /app/thesis

# Install python dependencies (NOTE: should be migrated to pipenv)
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Command to run app
CMD ["python3", "/app/thesis/optimize.py"]
