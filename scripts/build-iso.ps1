param(
    [string]$Distro = "Debian",
    [string]$Profile = "desktop-virt",
    [string]$WorkDir = "build/live-build"
)

$ErrorActionPreference = "Stop"
$RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Quote-Bash([string]$Value) {
    return "'" + $Value.Replace("'", "'\''") + "'"
}

$RepoPathLinux = (& wsl.exe -d $Distro -- wslpath -a $RepoPath).Trim()
if (-not $RepoPathLinux) {
    throw "Failed to map the repository path into WSL. Make sure distro '$Distro' is installed."
}

$Command = @(
    "set -euo pipefail",
    "cd $(Quote-Bash $RepoPathLinux)",
    "chmod +x scripts/*.sh bootstrap/*.sh",
    "sudo bash scripts/setup-build-deps.sh",
    "sudo bash scripts/build-iso.sh $(Quote-Bash $WorkDir) $(Quote-Bash $Profile)"
) -join "; "

& wsl.exe -d $Distro -- bash -lc $Command
