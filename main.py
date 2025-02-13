import numpy as np
import soundfile as sf
import os
import time
import sys
import tinytag
import datetime
import csv

os.system("cls")

class Audio:

    def __init__(self, filename):
        self.filename = filename
        self.data, self.samplerate = sf.read(filename, dtype="int16")
        self.metadata = tinytag.TinyTag.get(self.filename).as_dict()

    def signature(self, length=2**3):
        data = self.data.copy()
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        if data.ndim == 1:
            data = np.column_stack((data, data))
        data = np.abs(data.astype(np.float32)) / np.iinfo(np.int16).max
        min_val = np.min(data)
        max_val = np.max(data)
        data = (data - min_val) / (max_val - min_val)
        diff = np.diff(data, axis=0)
        diff = np.abs(diff).flatten()
        diff_non_constant = diff[diff > 0]
        section_size = len(diff_non_constant) // length
        averages = np.array([np.mean(diff_non_constant[i * section_size:(i + 1) * section_size])
                            for i in range(length)])
        max_avg = np.max(averages) if len(averages) > 0 else 1
        scaled_averages = np.floor((averages / max_avg) * (len(characters) - 1)).astype(int)
        return "".join([characters[i] for i in scaled_averages])
    
    def score(self):
        data, samplerate = self.data.copy(), self.samplerate
        if data.ndim > 1:
            data = data.mean(axis=1)
        N = len(data)
        fft_data = np.fft.rfft(data)
        energy = np.abs(fft_data) ** 2
        freqs = np.fft.rfftfreq(N, d=1/samplerate)
        magnitude = np.abs(fft_data)
        threshold = 0.01 * np.max(magnitude)
        signif_idx = np.where((magnitude >= threshold) & (freqs >= 20) & (freqs <= 20000))[0]
        if signif_idx.size != 0:
            lowest_freq = freqs[signif_idx[0]]
            highest_freq = freqs[signif_idx[-1]]
        bass_idx = np.where((freqs >= 20) & (freqs <= 250))[0]
        crisp_idx = np.where((freqs >= 4000) & (freqs <= 20000))[0]
        full_idx = np.where((freqs >= 20) & (freqs <= 20000))[0]
        bass_energy = np.sum(energy[bass_idx])
        crisp_energy = np.sum(energy[crisp_idx])
        total_energy = np.sum(energy[full_idx])
        return {
            "bass": float(bass_energy/total_energy),
            "treble": float(crisp_energy/total_energy),
            "frequency": {
                "range": float((highest_freq - lowest_freq)),
                "score": float((highest_freq - lowest_freq)/15960),
                "max": float(highest_freq),
                "min": float(lowest_freq)
            }
        }
    
def log(text):
    sys.stdout.write("\0337")
    sys.stdout.write(f"\033[{size.lines};{1}H")
    sys.stdout.write(u"\u001b[2K\u001b[0m\u001b[1000D\u001b[1m\u001b[31;1m")
    sys.stdout.write("{}".format(str(datetime.timedelta(seconds=round(((time.time() - start)/(index+1)) * (len(audiofiles) - (index+1)))))))
    sys.stdout.write(u"\u001b[37;1m ")
    sys.stdout.write("{}".format(file.split("\\")[-1]))
    sys.stdout.write(u"\u001b[0m ")
    sys.stdout.write("\0338")
    sys.stdout.write(u"{}".format(text))
    sys.stdout.flush()
    
if __name__ in "__main__":
    audiofiles = []
    ids = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".flac"):
                audiofiles.append(os.path.join(root, file))
    start = time.time()
    size = os.get_terminal_size()
    writer = csv.writer(open("tracks.csv", "w", newline=""))
    sys.stdout.write(f"\033[{1};{size.lines-1}r")
    sys.stdout.write(f"\033[{1};{1}H")
    sys.stdout.flush()
    for index, file in enumerate(audiofiles):
        audio = Audio(file)
        signature = audio.signature()
        metadata = {
            "title": audio.metadata["title"][0],
            "album": audio.metadata["album"][0],
            # "artists": audio.metadata["artist"],
            # "albumartist": audio.metadata["albumartist"] if audio.metadata["albumartist"][0] in audio.metadata["artist"] else "Various Artists",
            "mainartist": [artist for artist in audio.metadata["albumartist"] if artist in audio.metadata["artist"]][0] if len([artist for artist in audio.metadata["albumartist"] if artist in audio.metadata["artist"]]) > 0 else audio.metadata["artist"][0]
        }
        if index < 1:
            writer.writerow([item[0] for item in metadata.items()])
        if signature not in ids:
            writer.writerow([item[1] for item in metadata.items()])
            log(u"\u001b[32;1m{}".format(signature))
            ids.append(signature)
        else:
            log(u"\u001b[31;1m{}".format(signature))
        log(" {}".format(file.split("\\")[-1]))
        log("\u001b[37;1m {} - {}".format(metadata["title"], metadata["mainartist"]))
        log("\n")

sys.stdout.write("\0337")

sys.stdout.write(f"\033[{size.lines};{1}H")
sys.stdout.write(u"\u001b[2K\u001b[0m\u001b[1000D\u001b[1m\u001b[37;1m")
sys.stdout.write(u"\u001b[0m ")
sys.stdout.write("\0338")
sys.stdout.write("\nFinished Successfully.\n\n")
sys.stdout.flush()
