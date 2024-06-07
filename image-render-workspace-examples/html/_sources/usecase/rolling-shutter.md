
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
# Rolling-Shutter Rendering

Rolling shutter is a technique used in digital cameras and smartphones to capture images. Instead of capturing the entire frame at once, a rolling shutter captures the image by scanning the frame line by line. This scanning process starts from the top of the frame and moves down to the bottom.

As the scanning progresses, each line of the image is captured at a slightly different time. This can result in a distortion effect known as the rolling shutter effect. The rolling shutter effect is most noticeable when capturing fast-moving objects or when the camera itself is in motion.

The goal of the rolling shutter rendering action is to simulate a real rolling shutter as closely as possible. This is done by rendering a large number of sub-exposures at small time steps, which are combined into a final image in a post-processing step. 

For example, here are some of the partial exposures. You can see that while different parts of the scene are rendered, time advances and the cube rotates on.

| Separate Exposures |
|-------|
| ![Image 1](images/rs_raw_5.jpg) |
| ![Image 2](images/rs_raw_4.jpg) |
| ![Image 3](images/rs_raw_3.jpg) |
| ![Image 4](images/rs_raw_2.jpg) |
| ![Image 5](images/rs_raw_1.jpg) |

The post-processing step then combines these partial exposures to a final image, which clearly shows the typical rolling shutter effects. The cube appears twisted because its' top part was exposed earlier than its' bottom part.

<img src="images/rs_combined_raw.jpg">

The separate exposures are stored as raw images without any color space mapping. Therefore, the constructed image is also a HDR image. This HDR image can then be tone mapped with yet another post processing action.

Note that you can also generate constructed images with various rolling shutter exposures from the same single exposures, as long as the exposure is shorter or equal to the exposure used for the inital rendering. You can also simulate a sensor that generates HDR images by performing consecutive exposures with different exposure times.

```{note}
Note that Blender also has a rolling shutter rendering setting with a single parameter that uses the known movement of objects to approximate a rolling shutter effect for Blender native cameras. This method will not give correct results at depth edges or for varying reflections, but it is much faster.
```

An example [rolling-shutter rendering configuration](https://github.com/boschresearch/image-render-workspace-examples/tree/main/config/usecase/rolling-shutter) can be found in the module [image-render-workspace-examples](https://github.com/boschresearch/image-render-workspace-examples/tree/main). This configuration will be referenced in the following description.

## Scene Preparation

