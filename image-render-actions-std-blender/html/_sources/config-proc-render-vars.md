
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Automation Functions module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
# Configuration File Processing

:::{toctree}
---
maxdepth: 2
caption: Contents
---
:::

## Overview

## Render Variables

During rendering the modifier and generator configuration files are processed again for each new frame. 
The following variables are available. All variables have to be accessed as elements of the dictionary `render`, i.e.
to obtain the active camera name you need to write `${render:active-camera}`.

| Variable               | Description                                   | Type       |
| ---------------------- | --------------------------------------------- | ---------- |
| `target-frame-first`   | The first render target frame (`iFrameFirst`) | int        |
| `target-frame-last`    | The last render target frame (`iFrameLast`)   | int        |
| `target-frame-step`    | The frame step (`iFrameStep`)                 | int        |
| `target-frame`         | The current target frame                      | int        |
| `target-time`          | The current render target time                | float      |
| `target-fps`           | The target render fps                         | float      |
| `scene-fps`            | The fps value set in the scene                | float      |
| `scene-frame`          | The current scene render frame                | int        |
| `active-camera`        | The name of the active camera                 | string     |
| `active-camera-parent` | The name of the active camera's parent object | string     |
| `active-camera-anycam` | The anycam camera meta data dictionary        | dictionary |

