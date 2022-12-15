#!/usr/bin/python3
"""
opentrack-stick - opentrack to Linux HID stick events
=====================================================

Translate opentrack UDP-output to Linux-HID joystick events.

Usage:
======

    python3 opentrack-stick.py [-h] [-s <int>] [-a <float>] [-b <csv>] [-i ip-addr] [-o <port>] [-d]

Optional Arguments
------------------

    -w <float>   Wait seconds for input, then interpolate (default 0.001
                 to simulate a 1000 MHz mouse)
    -s <int>     Smooth over n values (default 250)
    -a <float>   Smoothing alpha 0.0..1.0, smaller values smooth more (default 0.05)
    -b <csv>     Bindings for opentrack-axis to virtual-control-number, must be 6 integers
                 (default 1,2,3,4,5,6)
    -i <ip-addr> The ip-address to listen on for the UDP feed from opentrack
    -p <port>    The UDP port number to listen on for the UDP feed from opentrack
    -h           Help
    -d           Output joystick event values to stdout for debugging purposes.

Description
===========

opentrack-stick listens for opentrack-output UDP-packets and uses evdev
to inject them into Linux input subsystem as HID joystick events.

The virtual-stick claims to have the same evdev capabilities as a
`Microsoft X-Box 360 pad` - but not all of them are functional (just the
stick axes at this stage)

By default, the x, y, z, yaw, pitch, and roll opentrack values are sent
to the virtual controller's left stick x, y, z and right stick x, y, z
(z is some kind of trigger based axes with a limited range, and
not recognised by some games).

The evdev joystick events are injected at the HID device level and are
independent of X11/Wayland, applications cannot differentiate them
from ordinary joystick events.  This means opentrack-stick will work in
any application, including environments such as Steam Proton.

Opentrack-stick will fill/smooth/interpolate a gap in input by feeding
the last move back into the smoothing algorithm. This will result in
the most recent value becoming dominant as time progresses.

Re-Mapping axis assignments
===========================

The binding of the virtual-controls to opentrack-track control can
be changed by using the `-b` option.

Opentrack controls in mapping order: x, y, z, yaw, pitch, roll.

A mapping specification allocates a numbered virtual control to each
opentrack axes in the mapping order: x, y, z, yaw, pitch, roll.

Virtual control numbers
-----------------------

0. no-control
1. left-stick, x-axis
2. left-stick, y-axis
3. left-stick, z-axis (some games don't recognise this axis)
4. right-stick x-axis
5. right-stick y-axis
6. right-stick z-axis (some games don't recognise this axis)
7. hat-x (some games don't recognise this control)
8. hat-y (some games don't recognise this control)

For example: `-b 0,0,1,4,5,0` binds opentrack-x to nothing,
opentrack-y to nothing, opentrack-z to control-1, opentrack-yaw
to control-4, opentrack-pitch to control-5 to, and opentrack-roll
to nothing.

Quick Start
===========

Get the python (python-3) ebdev library:

    pip install ebdev

Requires udev rule for access:

    sudo cat > /etc/udev/rules.d/65-opentrack-evdev.rules <EOF
    KERNEL=="event*", SUBSYSTEM=="input", ATTRS{name}=="opentrack*",  TAG+="uaccess"
    EOF
    sudo udevadm control --reload-rules ; udevadm trigger

Run this script:

    python3 opentrack-stick.py

Start opentrack; select Output `UDP over network`; configure the
output option to IP address 127.0.0.1, port 5005; start tracking.
Now start a game/application that makes use of a joystick;
in the game/application choose the joystick called `Microsoft X-Box 360 pad 0`.


Game Training Example: IL2 BoX
==============================

These are the steps I followed to get the controller to work for
head yaw and pitch in IL-2 BoX.

What I did:

I mapped opentrack head-z, head-yaw, head-pitch, and  to
virtual-control-1, virtual-control-4, and virtual-control-5,
that corresponds to `-b 0,0,1,4,5,0`.

1. Backup `.../IL-2 Sturmovik Battle of Stalingrad/data/input/`
2. Start opentrack-stick with only one axis mapped. For example
   yaw to  virtual-control-4, pass -b 0,0,0,4,0,0..
3. Start opentrack sending `Output` `UDP over network`
   with the port and address from step 1.
4. Check that the above is working (perhaps just run
   ``opentrack-stick -d`` at first to see if logs the events
   coming from opentrack).
6. Change the target curve so that head movement easily
   moves between the min and max output values. It's import
   that it ramps up smoothly and reaches the max value (or near
   to it).  If it doesn't ramp smoothy or doesn't get high
   enough, the game will ignore it as noise.
7. Start Steam and IL2 BoX and use the games key mapping
   menu to map pilot-head pitch to actual head pitch by
   moving your head appropriately.
8. Repeat for next target mapping.

Rather than restarting IL-2 BoX to perform each mapping,
I used two monitors. I used `alt-tab` between monitors
displaying the game and an xterm. Without restarting
IL-BoX or opentrack, I switched to the xterm,
interrupted (control-C) opentrack-stick, then started a
new opentrack-stick with the next `-b` value, for
example `opentrack-stick -b 0,0,0,5,0` to map opentrack-pitch
to virtual-control-5.

IL-2 BoX appears to ignore the virtual-controller's two Z axes,
virtual-control-3 and virtual-control-6. So they can't be used.

Having setup head yaw and pitch, I had no success in assigning
head movement (x, y, z).  Unlike head-movement, I did find
it possible to assign an axis to head-zoom, so I assigned
opentrack-z to virtual control-1.


Opentrack Protocol
==================

Each opentrack UDP-Output packet contains 6 little-endian
doubles: x, y, z, yaw, pitch, and roll.

Limitations
===========

Only pitch and yaw is implemented at this time.

The smoothing values need more research, as do other smoothing
methods.  A small alpha (less than 0.1) seems particularly good
at allowing smooth transitions.

Testing
=======

The following test rig can be employed:

1. Connect a real stick.
2. Start an opentrack, set the `Input` to `Linux joystick input`, then
   open the input option and choose the real joystick as the
   input `Device`.
3. Send the `opentrack` `UPD-Output` to UDP 127.0.0.1 Port 5005
   and start tracking.
4. Run `opentrack-stick.py`.
5. Start a second `opentrack`, under `Input` `Linux joystick input`, the
   `Device` options should now include `opentrack-stick`, choose this
   as the input.  Set up a UDP `Output` that goes nowhere by picking a port
   nothing is listening on.  Start it tracking.
6. The stick moves from the first opentrack should be passed to
   opentrack-stick, which should then be echoed by the second
   opentrack.

Or stop after step-4 and run an evdev listener on `/dev/input/event<N>`
device associated with the stick (see snoop-evdev.py).

Licence
=======

Copyright 2022 Michael Hamilton

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import datetime
import math
import select
import socket
import struct
import sys
import time
from collections import namedtuple
from pathlib import Path

import evdev
from evdev import AbsInfo
from evdev import ecodes

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

OpenTrackDataItem = namedtuple("OpenTrackDataItem", "name value min max")


class OpenTrackStick:

    def __init__(self, wait_secs=0.001, smoothing=500, smooth_alpha=0.1, bindings=(1, 2, 3, 4, 5, 6), debug=False):
        self.wait_secs = wait_secs
        self.debug = debug
        self.last_time = time.time_ns()
        self.smoothing = smoothing
        self.smooth_alpha = smooth_alpha
        print(f"Input wait max: {wait_secs * 1000} ms - will then feed the smoother with repeat values.")
        print(f"Smoothing: n={self.smoothing} alpha={self.smooth_alpha}")
        self.opentrack_data_items = [OpenTrackDataItem('x', 0, -75, 75),
                                     OpenTrackDataItem('y', 0, -75, 75),
                                     OpenTrackDataItem('z', 0, -75, 75),
                                     OpenTrackDataItem('yaw', 0, -90, 90),
                                     OpenTrackDataItem('pitch', 0, -90, 90),
                                     OpenTrackDataItem('roll', 0, -90, 90)]
        self.abs_outputs_defs = [
            StickOutputDef(ecodes.ABS_RX, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0),
                           smoothing=smoothing, smooth_alpha=smooth_alpha),
            StickOutputDef(ecodes.ABS_RY, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0),
                           smoothing=smoothing, smooth_alpha=smooth_alpha),
            StickOutputDef(ecodes.ABS_RZ, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0),
                           smoothing=smoothing, smooth_alpha=smooth_alpha),
            StickOutputDef(ecodes.ABS_X, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0),
                           smoothing=smoothing, smooth_alpha=smooth_alpha),
            StickOutputDef(ecodes.ABS_Y, AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0),
                           smoothing=smoothing, smooth_alpha=smooth_alpha),
            StickOutputDef(ecodes.ABS_Z, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
            HatOutputDef(ecodes.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
            HatOutputDef(ecodes.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),]
        print(f"Opentrack inputs:", ", ".join([otd.name for otd in self.opentrack_data_items]))
        print("Current outputs destinations: ", ','.join(str(i) for i in bindings))
        print(f"Possible output destinations: ",
              ", ".join([f"{i + 1}={d.name}" for i, d in enumerate(self.abs_outputs_defs)] + ["0=discard"]))
        # Have to include the buttons for the hid device to be ID'ed as a joystick:
        ui_input_capabilities = {
            ecodes.EV_KEY: [ecodes.BTN_A, ecodes.BTN_GAMEPAD, ecodes.BTN_SOUTH,
                            ecodes.BTN_B, ecodes.BTN_EAST, ecodes.BTN_NORTH, ecodes.BTN_X,
                            ecodes.BTN_WEST, ecodes.BTN_Y, ecodes.BTN_TL, ecodes.BTN_TR,
                            ecodes.BTN_SELECT, ecodes.BTN_START, ecodes.BTN_MODE, ecodes.BTN_THUMBL, ecodes.BTN_THUMBR,
                            ],
            ecodes.EV_ABS: [(output_def.evdev_code, output_def.evdev_abs_info) for output_def in self.abs_outputs_defs],
            ecodes.EV_FF: [ecodes.FF_EFFECT_MIN, ecodes.FF_RUMBLE]
        }
        self.hid_device = evdev.UInput(ui_input_capabilities, name="Microsoft X-Box 360 pad 0")
        self.destination_list = []
        for destination_num, opentrack_cap in zip(bindings, self.opentrack_data_items):
            if destination_num == 0:
                self.destination_list.append(None)
                print(f"Binding opentrack {opentrack_cap.name} to discard")
            else:
                index = destination_num - 1
                self.abs_outputs_defs[index].bind(opentrack_cap)
                destination = self.abs_outputs_defs[index]
                self.destination_list.append(destination)
                print(f"Binding opentrack {opentrack_cap.name} to {destination.name}")

    def start(self, udp_ip=UDP_IP, udp_port=UDP_PORT):
        print(f"UDP IP={udp_ip} PORT={udp_port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 48)
        sock.bind((udp_ip, udp_port))
        data_exhausted = True
        current = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        while True:
            sock.setblocking(data_exhausted)
            # Use previous data value if none is ready - keeps the mouse moving smoothly in the current direction
            if data_exhausted or select.select([sock], [], [], self.wait_secs)[0]:
                data, _ = sock.recvfrom(48)
                # Unpack 6 little endian doubles into a list:
                current = struct.unpack('<6d', data[:48])
                data_exhausted = False
            # Stop and wait if the data has settled down and is not changing.
            # Note: smoothing will keep changing the data for a while even though input may have stopped arriving.
            if not data_exhausted:
                data_exhausted = self.__send_to_hid__(current)
            if self.debug and data_exhausted:
                print("waiting for new data")

    def __send_to_hid__(self, values):
        debug = []
        data_exhausted = True
        for destination_def, raw_value in zip(self.destination_list, values):
            if destination_def:
                cooked_value = destination_def.cooked_value(raw_value)
                data_exhausted &= destination_def.send_to_hid(self.hid_device, cooked_value)
                if self.debug:
                    debug.append(f"{destination_def.name}={cooked_value} (raw={raw_value})")
        if debug:
            print(",".join(debug))
        self.hid_device.syn()
        return data_exhausted


class AbsOutputDef:
    def __init__(self, evdev_code, evdev_abs_info):
        self.evdev_type = ecodes.EV_ABS
        self.evdev_code = evdev_code
        self.evdev_abs_info = evdev_abs_info
        self.opentrack_info = None
        self.name = ecodes.ABS[self.evdev_code]
        self.data_exhausted = True

    def bind(self, opentrack_info):
        self.opentrack_info = opentrack_info

    def cooked_value(self, raw_value):
        pass

    def name(self):
        return self.opentrack_info('name')

    def evdev_code(self):
        return self.ev_info[0]

    def send_to_hid(self, hid_device, cooked_value):
        hid_device.write(ecodes.EV_ABS, self.evdev_code, cooked_value)
        return self.data_exhausted


class StickOutputDef(AbsOutputDef):

    def __init__(self, evdev_code, evdev_abs_info, smoothing=500, smooth_alpha=0.1):
        super().__init__(evdev_code, evdev_abs_info)
        self.previous_smoothed_value = 0.0
        self.smoother = Smooth(n=smoothing, alpha=smooth_alpha)

    def cooked_value(self, raw_value):
        ev_info = self.evdev_abs_info
        ot_info = self.opentrack_info
        # This may feed repeat data into the smoother, that should result in the latest value becoming stronger over time.
        smoothed = self.smoother.smooth(raw_value)
        self.data_exhausted = math.isclose(smoothed, self.previous_smoothed_value, abs_tol=0.1)
        self.previous_smoothed_value = smoothed
        scaled = ev_info.min + round(((smoothed - ot_info.min) / (ot_info.max - ot_info.min)) * (ev_info.max - ev_info.min))
        return scaled


class HatOutputDef(AbsOutputDef):

    def cooked_value(self, raw_value):
        # dif = round(raw_value - self.previous_raw_value)
        dif = round(raw_value)
        return 0 if dif == 0 else -dif // abs(dif)


class Smooth:
    def __init__(self, n, alpha=0.1):
        self.length = n
        self.values = [0] * n
        self.alpha = alpha
        self.total = sum(self.values)

    def smooth(self, v):
        return self.smooth_lp_filter(v)

    def smooth_simple(self, v):
        # Simple moving average - very efficient
        if self.length <= 1:
            return v
        self.total -= self.values[0]
        self.values.pop(0)
        self.values.append(v)
        self.total += v
        return self.total / self.length

    def smooth_lp_filter(self, v):
        # https://stackoverflow.com/questions/4611599/smoothing-data-from-a-sensor
        # https://en.wikipedia.org/wiki/Low-pass_filter#Simple_infinite_impulse_response_filter
        # The smaller the alpha, the more each previous value affects the following value.
        # So a smaller alpha results in more smoothing.
        # y[1] := alpha * x[1]
        # for i from 2 to n
        #     y[i] := y[i-1] + alpha * (x[i] - y[i-1])
        if self.length <= 1:
            return v
        self.values.pop(0)
        self.values.append(v)
        smoothed = self.values[0] * self.alpha
        for value in self.values[1:]:
            smoothed = smoothed + self.alpha * (value - smoothed)
        return smoothed


def main():
    if '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    if '--make-md' in sys.argv:
        with open(Path(__file__).with_suffix('.md').name, 'w') as md:
            md.write(__doc__)
        sys.exit(0)
    wait_secs = float(sys.argv[sys.argv.index('-w') + 1]) if '-w' in sys.argv else 0.001
    smooth_n = int(sys.argv[sys.argv.index('-s') + 1]) if '-s' in sys.argv else 250
    smooth_alpha = float(sys.argv[sys.argv.index('-q') + 1]) if '-q' in sys.argv else 0.05
    destinations = [int(c) for c in (sys.argv[sys.argv.index('-b') + 1] if '-b' in sys.argv else "1,2,3,4,5,6").split(',')]
    stick = OpenTrackStick(wait_secs=wait_secs,
                           smoothing=smooth_n,
                           smooth_alpha=smooth_alpha,
                           bindings=destinations,
                           debug='-d' in sys.argv)
    udp_ip = sys.argv[sys.argv.index('-i') + 1] if '-i' in sys.argv else UDP_IP
    udp_port = sys.argv[sys.argv.index('-p') + 1] if '-p' in sys.argv else UDP_PORT
    stick.start(udp_ip=udp_ip, udp_port=udp_port)


if __name__ == '__main__':
    main()
