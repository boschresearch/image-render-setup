
param (
    [string]$target = "",
    [string]$path = "$PSScriptRoot\..\repos"
)

$SphinxBuild = "sphinx-build"
Write-Output "Build: $SphinxBuild"
Write-Output "Target: $target"
Write-Output "Path: $path"


# Look for all paths that have a sphinx documentation setup
$dir = Get-ChildItem -path $path | 
       Where-Object {
           ($_.psIsContainer -eq $true) -and 
           (Test-Path -Path (Join-Path -path $_.FullName -ChildPath "docs/source/conf.py"))
        }

# Loop over all modules with documentation
foreach ($d in $dir) {
    Write-Host "Processing docs for project: $($d.FullName)"
    Invoke-Expression "$SphinxBuild -M $target $($d.FullName)/docs/source build/$($d.Name)"
}

# Build the main documentation
Write-Host "Build main documentation"
Invoke-Expression "$SphinxBuild -M $target source build"

