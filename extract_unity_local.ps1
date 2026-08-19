#requires -Version 5.1
<##
 extract_unity_local.ps1
 Extract C# code visible in LOCAL Unity tutorial videos.
 No YouTube download. No Ollama. No large Vision model.

 Usage:
   Set-ExecutionPolicy -Scope Process Bypass
   .\extract_unity_local.ps1
##>

[CmdletBinding()]
param(
    [string]$InputFolder = "",
    [string]$OutputFolder = "",
    [int]$IntervalSeconds = 3,
    [int]$MaxWidth = 1920,
    [switch]$SkipInstall
)

function Has-Cmd([string]$Name) { return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $env:Path = "$( [Environment]::GetEnvironmentVariable('Path','Machine') );$( [Environment]::GetEnvironmentVariable('Path','User') )"
}
function Install-Winget([string]$Id,[string]$Name) {
    if (-not (Has-Cmd winget)) { throw "winget is missing." }
    Write-Host "Installing $Name ..." -ForegroundColor Yellow
    winget install --id $Id --exact --accept-package-agreements --accept-source-agreements
    Refresh-Path
}
function Safe-Name([string]$Name) {
    foreach ($c in [IO.Path]::GetInvalidFileNameChars()) { $Name = $Name.Replace($c,'_') }
    return $Name.Trim()
}

try {
    Write-Host "`nUNITY LOCAL C# CODE EXTRACTOR" -ForegroundColor Green

    if ([string]::IsNullOrWhiteSpace($InputFolder)) { $InputFolder = Read-Host "Enter Unity videos folder path" }
    if (-not (Test-Path -LiteralPath $InputFolder -PathType Container)) { throw "Folder does not exist: $InputFolder" }
    $InputFolder = (Resolve-Path -LiteralPath $InputFolder).Path

    if ([string]::IsNullOrWhiteSpace($OutputFolder)) { $OutputFolder = Join-Path $InputFolder "_Extracted_CSharp" }
    New-Item -ItemType Directory -Force -Path $OutputFolder | Out-Null
    $OutputFolder = (Resolve-Path -LiteralPath $OutputFolder).Path

    # FFmpeg
    if (-not (Has-Cmd ffmpeg)) {
        if ($SkipInstall) { throw "FFmpeg is missing." }
        Install-Winget "Gyan.FFmpeg" "FFmpeg"
    }
    if (-not (Has-Cmd ffmpeg)) { throw "ffmpeg.exe not found in PATH." }

    # Tesseract
    if (-not (Has-Cmd tesseract)) {
        if (-not $SkipInstall) {
            try { Install-Winget "UB-Mannheim.TesseractOCR" "Tesseract OCR" } catch { }
        }
    }
    if (-not (Has-Cmd tesseract)) {
        foreach ($p in @('C:\Program Files\Tesseract-OCR','C:\Program Files (x86)\Tesseract-OCR')) {
            if (Test-Path $p) { $env:Path += ";$p"; break }
        }
    }
    if (-not (Has-Cmd tesseract)) { throw "Tesseract OCR is missing." }

    $extensions = @('.mp4','.mkv','.avi','.mov','.wmv','.webm','.m4v','.ts','.mts','.m2ts')
    $videos = @(Get-ChildItem -LiteralPath $InputFolder -Recurse -File | Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() })
    if ($videos.Count -eq 0) { throw "No video files found in: $InputFolder" }

    Write-Host "Found $($videos.Count) video(s).`n" -ForegroundColor Green
    $master = New-Object System.Collections.Generic.List[object]
    $index = 0

    foreach ($video in $videos) {
        $index++
        $base = Safe-Name $video.BaseName
        $out = Join-Path $OutputFolder $base
        $frames = Join-Path $out 'Frames'
        $candidates = Join-Path $out 'CandidateFrames'
        $ocr = Join-Path $out 'OCR'
        $scripts = Join-Path $out 'Scripts'
        New-Item -ItemType Directory -Force -Path $frames,$candidates,$ocr,$scripts | Out-Null

        Write-Host "[$index/$($videos.Count)] $($video.Name)" -ForegroundColor Cyan
        $pattern = Join-Path $frames 'frame_%06d.jpg'
        $vfFilter = "fps=1/$IntervalSeconds"
        try {
            & ffmpeg -hide_banner -loglevel quiet -i "$($video.FullName)" -vf $vfFilter -q:v 2 -y "$pattern" 2>$null
        } catch { }

        $frameFiles = @(Get-ChildItem -LiteralPath $frames -Filter '*.jpg' -File | Sort-Object Name)
        $candidateCount = 0
        $all = New-Object System.Text.StringBuilder

        foreach ($frame in $frameFiles) {
            $txtFile = Join-Path $ocr ($frame.BaseName + '.txt')
            try {
                & tesseract "$($frame.FullName)" stdout --psm 6 -l eng 2>$null | Set-Content -LiteralPath $txtFile -Encoding UTF8
            } catch { continue }

            if (-not (Test-Path -LiteralPath $txtFile)) { continue }
            $text = Get-Content -LiteralPath $txtFile -Raw -ErrorAction SilentlyContinue
            if ([string]::IsNullOrWhiteSpace($text)) { continue }

            $score = 0
            $patterns = @(
                '(?m)\busing\s+(UnityEngine|UnityEditor|System)\b',
                '(?m)\b(public|private|protected|internal)\s+(class|struct|enum|void|float|int|string|bool)\b',
                '(?m)\b(MonoBehaviour|GameObject|Transform|SerializeField|GetComponent|Instantiate|Destroy|Debug\.Log)\b',
                '(?m)\b(if|else|for|foreach|while|switch|return|new)\b',
                '(?m)[\{\}\(\)\;\=]',
                '(?m)\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^;]+;'
            )
            foreach ($p in $patterns) { if ($text -match $p) { $score++ } }

            if ($score -ge 2) {
                $candidateCount++
                Copy-Item $frame.FullName (Join-Path $candidates $frame.Name) -Force
                [void]$all.AppendLine("`r`n===== $($frame.Name) =====`r`n$text")
            }
        }

        $allPath = Join-Path $out 'ALL_CANDIDATE_CODE.txt'
        $all.ToString() | Set-Content -LiteralPath $allPath -Encoding UTF8

        # Conservative candidate .cs. OCR errors are expected and explicitly marked.
        $codeLines = New-Object System.Collections.Generic.List[string]
        foreach ($line in ($all.ToString() -split "`r?`n")) {
            $t = $line.TrimEnd()
            if ($t -match '^=====') { [void]$codeLines.Add('// ' + $t); continue }
            if ([string]::IsNullOrWhiteSpace($t)) { continue }
            if (($t -match '\b(using|namespace|class|struct|enum|public|private|protected|internal|void|float|int|string|bool|if|else|for|foreach|while|return|new)\b') -or
                ($t -match '[\{\}\(\)\;\=]') -or ($t -match '\b(UnityEngine|MonoBehaviour|GameObject|Transform|Debug|SerializeField)\b')) {
                [void]$codeLines.Add($t)
            }
        }

        $header = @"
// ============================================================
// AUTO-EXTRACTED FROM UNITY VIDEO
// Video: $($video.Name)
// Generated: $(Get-Date)
// WARNING: OCR candidate. REVIEW BEFORE COMPILING.
// ============================================================

"@
        ($header + ($codeLines -join "`r`n")) | Set-Content -LiteralPath (Join-Path $scripts 'Extracted_Candidate.cs') -Encoding UTF8

        @"
UNITY C# OCR REPORT
===================
Video: $($video.FullName)
Sampling interval: $IntervalSeconds seconds
Frames extracted: $($frameFiles.Count)
Candidate code frames: $candidateCount
Output: $out

Files:
  ALL_CANDIDATE_CODE.txt
  Scripts\Extracted_Candidate.cs
  CandidateFrames\
  OCR\

WARNING: OCR can confuse ; : . , { } ( ) _ and identifiers. Review the result before use.
"@ | Set-Content -LiteralPath (Join-Path $out 'REPORT.txt') -Encoding UTF8

        $master.Add([pscustomobject]@{ Video=$video.Name; Frames=$frameFiles.Count; CandidateFrames=$candidateCount; Output=$out })
        Write-Host "  Frames: $($frameFiles.Count) | Candidate code frames: $candidateCount" -ForegroundColor Green
    }

    $master | Export-Csv (Join-Path $OutputFolder 'MASTER_REPORT.csv') -NoTypeInformation -Encoding UTF8
    @"
UNITY LOCAL C# EXTRACTION
=========================
Input: $InputFolder
Output: $OutputFolder
Sampling interval: $IntervalSeconds seconds

Each video folder contains:
- ALL_CANDIDATE_CODE.txt
- Scripts\Extracted_Candidate.cs
- CandidateFrames\
- OCR\
- REPORT.txt

OCR is an extraction aid, not a source-code recovery guarantee.
"@ | Set-Content (Join-Path $OutputFolder 'README.txt') -Encoding UTF8

    Write-Host "`nAll videos processed successfully." -ForegroundColor Green
    Write-Host "Output: $OutputFolder" -ForegroundColor White
}
catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
