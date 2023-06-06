# Mycroft Precise

*A lightweight, simple-to-use, RNN wake word listener.*

Precise is a wake word listener.  The software monitors an audio stream ( usually a microphone ) and when it recognizes a specific phrase it triggers an event.  For example, at Mycroft AI the team has trained Precise to recognize the phrase "Hey, Mycroft".  When the software recognizes this phrase it puts the rest of Mycroft's software into command mode and waits for a command from the person using the device.  Mycroft Precise is fully open source and can be trined to recognize anything from a name to a cough.

In addition to Precise there are several proprietary wake word listeners out there.  If you are looking to spot a wakeword Precise might be a great solution, but if it's too resource intensive or isn't accurate enough here are some [alternative options][comparison].

[comparison]: https://github.com/MycroftAI/mycroft-precise/wiki/Software-Comparison

## Supported Operating Systems

Precise is designed to run on Linux.  It is known to work on a variety of Linux distributions including Debian, Ubuntu and Raspbian.  It probably operates on other \*nx distributions.

## Training Models

### Communal models

Training takes lots of data. The Mycroft community is working together to jointly
build datasets at: 
https://github.com/MycroftAI/precise-community-data.   
These datasets are available for anyone to download, use and contribute to. A number 
of models trained from this data are also provided.

The official models selectable in your device settings at Home.mycroft.ai 
[can be found here](https://github.com/MycroftAI/precise-data/tree/models).  

Please come and help make things better for everyone!

### Train your own model

You can find info on training your own models [here][train-guide]. It requires
running through the [**source install instructions**][source-install] first.

[train-guide]:https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word#how-to-train-your-own-wake-word
[source-install]:https://github.com/MycroftAI/mycroft-precise#source-install

## Installation

If you just want to use Mycroft Precise for running models in your own application,
you can use the binary install option. Note: This is only updated to the latest release,
indicated by the latest commit on the master branch. If you want to train your own models
or mess with the source code, you'll need to follow the **Source Install** instructions below.

### Binary Install

First download `precise-engine.tar.gz` from the [precise-data][precise-data] GitHub
repo. This will get the latest stable version (the master branch). Note that this requires the models to be built the the same latest version in the master branch. Currently, we support both 64 bit Linux desktops (x86_64) and the Raspberry Pi (armv7l).

[precise-data]: https://github.com/mycroftai/precise-data/tree/dist

Next, extract the tar to the folder of your choice. The following commands will work for the pi:

```bash
ARCH=armv7l
wget https://github.com/MycroftAI/precise-data/raw/dist/$ARCH/precise-engine.tar.gz
tar xvf precise-engine.tar.gz
```

Now, the Precise binary exists at `precise-engine/precise-engine`.

Next, install the Python wrapper with `pip3` (or `pip` if you are on Python 2):

```bash
sudo pip3 install precise-runner
```

Finally, you can write your program, passing the location of the precise binary like shown:

```python
#!/usr/bin/env python3

from precise_runner import PreciseEngine, PreciseRunner

engine = PreciseEngine('precise-engine/precise-engine', 'my_model_file.pb')
runner = PreciseRunner(engine, on_activation=lambda: print('hello'))
runner.start()

# Sleep forever
from time import sleep
while True:
    sleep(10)
```

### Source Install

Start out by cloning the repository:

```bash
git clone https://github.com/mycroftai/mycroft-precise
cd mycroft-precise
```

If you would like your models to run on an older version of precise, like the
stable version the binary install uses, check out the master branch.

Next, install the necessary system dependencies. If you are on Ubuntu, this
will be done automatically in the next step. Otherwise, feel free to submit
a PR to support other operating systems. The dependencies are:

 - python3-pip
 - libopenblas-dev
 - python3-scipy
 - cython
 - libhdf5-dev
 - python3-h5py
 - portaudio19-dev

After this, run the setup script:

```bash
./setup.sh
```

Finally, you can write your program and run it as follows:
```bash
source .venv/bin/activate  # Change the python environment to include precise library
```
Sample Python program:
```python
#!/usr/bin/env python3

from precise_runner import PreciseEngine, PreciseRunner

engine = PreciseEngine('.venv/bin/precise-engine', 'my_model_file.pb')
runner = PreciseRunner(engine, on_activation=lambda: print('hello'))
runner.start()

# Sleep forever
from time import sleep
while True:
    sleep(10)
```

In addition to the `precise-engine` executable, doing a **Source Install** gives you
access to some other scripts. You can read more about them [here][executables].
One of these executables, `precise-listen`, can be used to test a model using
your microphone:

[executables]:https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word#how-to-train-your-own-wake-word

```bash
source .venv/bin/activate  # Gain access to precise-* executables
precise-listen my_model_file.pb
```

## How it Works

At it's core, Precise uses just a single recurrent network, specifically a GRU.
Everything else is just a matter of getting data into the right form.

![Architecture Diagram](https://images2.imgbox.com/f7/44/6N4xFU7D_o.png)

## Running on Windows (Docker Installation)

### WSL2 Setup
On Windows, PulseAusio support is provided by the [WSL2 and WSLg backends][wsl2]. With WSL support, the audio configuration is similar to ubuntu.

[wsl2]:https://github.com/microsoft/wslg

- Ensure latest version of WSL is installed `wsl --update` [requires admin privileges]
- Set default version as WSL2 `wsl --set-default-version 2` [requires admin privileges]
- Create an environemnt file wsl.env
Copy/paste the following commands into a shell terminal to create a file wsl.env in the current directory.

The file encoding must be readbale/supported by the underlying *nix shell. The PowerShell Write-Output command may produce a file with unexpected encodings/line terminations. The safest method is to create this file via text editor (e.g. notepad) and paste the two lines with export.

```bash
cat > wsl.env << EOF
export PULSE_SERVER=unix:/mnt/wslg/PulseServer
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
EOF
```
To install WSL 2 follow these commands:

1. To install wsl: `wsl --install`
2. Download this [WSL 2 kernel update][kernel-update] (required).

[kernel-update]:https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
3. Double-click the wsl_update_x64.msi file and apply the update.
4. Open Start. Search for PowerShell, right-click the top result, and select the Run as administrator option.
5. Type the following command to set Windows Subsystem for Linux 2 your default architecture for new distros that you install, and press Enter:

```bash
wsl --set-default-version 2
```

6. (Optional) Type the following command to convert the distro from WSL to WSL 2 and press Enter:

```bash
wsl --set-version Ubuntu 2
```
In the command, change “Ubuntu” for the distro’s name you want to convert. If you do not know the distro’s name, use the `wsl -l -v command`. Steps to install Ubuntu distro and make it default after installing WSL 2:

- To list all the available distros: `wsl.exe --list --online`
- To install a specific Distro like 'Ubuntu': `wsl.exe --install <Distro>`
- To set 'Ubuntu' as the default distro: `wsl --setdefault Ubuntu`

You would want to make sure that you are running the updated version so use command `wsl --update`. For more info around WSL 2 setup you can refer [here][pure-info-tech]

[pure-info-tech]:https://pureinfotech.com/install-windows-subsystem-linux-2-windows-10/

### Pulseaudio Setup

1. After having WSL2 support and setting wsl.env go ahead and install pulseaudio using (use sudo if necessary):

```bash
apt install pulseaudio
apt-get update
```
2. Start pulseaduio using the following command:

```bash
sudo pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon --system -v
```
### Running Docker

Use below commands to run the container:

```bash
wsl docker compose build
wsl docker compose run tali-mycroft-precise
source .venv/bin/activate
```
If you are running for the first time, create network using: `docker network create -d bridge secretsauce`
After the source is activated, you can start recording your voice and training your own wake-word. For further instructions follow the commands from this [wiki][wiki]. 

[wiki]:https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word

### Test the audio
- Play a known sound with `aplay /usr/share/sounds/alsa/Front_Center.wav`.
- Record a sound with `arecord -d 5 -f U8 sample.mp3` and playback with aplay command.

If the above tests are able to playback and record, then docker is able to use the speaker and microphone from the container app. Otherwise, further troubleshooting may be needed([refer this][refer]).

[refer]:https://askubuntu.com/questions/57810/how-to-fix-no-soundcards-found/815516#815516

To test speaker to check if the audio can be played from inside container try running `docker run -it -e PULSE_SERVER=host.docker.internal -v ~/.config/pulse:/home/pulseaudio/.config/pulse --entrypoint speaker-test --rm jess/pulseaudio -c 2 -l 1 -t wav`

In case of a situation where you would want to kill pulseaudio and start again you can do so by using commands like `pulseaudio --kill` or `brew services stop pulseaudio`

