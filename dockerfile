FROM python:3.7.12

# Install Packages via apt and pip
RUN apt-get update
# sudo apt-get install -y python3-pip curl libopenblas-dev python3-scipy cython libhdf5-dev python3-h5py portaudio19-dev swig libpulse-dev libatlas-base-dev

RUN apt-get install git libopenblas-dev python3-scipy libhdf5-dev python3-h5py portaudio19-dev ffmpeg -y --force-yes
#RUN apt-get install git-buildpackage -y
#RUN apt-get install libttspico-utils libttspico0
RUN pip install --upgrade pip
RUN pip install Cython

# Because of course, you can't just apt-get install libttspico0 libttspico-utils
RUN apt-get install libpopt-dev -y
RUN mkdir /picotts
RUN git clone https://github.com/naggety/picotts.git
WORKDIR /picotts/pico
RUN ./autogen.sh
RUN ./configure
RUN make install

# Clone Precise Wakeword Model Maker from Secret Sauce AI git repo
RUN mkdir /app 
WORKDIR /app
COPY . tali-mycroft-precise/ 
# ENV VENV=/app/tali-mycroft-precise/.venv
RUN python3 -m venv .venv
RUN /app/.venv/bin/python3 -m pip install --upgrade pip
# RUN .venv/bin/pip install -e wakeword-data-collector

# if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV" --without-pip; fi
# source "$VENV/bin/activate"
# if [ ! -x "$VENV/bin/pip" ]; then curl https://bootstrap.pypa.io/get-pip.py | python; fi

# remove stuff that would break the setup from setup.sh (the default installation script from Precise uses sudo, while the container is already run in root, also we installed Cython above)
RUN sed -i -e 's/sudo //g' /app/tali-mycroft-precise/setup.sh
RUN sed -i -e 's/cython //g' /app/tali-mycroft-precise/setup.sh
CMD bash
# run modified setup.sh and install other requirements
# RUN chmod u+x setup.sh
# RUN ./setup.sh
