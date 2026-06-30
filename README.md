# SchwebKlang

Turn a graphics tablet into a continuous MIDI performance controller. SchwebKlang uses a pen tablet together with LoopMIDI to create a theremin-like instrument for expressive synthesizer performance.

The pen position and pressure are converted into MIDI Pitch Bend and Control Change messages, allowing smooth glides, continuous dynamics, and expressive modulation.

## Features

- 🎵 Continuous pitch control
- ✍️ Pressure-sensitive volume control
- 🎛️ Configurable mapping of tablet X, Y and pressure to Pitch, Volume and Modulation
- ↕️ Landscape and portrait tablet orientations
- 🔁 Octave shifting by double-tapping designated tablet regions
- 🖥️ Optional visualization of the playing area
- 🎹 Works with any DAW or synthesizer that accepts MIDI input

---

## Requirements

- Python 3.10+
- A pressure-sensitive graphics tablet (tested with Wacom tablets)
- Windows (recommended, because of LoopMIDI)
- LoopMIDI
- A DAW or synthesizer (e.g. Reaper, Vital, Surge XT, etc.)

### Python packages

Install the required dependencies:

```bash
pip install PySide6 mido python-rtmidi numpy
```

`python-rtmidi` provides the MIDI backend used by `mido`.

---

## MIDI Setup

1. Install and start **LoopMIDI**.
2. Create a virtual MIDI port (default name):

```
TabletTheremin 2
```

or specify another name with `--port_name`.

3. Configure your DAW to receive MIDI from the LoopMIDI port.

---

## Running

Default:

```bash
python schwebklang.py
```

### Visualization mode

Shows the active playing area and controller values instead of running fullscreen.

```bash
python schwebklang.py --visualize
```

### Portrait mode

Rotate the tablet and use portrait orientation.

```bash
python schwebklang.py --upright
```

### Different starting note

```bash
python schwebklang.py --note 60
```

---

## Command Line Options

| Option | Description |
|---------|-------------|
| `--port_name` | LoopMIDI output port name |
| `--note` | Starting MIDI note |
| `--upright`, `-u` | Use portrait orientation |
| `--controls`, `-c` | Assign Pitch, Volume and Mod to `x`, `y`, or `p` |
| `--visualize`, `-v` | Show instrument geometry instead of fullscreen |

Example:

```bash
python schwebklang.py \
    --controls y p x \
    --note 69 \
    --visualize
```

---

## Control Mapping

The three available controller sources are

| Symbol | Meaning |
|---------|---------|
| `x` | Horizontal pen position |
| `y` | Vertical pen position |
| `p` | Pen pressure |

These can be assigned to:

- Pitch
- Volume
- Modulation

Example:

```bash
--controls y p x
```

means

- Pitch ← Y position
- Volume ← Pen pressure
- Modulation ← X position

Any combination is possible.

---

## Playing Area

The tablet surface is divided into regions.

### Inner rectangle

The inner rectangle is the active performance area.

Its coordinates are normalized to values between 0 and 1 before being converted to MIDI.

### Margins

The margins provide additional functionality without affecting performance.

The left margin is reserved for octave shifting.

---

## Octave Shifting

Double-tap inside the octave shift regions.

Landscape mode:

- upper-left corner → +1 octave
- lower-left corner → −1 octave

Portrait mode:

The direction is adjusted automatically so that the physical gesture remains intuitive.

---

## MIDI Messages

SchwebKlang currently sends:

| MIDI Message | Purpose |
|--------------|---------|
| Note On | Starts the sustained note |
| Note Off | Stops the note |
| Pitch Bend | Continuous pitch |
| CC11 | Expression / volume |
| CC1 | Modulation |

Pitch bend range depends on your synthesizer.

**Remember to configure your synth's Pitch Bend Range** to match the desired playing range.

---

## Suggested Synth Settings

For expressive playing:

- Mono mode
- Legato enabled
- Portamento off (optional)
- Pitch Bend Range: ±12 semitones (recommended)

Map:

- CC11 → Expression or Volume
- CC1 → Vibrato, Filter Cutoff, or another expressive parameter

---

## Visualization Mode

Visualization mode displays

- normalized X position
- normalized Y position
- pressure
- volume
- pitch bend value
- modulation value
- current octave shift

It also draws

- the active playing rectangle
- octave shift regions

This mode is useful when adjusting controller mappings.

---

## Example Workflow

```
Graphics Tablet
        │
        ▼
  SchwebKlang
        │
   LoopMIDI Port
        │
        ▼
     Reaper
        │
        ▼
   Software Synth
```

---

## Ideas for Future Improvements

- Configurable pitch response curves
- Multiple playing scales
- Quantized pitch mode
- Vibrato gestures
- Multiple MIDI CC outputs
- User-configurable playing zones
- Presets
- OSC support

---

## License

MIT License