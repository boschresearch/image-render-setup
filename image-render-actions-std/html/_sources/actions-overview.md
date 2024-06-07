
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Standard Actions module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
# Standard Actions Overview

In the following tables the *Action DTI* is the action identifier that has to be used in the launch configuration to reference an action.

## Blender Rendering Actions

These actions run within a Blender context.

:::{include} ../../../image-render-actions-std-blender/docs/source/actions-list.md
:::


## Render Post-Processing

These actions only start a Python job to process.

**Construct depth ground truth**
:DTI: `/catharsys/action/std/blender/post-render/proc-depth:1.0`
:Description: Uses the rendered 3D-position images to generate depth maps. 

---

**Construct label ground truth**
:DTI: `/catharsys/action/std/blender/post-render/proc-label:1.0`
:Description: Uses the rendered raw label images and JSONs to generate the final label images with previews

---

**Construct Rolling Shutter**
:DTI: `/catharsys/action/std/blender/post-render/proc-rs:1.0`
:Description: Uses the separate rolling shutter exposure renders to create the final frame with (possibly) motion blur

---

**Tonemapping**
:DTI: `/catharsys/action/std/blender/post-render/tonemap:1.0`
:Description: Offers various algorithms for tonemapping of raw render images


