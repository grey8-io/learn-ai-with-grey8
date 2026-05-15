<#
.SYNOPSIS
    Build HTML and PDF exports for the Marp pitch decks in pitch/.

.DESCRIPTION
    Marp CLI does not render Mermaid diagrams natively. This script:
      1. Ensures @mermaid-js/mermaid-cli (mmdc) and @marp-team/marp-cli (marp) are installed globally.
      2. Extracts each Mermaid code block from each deck source.
      3. Renders each block to a standalone SVG via mmdc.
      4. Substitutes the code block with an image reference to the rendered SVG.
      5. Runs marp on the processed file to produce HTML and PDF.

    Outputs land in pitch/build/ and are gitignored.

.NOTES
    On Windows the script explicitly invokes .cmd shims (npm.cmd, mmdc.cmd, marp.cmd)
    because Node.js's npm.ps1 wrapper has known argument-parsing issues on PowerShell 5.1.

    First run installs mermaid-cli and marp-cli globally and downloads Puppeteer's
    Chromium (~150 MB). Subsequent runs reuse both.
#>

$ErrorActionPreference = "Stop"

function Resolve-CmdShim {
    param([string]$Name)
    $found = Get-Command "$Name.cmd" -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
    return $null
}

# Locate npm.cmd (avoid Node.js's broken npm.ps1 wrapper)
$npmCmd = Resolve-CmdShim "npm"
if (-not $npmCmd) {
    $npmCmd = "C:\Program Files\nodejs\npm.cmd"
}
if (-not (Test-Path $npmCmd)) {
    throw "Cannot locate npm.cmd. Is Node.js installed?"
}

function Ensure-NpmTool {
    param([string]$ShimName, [string]$Package)
    $existing = Resolve-CmdShim $ShimName
    if ($existing) { return $existing }
    Write-Host "Installing $Package globally (one-time)..." -ForegroundColor Yellow
    # Pipe npm output to Out-Host so it displays but does NOT pollute the function's return stream
    & $script:npmCmd install -g $Package | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "Failed to install $Package" }
    $resolved = Resolve-CmdShim $ShimName
    if (-not $resolved) { throw "$ShimName.cmd not found after installing $Package" }
    return $resolved
}

$mmdcCmd = Ensure-NpmTool -ShimName "mmdc" -Package "@mermaid-js/mermaid-cli"
$marpCmd = Ensure-NpmTool -ShimName "marp" -Package "@marp-team/marp-cli"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pitchDir = Join-Path $repoRoot "pitch"
$buildDir = Join-Path $pitchDir "build"

if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}

$decks = @("university-deck", "enterprise-deck")

foreach ($name in $decks) {
    Write-Host ""
    Write-Host "==> Building $name" -ForegroundColor Cyan

    $src = Join-Path $pitchDir "$name.md"
    if (-not (Test-Path $src)) {
        Write-Warning "missing: $src"
        continue
    }

    $content = Get-Content -Path $src -Raw

    $mermaidRegex = [regex]::new('(?ms)```mermaid\r?\n(.*?)\r?\n```')
    $matches = $mermaidRegex.Matches($content)

    Write-Host "    found $($matches.Count) mermaid diagram(s)" -ForegroundColor DarkGray

    $diagramIdx = 0
    foreach ($match in $matches) {
        $mmd = $match.Groups[1].Value
        $mmdFile = Join-Path $buildDir "$name.diagram.$diagramIdx.mmd"
        $svgFile = Join-Path $buildDir "$name.diagram.$diagramIdx.svg"

        Set-Content -Path $mmdFile -Value $mmd -Encoding utf8

        Write-Host "    rendering diagram $diagramIdx -> SVG..." -ForegroundColor DarkGray
        & $mmdcCmd -i $mmdFile -o $svgFile -b transparent
        if ($LASTEXITCODE -ne 0) { throw "mmdc failed for diagram $diagramIdx in $name" }
        $diagramIdx++
    }

    # Substitute each mermaid block with an image reference (one at a time so we can index correctly).
    # The path is relative to the processed file's location (pitch/build/), so just the SVG filename.
    $processed = $content
    $diagramIdx = 0
    while ($mermaidRegex.IsMatch($processed)) {
        $svgRel = "$name.diagram.$diagramIdx.svg"
        $processed = $mermaidRegex.Replace($processed, "![architecture]($svgRel)", 1)
        $diagramIdx++
    }

    $processedFile = Join-Path $buildDir "$name.processed.md"
    Set-Content -Path $processedFile -Value $processed -Encoding utf8

    $htmlOut = Join-Path $buildDir "$name.html"
    $pdfOut  = Join-Path $buildDir "$name.pdf"

    Write-Host "    exporting HTML..." -ForegroundColor DarkGray
    & $marpCmd --no-stdin --html --allow-local-files -o $htmlOut $processedFile
    if ($LASTEXITCODE -ne 0) { throw "marp HTML export failed for $name" }

    Write-Host "    exporting PDF..." -ForegroundColor DarkGray
    & $marpCmd --no-stdin --pdf --allow-local-files -o $pdfOut $processedFile
    if ($LASTEXITCODE -ne 0) { throw "marp PDF export failed for $name" }

    Write-Host "    done:" -ForegroundColor Green
    Write-Host "      $htmlOut" -ForegroundColor Green
    Write-Host "      $pdfOut" -ForegroundColor Green
}

Write-Host ""
Write-Host "All decks built. Files are in $buildDir." -ForegroundColor Cyan
Write-Host "Attach the PDFs to a GitHub Release:" -ForegroundColor Cyan
Write-Host "  gh release create pitch-v1 pitch/build/*.pdf --title 'Pitch decks v1' --notes 'Stakeholder decks.'" -ForegroundColor DarkGray
