# LimeSDR Quick Reference

Personal cheat sheet for working with LimeSDR Mini and LimeSDR-USB across Linux/Pi OS, macOS, and Windows.

## Hardware Summary

| Device | Chip | RX Channels | TX Channels | Max Sample Rate (approx) | Notes |
|---|---|---|---|---|---|
| LimeSDR Mini | FTDI FT601 | 1 | 1 | ~30.72 MS/s | USB 2.0, separate RX/TX SMA ports |
| LimeSDR-USB | Cypress FX3 | 2 | 2 | ~61.44 MS/s | USB 3.0, MIMO capable |

## LimeSDR-USB Physical Port Layout

Looking at the front of the board (logo facing you, USB male port at the top):

```
                                    USB Male

TX_0                                                            RX_0
                                         Lime
TX_1                                                             RX_1
```

- **RX_0** = SoapySDR RX channel `0`, best performance with antenna set to **LNAL**
- **RX_1** = SoapySDR RX channel `1`
- **TX_0** = SoapySDR TX channel `0`
- **TX_1** = SoapySDR TX channel `1`

Valid antenna names for this board/driver (confirmed via error message from SoapySDR): `NONE, LNAH, LNAL, LNAW, LB1, LB2`
- `LNAW` = wideband LNA — safe default for most general-purpose testing (covers HF through low GHz range)
- `LNAH` = high-band LNA
- `LNAL` = low-band LNA — best receiver performance observed on **RX_0** for lower-frequency testing (e.g. FM broadcast band, 25 MHz signal generator tests)
- `LB1` / `LB2` = internal loopback (not physical antenna inputs)

TX side likely follows the same channel-to-port mapping (0 → TX_0, 1 → TX_1), based on the RX pattern — not yet independently confirmed by direct test.

## Environment Setup

### Linux / Raspberry Pi OS
```bash
sudo apt update
sudo apt install -y limesuite limesuite-udev liblimesuite-dev soapysdr-tools soapysdr-module-lms7 python3-soapysdr python3-matplotlib python3-numpy

sudo udevadm control --reload-rules
sudo udevadm trigger

sudo usermod -aG plugdev $USER   # then log out/in or reboot
```

### macOS
```bash
brew install limesuite soapysdr soapysdr-module-lms7 pothosware/pothos/soapysdr
```

### Windows
- Use PothosSDR bundle or radioconda (`conda install -c conda-forge limesuite`)
- LimeSDR-USB: bind **WinUSB** via Zadig
- LimeSDR Mini: requires **FTDI D3XX driver** (NOT WinUSB) — install from https://ftdichip.com/drivers/d3xx-drivers/
  - If Windows keeps reverting to WinUSB, delete the old driver package first: `pnputil /delete-driver oemXX.inf /uninstall /force` (run as admin)

## Command-Line Tools

### Detect devices
```bash
LimeUtil --find
```

### Full device/library info
```bash
LimeUtil --info
```

### SoapySDR device discovery
```bash
SoapySDRUtil --find
SoapySDRUtil --info          # lists loaded modules/drivers (confirm "lime" is present)
SoapySDRUtil --probe="driver=lime"
```

## Python (SoapySDR) — Core Patterns

### Opening a device (reliable method)
Passing `dict(driver="lime")` directly can sometimes fail to match ("no match" error).
Enumerating first and passing the exact kwargs back is more reliable:

```python
import SoapySDR
devs = SoapySDR.Device.enumerate()
sdr = SoapySDR.Device(devs[0])          # or match by serial, see below
```

### Selecting a specific device by serial (useful when both SDRs are plugged in)
```python
devs = SoapySDR.Device.enumerate()
target = next(d for d in devs if dict(d)["serial"] == "1D5387F5DA8ABB")
sdr = SoapySDR.Device(target)
```

### RX setup
```python
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32

sdr.setSampleRate(SOAPY_SDR_RX, 0, 2e6)      # channel 0 = RX1
sdr.setFrequency(SOAPY_SDR_RX, 0, 100.1e6)
sdr.setGain(SOAPY_SDR_RX, 0, 30)             # 0-70 typical range

rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32, [0])
sdr.activateStream(rx_stream)

import numpy as np
buff = np.zeros(1024*1024, np.complex64)
sr = sdr.readStream(rx_stream, [buff], len(buff))   # sr.ret = samples actually read

sdr.deactivateStream(rx_stream)
sdr.closeStream(rx_stream)
```

### TX setup (generate + transmit your own signal)
```python
from SoapySDR import SOAPY_SDR_TX, SOAPY_SDR_CF32
import numpy as np

sdr.setSampleRate(SOAPY_SDR_TX, 0, 2e6)
sdr.setFrequency(SOAPY_SDR_TX, 0, 100.1e6)
sdr.setGain(SOAPY_SDR_TX, 0, 40)             # start LOW, increase gradually

t = np.arange(int(2e6 * 2)) / 2e6             # 2 sec of samples
signal = (0.5 * np.exp(2j*np.pi*50e3*t)).astype(np.complex64)   # 50kHz offset tone

tx_stream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32, [0])
sdr.activateStream(tx_stream)

chunk = 4096
for i in range(0, len(signal), chunk):
    sdr.writeStream(tx_stream, [signal[i:i+chunk]], len(signal[i:i+chunk]))

sdr.deactivateStream(tx_stream)
sdr.closeStream(tx_stream)
```

### Dual-channel (MIMO) — LimeSDR-USB only
```python
# RX both channels at once
rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32, [0, 1])
sdr.activateStream(rx_stream)

buff0 = np.zeros(1024*1024, np.complex64)
buff1 = np.zeros(1024*1024, np.complex64)
sr = sdr.readStream(rx_stream, [buff0, buff1], len(buff0))

# Per-channel config (independent freq/gain per channel)
sdr.setFrequency(SOAPY_SDR_RX, 0, 100.1e6)   # RX1
sdr.setFrequency(SOAPY_SDR_RX, 1, 433e6)     # RX2
```
Channel index: `0` = channel 1, `1` = channel 2. LimeSDR Mini only ever uses channel `0`.

### Plot spectrum from a capture (headless-safe, saves PNG)
```python
import matplotlib
matplotlib.use('Agg')      # required over SSH with no X11 forwarding
import matplotlib.pyplot as plt

spectrum = np.fft.fftshift(np.fft.fft(buff))
freqs = np.fft.fftshift(np.fft.fftfreq(len(buff), 1/sample_rate)) + center_freq
power_db = 20*np.log10(np.abs(spectrum) + 1e-12)

plt.plot(freqs/1e6, power_db)
plt.xlabel("Frequency (MHz)"); plt.ylabel("Power (dB)")
plt.savefig("spectrum.png", dpi=150)
```

## Useful gotchas / lessons learned

- **`dict(driver="lime")` can fail to match** even when the device is detected fine by `LimeUtil --find` — enumerate and pass exact kwargs instead (see above).
- **SSH without `-X`/`-Y` has no GUI** — save plots as PNG (`matplotlib.use('Agg')`) and view via VSCode Remote-SSH or `scp`.
- **Windows: LimeSDR Mini ≠ LimeSDR-USB driver.** Mini needs FTDI D3XX; USB needs WinUSB (via Zadig). Don't bind WinUSB to the Mini — it will enumerate as "OK" in Device Manager but LimeSuite/SoapySDR won't find it.
- **Pi USB is bus/power limited** — running both SDRs simultaneously, especially LimeSDR-USB with dual TX/RX at high sample rates, can cause power/bandwidth issues on a Pi. Use a powered USB hub if you see dropouts.
- **Watch legal/regulatory limits when transmitting** — FM broadcast band, cellular, aviation, etc. are protected. Test into an attenuator/dummy load or with a licensed frequency, not an open antenna into protected spectrum.
- **Check `sr.ret`** after `readStream`/`writeStream` calls — negative or mismatched values indicate overflow/underflow, common at high sample rates or under CPU load.
- **GRC "Soapy Custom Source" gotcha:** adding `channel=1` manually into the Device Arguments field caused channel 1 to silently fail to pick up any signal, even with correct antenna/gain/port. Removing it from Device Arguments (and instead relying on the block's own Nchan/channel output wiring) fixed RX_1 detection. Device Arguments should generally be left for device selection only (e.g. `driver=lime,serial=...`), not channel selection.
- **Antenna name errors are informative** — if you pass an invalid antenna string (e.g. `RX`), SoapySDR's error message lists the exact valid names for your board/driver version. Read the error text rather than guessing from older docs, since naming schemes (`RX1_L` vs `LNAL`) can differ by driver version.

## Current working allocation

| Device | Platform | Status |
|---|---|---|
| LimeSDR Mini | Raspberry Pi (Bookworm) | Working |
| LimeSDR Mini | macOS | Working |
| LimeSDR-USB | macOS | Working |
| LimeSDR-USB | Windows PC | Working |
| LimeSDR Mini | Windows PC | Not used (driver conflict, using Mac/Pi instead) |
