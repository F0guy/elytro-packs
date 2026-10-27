# Rebuild and publish the single Elytro pack (boss pack + emoji pack) after ANY pack change:
# new/changed boss models (BetterModel), files under plugins/ElyBosses/pack/, or the emoji pack
# (ElyEmojis pack-site/elytro-emojis.zip). Players get it from GitHub raw; ElyEmojis sends it.
# Steps: fetch sources -> build_merged.py -> push if changed -> wait for GitHub to serve it ->
# put the new SHA-1 in plugins/ElyEmojis/config.yml -> /emojis reload (re-sends to everyone online).
# Usage: .\rebuild.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$root = Split-Path $PSScriptRoot -Parent
$src = Join-Path $PSScriptRoot 'src'
New-Item -ItemType Directory -Force $src | Out-Null
if (Test-Path "$src/pack") { Remove-Item -Recurse -Force "$src/pack" }
$s = $src.Replace('\', '/')
& "$root\sftp.ps1" "get plugins/BetterModel/build.zip $s/build.zip" "get -r plugins/ElyBosses/pack $s/" | Out-Null
Copy-Item -Force "$env:USERPROFILE\Downloads\transfer stuff\TqsksFishingMacro_v11\ElyEmojis\pack-site\elytro-emojis.zip" "$src\emojis.zip"

$old = if (Test-Path elytro-pack.zip) { (Get-FileHash elytro-pack.zip -Algorithm SHA1).Hash.ToLower() } else { '' }
python -I build_merged.py
if ($LASTEXITCODE -ne 0) { throw 'build_merged.py failed' }
$new = (Get-FileHash elytro-pack.zip -Algorithm SHA1).Hash.ToLower()
if ($new -ne $old) {
    git add elytro-pack.zip
    git commit -q -m "Rebuild Elytro pack ($($new.Substring(0,8)))"
    git push -q origin main
}

# GitHub raw caches for a few minutes: only switch the hash once it serves the new file.
$url = 'https://raw.githubusercontent.com/F0guy/elytro-packs/main/elytro-pack.zip'
$tmp = Join-Path $env:TEMP 'elytro-pack.check.zip'
for ($i = 0; $i -lt 60; $i++) {
    curl.exe -s -f -m 120 -o $tmp $url
    if ($LASTEXITCODE -eq 0 -and (Get-FileHash $tmp -Algorithm SHA1).Hash.ToLower() -eq $new) { break }
    Start-Sleep -Seconds 10
}
if ((Get-FileHash $tmp -Algorithm SHA1).Hash.ToLower() -ne $new) { throw "GitHub still serves an old copy; re-run in a few minutes." }

# Patch only the sha1 line of a fresh copy of the ElyEmojis config (other sessions edit it too).
$cfg = Join-Path $env:TEMP 'elyemojis-config.yml'
& "$root\sftp.ps1" "get plugins/ElyEmojis/config.yml $($cfg.Replace('\','/'))" | Out-Null
$bytes = [IO.File]::ReadAllBytes($cfg); $text = [Text.Encoding]::UTF8.GetString($bytes)
$m = [regex]::Match($text, '(?m)^  sha1: "([0-9a-f]{40})"')
if (-not $m.Success) { throw 'No pack.sha1 line in the ElyEmojis config.' }
if ($m.Groups[1].Value -eq $new) { Write-Output "Pack unchanged and live ($new)."; exit 0 }
$text = $text.Substring(0, $m.Groups[1].Index) + $new + $text.Substring($m.Groups[1].Index + 40)
[IO.File]::WriteAllBytes($cfg, [Text.Encoding]::UTF8.GetBytes($text))
& "$root\sftp.ps1" "put $($cfg.Replace('\','/')) plugins/ElyEmojis/config.yml" | Out-Null
& "$root\rcon.ps1" "emojis reload"
Write-Output "Elytro pack live: $old -> $new"
