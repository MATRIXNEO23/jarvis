$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
try {
    $data = [Console]::In.ReadToEnd() | ConvertFrom-Json
    if ($data.operation -in @('view','navigate')) {
        $shell = New-Object -ComObject Shell.Application
        $windows = @($shell.Windows() | Where-Object {
            [IO.Path]::GetFileName([string]$_.FullName) -ieq 'explorer.exe'
        } | Select-Object -First 50)
        $matches = @($windows | Where-Object { [long]$_.HWND -eq [long]$data.hwnd })
        if ($matches.Count -eq 0 -and $data.operation -eq 'view') { $matches = $windows }
        if ($matches.Count -eq 0) { @{status='none';rows=@()} | ConvertTo-Json -Compress; exit }
        if ($matches.Count -ne 1) { @{status='ambiguous';rows=@()} | ConvertTo-Json -Compress; exit }
        $window = $matches[0]
        $folder = $window.Document.Folder.Self
        if (-not $folder.IsFileSystem -or -not [IO.Path]::IsPathRooted([string]$folder.Path)) { throw 'Not a filesystem folder' }
        if ($data.operation -eq 'navigate') {
            if (-not ($data.target -is [string]) -or $data.target.Length -gt 32767 -or
                -not [IO.Path]::IsPathRooted($data.target) -or $data.target.StartsWith('\\') -or
                -not [IO.Directory]::Exists($data.target) -or
                -not [string]::Equals([string]$folder.Path,[string]$data.source,[StringComparison]::OrdinalIgnoreCase)) { throw 'Folder changed or invalid target' }
            $window.Navigate2([string]$data.target)
            @{status='ok';rows=@()} | ConvertTo-Json -Compress; exit
        }
        $selected = @($window.Document.SelectedItems() | Select-Object -First 20 | ForEach-Object { [string]$_.Path })
        @{status='ok';path=[string]$folder.Path;hwnd=[long]$window.HWND;selected=$selected;rows=@()} | ConvertTo-Json -Compress
        exit
    }
    if ($data.operation -ne 'installed' -or -not ($data.query -is [string]) -or
        $data.query.Length -lt 1 -or $data.query.Length -gt 160) { throw 'Invalid request' }
    $query = $data.query
    $apps = @()
    try { $apps = @(Get-StartApps -ErrorAction Stop) } catch {}
    $rows = [System.Collections.Generic.List[object]]::new()
    foreach ($package in @(Get-AppxPackage -ErrorAction Stop)) {
        $matches = @($apps | Where-Object {
            ([string]$_.AppID).StartsWith(([string]$package.PackageFamilyName + '!'), [StringComparison]::OrdinalIgnoreCase) -and
            ([string]$_.Name).IndexOf($query, [StringComparison]::OrdinalIgnoreCase) -ge 0
        })
        if ($matches.Count -eq 0 -and ([string]$package.Name).IndexOf($query, [StringComparison]::OrdinalIgnoreCase) -lt 0) { continue }
        $name = [string]$package.Name
        if ($matches.Count -gt 0) { $name = [string]$matches[0].Name }
        if ($package.InstallLocation) { $rows.Add(@{path=[string]$package.InstallLocation;name=$name}) }
        if ($rows.Count -ge 50) { break }
    }
    @{status='ok';rows=@($rows.ToArray())} | ConvertTo-Json -Compress
} catch {
    @{status='unavailable';rows=@()} | ConvertTo-Json -Compress
}
