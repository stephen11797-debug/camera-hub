# Camera Hub

GTK control panel for USB webcams and OBSBOT cameras on Linux. Live preview,
per-camera image/pan/tilt/zoom controls, instrument tracking, and on-camera
presets.

## Requirements

System packages:

```
sudo apt install python3-gi python3-cairo gir1.2-gtk-3.0 \
    gir1.2-gdkpixbuf-2.0 gir1.2-pango-1.0 gstreamer1.0-tools \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly python3-numpy v4l-utils
```

You also need to be in the `video` group (`sudo usermod -aG video $USER`).

## Run

```
python3 media_control.py
```

## Integrate into another project

`media_control.py` does not run anything at import time — the app only starts
from the `if __name__ == "__main__"` block, so you can import it safely:

```python
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from media_control import MediaApp

app = MediaApp()          # builds the UI; app.window is a Gtk.Window
# embed app.window in your own layout, then run your own main loop:
Gtk.main()
```

`MediaApp` exposes:

- `app.window` — the `Gtk.Window` (present/embed it as needed)
- `app.preview` — the live `Preview` feed (a `Gtk.Image` via GStreamer)
- `app.cam()` / `app.cam_combo` — current camera selection
- `app._poll()` / `app.refresh_cameras()` — refresh controls and device list

`obsbot_control.py` is the standalone camera library (`Obsbot`, `Webcam`) and
has no GUI dependencies.

## Hardware support

`obsbot_control.py` is an **independent V4L2/UVC implementation** — it talks to
cameras over the standard Linux `video4linux2` and UVC (`VIDIOC_*`, `UVCIOC_*`)
ioctls. It does **not** bundle or depend on any vendor SDK, proprietary driver,
or OBSBOT firmware. OBSBOT-specific controls (pan/tilt/zoom, AI tracking, HDR,
FOV, presets) are accessed via the camera's own UVC extension units.

## License

MIT — see [LICENSE](LICENSE).
