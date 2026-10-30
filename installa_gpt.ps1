# Installa il SOLO SDK locale ufficiale Sign in with ChatGPT per Jarvis.
# Download su richiesta: nessun servizio a pagamento, nessuna API key.
$ErrorActionPreference = 'Stop'
$SdkCommit = '0a36fefeb913055c8c7a1a29b63d82b96b2e841a'
$AppDir = Join-Path $env:LOCALAPPDATA 'Jarvis'
$Runtime = Join-Path $AppDir 'runtime'
$Target = Join-Path $Runtime 'siwc'
$SdkEntry = Join-Path $Target 'packages\local\dist\index.js'

if (-not [Environment]::Is64BitOperatingSystem) {
    throw 'Jarvis GPT richiede Windows a 64 bit.'
}
if (-not (Get-Command node.exe -ErrorAction SilentlyContinue)) {
    throw 'Installa Node.js 22.12 o successivo dal sito ufficiale https://nodejs.org/ e riapri questo installatore.'
}
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw 'npm non disponibile: installa Node.js con npm dal sito ufficiale.'
}
$NodeVersion = (& node.exe --version).TrimStart('v')
if ([version]$NodeVersion -lt [version]'22.12.0') {
    throw "Node.js $NodeVersion troppo vecchio: serve almeno 22.12."
}
if (Test-Path -LiteralPath $SdkEntry) {
    Write-Host 'SDK Sign in with ChatGPT gia installato. Nessuna modifica necessaria.'
    exit 0
}
New-Item -Path $Runtime -ItemType Directory -Force | Out-Null
$TempRoot = Join-Path ([IO.Path]::GetTempPath()) ('jarvis-gpt-' + [guid]::NewGuid().ToString('N'))
$Zip = Join-Path $TempRoot 'sdk.zip'
$Extract = Join-Path $TempRoot 'source'
New-Item -Path $TempRoot -ItemType Directory -Force | Out-Null
try {
    Write-Host 'Scaricamento sorgenti SDK ufficiale OpenAI (versione fissata)...'
    $Uri = 'https://github.com/openai/sign-in-with-chatgpt-devkit/archive/' + $SdkCommit + '.zip'
    Invoke-WebRequest -Uri $Uri -OutFile $Zip -UseBasicParsing
    Expand-Archive -LiteralPath $Zip -DestinationPath $Extract
    $SourceDir = Get-ChildItem -LiteralPath $Extract -Directory | Where-Object {
        Test-Path -LiteralPath (Join-Path $_.FullName 'packages\local\package.json')
    } | Select-Object -First 1
    if ($null -eq $SourceDir) {
        throw 'Archivio SDK inatteso o incompleto.'
    }
    $SourceDir = $SourceDir.FullName
    if (Test-Path -LiteralPath $Target) {
        throw 'Esiste gia una cartella runtime incompleta: cancellala manualmente solo dopo un backup.'
    }
    Move-Item -LiteralPath $SourceDir -Destination $Target
    Push-Location $Target
    try {
        Write-Host 'Installazione delle sole dipendenze del modulo locale...'
        & npm.cmd ci --workspace '@siwc/local' --include-workspace-root --ignore-scripts --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'npm ci non riuscito.' }
        & npm.cmd run build --workspace '@siwc/local'
        if ($LASTEXITCODE -ne 0) { throw 'Compilazione SDK non riuscita.' }
    }
    finally { Pop-Location }
    if (-not (Test-Path -LiteralPath $SdkEntry)) {
        throw 'SDK non compilato: manca packages/local/dist/index.js.'
    }
    Write-Host 'SDK installato in:' $Target
    Write-Host 'Apri Jarvis e scegli Connetti ChatGPT per autorizzare il tuo account.'
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
