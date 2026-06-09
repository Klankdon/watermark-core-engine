import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageChops, ImageEnhance


def decode_difference(original_path, suspected_path, output_path, multiplier):
    try:
        with Image.open(original_path).convert("RGB") as orig, Image.open(
            suspected_path
        ).convert("RGB") as susp:
            # If the suspected image went through an upscale pipeline,
            # scale the original up to match its exact resolution.
            if orig.size != susp.size:
                orig = orig.resize(susp.size, Image.Resampling.LANCZOS)

            # Extract the raw mathematical difference matrix
            diff = ImageChops.difference(orig, susp)

            # Amplify the difference so it's visible to the human eye
            # We use a color contrast enhancement multiplier
            enhancer = ImageEnhance.Contrast(diff)
            amplified_diff = enhancer.enhance(multiplier)

            amplified_diff.save(output_path, quality=100)
            return True
    except Exception as e:
        messagebox.showerror("Decoding Error", f"An error occurred: {str(e)}")
        return False


class DecoderApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Difference Matrix Decoder v1.0")
        self.root.geometry("550x300")
        self.root.resizable(False, False)

        self.orig_file = tk.StringVar()
        self.susp_file = tk.StringVar()
        self.amp_val = tk.DoubleVar(value=20.0)  # High default to pop low-density marks

        frame = ttk.Frame(root, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        # Original Image Row
        ttk.Label(frame, text="Original Base Image:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(frame, textvariable=self.orig_file, width=42).grid(
            row=0, column=1, pady=5, padx=5
        )
        ttk.Button(frame, text="Browse", command=self.browse_orig).grid(
            row=0, column=2, pady=5
        )

        # Suspected Image Row
        ttk.Label(frame, text="Watermarked/AI Image:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(frame, textvariable=self.susp_file, width=42).grid(
            row=1, column=1, pady=5, padx=5
        )
        ttk.Button(frame, text="Browse", command=self.browse_susp).grid(
            row=1, column=2, pady=5
        )

        # Amplification Slider Row
        ttk.Label(frame, text="Extraction Multiplier:").grid(
            row=2, column=0, sticky=tk.W, pady=15
        )

        slider_frame = ttk.Frame(frame)
        slider_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=15)

        self.slider = ttk.Scale(
            slider_frame,
            from_=1.0,
            to=50.0,
            variable=self.amp_val,
            orient=tk.HORIZONTAL,
            length=250,
            command=self.update_slider_label,
        )
        self.slider.pack(side=tk.LEFT)

        self.amp_label = ttk.Label(
            slider_frame, text=f"{self.amp_val.get():.1f}x"
        )
        self.amp_label.pack(side=tk.LEFT, padx=10)

        # Decode Button
        self.process_btn = ttk.Button(
            frame, text="Extract Hidden Matrix", command=self.run_decode
        )
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=20)

    def browse_orig(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )
        if file:
            self.orig_file.set(file)

    def browse_susp(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )
        if file:
            self.susp_file.set(file)

    def update_slider_label(self, val):
        self.amp_label.config(text=f"{float(val):.1f}x")

    def run_decode(self):
        if not self.orig_file.get() or not self.susp_file.get():
            messagebox.showwarning(
                "Missing Files", "Please select both the original and suspected images."
            )
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        )

        if output_file:
            success = decode_difference(
                self.orig_file.get(),
                self.susp_file.get(),
                output_file,
                self.amp_val.get(),
            )
            if success:
                messagebox.showinfo(
                    "Verification Complete", "Difference matrix extracted and saved!"
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = DecoderApp(root)
    root.mainloop()
