# ==============================================================================
# EXTRACT UNITY LOCAL C# CODE - VERSION 2 (FFmpeg + Tesseract OCR + Reconstructor)
# ==============================================================================
param (
    [string]$VideoDir = ".",
    [string]$OutputDir = ".\_Extracted_CSharp_V2",
    [int]$IntervalSec = 3
)

$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " UNITY LOCAL C# CODE EXTRACTOR & RECONSTRUCTOR (VERSION 2)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Locate FFmpeg
$ffmpegCmd = "ffmpeg"
if (-not (Get-Command "ffmpeg" -ErrorAction SilentlyContinue)) {
    $factoryPath = "C:\Program Files\FormatFactory\ffmpeg.exe"
    if (Test-Path $factoryPath) {
        $ffmpegCmd = $factoryPath
    } else {
        Write-Host "ERROR: FFmpeg binary not found." -ForegroundColor Red
        exit 1
    }
}
Write-Host "[+] FFmpeg binary: $ffmpegCmd" -ForegroundColor Green

# 2. Locate Tesseract OCR
$scriptDir = $PSScriptRoot
$localTess = Join-Path $scriptDir "tesseract\tesseract.exe"
$tessCmd = "tesseract"
if (Test-Path $localTess) {
    $tessCmd = $localTess
    $env:TESSDATA_PREFIX = Join-Path $scriptDir "tesseract\tessdata"
} elseif (-not (Get-Command "tesseract" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Tesseract binary not found." -ForegroundColor Red
    exit 1
}
Write-Host "[+] Tesseract binary: $tessCmd" -ForegroundColor Green

# 3. Locate Python Reconstructor
$pythonEngine = Join-Path $scriptDir "reconstruct_csharp.py"
if (-not (Test-Path $pythonEngine)) {
    Write-Host "ERROR: Python reconstructor engine missing at $pythonEngine" -ForegroundColor Red
    exit 1
}

# 4. Search Videos
$extensions = "*.mp4", "*.mkv", "*.avi", "*.mov", "*.webm"
$videos = Get-ChildItem -Path $VideoDir -Include $extensions -Recurse | Where-Object { $_.FullName -notmatch "_Extracted_CSharp" }

if ($videos.Count -eq 0) {
    Write-Host "[-] No videos found in $VideoDir" -ForegroundColor Yellow
    exit 0
}

Write-Host "[+] Found $($videos.Count) video(s)." -ForegroundColor Green

# 5. Process Videos
$vIdx = 0
foreach ($v in $videos) {
    $vIdx++
    Write-Host "`n[$vIdx/$($videos.Count)] Processing: $($v.Name)" -ForegroundColor Yellow

    $safeName = [System.IO.Path]::GetFileNameWithoutExtension($v.Name)
    $vOutDir = Join-Path $OutputDir $safeName
    $framesDir = Join-Path $vOutDir "Frames"
    $candDir = Join-Path $vOutDir "CandidateFrames"
    $ocrDir = Join-Path $vOutDir "OCR"

    New-Item -ItemType Directory -Force -Path $framesDir | Out-Null
    New-Item -ItemType Directory -Force -Path $candDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ocrDir | Out-Null

    # Frame extraction
    Write-Host "  -> Extracting frames (1 frame every $IntervalSec s)..." -ForegroundColor Gray
    $fpsExpr = "1/$IntervalSec"
    $ffmpegArgs = @("-y", "-i", "`"$($v.FullName)`"", "-vf", "fps=$fpsExpr", "-q:v", "2", "`"$framesDir\frame_%06d.jpg`"")
    Start-Process -FilePath $ffmpegCmd -ArgumentList ($ffmpegArgs -join " ") -NoNewWindow -Wait

    $frameFiles = Get-ChildItem -Path $framesDir -Filter "frame_*.jpg" | Sort-Object Name
    Write-Host "  -> Total frames extracted: $($frameFiles.Count)" -ForegroundColor Gray

    # OCR Processing
    $candCount = 0
    foreach ($f in $frameFiles) {
        $txtOutBase = Join-Path $ocrDir $f.BaseName
        $txtFile = "$txtOutBase.txt"

        $tessArgs = @("`"$($f.FullName)`"", "`"$txtOutBase`"", "--psm", "6", "txt")
        Start-Process -FilePath $tessCmd -ArgumentList ($tessArgs -join " ") -NoNewWindow -Wait

        if (Test-Path $txtFile) {
            $rawText = Get-Content -Path $txtFile -Raw -ErrorAction SilentlyContinue
            if ($rawText -match "using\s+System" -or $rawText -match "MonoBehaviour" -or $rawText -match "public\s+class" -or $rawText -match "void\s+Start" -or $rawText -match "void\s+Update") {
                $candCount++
                Copy-Item -Path $f.FullName -Destination $candDir -Force
            }
        }
    }

    Write-Host "  -> Candidate C# frames identified: $candCount" -ForegroundColor Green

    # Run Python Code Reconstructor (Version 2 Engine)
    Write-Host "  -> Running Version 2 Code Reconstruction Engine..." -ForegroundColor Cyan
    python "`"$pythonEngine`"" "`"$vOutDir`""

    # Clean up raw frames
    Remove-Item -Path $framesDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host " ALL VIDEOS PROCESSED WITH VERSION 2 RECONSTRUCTION ENGINE" -ForegroundColor Green
Write-Host " Output Directory: $OutputDir" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
