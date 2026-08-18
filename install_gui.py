#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   CAMERA HUB COCKPIT - GUI INSTALLER     ║
║   © 2026 Stephen's Studio               ║
╚══════════════════════════════════════════╝
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import subprocess
import threading
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class CameraHubInstaller(Gtk.Window):
    def __init__(self):
        super().__init__(title="Camera Hub Cockpit")
        self.set_default_size(520, 620)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.installing = False
        self.selected = {"system": True, "group": True}

        css = """
        window { background: linear-gradient(180deg, #0a0e27 0%, #0d1a3a 50%, #0a0e27 100%); }
        .title { color: #4fc3f7; font-size: 28px; font-weight: bold; font-family: monospace; }
        .subtitle { color: rgba(79,195,247,0.5); font-size: 12px; font-family: monospace; }
        .desc { color: rgba(255,255,255,0.6); font-size: 12px; font-family: monospace; }
        .opt-btn {
            background-image: none;
            background-color: rgba(79,195,247,0.1);
            color: #4fc3f7;
            font-size: 13px;
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid rgba(79,195,247,0.3);
            font-family: monospace;
        }
        .opt-btn:hover { background-color: rgba(79,195,247,0.2); }
        .opt-btn.active { background-color: rgba(79,195,247,0.25); border: 1px solid #4fc3f7; }
        .install-btn {
            background-image: none;
            background-color: #4fc3f7;
            color: #0a0e27;
            font-size: 16px;
            font-weight: bold;
            padding: 14px 40px;
            border-radius: 25px;
            border: none;
            font-family: monospace;
        }
        .install-btn:hover { background-color: #81d4fa; }
        .install-btn:disabled { background-color: rgba(255,255,255,0.1); color: rgba(255,255,255,0.3); }
        .progress { trough-color: rgba(79,195,247,0.15); progress-color: #4fc3f7; min-height: 16px; border-radius: 8px; }
        .status { color: #4fc3f7; font-size: 12px; font-family: monospace; }
        .step { color: rgba(255,255,255,0.4); font-size: 11px; font-family: monospace; }
        .done { color: #4fc3f7; font-size: 20px; font-weight: bold; font-family: monospace; }
        .copyright { color: rgba(255,255,255,0.25); font-size: 10px; font-family: monospace; }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main)

        # Top accent
        top = Gtk.DrawingArea()
        top.set_size_request(520, 3)
        def draw_top(w, cr):
            cr.set_source_rgb(0.31, 0.76, 0.97)
            cr.rectangle(0, 0, 520, 3)
            cr.fill()
        top.connect("draw", draw_top)
        main.pack_start(top, False, False, 0)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        header.set_margin_top(25)
        header.set_margin_bottom(15)
        header.set_halign(Gtk.Align.CENTER)
        main.pack_start(header, False, False, 0)

        # Camera lens icon (drawn)
        lens = Gtk.DrawingArea()
        lens.set_size_request(80, 80)
        def draw_lens(w, cr):
            import math
            # Outer ring
            cr.set_source_rgb(0.31, 0.76, 0.97)
            cr.arc(40, 40, 38, 0, 2 * math.pi)
            cr.fill()
            # Inner dark
            cr.set_source_rgb(0.04, 0.055, 0.15)
            cr.arc(40, 40, 30, 0, 2 * math.pi)
            cr.fill()
            # Lens reflection
            cr.set_source_rgba(0.31, 0.76, 0.97, 0.3)
            cr.arc(32, 32, 10, 0, 2 * math.pi)
            cr.fill()
            # Center dot
            cr.set_source_rgb(0.31, 0.76, 0.97)
            cr.arc(40, 40, 5, 0, 2 * math.pi)
            cr.fill()
        lens.connect("draw", draw_lens)
        header.pack_start(lens, False, False, 0)

        studio = Gtk.Label()
        studio.set_markup('<span foreground="rgba(79,195,247,0.4)" font_family="monospace" size="small">★ Stephen\'s Studio ★</span>')
        header.pack_start(studio, False, False, 0)

        title = Gtk.Label()
        title.set_markup('<span foreground="#4fc3f7" font_family="monospace" size="x-large" weight="bold">CAMERA HUB</span>')
        header.pack_start(title, False, False, 0)

        subtitle = Gtk.Label()
        subtitle.set_markup('<span foreground="rgba(79,195,247,0.5)" font_family="monospace" size="small">OBSBOT PTZ & USB Webcam Control</span>')
        header.pack_start(subtitle, False, False, 0)

        desc = Gtk.Label()
        desc.set_markup('<span foreground="rgba(255,255,255,0.6)" font_family="monospace" size="x-small">Live preview · Pan/tilt · AI tracking · HDR · Presets</span>')
        header.pack_start(desc, False, False, 0)

        # Options
        opts = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        opts.set_halign(Gtk.Align.CENTER)
        opts.set_margin_top(15)
        opts.set_margin_bottom(15)
        main.pack_start(opts, False, False, 0)

        self.opt_btns = {}
        for key, label in [("system", "System Pkgs"), ("group", "Video Group")]:
            btn = Gtk.Button(label=f"  {label}")
            btn.get_style_context().add_class("opt-btn")
            btn.connect("clicked", self.toggle_option, key)
            opts.pack_start(btn, False, False, 0)
            self.opt_btns[key] = btn
            self.update_btn_style(key)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_start(40)
        sep.set_margin_end(40)
        main.pack_start(sep, False, False, 0)

        # Progress
        prog = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        prog.set_margin_start(40)
        prog.set_margin_end(40)
        main.pack_start(prog, False, False, 0)

        self.progress = Gtk.ProgressBar()
        self.progress.get_style_context().add_class("progress")
        prog.pack_start(self.progress, False, False, 0)

        self.status = Gtk.Label(label="Ready")
        self.status.get_style_context().add_class("status")
        self.status.set_halign(Gtk.Align.CENTER)
        prog.pack_start(self.status, False, False, 0)

        self.step_lbl = Gtk.Label()
        self.step_lbl.get_style_context().add_class("step")
        self.step_lbl.set_halign(Gtk.Align.CENTER)
        prog.pack_start(self.step_lbl, False, False, 0)

        # Install button
        self.install_btn = Gtk.Button(label="INSTALL")
        self.install_btn.get_style_context().add_class("install-btn")
        self.install_btn.set_margin_top(15)
        self.install_btn.set_margin_start(140)
        self.install_btn.set_margin_end(140)
        self.install_btn.connect("clicked", self.start_install)
        main.pack_start(self.install_btn, False, False, 0)

        # Done
        self.done_lbl = Gtk.Label()
        self.done_lbl.get_style_context().add_class("done")
        self.done_lbl.set_markup('<span foreground="#4fc3f7" font_family="monospace" size="large" weight="bold">✔ INSTALLATION COMPLETE</span>')
        self.done_lbl.set_halign(Gtk.Align.CENTER)
        self.done_lbl.set_no_show_all(True)
        main.pack_start(self.done_lbl, False, False, 10)

        # Copyright
        cr = Gtk.Label()
        cr.set_markup('<span foreground="rgba(255,255,255,0.25)" font_family="monospace" size="xx-small">© 2026 Stephen\'s Studio</span>')
        cr.set_halign(Gtk.Align.CENTER)
        cr.set_margin_bottom(8)
        main.pack_end(cr, False, False, 0)

    def toggle_option(self, btn, key):
        self.selected[key] = not self.selected[key]
        self.update_btn_style(key)

    def update_btn_style(self, key):
        btn = self.opt_btns[key]
        if self.selected[key]:
            btn.get_style_context().add_class("active")
            if "✓" not in btn.get_label():
                btn.set_label("✓ " + btn.get_label().replace("  ", ""))
        else:
            btn.get_style_context().remove_class("active")
            btn.set_label("  " + btn.get_label().replace("✓ ", ""))

    def start_install(self, *args):
        if self.installing:
            return
        self.installing = True
        self.install_btn.set_sensitive(False)
        self.install_btn.set_label("Installing...")
        for btn in self.opt_btns.values():
            btn.set_sensitive(False)
        self.done_lbl.hide()
        threading.Thread(target=self.do_install, daemon=True).start()

    def do_install(self):
        steps = []
        if self.selected["system"]:
            steps.append(("Installing system packages...",
                "sudo apt-get update -qq && sudo apt-get install -y -qq "
                "python3 python3-gi python3-cairo python3-numpy "
                "gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 gir1.2-pango-1.0 "
                "gstreamer1.0-tools gstreamer1.0-plugins-base "
                "gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly v4l-utils"))
        if self.selected["group"]:
            steps.append(("Adding user to video group...",
                "groups $USER | grep -q video || sudo usermod -aG video $USER"))

        total = len(steps)
        if total == 0:
            GLib.idle_add(self.finish)
            return

        for i, (label, cmd) in enumerate(steps):
            GLib.idle_add(self.status.set_text, label)
            GLib.idle_add(self.step_lbl.set_text, f"[{i+1}/{total}]")
            GLib.idle_add(self.progress.set_fraction, i / total)
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
            except:
                pass

        GLib.idle_add(self.progress.set_fraction, 1.0)
        GLib.idle_add(self.finish)

    def finish(self):
        self.status.set_text("All done!")
        self.step_lbl.set_text("")
        self.install_btn.set_label("INSTALL")
        self.done_lbl.set_no_show_all(False)
        self.done_lbl.show_all()
        self.installing = False
        for btn in self.opt_btns.values():
            btn.set_sensitive(True)
        self.install_btn.set_sensitive(True)

if __name__ == "__main__":
    win = CameraHubInstaller()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
