
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Setup module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
# PowerShell Basics

While PowerShell is the default shell for the current Windows versions, you can also install it on Linux.

## Basic Features

- `$env:[Variable]` references an environment variable.
- `$env:HOME` is the user's home directory.
- Use `~` in a path to reference the user`s home directory (just as in Linux).

## Useful Commands

- `ls` lists the current directory contents
- `(get-command python).Path` gets you the path of the executable referenced by the command `python`.


## User Profile

The variable `$PROFILE` contains the path to the current user's powershell profile file. You can define functions in this file, which are available as commands at the powershell prompt.

For example, if you paste the following script into the file referenced by `$PROFILE.CurrentUserAllHosts`, you can activate the anaconda base configuration from any powershell with the command `conda-act`.

```ps1
function conda-act {
    Write-Output "Activating default Anaconda environment..."
    $condahook = "~\\Anaconda3\\shell\\condabin\\conda-hook.ps1"

    if (!(Test-Path $condahook)) {
        $condahook = "$env:PROGRAMFILES\\Anaconda3\\shell\\condabin\\conda-hook.ps1"
        if (!(Test-Path $condahook)) {
            Write-Output "ERROR: Conda hook script could not be found"
            $condahook = ""
        }
    }

    if ($condahook.length -gt 0) {
        invoke-expression -Command "& '$condahook'"
        conda activate
    } else {
        Write-Output "ERROR: Anaconda environment not activated."
    }
}
```

