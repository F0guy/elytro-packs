# Re-sync the boss pack on GitHub with what ElyBosses builds on the server.
# ElyBosses offers players the GitHub copy with the SHA-1 of its OWN build, so the two must match
# byte for byte. Run this after any change to boss models, plugins/ElyBosses/pack/ or BetterModel.
# Usage: .\sync.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$local = Join-Path $PSScriptRoot 'elytro-boss-pack.zip'
$tmp = Join-Path $env:TEMP 'elytro-boss-pack.new.zip'
# The server still builds and serves the pack on its own port (reachable directly, not via Minehut).
curl.exe -s -f -m 120 -o $tmp 'http://p-na-us-01.foliumhosting.net:25678/elytro-pack.zip'
if ($LASTEXITCODE -ne 0) { throw 'Could not download the boss pack from the server.' }
$new = (Get-FileHash $tmp -Algorithm SHA1).Hash.ToLower()
$old = if (Test-Path $local) { (Get-FileHash $local -Algorithm SHA1).Hash.ToLower() } else { '' }
if ($new -eq $old) { Write-Output "Boss pack unchanged ($new)."; Remove-Item $tmp; exit 0 }
Move-Item -Force $tmp $local
git add elytro-boss-pack.zip
git commit -q -m "Sync boss pack ($($new.Substring(0,8)))"
git push -q origin main
Write-Output "Boss pack updated: $old -> $new. Players get it on next join or /bosses pack (GitHub raw can take ~5 min)."
