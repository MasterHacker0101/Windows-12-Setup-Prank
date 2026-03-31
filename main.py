import ctypes
import os
import random
import sys
import tkinter as tk
from tkinter import ttk

try:
    import winsound
except ImportError:  # pragma: no cover - Windows-only nicety
    winsound = None


class FakeInstallerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Windows 12 Setup")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 720)
        self.root.configure(bg="#06111c")
        self.configure_window_icon()
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<F11>", self.toggle_fullscreen)

        self.is_fullscreen = False
        self.progress_value = 0
        self.step_index = 0
        self.spinner_index = 0
        self.visited_sticky_points: set[int] = set()
        self.kernel_warning_logged = False
        self.warning_sound_played = False
        self.restart_overlay: tk.Frame | None = None
        self.device_name = os.environ.get("COMPUTERNAME", "DESKTOP")
        self.minute_estimate = random.randint(18, 26)
        self.second_estimate = random.randint(10, 55)
        self.spinner_frames = ["|", "/", "-", "\\"]

        self.steps = [
            {
                "phase": "Preparing setup environment",
                "detail": "Checking device compatibility and reserving temporary workspace.",
                "target": 7,
                "eta_drop": (1, 35),
                "logs": [
                    "Setup host initialized.",
                    "Reading platform profile.",
                    "Storage space requirement verified.",
                ],
                "active_item": 0,
            },
            {
                "phase": "Copying installation files",
                "detail": "Staging the base image and validating package signatures.",
                "target": 18,
                "eta_drop": (2, 5),
                "logs": [
                    "Core package manifest loaded.",
                    "Base image mounted successfully.",
                    "Local cache populated.",
                ],
                "active_item": 0,
            },
            {
                "phase": "Installing system components",
                "detail": "Applying shell, runtime, accessibility, and graphics feature packs.",
                "target": 36,
                "eta_drop": (3, 15),
                "logs": [
                    "Shell experience pack queued.",
                    "Graphics stack refresh prepared.",
                    "Security baseline template applied.",
                ],
                "active_item": 1,
            },
            {
                "phase": "Applying device support",
                "detail": "Synchronizing generic drivers and tuning startup services.",
                "target": 52,
                "eta_drop": (2, 45),
                "logs": [
                    "Display profile synchronized.",
                    "Input service map rebuilt.",
                    "Audio endpoint configuration saved.",
                ],
                "active_item": 1,
            },
            {
                "phase": "Installing updates",
                "detail": "Integrating cumulative patches and visual enhancements.",
                "target": 71,
                "eta_drop": (3, 40),
                "logs": [
                    "Update package 1 of 4 integrated.",
                    "Update package 2 of 4 integrated.",
                    "Servicing stack committed.",
                ],
                "active_item": 2,
            },
            {
                "phase": "Optimizing your experience",
                "detail": "Personalizing startup, security defaults, and first-run animation.",
                "target": 86,
                "eta_drop": (2, 20),
                "logs": [
                    "Taskbar assets generated.",
                    "Window compositor preset selected.",
                    "Privacy defaults staged.",
                ],
                "active_item": 2,
            },
            {
                "phase": "Finalizing installation",
                "detail": "Cleaning temporary files and preparing the first sign-in experience.",
                "target": 97,
                "eta_drop": (1, 30),
                "logs": [
                    "Final pass integrity check completed.",
                    "Startup profile sealed.",
                    "Recovery snapshot noted.",
                ],
                "active_item": 3,
            },
            {
                "phase": "Completing setup",
                "detail": "This may take a few moments. Your PC might restart several times.",
                "target": 100,
                "eta_drop": (0, 50),
                "logs": [
                    "Setup transaction finished.",
                    "Handing control to prank reveal sequence.",
                ],
                "active_item": 3,
            },
        ]

        self.check_items = [
            "Copying files",
            "Installing features",
            "Installing updates",
            "Finishing up",
        ]

        self.build_ui()
        self.animate_spinner()
        self.root.after(80, self.start_maximized)
        self.root.after(1200, self.run_next_step)

    def get_resource_path(self, filename: str) -> str:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, filename)

    def configure_window_icon(self) -> None:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("windows12.setup.prank")
        except Exception:
            pass

        icon_path = self.get_resource_path("icon.ico")
        if not os.path.exists(icon_path):
            return

        try:
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            pass

    def build_ui(self) -> None:
        header = tk.Frame(self.root, bg="#06111c")
        header.pack(fill="x", padx=24, pady=(20, 12))

        tk.Label(
            header,
            text="Windows 12 Setup",
            font=("Segoe UI", 28, "bold"),
            fg="#f4f8fb",
            bg="#06111c",
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Installing features and updates",
            font=("Segoe UI", 12),
            fg="#9fc7e5",
            bg="#06111c",
        ).pack(anchor="w", pady=(4, 0))

        shell = tk.Frame(self.root, bg="#0c1a2b", highlightbackground="#1e4264", highlightthickness=1)
        shell.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        main_area = tk.Frame(shell, bg="#0c1a2b")
        main_area.pack(fill="both", expand=True, padx=20, pady=20)

        left = tk.Frame(main_area, bg="#0c1a2b")
        left.pack(side="left", fill="both", expand=True, padx=(0, 18))

        right = tk.Frame(main_area, bg="#10233a", width=260, highlightbackground="#22496f", highlightthickness=1)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        top_row = tk.Frame(left, bg="#0c1a2b")
        top_row.pack(fill="x")

        self.phase_label = tk.Label(
            top_row,
            text="Preparing setup environment",
            font=("Segoe UI", 18, "bold"),
            fg="#f3f8fc",
            bg="#0c1a2b",
            anchor="w",
        )
        self.phase_label.pack(side="left")

        self.spinner_label = tk.Label(
            top_row,
            text="|",
            font=("Consolas", 20, "bold"),
            fg="#72d0ff",
            bg="#0c1a2b",
        )
        self.spinner_label.pack(side="right")

        self.detail_label = tk.Label(
            left,
            text="Checking device compatibility and reserving temporary workspace.",
            font=("Segoe UI", 11),
            fg="#9cc2dc",
            bg="#0c1a2b",
            justify="left",
            wraplength=560,
            anchor="w",
        )
        self.detail_label.pack(fill="x", pady=(8, 18))

        self.percent_label = tk.Label(
            left,
            text="0% complete",
            font=("Segoe UI", 12, "bold"),
            fg="#dff4ff",
            bg="#0c1a2b",
        )
        self.percent_label.pack(anchor="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Setup.Horizontal.TProgressbar",
            troughcolor="#091626",
            background="#47bfff",
            lightcolor="#47bfff",
            darkcolor="#2b9fe2",
            bordercolor="#091626",
            thickness=20,
        )

        self.progress = ttk.Progressbar(
            left,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            style="Setup.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x", pady=(10, 24))

        checklist_title = tk.Label(
            left,
            text="Setup progress",
            font=("Segoe UI", 11, "bold"),
            fg="#dff4ff",
            bg="#0c1a2b",
        )
        checklist_title.pack(anchor="w")

        self.check_labels = []
        for item in self.check_items:
            label = tk.Label(
                left,
                text=f"[ ] {item}",
                font=("Segoe UI", 12),
                fg="#9cc2dc",
                bg="#0c1a2b",
                anchor="w",
            )
            label.pack(fill="x", pady=4)
            self.check_labels.append(label)

        log_title = tk.Label(
            left,
            text="Activity log",
            font=("Segoe UI", 11, "bold"),
            fg="#dff4ff",
            bg="#0c1a2b",
        )
        log_title.pack(anchor="w", pady=(26, 8))

        self.console = tk.Text(
            left,
            height=10,
            bg="#071320",
            fg="#9fe7ff",
            insertbackground="#9fe7ff",
            relief="flat",
            font=("Consolas", 10),
            padx=12,
            pady=12,
        )
        self.console.pack(fill="both", expand=True)
        self.console.insert("end", "[00:00] Launching setup host.\n")
        self.console.insert("end", "[00:03] Preparing installation session.\n")
        self.console.configure(state="disabled")

        self.build_sidebar(right)
        self.refresh_checklist(active_item=0)
        self.update_eta_text()

        footer = tk.Label(
            shell,
            text="Windows 12 Pro Build 26001.microsoft.",
            font=("Segoe UI", 9),
            fg="#6f9abb",
            bg="#0c1a2b",
        )
        footer.pack(anchor="w", padx=24, pady=(0, 18))

    def build_sidebar(self, parent: tk.Frame) -> None:
        tk.Label(
            parent,
            text="Details",
            font=("Segoe UI", 13, "bold"),
            fg="#eff8ff",
            bg="#10233a",
        ).pack(anchor="w", padx=18, pady=(18, 14))

        self.machine_label = self.make_sidebar_item(parent, "Device", self.device_name)
        self.edition_label = self.make_sidebar_item(parent, "Edition", "Windows 12 Pro")
        self.compat_label = self.make_sidebar_item(parent, "Compatibility", f"{random.randint(94, 99)}%")
        self.eta_label = self.make_sidebar_item(parent, "Estimated time", "")
        self.stage_label = self.make_sidebar_item(parent, "Current stage", "Initializing")

        tk.Label(
            parent,
            text="Messages",
            font=("Segoe UI", 11, "bold"),
            fg="#eff8ff",
            bg="#10233a",
        ).pack(anchor="w", padx=18, pady=(18, 8))

        self.message_box = tk.Label(
            parent,
            text="Keep your PC on and plugged in while setup completes.",
            font=("Segoe UI", 10),
            fg="#c0daee",
            bg="#0f2034",
            justify="left",
            wraplength=220,
            padx=12,
            pady=12,
        )
        self.message_box.pack(fill="x", padx=18)

    def make_sidebar_item(self, parent: tk.Frame, title: str, value: str) -> tk.Label:
        tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 9),
            fg="#89aeca",
            bg="#10233a",
        ).pack(anchor="w", padx=18)

        value_label = tk.Label(
            parent,
            text=value,
            font=("Segoe UI", 12, "bold"),
            fg="#f4f8fb",
            bg="#10233a",
        )
        value_label.pack(anchor="w", padx=18, pady=(2, 12))
        return value_label

    def toggle_fullscreen(self, _event=None) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def start_maximized(self) -> None:
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

    def animate_spinner(self) -> None:
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)
        self.spinner_label.config(text=self.spinner_frames[self.spinner_index])
        self.root.after(120, self.animate_spinner)

    def append_log(self, message: str) -> None:
        elapsed = self.progress_value * 2 + self.step_index * 5
        minute, second = divmod(elapsed, 60)
        self.console.configure(state="normal")
        self.console.insert("end", f"[{minute:02d}:{second:02d}] {message}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def update_eta(self, minutes_drop: int, seconds_drop: int) -> None:
        total_seconds = self.minute_estimate * 60 + self.second_estimate
        total_seconds = max(80, total_seconds - (minutes_drop * 60 + seconds_drop))
        self.minute_estimate, self.second_estimate = divmod(total_seconds, 60)
        self.update_eta_text()

    def update_eta_text(self) -> None:
        self.eta_label.config(text=f"{self.minute_estimate} min {self.second_estimate:02d} sec")

    def refresh_checklist(self, active_item: int) -> None:
        for index, label in enumerate(self.check_labels):
            if index < active_item:
                label.config(text=f"[x] {self.check_items[index]}", fg="#dbf8ff")
            elif index == active_item:
                label.config(text=f"[>] {self.check_items[index]}", fg="#71d0ff")
            else:
                label.config(text=f"[ ] {self.check_items[index]}", fg="#8fb3cd")

    def animate_progress(self, target: int, on_complete) -> None:
        if self.progress_value >= target:
            on_complete()
            return

        sticky_points = {
            31: 1000,
            67: 1400,
            99: 2400,
        }

        if (
            self.progress_value in sticky_points
            and self.progress_value < target
            and self.progress_value not in self.visited_sticky_points
        ):
            self.visited_sticky_points.add(self.progress_value)
            self.root.after(sticky_points[self.progress_value], lambda: self.animate_progress(target, on_complete))
            return

        increment = 1
        if target - self.progress_value > 10 and random.random() > 0.72:
            increment = 2

        self.progress_value = min(target, self.progress_value + increment)
        self.progress["value"] = self.progress_value
        self.percent_label.config(text=f"{self.progress_value}% complete")

        if self.progress_value == 86 and not self.kernel_warning_logged:
            self.kernel_warning_logged = True
            self.append_log("Critical error detected: Rebuilding system kernel...")

        if self.progress_value >= 90:
            self.message_box.config(text="Almost done. This usually takes longer than expected.")
            if not self.warning_sound_played and winsound is not None:
                self.warning_sound_played = True
                try:
                    winsound.Beep(700, 200)
                except RuntimeError:
                    pass
        elif self.progress_value >= 55:
            self.message_box.config(text="Installing updates and preparing the first sign-in experience.")

        delay = random.randint(120, 210)
        if self.progress_value >= 90:
            delay = random.randint(180, 260)

        self.root.after(delay, lambda: self.animate_progress(target, on_complete))

    def run_next_step(self) -> None:
        if self.step_index >= len(self.steps):
            self.finish_prank()
            return

        step = self.steps[self.step_index]
        self.phase_label.config(text=step["phase"])
        self.detail_label.config(text=step["detail"])
        self.stage_label.config(text=step["phase"])
        self.refresh_checklist(step["active_item"])

        for log in random.sample(step["logs"], k=len(step["logs"])):
            self.append_log(log)

        minutes_drop, seconds_drop = step["eta_drop"]
        self.update_eta(minutes_drop, seconds_drop)
        self.step_index += 1

        self.animate_progress(
            step["target"],
            lambda: self.root.after(random.randint(900, 1800), self.run_next_step),
        )

    def finish_prank(self) -> None:
        self.refresh_checklist(active_item=4)
        self.phase_label.config(text="Restarting your PC")
        self.detail_label.config(text="This may take several minutes. Do not turn off your computer.")
        self.percent_label.config(text="100% complete")
        self.eta_label.config(text="0 min 00 sec")
        self.stage_label.config(text="Restarting")
        self.message_box.config(text="Restarting your PC. Please do not turn off your computer.")
        self.append_log("Restart sequence initiated.")

        self.restart_overlay = tk.Frame(self.root, bg="#0a1830")
        self.restart_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(
            self.restart_overlay,
            text="Restarting your PC...",
            font=("Segoe UI", 26, "bold"),
            fg="#f4f8fb",
            bg="#0a1830",
        ).place(relx=0.5, rely=0.42, anchor="center")

        tk.Label(
            self.restart_overlay,
            text="Please do not turn off your computer.",
            font=("Segoe UI", 14),
            fg="#a8c8e7",
            bg="#0a1830",
        ).place(relx=0.5, rely=0.50, anchor="center")

        tk.Label(
            self.restart_overlay,
            text="Working on updates 100%",
            font=("Segoe UI", 12),
            fg="#7ab7e6",
            bg="#0a1830",
        ).place(relx=0.5, rely=0.57, anchor="center")

        self.root.after(3000, self.show_april_fools)

    def show_april_fools(self) -> None:
        if self.restart_overlay is not None:
            self.restart_overlay.destroy()
            self.restart_overlay = None

        self.phase_label.config(text="Setup complete")
        self.detail_label.config(text="April Fools. Nothing was installed, changed, or removed.")
        self.stage_label.config(text="Prank reveal")
        self.message_box.config(text="Your PC is perfectly fine. This was only a fake installer screen.")
        self.append_log("Setup simulation closed without modifying the system.")
        self.append_log("Press Esc to exit or F11 to go fullscreen again.")

        overlay = tk.Frame(self.root, bg="#daf6ff", highlightbackground="#89dfff", highlightthickness=2)
        overlay.place(relx=0.5, rely=0.52, anchor="center")

        tk.Label(
            overlay,
            text="APRIL FOOLS",
            font=("Segoe UI", 26, "bold"),
            fg="#082136",
            bg="#daf6ff",
            padx=38,
            pady=14,
        ).pack()

        tk.Label(
            overlay,
            text="No files were touched. No installation happened.",
            font=("Segoe UI", 12),
            fg="#14324c",
            bg="#daf6ff",
            padx=24,
            pady=0,
        ).pack(pady=(0, 18))

        tk.Button(
            overlay,
            text="Close",
            font=("Segoe UI", 11, "bold"),
            bg="#082136",
            fg="#ffffff",
            activebackground="#10304b",
            activeforeground="#ffffff",
            relief="flat",
            padx=22,
            pady=9,
            command=self.root.destroy,
        ).pack(pady=(0, 22))


def main() -> None:
    root = tk.Tk()
    FakeInstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
