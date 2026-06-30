import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
import mido
import time
import numpy as np
import argparse

class TabletWindow(QLabel):
    def __init__(self, args):
        super().__init__()
        self.setStyleSheet("""
            background-color: #c8f3d2;
            color: #1a1a1a;
            font-size: 16px;
        """)
        self.setWindowTitle("Tablet")

        self.visualize = args.visualize
        if not self.visualize:
            self.showFullScreen()
        else:
            screen = QApplication.primaryScreen().geometry()
            print(screen.width(), screen.height())
            self.width = screen.width
            self.height = screen.height

            
        
        self.setWindowOpacity(0.5)  # transparent window

        self.setText("Touch the tablet with the pen...")
        self.setAlignment(Qt.AlignCenter)


        # controls
        self.upright = args.upright
        self.invert_y = None

        if not self.upright:
            self.inverted_y = True #makes y intuitive (high pos. values at top of screen)
            self.i_x = 0 #positions in tabletinput array (makes horizontal programmable)
            self.i_y = 1
            self.i_p = 2

            # window organization
            self.left_margin_width = self.width()*.2
            self.right_margin_width = self.width()*.1
            self.upper_margin_height = self.height()*.1
            self.lower_margin_height = self.height()*.0
            self.inner_width = self.width()-(self.left_margin_width+self.right_margin_width)
            self.inner_height = self.height()-(self.upper_margin_height+self.lower_margin_height)
            self.inner_rect_coors = [self.left_margin_width, self.upper_margin_height,self.inner_width,self.inner_height]#x1,y1,w,h


        else: 
            self.inverted_y = False #makes y intuitive (high pos. values at top of screen)
            self.i_x = 1 #positions in tabletinput array (makes horizontal programmable)
            self.i_y = 0
            self.i_p = 2

            # window organization
            self.left_margin_width = self.height()*.2
            self.right_margin_width = self.height()*.1
            self.upper_margin_height = self.width()*.0
            self.lower_margin_height = self.width()*.05
            self.inner_width = self.height()-(self.left_margin_width+self.right_margin_width)
            self.inner_height = self.width()-(self.upper_margin_height+self.lower_margin_height)

            self.inner_rect_coors = [self.upper_margin_height, self.left_margin_width,self.inner_height, self.inner_width]#x1,y1,w,h

        controls_dict = {"x": self.i_x, "y": self.i_y, "p": self.i_p}
        self.i_pitch = controls_dict[args.controls[0]]
        self.i_volume = controls_dict[args.controls[1]]
        self.i_mod = controls_dict[args.controls[2]]


        ## to be able to detect double clicks:
        #double click window: left margin width
        self.upper_octshift_coors = [0, 
                                     0, 
                                     self.left_margin_width if not self.upright else 2*self.left_margin_width,
                                     self.left_margin_width]#x1,y1,w,h
        self.lower_octshift_coors = [0 if not self.upright else (self.width()-2*self.left_margin_width), 
                                     (self.height()-self.left_margin_width) if not self.upright else 0, 
                                     self.left_margin_width  if not self.upright else 2*self.left_margin_width, 
                                     self.left_margin_width]

        #vars for defining double click:
        self.last_tap_time = 0.0
        self.last_tap_pos = None
        self.double_click_interval = 0.4  # seconds
        self.double_click_distance = 40   # pixels

        self.octave_shift = 0

        # Receive tablet events even when mouse tracking is off
        self.setAttribute(Qt.WA_TabletTracking)
        
        self.pressure_threshhold = 0.08

        #prerequisites for loop Midi interaction
        self.port = mido.open_output(args.port_name)

        #midi logic prerequisites
        self.pitch_wheel_min = -8192
        self.pitch_wheel_max = 8191
        self.volume_min = 0
        self.volume_max = 127

        self.note_playing = False
        self.note = 69 #A

        self.low_note = 60-12
        self.high_note = 60+12


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def check_octave_shift(self, tabletinput_raw):
        """
        if doubleclick in left lower and left upper margin change note by +- one octave
        """
        x,y,_ = tabletinput_raw[0], tabletinput_raw[1], tabletinput_raw[2]
        # if self.upright:
        #     y = self.height()-y
        now = time.time()

        # Detect two taps close in time and space
        if self.last_tap_pos is not None:
            dt = now - self.last_tap_time
            dx = x - self.last_tap_pos[0]
            dy = y - self.last_tap_pos[1]
            if dt < self.double_click_interval and (dx*dx + dy*dy)**0.5 < self.double_click_distance:
                
                ## octave shift:
                # # Upper part of the left margin?
                # if x < self.left_margin_width and y < self.upper_doubleclick_height:
                #     self.note += 12
                #     self.octave_shift += 1

                # #lower part of left margin
                # if x < self.left_margin_width and y > (self.height()-self.lower_doubleclick_height):
                #     self.note -= 12
                #     self.octave_shift -= 1

                                # Upper part of the left margin?
                if x > self.upper_octshift_coors[0] and x < (self.upper_octshift_coors[0]+self.upper_octshift_coors[2]):
                    if y > self.upper_octshift_coors[1] and y < (self.upper_octshift_coors[1]+self.upper_octshift_coors[3]):
                        self.note += 12 if not self.upright else -12
                        self.octave_shift += 1 if not self.upright else -1

                #lower part of left margin
                if x > self.lower_octshift_coors[0] and x < (self.lower_octshift_coors[0]+self.lower_octshift_coors[2]):
                    if y > self.lower_octshift_coors[1] and y < (self.lower_octshift_coors[1]+self.lower_octshift_coors[3]):
                        self.note += -12 if not self.upright else 12
                        self.octave_shift += -1 if not self.upright else 1


        self.last_tap_time = now
        self.last_tap_pos = (x, y)

    def tabletEvent(self, event):
        tabletinput_raw = [event.position().x(),event.position().y(),event.pressure()]
        tabletinput_normed = self._inner_window_pos_norm(tabletinput_raw)

        if event.type() == event.Type.TabletPress:
            self.check_octave_shift(tabletinput_raw)        

        pitch = self.pitch(tabletinput_normed[self.i_pitch])
        volume = self.volume(tabletinput_normed[self.i_volume])
        mod = self.mod(tabletinput_normed[self.i_mod])


        if tabletinput_normed[self.i_p] > self.pressure_threshhold and tabletinput_normed[self.i_x]>0:
            if not self.note_playing:
                self.port.send(mido.Message("note_on", note=self.note, velocity=127))
                self.note_playing = True

            self.port.send(mido.Message("pitchwheel", pitch=pitch)) #Pitch wheel range has to be set in Reaper
            self.port.send(mido.Message("control_change", control=11, value=volume)) 
            self.port.send(mido.Message("control_change", control=1, value=mod)
)

        else:
            if self.note_playing:
                self.port.send(mido.Message("note_off", note=self.note))
                self.note_playing = False

        self.monitor(tabletinput_normed, [volume,pitch,mod])

        event.accept()

    def _inner_window_pos(self,tabletinput):        
        x,y,_ = tabletinput[self.i_x], tabletinput[self.i_y], tabletinput[self.i_p]
        x_inner = x-self.left_margin_width
        x_inner = np.clip(x_inner, 0, self.inner_width)

        y_inner = y-self.upper_margin_height
        y_inner = np.clip(y_inner, 0, self.inner_height)

        tabletinput_out = [None,None,None]
        tabletinput_out[self.i_x] = x_inner
        tabletinput_out[self.i_y] = y_inner
        tabletinput_out[self.i_p] = _
        return tabletinput_out
    
    def _inner_window_pos_norm(self, tabletinput):
        """returns coordinates of position in inner window normed to 0-1
        flipps y coordinate to be intuitive (1 = up)
        """
        tabletinput_inner = self._inner_window_pos(tabletinput)
        x,y,_ = tabletinput_inner[self.i_x], tabletinput_inner[self.i_y], tabletinput_inner[self.i_p]
        
        x_norm = x/self.inner_width
        
        if self.inverted_y:
            y_norm = (self.inner_height-y)/self.inner_height
        else:
            y_norm = (y)/self.inner_height
        
        tabletinput_out = [None,None,None]
        tabletinput_out[self.i_x] = x_norm
        tabletinput_out[self.i_y] = y_norm
        tabletinput_out[self.i_p] = _
        return tabletinput_out

    def pitch(self, control):
        """
        calculate pitch here. For now using x position for pitch
        pitchwheel must be in range -8192, 8191
        Pitchwheel range has to be set in reaper

        only bends up
        """
         # pitch = int((np.log(x) / np.log(self.width())) * 16383) - 8192
        # pitch_norm = self._pitch_norm(y, self.height(), inverted=True)
        # pitch_norm = (self.inner_height-y)/self.inner_height
        # pitch = int((pitch_norm) * (16383)) - 8192
        
        # pitch = int((pitch_norm) * (self.pitch_wheel_max-self.pitch_wheel_min)) - int((self.pitch_wheel_max-self.pitch_wheel_min)/2)
        
        pitch = int(control*(self.pitch_wheel_max))
        return pitch
        
    def volume(self, control):
        """
        calculate volume here. For now using pressure
        volume in range 0,127
        Volume slider has to be learned in reaper

        Implemented with a left margin where volume is 0
        """
        volume = int(control*127)
        return volume
    
    def mod(self, control):
        """
        Temporary function, returns None
        range 0,127
        """
        mod = int(control*127)
        return mod

    def monitor(self, tabletinput, output):
        x,y,pressure = tabletinput[self.i_x], tabletinput[self.i_y], tabletinput[self.i_p]
        volume, pitch, effect = output
        #  print(f"X={x:.1f}  Y={y:.1f}  Pressure={pressure:.3f} ||  V={volume}  P={pitch}  E={effect}")
        self.setText(
            f"X: {x:.1f}\n"
            f"Y: {y:.1f}\n"
            f"Pressure: {pressure:.3f}\n\n"
            # f"left margin: {self.left_margin_width}, right margin: {self.right_margin_width}, upper margin: {self.upper_margin_height}, lower margin: {self.lower_margin_height}\n"
            # f"inner width: {self.inner_width}, inner_height: {self.inner_height}\n"
            # f"width: {self.width()}, height: {self.height()}\n\n"
            f"volume={round(volume/self.volume_max *100)}% \npitch={round(pitch/self.pitch_wheel_max,2)}\nmod={effect}\n\n"
            f"octave: {self.octave_shift}"
        )
    def ensure_geometry(self):
        if not hasattr(self, "left_margin_width"):
            self.setup_geometry()


    def paintEvent(self, event): 
        if self.visualize:
            super().paintEvent(event)

            with QPainter(self) as painter:
                pen = QPen(QColor(0, 0, 0, 120), 2)
                painter.setPen(pen)
                x1,y1,w,h=self.inner_rect_coors[0], self.inner_rect_coors[1], self.inner_rect_coors[2], self.inner_rect_coors[3]
                painter.drawRect(x1,y1,w,h) #inner rectangle
                x2,y2,w2,h2=self.upper_octshift_coors[0], self.upper_octshift_coors[1], self.upper_octshift_coors[2], self.upper_octshift_coors[3]
                x3,y3,w3,h3=self.lower_octshift_coors[0], self.lower_octshift_coors[1], self.lower_octshift_coors[2], self.lower_octshift_coors[3]
                painter.drawRect(x2,y2,w2,h2) #upper octshift
                painter.drawRect(x3,y3,w3,h3) #lower octshift

                # painter.drawRect(0, 0, int(self.left_margin_width), h) #left margin rectangle
                # painter.drawRect(w - int(self.right_margin_width), 0, int(self.right_margin_width), h) #right margin rectangle
                # painter.drawRect(0, 0, w, int(self.upper_margin_height)) #upper margin rectangle
                # painter.drawRect(0, h - int(self.lower_margin_height), w, int(self.lower_margin_height)) #lower margin rectangle




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SchwebKlang")
    parser.add_argument("--port_name", default = "TabletTheremin 2", help="LoopMIDI output port name")
    parser.add_argument("--note", type=int, default=69, help="Starting MIDI note (default: 69 (A4)). Bending up from this note.")
    parser.add_argument("--upright", "-u", default = False, action="store_true", help="control tablet in upright mode (Default: Landscape mode). Turn tablet to the left.")
    # parser.add_argument("--pitch", default="y", choices=["x", "y", "p"], help = "choose pitch as a function of x (lateral) position, y (vertical) position or pen pressure")
    # parser.add_argument("--volume", default="p", choices=["x", "y", "p"], help = "choose volume as a function of x (lateral) position, y (vertical) position or pen pressure")
    # parser.add_argument("--mod", default="x", choices=["x", "y", "p"], help = "choose mod as a function of x (lateral) position, y (vertical) position or pen pressure")
    parser.add_argument("--controls", "-c", nargs=3, metavar=("PITCH", "VOLUME", "MOD"), default=["y", "p", "x"], choices=["x", "y", "p"], help = "choose PITCH, VOLUME, MOD as a function of (lateral) position x, (vertical) position y and pen pressure p. Enter in order PITCH VOLUME MOD. Default: y p x (pitch=y, volume=p, mod=x)")
    parser.add_argument("--visualize", "-v", default = False, action="store_true", help="Visualize instrument geometry and outputs")

    args = parser.parse_args()

    print(args)

    app = QApplication(sys.argv)
    instrument = TabletWindow(args)
    instrument.note = args.note
    instrument.showFullScreen()   
    instrument.show()

    sys.exit(app.exec())