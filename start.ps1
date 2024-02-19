# Define paths to your programs
$programA = ".\abdada.exe"
$programB = ".\board.py"


# Function to create named pipe
function Create-NamedPipe {
    param(
        [string]$pipeName
    )
    $pipeSecurity = New-Object System.IO.Pipes.PipeSecurity
    $pipeSecurity.AddAccessRule((New-Object System.IO.Pipes.PipeAccessRule("Users", "FullControl", "Allow")))
    $pipe = New-Object System.IO.Pipes.NamedPipeServerStream($pipeName, [System.IO.Pipes.PipeDirection]::InOut, 1, [System.IO.Pipes.PipeTransmissionMode]::Byte, [System.IO.Pipes.PipeOptions]::Asynchronous, 1024, 1024, $pipeSecurity)
    return $pipe
}

# Create named pipes for communication
$pipeA = Create-NamedPipe -pipeName "ProgramAPipe"
$pipeB = Create-NamedPipe -pipeName "ProgramBPipe"

# Start program A with its input coming from pipe B and output going to pipe A
$processA = Start-Process -FilePath $programA -ArgumentList $pipeB, $pipeA -PassThru -NoNewWindow

# Start program B with its input coming from pipe A and output going to pipe B
$processB = Start-Process -FilePath "python" -ArgumentList "$programB", "$pipeA", "$pipeB" -PassThru -NoNewWindow

# Wait for both processes to finish
$processA.WaitForExit()
$processB.WaitForExit()

# Close the named pipes
$pipeA.Dispose()
$pipeB.Dispose()
