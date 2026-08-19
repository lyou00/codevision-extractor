$env:Path = "$env:Path;C:\Program Files\FormatFactory;d:\Programming\New folder\Mobile Game Development Tutorial 2025\extract_unity_local\tesseract"
$env:TESSDATA_PREFIX = "d:\Programming\New folder\Mobile Game Development Tutorial 2025\extract_unity_local\tesseract\tessdata"

$videoPath = "D:\Programming\New folder\Mobile Game Development Tutorial 2025\26 - Unity Shop System Tutorial Mobile Game Development Full Course GTA Vice City Game Clone(720P_60FPS).mp4"
$inputDir = "d:\Programming\New folder\Mobile Game Development Tutorial 2025\Test_Video_26"

if (-not (Test-Path $inputDir)) {
    New-Item -ItemType Directory -Path $inputDir | Out-Null
}

$targetVideo = Join-Path $inputDir (Split-Path $videoPath -Leaf)
if (-not (Test-Path $targetVideo)) {
    New-Item -ItemType HardLink -Path $targetVideo -Target $videoPath | Out-Null
}

$script = "d:\Programming\New folder\Mobile Game Development Tutorial 2025\extract_unity_local\extract_unity_local.ps1"
& $script -InputFolder $inputDir -IntervalSeconds 3 -SkipInstall
