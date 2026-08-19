<div dir="rtl" align="right">

[English](#-codevision-extractor) | **العربية**

# 🎮 CodeVision Extractor — مستخلص الأكواد من الفيديو

أداة مفتوحة المصدر لاستخراج الأكواد البرمجية (C#/Unity) تلقائياً من فيديوهات الدورات التعليمية — بدون إنترنت، بدون سحابة، محلياً بالكامل.

> **سايبر برو للأعمال التقنية والهندسية**
> المهندس إبراهيم أنس العزاني

</div>

---

# 🎮 CodeVision Extractor

**Video-to-Code Reconstruction Engine** — Automatically extract C# source code from Unity/programming tutorial videos using OCR. 100% local, no cloud, no API keys.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **Batch Processing** | Process a single video or an entire folder of tutorials in one command |
| 🔍 **Smart OCR** | Tesseract-powered text extraction with C# code candidate scoring |
| 🧹 **IDE Noise Filter** | Strips Visual Studio / VS Code UI elements, line numbers, and autocomplete |
| 🔧 **OCR Auto-Correction** | Fixes common OCR typos (`Unityéngine` → `UnityEngine`) |
| 📝 **Script Reconstruction** | Chronological frame diffing & incremental line merging |
| 📚 **Build History** | See how the instructor built the code step-by-step |
| 🛡️ **Clean Architecture** | SOLID principles, modular packages, swappable components |
| 💻 **100% Offline** | No internet, no cloud APIs, no AI model downloads |

---

## 🏗️ Architecture

```
codevision-extractor/
├── codevision.py              # CLI Entry Point
├── core/                      # Domain Layer (Models, Interfaces, Exceptions)
├── extraction/                # FFmpeg Frame Extraction
├── ocr/                       # Tesseract OCR + Noise Filter
├── reconstruction/            # Code Reconstruction Engine
├── utils/                     # Banner, Logger, Validator
└── tests/                     # Unit Tests
```

Built following **SOLID Principles** and **Clean Architecture**:
- **S** — Single Responsibility: Each module handles one concern
- **O** — Open/Closed: Add new OCR engines without modifying existing code
- **L** — Liskov Substitution: All engines implement abstract interfaces
- **I** — Interface Segregation: Small, focused interfaces
- **D** — Dependency Inversion: High-level modules depend on abstractions

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** — [Download](https://python.org)
2. **FFmpeg** — [Download](https://ffmpeg.org/download.html) and add to PATH
3. **Tesseract OCR** — [Download](https://github.com/UB-Mannheim/tesseract/wiki)
   - Or place portable Tesseract in `./tesseract/` folder

### Installation

```bash
git clone https://github.com/lyou00/codevision-extractor.git
cd codevision-extractor
```

No pip packages needed — uses only Python standard library!

### Usage

**Option 1: Interactive Mode (Simplest — just run without flags!)**
```bash
python codevision.py
```
> The tool will ask you whether you want to process a file or folder, and you can simply **drag and drop** the file/folder into the terminal!

**Option 2: Direct Command Line Flags**

*Process a single video:*
```bash
python codevision.py --file "path/to/tutorial.mp4"
```

*Process an entire folder:*
```bash
python codevision.py --folder "path/to/video/folder/"
```

**Custom options:**
```bash
python codevision.py --folder "." --interval 5 --output "./my_output"
```

### All CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--file` | `-f` | — | Path to a single video file |
| `--folder` | `-d` | — | Path to a folder of videos |
| `--output` | `-o` | `./_CodeVision_Output` | Output directory |
| `--interval` | `-i` | `3` | Frame extraction interval (seconds) |
| `--ffmpeg-path` | — | auto-detect | Custom FFmpeg binary path |
| `--tesseract-path` | — | auto-detect | Custom Tesseract binary path |

---

## 📁 Output Structure

For each video, the tool generates:

```
_CodeVision_Output/
├── Video_Name_1/
│   ├── Scripts/
│   │   └── GameManager.cs          # Final reconstructed code
│   ├── ScriptHistory/
│   │   ├── GameManager_001.cs      # Step-by-step build history
│   │   ├── GameManager_002.cs
│   │   └── GameManager_FINAL.cs
│   ├── CandidateFrames/            # Screenshots of code frames
│   ├── OCR/                        # Raw OCR text per frame
│   └── REPORT.txt                  # Video processing report
│
├── Video_Name_2/
│   └── ...
│
└── MASTER_REPORT.csv               # Summary of all videos
```

---

## 🔮 Roadmap

- [x] **V1** — Basic FFmpeg + Tesseract OCR extraction
- [x] **V2** — Code reconstruction engine with deduplication
- [x] **V2.1** — Clean Architecture refactoring + GitHub release
- [ ] **V3** — AI integration for intelligent code cleanup (Human-in-the-Loop)
- [ ] **V4** — Desktop GUI application (WinUI / Electron)
- [ ] **V5** — Flutter mobile app for browsing extracted code

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Eng. Ibrahim Anas Al-Azzani**
**المهندس إبراهيم أنس العزاني**

CyberPro for Technical & Engineering Works
سايبر برو للأعمال التقنية والهندسية

📞 +967 773 256 961

---

> ⚠️ **Disclaimer**: OCR extraction is not perfect. Always review reconstructed scripts before compiling or using in production. This tool is designed to assist learning, not replace it.
