$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$connection = $null
$record = $null
try {
    $inputData = [Console]::In.ReadToEnd() | ConvertFrom-Json
    if ($inputData.query.Length -gt 160 -or $inputData.root.Length -gt 32767) { throw 'Input too long' }
    # Values are SQL literals only; wildcard characters are escaped for LIKE.
    $name = ([string]$inputData.query).Replace("'", "''").Replace('[', '[[]').Replace('%', '[%]').Replace('_', '[_]')
    $scope = ([string]$inputData.root).Replace("'", "''")
    $connection = New-Object -ComObject ADODB.Connection
    $connection.ConnectionTimeout = 3
    $connection.CommandTimeout = 4
    $connection.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
    $sql = "SELECT TOP 50 System.ItemPathDisplay FROM SYSTEMINDEX WHERE SCOPE='file:$scope' AND System.FileName LIKE '%$name%'"
    $record = $connection.Execute($sql)
    $paths = [System.Collections.Generic.List[string]]::new()
    while (-not $record.EOF -and $paths.Count -lt 50) {
        $value = $record.Fields.Item(0).Value
        if ($value -is [string] -and $value.Length -le 32767) { $paths.Add($value) }
        $record.MoveNext()
    }
    @{status='ok';paths=@($paths.ToArray())} | ConvertTo-Json -Compress
} catch {
    @{status='unavailable';paths=@()} | ConvertTo-Json -Compress
} finally {
    if ($null -ne $record) { try { $record.Close() } catch {} }
    if ($null -ne $connection) { try { $connection.Close() } catch {} }
}
