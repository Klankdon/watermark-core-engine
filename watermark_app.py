# =====================================================================
# Copyright (c) 2026 Jeremy McGehee (Klankton)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
# =====================================================================
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageChops, ImageOps


def process_image(source_path, watermark_path, output_path, density):
    try:
        with Image.open(source_path).convert("RGB") as src, Image.open(
            watermark_path
        ).convert("RGB") as wm:
            # Match the watermark size to the source dimensions
            if src.size != wm.size:
                wm = wm.resize(src.size, Image.Resampling.LANCZOS)

            # Invert the watermark mask
            inverted_wm = ImageOps.invert(wm)

            # Blend source and inverted mask based on density
            # Formula: result = src * (1.0 - density) + inverted_wm * density
            marked_image = Image.blend(src, inverted_wm, alpha=density)

            # Save with zero color subsampling to keep pixel data pristine
            marked_image.save(output_path, quality=100, subsampling=0)
            return True
    except Exception as e:
        messagebox.showerror("Processing Error", f"An error occurred: {str(e)}")
        return False


class WatermarkApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Watermark Core Engine v2.0")
        self.root.geometry("550x300")
        self.root.resizable(False, False)

        self.source_file = tk.StringVar()
        self.watermark_file = tk.StringVar()
        self.density_val = tk.DoubleVar(value=0.10)

        # UI Layout
        frame = ttk.Frame(root, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        # UI Elements: Source Image
        ttk.Label(frame, text="Source Image:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(frame, textvariable=self.source_file, width=45).grid(
            row=0, column=1, pady=5, padx=5
        )
        ttk.Button(frame, text="Browse", command=self.browse_source).grid(
            row=0, column=2, pady=5
        )

        # UI Elements: Watermark
        ttk.Label(frame, text="Watermark Mask:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(frame, textvariable=self.watermark_file, width=45).grid(
            row=1, column=1, pady=5, padx=5
        )
        ttk.Button(frame, text="Browse", command=self.browse_watermark).grid(
            row=1, column=2, pady=5
        )

        # UI Elements: Density Slider
        ttk.Label(frame, text="Bake-in Density:").grid(
            row=2, column=0, sticky=tk.W, pady=15
        )
        slider_frame = ttk.Frame(frame)
        slider_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=15)

        self.slider = ttk.Scale(
            slider_frame,
            from_=0.01,
            to=0.50,
            variable=self.density_val,
            orient=tk.HORIZONTAL,
            length=250,
            command=self.update_slider_label,
        )
        self.slider.pack(side=tk.LEFT)

        self.density_label = ttk.Label(
            slider_frame, text=f"{self.density_val.get():.2f}"
        )
        self.density_label.pack(side=tk.LEFT, padx=10)

        # Execution Button
        self.process_btn = ttk.Button(
            frame, text="Bake Watermark & Save", command=self.run_bake
        )
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=20)

    def browse_source(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )
        if file:
            self.source_file.set(file)

    def browse_watermark(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )
        if file:
            self.watermark_file.set(file)

    def update_slider_label(self, val):
        self.density_label.config(text=f"{float(val):.2f}")

    def run_bake(self):
        if not self.source_file.get() or not self.watermark_file.get():
            messagebox.showwarning(
                "Missing Files", "Please select both a source and watermark image."
            )
            return

        ext = os.path.splitext(self.source_file.get())[1]
        output_file = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        )

        if output_file:
            success = process_image(
                self.source_file.get(),
                self.watermark_file.get(),
                output_file,
                self.density_val.get(),
            )
            if success:
                messagebox.showinfo("Success", "Watermark successfully baked!")


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
