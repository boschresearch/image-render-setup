
# <LICENSE id="Apache-2.0">
#
#   Image-Render Setup module
#   Copyright 2022 Robert Bosch GmbH and its subsidiaries
#   
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#   
#     http://www.apache.org/licenses/LICENSE-2.0
#   
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# </LICENSE>
param (
    [string]$Command = ""
)

if (Test-Path "~\\.catharsys\\CondaActivateCathUser.ps1") {
    Write-Output "Activating user Catharsys Anaconda environment..."
    invoke-expression -Command "~\\.catharsys\\CondaActivateCathUser.ps1"
} else {
    Write-Output "Activating default Catharsys Anaconda environment..."
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

# if a "-Command" parameter is passed to this script,
# then execute this command here.
# This is needed if this script is used as default shell
# by VSCode to run "shell" tasks.
if (![string]::IsNullOrWhitespace($Command)) {
    Write-Output "Command: $Command"
    Write-Output "Arguments: $args"
    invoke-expression -Command "$Command $args"
    exit
}

