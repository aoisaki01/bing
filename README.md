# Bing Video Clipper & Subtitle Generator

Desktop application for automated video downloading, clipping, and subtitle generation built with Python, CustomTkinter, and OpenAI Whisper.

## Features

* Multi-platform video downloading powered by `yt-dlp`
* Automatic speech-to-text transcription using OpenAI Whisper
* Subtitle generation with timestamp alignment
* Resolution selector supporting 360p through 4K UHD
* Dual clipping modes: custom timestamps and automated segment extraction
* Modern dark interface built with CustomTkinter

## Tech Stack

* Python 3.10+
* CustomTkinter
* OpenAI Whisper
* yt-dlp
* FFmpeg

## Prerequisites

FFmpeg must be installed and available in your system PATH.

## Installation

1. Clone repository:

```bash
git clone https://github.com/aoisaki01/bing.git
cd bing
```

2. Install dependencies:

```bash
pip install customtkinter yt-dlp openai-whisper
```

3. Run the application:

```bash
python a.py
```