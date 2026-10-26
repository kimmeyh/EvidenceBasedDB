# F114: start one cloud session and keep what it printed.
#
# `claude --cloud` creates a session only from an interactive terminal, so `scripts/f114_cloud.py` runs this
# in a console window of its own. Its output is the console, never a pipe, and so cannot be captured as
# output; once claude exits, this reads the console's own screen buffer and writes it to the log, where
# `f114_cloud.py` finds the new session's id.
param([string]$Message, [string]$Model, [string]$Log)

& claude --cloud $Message --model $Model
$code = $LASTEXITCODE
$raw = $Host.UI.RawUI
$width = $raw.BufferSize.Width
$last = $raw.CursorPosition.Y
$rect = New-Object System.Management.Automation.Host.Rectangle 0, 0, ($width - 1), $last
$cells = $raw.GetBufferContents($rect)
$text = [System.Text.StringBuilder]::new()
for ($y = 0; $y -le $last; $y++) {
    for ($x = 0; $x -lt $width; $x++) { [void]$text.Append($cells[$y, $x].Character) }
    [void]$text.AppendLine()
}
"exit $code" | Out-File -FilePath $Log -Encoding utf8
$text.ToString() | Out-File -FilePath $Log -Encoding utf8 -Append
exit $code
