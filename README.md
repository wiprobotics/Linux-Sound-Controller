# Linux-Sound-Controller

This is a simple sound controller object for python running on linux. It has several methods to control the sound on your linux machine. It uses the `subprocess` module to run  commands in the terminal.

## Installation

Requirements:

- `python3` (can be installed with `sudo apt-get install python3`)
- `pip3` (should be installed by default)
- `subprocess` module (should be installed by default)
- `time` module (should be installed by default)
- `portaudio19-dev` (sudo apt-get install portaudio19-dev)
- `pyaudio` (pip3 install pyaudio)
- `sox` (sudo apt-get install sox)
- `ffmpeg` (sudo apt-get install ffmpeg)

To install the sound controller, simply clone the repository and type: `from LinuxSoundController import SoundController` in your python file.

## Usage

The sound controller has several methods to control the sound on your linux machine. Here are the methods:

    - GetSinks: Gets all sinks and monitors
    - CheckSinkState: Checks if sink is running or not
    - PlaySound: Plays a sound through the default sink
    - SoundLevel: Gets the sound level of the sink monitor, designed to be polled continuously to get a live sound level
    - StartAudioRecording: Starts recording the audio from the sink monitor
    - StopAudioRecording: Stops the audio recording

All the methods are documented using docstrings. So just highlight the method in your editor to see what it does.

## Examples

Here are some examples of how to use the sound controller:

### Play a sound

```python
from LinuxSoundController import SoundController

# Create a sound controller object
sound_controller = SoundController()

# Get all sinks and monitors (note that this is nessesary if you dont want to manually specify the sink monitor)
sinks = sound_controller.GetSinks()
print(sinks)

# Check if sink is running
running = sound_controller.CheckSinkState(sinks[0])
print(running)

# Play a sound
sound_controller.PlaySound("path/to/sound.wav")
```

### Get sound level

```python
from LinuxSoundController import SoundController

# Create a sound controller object
sound_controller = SoundController()

# Get all sinks and monitors (note that this is nessesary if you dont want to manually specify the sink monitor)
sound_controller.GetSinks()

# Get sound level
while True:
    sound_level = sound_controller.SoundLevel()
    print(sound_level)
```

### Record audio

```python
import time
from LinuxSoundController import SoundController

# Create a sound controller object
sound_controller = SoundController()

# Get all sinks and monitors (note that this is nessesary if you dont want to manually specify the sink monitor)
sound_controller.GetSinks()

# Start audio recording
sound_controller.StartAudioRecording("path/to/recording.wav")
time.sleep(5)
sound_controller.StopAudioRecording()
```

## To Do

- [ ] Make into a pip package
- [ ] Make a .sh to install all dependencies

