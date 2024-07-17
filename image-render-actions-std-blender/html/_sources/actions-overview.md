
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render standard Blender actions module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
# Standard Blender Actions Overview

In the following tables the *Action DTI* is the action identifier that has to be used in the launch configuration to reference an action.

## Blender Rendering Actions

These actions run within a Blender context.

### Standard rendering

- DTI: `/catharsys/action/std/blender/render/std:1.0`
- Summary: Standard rendering as you would do it in Blender



### Rolling shutter rendering

- DTI: `/catharsys/action/std/blender/render/rs:1.0`
- Summary: For each final frame renders multiple frames in a time resoltion that matches the rolling shutter exposures
- Example: {external+image-render-workspace-examples:doc}`Rolling Shutter Configuration Example <usecase/rolling-shutter>`


### Log output

- DTI: `/catharsys/action/std/blender/render/log:1.0`
- Description: Generates a JSON file containing information about the scene for each frame.
 

