<#
.SYNOPSIS
    Meeting-to-memory automation pipeline for VEGO-AI.

.DESCRIPTION
    Transcribes an MP4 meeting recording using Whisper, extracts metadata,
    generates a meeting notes template, and registers it in resource-memory.md.

.PARAMETER VideoPath
    Path to the MP4 recording (e.g. presentations/video1832857678.mp4).

.PARAMETER ReTranscribe
    If set, forces transcription even if the text transcript file already exists.

.EXAMPLE
    .\scripts\process-meeting.ps1 -VideoPath presentations/video1832857678.mp4
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$VideoPath,
    [switch]$ReTranscribe
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$memoryDir = Join-Path $repoRoot "docs\agent-memory"
$meetingNotesDir = Join-Path $memoryDir "meeting-notes"

# Ensure dirs exist
if (-not (Test-Path -LiteralPath $meetingNotesDir)) {
    New-Item -ItemType Directory -Path $meetingNotesDir | Out-Null
}

$videoAbs = Resolve-Path -LiteralPath $VideoPath
$videoName = [System.IO.Path]::GetFileNameWithoutExtension($videoAbs)
$videoDir = [System.IO.Path]::GetDirectoryName($videoAbs)

$transcriptTxt = Join-Path $videoDir "$videoName`_transcript.txt"
$transcriptSrt = Join-Path $videoDir "$videoName`_transcript.srt"

Write-Host "Processing meeting: $VideoPath"
Write-Host "Expected transcript: $transcriptTxt"

# Step 1: Transcribe if needed
$transcribeScript = Join-Path $repoRoot "presentations\transcribe_hebrew.py"
if (-not (Test-Path -LiteralPath $transcriptTxt) -or $ReTranscribe) {
    if (-not (Test-Path -LiteralPath $transcribeScript)) {
        throw "Transcribe script not found: $transcribeScript"
    }
    Write-Host "Transcript not found or Retranscribe flag set. Invoking Whisper transcription script..."
    
    # Run the transcription python script
    $env:PYTHONIOENCODING = "utf-8"
    & python $transcribeScript $videoAbs
    
    if (-not (Test-Path -LiteralPath $transcriptTxt)) {
        throw "Whisper transcription failed to produce output file."
    }
} else {
    Write-Host "Found existing transcript text file. Skipping transcription."
}

# Step 2: Generate Meeting Notes draft if not exists
$dateStr = (Get-Date).ToString("yyyy-MM-dd")
$notesPath = Join-Path $meetingNotesDir "$dateStr`-$videoName.md"

if (-not (Test-Path -LiteralPath $notesPath)) {
    Write-Host "Generating draft meeting notes at: $notesPath"
    
    $notesTemplate = @"
# Supervisor/Collaborator Meeting - $dateStr

**Source Video:** [$([System.IO.Path]::GetFileName($videoAbs))](file:///$($videoAbs.Replace('\', '/')))
**Transcript Text:** [$([System.IO.Path]::GetFileName($transcriptTxt))](file:///$($transcriptTxt.Replace('\', '/')))
**Transcript SRT:** [$([System.IO.Path]::GetFileName($transcriptSrt))](file:///$($transcriptSrt.Replace('\', '/')))
**Date Processed:** $(Get-Date -Format "yyyy-MM-dd HH:mm zzz")

---

## 1. Meeting Overview
* **Participants:** Iris (Supervisor), Ali, Collaborators
* **Duration:** Unknown
* **Context/Topic:** Discussing project progress, MSc/PhD trajectory, and architectural updates.

## 2. Key Architectural & Research Decisions
* **Decision 1:** [Describe architectural decision]
* **Decision 2:** [Describe research direction decision]

## 3. Feedback & Action Items
* [ ] Action item 1 (Owner: Ali, Priority: High)
* [ ] Action item 2 (Owner: Ali, Priority: Medium)

## 4. Notes & Discussion Points
* Summarize key discussion points from the meeting transcript.

## 5. Quotes of Interest
* Add key verbatim quotes from the transcript if relevant.
"@
    Set-Content -LiteralPath $notesPath -Value $notesTemplate -Encoding UTF8
    Write-Host "Created template meeting notes at $notesPath. Please review and populate decisions."
} else {
    Write-Host "Notes file already exists: $notesPath. Skipping template generation."
}

# Step 3: Register in resource-memory.md
$resourceMemoryPath = Join-Path $memoryDir "resource-memory.md"
if (Test-Path -LiteralPath $resourceMemoryPath) {
    Write-Host "Verifying entry in resource-memory.md..."
    $resourceContent = Get-Content -Raw -LiteralPath $resourceMemoryPath
    
    $relNotes = $notesPath.Replace($repoRoot, "").TrimStart("\").Replace("\", "/")
    $relVideo = $VideoPath.Replace("\", "/")
    $relTxt = $transcriptTxt.Replace($repoRoot, "").TrimStart("\").Replace("\", "/")
    $relSrt = $transcriptSrt.Replace($repoRoot, "").TrimStart("\").Replace("\", "/")
    
    if ($resourceContent -notmatch $videoName) {
        Write-Host "Adding entries to resource-memory.md..."
        # Locate the "## Presentations & Meetings" section to insert
        $targetSection = '## Presentations & Meetings'
        if ($resourceContent -match $targetSection) {
            # Generate a new ID based on existing ones
            $matches = [regex]::Matches($resourceContent, 'PRES-(\d{3})')
            $nextIdNum = 1
            if ($matches.Count -gt 0) {
                $maxId = 0
                foreach ($m in $matches) {
                    $idNum = [int]$m.Groups[1].Value
                    if ($idNum -gt $maxId) { $maxId = $idNum }
                }
                $nextIdNum = $maxId + 1
            }
            $idStr1 = "PRES-" + ($nextIdNum).ToString("D3")
            $idStr2 = "PRES-" + ($nextIdNum + 1).ToString("D3")
            
            # Construct lines to insert
            $newRows = "| $idStr1 | Meeting Video: $videoName | $relVideo | Unprocessed |`r`n| $idStr2 | Meeting Notes: $videoName | $relNotes | Extracted |"
            
            # Find insertion point after the header row of the table
            # We look for the first table after ## Presentations & Meetings
            $pattern = "(?s)(## Presentations & Meetings.*?\|\s*---.*?\|)(.*?)(`r?`n`r?`n)"
            if ($resourceContent -match $pattern) {
                $matchedTable = $Matches[1]
                $matchedRows = $Matches[2].TrimEnd()
                
                $updatedRows = $matchedRows + "`r`n" + $newRows
                $replacement = $matchedTable + "`r`n" + $updatedRows + "`r`n`r`n"
                
                $resourceContent = $resourceContent -replace [regex]::Escape($Matches[0]), $replacement
                Set-Content -LiteralPath $resourceMemoryPath -Value $resourceContent -Encoding UTF8
                Write-Host "Registered new resources $idStr1 and $idStr2 in resource-memory.md."
            }
        }
    } else {
        Write-Host "Resources already indexed in resource-memory.md."
    }
}

# Recompile memory
Write-Host "Recompiling memory..."
$startScript = Join-Path $PSScriptRoot "agent-memory-start.ps1"
& $startScript | Out-Host

Write-Host "Meeting processing complete."
