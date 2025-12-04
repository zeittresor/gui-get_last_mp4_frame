# Requirements: pip install opencv-python Pillow
# Code by github.com/zeittresor
# Description: Create a screenshot of the last frame from a .mp4 video

import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Versuchen, die benötigten Bibliotheken zu importieren
try:
    import cv2
except ImportError:
    print("Dieses Script benötigt 'opencv-python'. Installiere es mit:")
    print("    pip install opencv-python")
    raise

try:
    from PIL import Image
except ImportError:
    print("Dieses Script benötigt 'Pillow'. Installiere es mit:")
    print("    pip install Pillow")
    raise


class LastFrameExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Last Frame Extractor")
        self.root.geometry("520x220")

        self.video_path = None

        # Label für ausgewählte Datei
        self.file_label = tk.Label(root, text="No video selected", wraplength=500)
        self.file_label.pack(pady=10)

        # Buttons (Datei auswählen, Extrahieren)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.select_btn = tk.Button(
            btn_frame, text="Select MP4 video", command=self.select_video
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.extract_btn = tk.Button(
            btn_frame, text="Extract last frame", command=self.extract_last_frame,
            state=tk.DISABLED
        )
        self.extract_btn.pack(side=tk.LEFT, padx=5)

        # Option: 2x Upscale mit Lanczos
        self.upscale_var = tk.BooleanVar(value=True)
        self.upscale_check = tk.Checkbutton(
            root,
            text="Upscale 2× with Lanczos",
            variable=self.upscale_var
        )
        self.upscale_check.pack(pady=5)

        # Statusanzeige
        self.status_label = tk.Label(root, text="", fg="gray")
        self.status_label.pack(pady=5)

    def select_video(self):
        path = filedialog.askopenfilename(
            title="Select MP4 video",
            filetypes=[("MP4 Video", "*.mp4"), ("All Files", "*.*")]
        )
        if path:
            self.video_path = path
            self.file_label.config(text=f"Selected: {os.path.basename(path)}")
            self.status_label.config(text="")
            self.extract_btn.config(state=tk.NORMAL)

    def extract_last_frame(self):
        if not self.video_path:
            messagebox.showerror("Error", "No video selected.")
            return

        self.status_label.config(text="Processing last frame...")
        self.root.update_idletasks()

        out_path = self._process_video(
            self.video_path,
            upscale_2x=self.upscale_var.get()
        )

        if out_path:
            self.status_label.config(text=f"Saved: {os.path.basename(out_path)}")
            messagebox.showinfo("Done", f"Saved last frame as:\n{out_path}")
        else:
            self.status_label.config(text="Error while processing")

    def _process_video(self, path, upscale_2x=True):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video.")
            return None

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            cap.release()
            messagebox.showerror("Error", "Could not read frames from video.")
            return None

        # Wir versuchen von hinten nach vorne, falls der allerletzte Frame kaputt ist
        frame = None
        for offset in range(0, 3):  # last, last-1, last-2
            idx = frame_count - 1 - offset
            if idx < 0:
                break
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame_candidate = cap.read()
            if ret and frame_candidate is not None:
                frame = frame_candidate
                break

        cap.release()

        if frame is None:
            messagebox.showerror("Error", "Could not read last frame.")
            return None

        # OpenCV BGR -> PIL RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Optional 2x Upscale mit Lanczos
        if upscale_2x:
            new_size = (img.width * 2, img.height * 2)
            img = img.resize(new_size, resample=Image.LANCZOS)

        base, _ = os.path.splitext(path)
        out_path = base + "_lastframe.png"

        try:
            img.save(out_path, format="PNG")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image:\n{e}")
            return None

        return out_path


if __name__ == "__main__":
    root = tk.Tk()
    app = LastFrameExtractorApp(root)
    root.mainloop()
