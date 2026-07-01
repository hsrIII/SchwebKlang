# SchwebKlang

SchwebKlang turns a pressure-sensitive graphics tablet into a continuous MIDI controller for expressive synthesizer performance.

Inspired by the theremin, it allows smooth, continuous pitch control while simultaneously controlling dynamics and another modulation parameter using the tablet position and pen pressure.

The application outputs MIDI through a virtual MIDI port (e.g. LoopMIDI), allowing it to be used with any DAW or software synthesizer.

---

## Features

- 🎵 Continuous pitch control using MIDI Pitch Bend
- ✍️ Pressure-sensitive dynamics
- 🎛️ Freely assign Pitch, Volume and Modulation to tablet X, Y or pressure
- ↔️ Landscape and portrait ("upright") tablet orientations
- 🔁 Quick octave shifting via double taps
- 🖥️ Visualization mode for learning the playing area and controller mapping
- 🎹 Compatible with any MIDI-capable DAW or synthesizer

---

## Requirements

- A pressure-sensitive graphics tablet
- LoopMIDI (or another virtual MIDI port)
- A DAW or synthesizer capable of receiving MIDI

Install the Python dependencies with

```bash
pip install -r requirements.txt
```

---

## Reaper Setup

SchwebKlang sends the following MIDI messages:

| MIDI Message | Function |
|--------------|----------|
| Note On / Off | Starts and stops the note |
| Pitch Bend | Continuous pitch |
| CC7 | Volume |
| CC1 | Modulation |

Before playing, configure your instrument in Reaper:

- **Pitch Bend Range:** Set your synth's pitch bend range to **+24 semitones** (recommended). Since SchwebKlang supports octave shifts, the bend range should be **at least +12 semitones**.
- **CC7 (Volume):** Learn or map this controller to your instrument's volume or expression parameter.
- **CC1 (Modulation):** Learn or map this controller to the parameter you want to control (e.g. vibrato, filter cutoff, effects).

---

## Running

Run the program with:

```bash
python main.py
```


For your first start, it is recommended to use visualization mode:

```bash
python main.py --visualize
```

Visualization mode displays the active playing area together with the current controller values, making it easy to understand how the tablet is mapped before performing.


### Portrait mode

Rotate the tablet and enable portrait orientation:

```bash
python main.py --upright
```

### Different starting note

Setting a note can be done using:

```bash
python main.py --note 60
```

Here, C4 = 60 is set as the base note. Pitch is modulated by bending this note up using the pitchwheel midi commands.
As default base note A4=69 is set.

---

## Command Line Options

| Option | Description |
|---------|-------------|
| `--port_name` | LoopMIDI output port name |
| `--note` | Starting MIDI note |
| `--upright`, `-u` | Use portrait orientation |
| `--controls`, `-c` | Assign Pitch, Volume and Modulation to `x`, `y` or `p` |
| `--visualize`, `-v` | Display the controller layout and current MIDI values while playing |

Example:

```bash
python main.py \
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

These can be assigned freely to

- Pitch
- Volume
- Modulation

For example,

```bash
--controls y p x
```

assigns

- Pitch ← vertical position
- Volume ← pen pressure
- Modulation ← horizontal position

When using `--upright`, the coordinate system is rotated internally so that **horizontal** and **vertical** always refer to the physical movement of the pen across the tablet, regardless of its orientation.

---

## Octave Shifting

Double-tap inside the octave shift regions.

- upper-left corner → +1 octave
- lower-left corner → −1 octave


---

## Visualization Mode

Visualization mode displays the active playing area and the octave shift regions on the screen relative to their position on the tablet, as well as outputs, making it useful when learning the instrument or experimenting with different controller mappings.

---

## Signal Flow

```
Graphics Tablet
        │
        ▼
   SchwebKlang
        │
    LoopMIDI
        │
        ▼
      Reaper
        │
        ▼
 Software Synth
```

---

## Future Ideas

- Custom pitch response curves
- Quantized scales
- Alternative tuning systems
- User-defined playing zones
- Multiple MIDI CC outputs
- Presets
- OSC support

---

## License

MIT License