# FROM python:3.7.12
# debian is not compatible with mycroft and TF, ubuntu is compatible
FROM mambaorg/micromamba:1.4.1-jammy

ARG REPO_FOLDER=tali-mycroft-precise
USER root
# Install Packages via apt and pip
RUN apt-get update && \
    apt-get install -y --force-yes git alsa-utils pulseaudio portaudio19-dev \
            libopenblas-dev python3-scipy libhdf5-dev python3-h5py portaudio19-dev ffmpeg
            
RUN micromamba install --yes --name base --channel conda-forge \
      python=3.7 && \
    micromamba clean --all --yes
# (otherwise python will not be found)
ARG MAMBA_DOCKERFILE_ACTIVATE=1  

RUN pip install --upgrade pip
RUN pip install Cython

# Clone Precise Wakeword Model Maker from Secret Sauce AI git repo
RUN mkdir /app 
WORKDIR /app
RUN touch version-`date +%Y-%m-%d:%H:%M.%p`.dev
# COPY . tali-mycroft-precise/ 
COPY . ${REPO_FOLDER}/ 
# RUN git clone https://github.com/sfu-bigdata/tali-mycroft-precise.git

# remove stuff that would break the setup from setup.sh (the default installation script from Precise uses sudo, while the container is already run in root, also we installed Cython above)
RUN sed -i -e 's/sudo //g' ${REPO_FOLDER}/setup.sh
RUN sed -i -e 's/cython //g' ${REPO_FOLDER}/setup.sh
# Remove extra '\r' in case of Windows file endings
RUN sed -i $'s/\r$//' ${REPO_FOLDER}/setup.sh 

# run modified setup.sh and install other requirements
WORKDIR /app
RUN chmod u+x ${REPO_FOLDER}/setup.sh
RUN ${REPO_FOLDER}/setup.sh

WORKDIR /app/${REPO_FOLDER}
# RUN pip install -e runner/
# RUN pip install -e .
# RUN pip install pocketsphinx 

RUN apt-get clean

CMD bash