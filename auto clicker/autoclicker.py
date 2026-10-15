#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoClicker Pro
===============
Auto-clic de escritorio para Windows, macOS y Linux.

- Inicia y detiene la automatización con la tecla F6 (global).
- Intervalo configurable en milisegundos o clics por segundo (CPS).
- Botón izquierdo, derecho o central, con clic simple o doble.
- Posición fija del cursor, límite de clics y jitter aleatorio.

Autor: kalan
Licencia: MIT
"""

from __future__ import annotations

import queue
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from pynput import keyboard, mouse
except ImportError:
    print(
        "Falta la dependencia 'pynput'.\n"
        "Instálala con:  pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


APP_NAME = "AutoClicker Pro"
APP_VERSION = "1.0.0"
HOTKEY = "f6"

BG = "#1e1e2e"
BG_CARD = "#282a3a"
BG_INPUT = "#313244"
FG = "#e0e0e8"
FG_MUTED = "#a6adc8"
ACCENT = "#7aa2f7"
ACCENT_HOVER = "#9ab4ff"
OK = "#9ece6a"
DANGER = "#f7768e"

BUTTONS = {
    "Izquierdo": mouse.Button.left,
    "Derecho": mouse.Button.right,
    "Central": mouse.Button.middle,
}


class AutoClicker:
    """Ventana principal del auto-clic."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.mouse = mouse.Controller()

        self.running = False
        self.clicks = 0
        self.fixed_pos: tuple[int, int] | None = None

        self.events: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self.listener: keyboard.Listener | None = None

        self._build_ui()
        self._start_hotkey_listener()
        self._poll_events()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=BG_CARD, foreground=FG, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG_CARD, foreground=FG_MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=BG, foreground=FG, font=("Segoe UI Semibold", 16))
        style.configure("TButton", font=("Segoe UI Semibold", 10), padding=6, borderwidth=0)
        style.configure("Accent.TButton", foreground="#1e1e2e", background=ACCENT)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER), ("disabled", BG_INPUT)])
        style.configure("TCheckbutton", background=BG_CARD, foreground=FG, font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[("active", BG_CARD)])
        style.configure("TSpinbox", fieldbackground=BG_INPUT, background=BG_INPUT,
                        foreground=FG, arrowcolor=FG, bordercolor=BG_INPUT, insertcolor=FG)
        style.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT,
                        foreground=FG, arrowcolor=FG)
        style.map("TCombobox", fieldbackground=[("readonly", BG_INPUT)],
                  foreground=[("readonly", FG)])
        self.root.option_add("*TCombobox*Listbox.background", BG_INPUT)
        self.root.option_add("*TCombobox*Listbox.foreground", FG)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)

        outer = ttk.Frame(self.root, padding=16)
        outer.grid(row=0, column=0, sticky="nsew")

        ttk.Label(outer, text=APP_NAME, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(outer, text=f"Tecla rápida: {HOTKEY.upper()} para iniciar / detener",
                  foreground=FG_MUTED, background=BG, font=("Segoe UI", 9)).grid(
            row=1, column=0, sticky="w", pady=(0, 12))

        # --- Tarjeta de estado -------------------------------------------
        card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        card.grid(row=2, column=0, sticky="ew")
        card.columnconfigure(1, weight=1)

        self.status_dot = tk.Label(card, text="●", bg=BG_CARD, fg=DANGER, font=("Segoe UI", 14))
        self.status_dot.grid(row=0, column=0, sticky="w")
        self.status_lbl = ttk.Label(card, text="Detenido", style="Card.TLabel",
                                    font=("Segoe UI Semibold", 12))
        self.status_lbl.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.counter_lbl = tk.Label(card, text="0 clics", bg=BG_CARD, fg=ACCENT,
                                    font=("Consolas", 18, "bold"))
        self.counter_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # --- Configuración -----------------------------------------------
        cfg = ttk.Frame(outer, style="Card.TFrame", padding=14)
        cfg.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        cfg.columnconfigure(1, weight=1)
        cfg.columnconfigure(3, weight=1)

        ttk.Label(cfg, text="Intervalo (ms)", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.interval_var = tk.IntVar(value=100)
        ttk.Spinbox(cfg, from_=1, to=60000, textvariable=self.interval_var, width=8,
                    command=self._update_cps).grid(row=0, column=1, sticky="w", padx=(8, 16))
        self.interval_var.trace_add("write", lambda *_: self._update_cps())

        ttk.Label(cfg, text="Botón", style="Card.TLabel").grid(row=0, column=2, sticky="w")
        self.button_var = tk.StringVar(value="Izquierdo")
        ttk.Combobox(cfg, textvariable=self.button_var, values=list(BUTTONS),
                     state="readonly", width=10).grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.cps_lbl = ttk.Label(cfg, text="≈ 10.0 clics/segundo", style="Muted.TLabel")
        self.cps_lbl.grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))

        self.double_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cfg, text="Doble clic", variable=self.double_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.jitter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cfg, text="Jitter aleatorio (±30%)", variable=self.jitter_var).grid(
            row=2, column=2, columnspan=2, sticky="w", pady=(8, 0))

        self.fixed_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cfg, text="Fijar posición actual del cursor", variable=self.fixed_var,
                        command=self._on_fixed_toggle).grid(
            row=3, column=0, columnspan=4, sticky="w", pady=(4, 0))

        ttk.Label(cfg, text="Límite de clics (0 = infinito)", style="Card.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.limit_var = tk.IntVar(value=0)
        ttk.Spinbox(cfg, from_=0, to=10_000_000, textvariable=self.limit_var, width=10).grid(
            row=4, column=2, columnspan=2, sticky="w", pady=(8, 0))

        # --- Botones ------------------------------------------------------
        actions = ttk.Frame(outer, padding=(0, 14, 0, 0))
        actions.grid(row=4, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(2, weight=1)

        self.start_btn = ttk.Button(actions, text="Iniciar", style="Accent.TButton",
                                    command=self.start)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.stop_btn = ttk.Button(actions, text="Detener", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(actions, text="Reiniciar", command=self.reset_counter).grid(
            row=0, column=2, sticky="ew", padx=(6, 0))

        ttk.Label(outer, text="Consejo: deja esta ventana abierta y usa F6 en cualquier programa.",
                  foreground=FG_MUTED, background=BG, font=("Segoe UI", 8),
                  wraplength=360).grid(row=5, column=0, sticky="w", pady=(12, 0))

        self.root.update_idletasks()
        self._center()

    def _center(self) -> None:
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ------------------------------------------------------------- Lógica
    def _update_cps(self, *_: object) -> None:
        try:
            ms = max(1, int(self.interval_var.get()))
        except (tk.TclError, ValueError):
            return
        self.cps_lbl.configure(text=f"≈ {1000 / ms:.1f} clics/segundo")

    def _on_fixed_toggle(self) -> None:
        if self.fixed_var.get() and not self.running:
            self.fixed_pos = self.mouse.position
            x, y = int(self.fixed_pos[0]), int(self.fixed_pos[1])
            self._set_hint(f"Posición fijada en ({x}, {y})")

    def _set_hint(self, text: str) -> None:
        self.cps_lbl.configure(text=text)

    def start(self) -> None:
        if self.running:
            return
        try:
            interval = max(1, int(self.interval_var.get())) / 1000.0
        except (tk.TclError, ValueError):
            messagebox.showerror(APP_NAME, "El intervalo debe ser un número entero (ms).")
            return
        try:
            limit = max(0, int(self.limit_var.get()))
        except (tk.TclError, ValueError):
            limit = 0

        self.running = True
        self.root.after(0, self._apply_running_style)
        if self.fixed_var.get():
            self.fixed_pos = self.mouse.position

        self.worker = threading.Thread(
            target=self._click_loop,
            args=(interval, limit, BUTTONS[self.button_var.get()], self.double_var.get()),
            daemon=True,
        )
        self.worker.start()

    def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        self.root.after(0, self._apply_running_style)

    def _apply_running_style(self) -> None:
        if self.running:
            self.status_dot.configure(fg=OK)
            self.status_lbl.configure(text="Activo")
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.status_dot.configure(fg=DANGER)
            self.status_lbl.configure(text="Detenido")
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def reset_counter(self) -> None:
        self.clicks = 0
        self._render_counter()

    def _click_loop(self, interval: float, limit: int, button: mouse.Button,
                    double: bool) -> None:
        count = 2 if double else 1
        while self.running:
            if limit and self.clicks >= limit:
                self.events.put(("stop", None))
                break
            try:
                if self.fixed_pos is not None:
                    self.mouse.position = self.fixed_pos
                self.mouse.click(button, count)
            except Exception:  # pragma: no cover - entorno sin permisos
                self.events.put(("error", "No se pudo simular el clic. Revisa los permisos."))
                break

            self.clicks += 1
            self.events.put(("count", self.clicks))

            delay = interval
            if self.jitter_var.get():
                delay *= random.uniform(0.7, 1.3)
            time.sleep(max(0.001, delay))

        self.events.put(("stopped", None))

    # --------------------------------------------------------- Hotkey/eventos
    def _start_hotkey_listener(self) -> None:
        try:
            self.listener = keyboard.GlobalHotKeys(
                {f"<{HOTKEY}>": lambda: self.events.put(("toggle", None))}
            )
            self.listener.daemon = True
            self.listener.start()
        except Exception as exc:  # pragma: no cover
            self.listener = None
            print(f"Advertencia: no se pudo registrar F6 ({exc})", file=sys.stderr)

    def _poll_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "count":
                    self._render_counter(payload)
                elif kind == "toggle":
                    self.stop() if self.running else self.start()
                elif kind == "stop":
                    self.stop()
                elif kind == "error":
                    self.stop()
                    messagebox.showerror(APP_NAME, payload)
                elif kind == "stopped":
                    if self.running:
                        self.running = False
                        self._apply_running_style()
        except queue.Empty:
            pass
        self.root.after(30, self._poll_events)

    def _render_counter(self, value: int | None = None) -> None:
        if value is None:
            value = self.clicks
        self.counter_lbl.configure(text=f"{value:,} clics".replace(",", "."))

    def _on_close(self) -> None:
        self.running = False
        if self.listener is not None:
            self.listener.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    AutoClicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
