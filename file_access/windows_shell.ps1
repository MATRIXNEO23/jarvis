$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
try {
    $data = [Console]::In.ReadToEnd() | ConvertFrom-Json
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
