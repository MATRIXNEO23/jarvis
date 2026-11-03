$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$apps = [Collections.Generic.List[object]]::new()
$warnings = [Collections.Generic.List[string]]::new()
try {
    foreach ($app in @(Get-StartApps -ErrorAction Stop)) {
        $id = [string]$app.AppID
        if (-not $id -or -not $app.Name) { continue }
        $kind = 'shell'
        if ($id.Contains('!')) { $kind = 'store' }
        $apps.Add(@{name=[string]$app.Name;kind=$kind;target=$id})
    }
} catch { $warnings.Add('Menu Start non disponibile: copertura incompleta.') }
try {
    foreach ($package in @(Get-AppxPackage -ErrorAction Stop)) {
        if ($package.IsFramework -or $package.IsResourcePackage) { continue }
        try {
            $manifest=Get-AppxPackageManifest -Package $package.PackageFullName -ErrorAction Stop
            foreach ($application in @($manifest.Package.Applications.Application)) {
                if (-not $application.Id -or -not $application.VisualElements -or
                    $application.VisualElements.AppListEntry -eq 'none') { continue }
                $id=[string]$package.PackageFamilyName+'!'+[string]$application.Id
                $name=[string]$application.VisualElements.DisplayName
                if (-not $name -or $name.StartsWith('ms-resource:')) { $name=[string]$package.Name }
                # Start carries the localized display name when this ID is listed.
                if (@($apps | Where-Object { $_.target -eq $id }).Count -eq 0) {
                    $apps.Add(@{name=$name;kind='store';target=$id})
                }
            }
        } catch { $warnings.Add('Manifest di una app Store non leggibile: copertura incompleta.') }
    }
} catch { $warnings.Add('Pacchetti Store non disponibili: copertura incompleta.') }
try {
    $shell = New-Object -ComObject WScript.Shell
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $pending = [Collections.Generic.Stack[string]]::new()
    foreach ($key in @('Desktop','AllUsersDesktop','StartMenu','AllUsersStartMenu')) {
        $path = [string]$shell.SpecialFolders.Item($key)
        if ($path) { $pending.Push($path) }
    }
    while ($pending.Count) {
        $path=$pending.Pop()
        if (-not $seen.Add($path)) { continue }
        try {
            foreach ($item in @(Get-ChildItem -LiteralPath $path -Force -ErrorAction Stop)) {
                if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                if ($item.PSIsContainer) { $pending.Push($item.FullName); continue }
                if ($item.Extension -ine '.lnk') { continue }
                $link=$shell.CreateShortcut($item.FullName)
                if (-not $link.TargetPath -or -not [IO.File]::Exists($link.TargetPath)) { continue }
                if ([IO.Path]::GetExtension($link.TargetPath) -ine '.exe') { continue }
                $apps.Add(@{name=$item.BaseName;kind='lnk';target=$item.FullName})
            }
        } catch { $warnings.Add('Una cartella dei collegamenti non leggibile: copertura incompleta.') }
    }
} catch { $warnings.Add('Collegamenti Windows non disponibili: copertura incompleta.') }
foreach ($root in @('Registry::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\App Paths',
 'Registry::HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\App Paths',
 'Registry::HKEY_LOCAL_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths')) {
    if (-not (Test-Path -LiteralPath $root)) { continue }
    try {
        foreach ($key in @(Get-ChildItem -LiteralPath $root -ErrorAction Stop)) {
            $target=[Environment]::ExpandEnvironmentVariables([string]$key.GetValue('')).Trim('"')
            if ([IO.Path]::GetExtension($target) -ine '.exe' -or -not [IO.File]::Exists($target)) { continue }
            $name=[IO.Path]::GetFileNameWithoutExtension($target)
            try { $description=[Diagnostics.FileVersionInfo]::GetVersionInfo($target).FileDescription
                  if ($description) { $name=$description } } catch {}
            $apps.Add(@{name=$name;kind='exe';target=$target})
        }
    } catch { $warnings.Add('Registro App Paths non leggibile: copertura incompleta.') }
}
@{apps=@($apps.ToArray());warnings=@($warnings.ToArray() | Select-Object -Unique)} | ConvertTo-Json -Depth 5 -Compress
