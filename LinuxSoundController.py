import subprocess
import time


class SoundController():
    """Class for interacting with the sound device(s) on linux

    Functions:
        GetSinks: Gets all sinks and monitors
        CheckSinkState: Checks if sink is running or not
        PlaySound: Plays a sound through the default sink
        SoundLevel: Gets the sound level of the sink monitor, designed to be polled continuously to get a live sound level
        StartAudioRecording: Starts recording the audio from the sink monitor
        StopAudioRecording: Stops the audio recording
    """

    def __init__(self):
        self.sinkNames, self.sinkMonitors = self.GetSinks()

    def GetSinks(self, debug=False):
        """Gets all sinks and monitors

        Args:
            debug (bool, optional): Enable to print debug messages. Defaults to False.

        Returns:
            list: List of sink names
            list: List of monitor names
        """
        # Get sinks
        sinks = subprocess.check_output("pacmd list-sinks | grep -e 'name:'", shell=True).decode("utf-8").split('\n')
        sinkNames = []
        sinkMonitors = []
        for sink in sinks:
            if "name:" in sink:
                sinkNames.append(sink.split('name: ')[1])
                sinkMonitors.append(sink.split('name: ')[1].replace("<", "").replace(">", "") + ".monitor")

        if debug:
            print("Sinks:", sinkNames)

        return sinkNames, sinkMonitors

    def CheckSinkState(self, debug=False):
        """Checks if sink is running or not

        Args:
            debug (bool, optional): Enable to print debug messages. Defaults to False.

        Returns:
            bool: True if sink is running, False if not
        """

        # Check if sink is running
        sinkRunning = subprocess.check_output("pacmd list-sinks | grep -e 'state:'", shell=True).decode("utf-8").split('\n')
        state = sinkRunning[0].split('state: ')[1]

        if debug:
            print("State:", state)

        if state == "RUNNING":
            return True
        else:
            return False

    def PlaySound(self, soundPath):
        """Plays a sound through the default sink - note that the playsound library is probably a better option for this

        Args:
            soundPath (string): Path to the sound file
        """

        subprocess.run("pactl play-sample {} 0".format(soundPath), shell=True)

    def SoundLevel(self, debug=False, sinkMonitor=None, tempFile="out.wav"):
        """Gets the sound level of the sink monitor, designed to be polled continuously to get a live sound level

        Args:
            debug (bool, optional): Enable to print debug messages. Defaults to False.
            sinkMonitor (string, optional): The sink monitor to use. Defaults to the first sink monitor in the list from GetSinks().
            tempFile (string, optional): The temporary file to save the recording to. Defaults to "out.wav".

        Returns:
            float: The sound level in decibels (I think, just a value between 1 and 100 basically)
        """

        vol = -100

        if sinkMonitor is None:
            sinkMonitor = self.sinkMonitors[0]

        if debug:
            print("Killing old parec functions")

        subprocess.run("pkill -f 'parec --format=s16le'", shell=True)

        if debug:
            print("Starting recording")

        # Start recording with parec
        recording = subprocess.Popen(
            "parec --format=s16le -d {} | sox -t raw -r 44100 -b 16 -c 2 -e signed-integer - -t wav out.wav".format(sinkMonitor),
            shell=True
        )
        time.sleep(0.1)  # Adjust the duration based on your sample length

        # Stop recording
        recording.send_signal(subprocess.signal.SIGINT)

        if debug:
            print("Recording stopped")

        time.sleep(0.1)

        try:

            if debug:
                print("Running ffmpeg")

            # Run ffmpeg to get volume information
            cmd = "ffmpeg -i out.wav -af 'volumedetect' -vn -sn -dn -f null /dev/null"
            reading = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for the process to finish
            out, err = reading.communicate()

            if debug:
                print("ffmpeg volume check finished")

            # If invalid data detected set volume to -100 to indicate no sound detected
            errlines = err.decode("utf-8").split('\n')
            for line in errlines:
                if "Invalid Data" in line:
                    print("Invalid data detected")
                    vol = -100

            # Get the volume
            outlines = err.decode("utf-8").split('\n')
            for line in outlines:
                # print(line)  # Print each line for debugging
                if "mean_volume" in line:
                    vol = float(line.split("mean_volume: ")[1].split(" dB")[0])
                    break

        except Exception as e:
            if debug:
                print("Error in ffmpeg:", str(e))

        outVol = round((100 - vol*-1), 1)
        if debug:
            print("Volume:", outVol)

        return outVol

    def StartAudioRecording(self, debug=False, sinkMonitor=None, tempFile="output.wav"):
        """Starts recording the audio from the sink monitor

        Args:
            debug (bool, optional): Enable to print debug messages. Defaults to False.
            sinkMonitor (string, optional): The sink monitor to use. Defaults to the first sink monitor in the list from GetSinks().
            tempFile (string, optional): The temporary file to save the recording to. Defaults to "output.wav".
        """

        if sinkMonitor is None:
            sinkMonitor = self.sinkMonitors[0]
       
        if debug:
            print("Using sink monitor:", sinkMonitor)

        self.longRecording = subprocess.Popen(
            "parec --format=s16le -d {} | sox -t raw -r 44100 -b 16 -c 2 -e signed-integer - -t wav {}".format(sinkMonitor, tempFile),
            shell=True
        )

        if debug:
            print("Recording started")

    def StopAudioRecording(self, debug=False):
        """Stops the audio recording

        Returns:
            bool: True if the recording was successful, False if not
        """

        try:
            if self.longRecording is not None:
                self.longRecording.send_signal(subprocess.signal.SIGINT)
                time.sleep(0.1)
                self.longRecording = None

                if debug:
                    print("Recording stopped")

                return True

        except Exception as e:
            if debug:
                print("Error stopping recording:", str(e))
            
            return False

