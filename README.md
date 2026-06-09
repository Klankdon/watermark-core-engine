# Watermark Core Engine v2.0

As art theft in the digital age becomes increasingly common, this lightweight, localized Python toolkit allows creators to protect ownership without altering the aesthetic value of an image. 

Conventional visible watermarks can be easily cropped, painted over, or erased by AI tools. This engine bakes a watermark directly into the pixel data. It remains invisible to the naked eye, survives upscaling pipelines, and can be extracted later using a basic image difference calculation.

---

## How It Works: The Mechanics of Inversion Blending
The engine takes a base image and a black-and-white watermark mask (where the text/logo is white and the background is black). 

* **Inversion & Blending:** The engine takes the watermark mask, inverts it, and blends it slightly into the source image using an adjustable Bake-in Density slider.
* **The Hidden Data:** At a low density (like 0.05 or 0.10), the shifts in the pixel values are so infinitesimal that human eyes perceive them as compression artifacts or natural noise.
* **The Extraction:** To extract, run a pixel-by-pixel difference check (`ImageChops.difference` in Python) between the unwatermarked original and your altered copy. The hidden watermark will instantly pop out as a bright, crisp shape.

---

## Prerequisites & Installation

For security-conscious environments, you can run or compile these scripts locally on your machine.

1. Download and install **Python 3.10+**.
2. Open your terminal or command prompt and install the required dependencies:
   ```bash
   pip install pillow pyinstaller

   Tool 1: The Encoder (watermark_app.py)
Running the Code Natively
To run the raw encoding script:

Bash
python watermark_app.py
Step-by-Step Compilation (Windows .EXE)
Open your terminal/command prompt and navigate to the directory containing watermark_app.py.

Run the compiler:

Bash
pyinstaller --noconsole --onefile watermark_app.py
(Note: If that doesn't work after installing pyinstaller, use python -m PyInstaller --noconsole --onefile watermark_app.py)

Once the build finishes, your self-built, secure watermark_app.exe will be waiting inside the newly generated dist/ folder.

Pro-Tips for Tuning Your Encoder
The 0.10 Sweet Spot: Leaving the density slider at 0.10 ensures that the watermark can withstand heavy AI upscaling, mild compression, and minor color grading passes while remaining invisible.

Going Stealth (0.02 - 0.05): If your target platform doesn't use heavy post-processing compression, dropping the density down to 0.02 makes the watermark completely mathematical—undetectable even under extreme zoom-ins, but still verifiable via a difference matrix.

🔍 Tool 2: The Decoder (decoder_app.py)
Just like the encoder, keeping this pipeline completely open-source and compiled locally ensures total data security.

Running the Code Natively
To run the raw decoding script:

Bash
python decoder_app.py
Step-by-Step Compilation (Windows .EXE)
Open your terminal/command prompt and navigate to the directory containing decoder_app.py.

Run the compiler:

Bash
pyinstaller --noconsole --onefile decoder_app.py
(Note: If that doesn't work after installing pyinstaller, use python -m PyInstaller --noconsole --onefile decoder_app.py)

Fetch your secure executable from the newly built dist/ directory.

Decoding Analysis Tips for Users
If the extraction is pure black: The image has not been altered, or the watermark was completely stripped by a heavy compression re-encode (like a low-quality JPEG save that discarded sub-pixel data).

If a chaotic ghost image appears: If you see a faint, blurry outline of the actual image contents instead of a clean watermark, it means the watermarked image underwent an AI upscale step or a compression algorithm that shifted surrounding pixel values slightly. Turn the Extraction Multiplier slider up to 30.0x or higher to pull the sharp geometry of your mask out of the noise.

License
Distributed under the MIT License. See LICENSE for more information.
