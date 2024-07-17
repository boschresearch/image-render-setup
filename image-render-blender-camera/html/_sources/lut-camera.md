# LUT Camera

In this section the process to define a LUT (Look Up Table) camera is described. A LUT camera uses as look-up table a `RGBA` floating point image, where each pixel defines the direction of a projection ray that passes through the **center** of that pixel. The `(x,y,z)`-coordinates of the ray are stored in the red, green and blue color channels of the image, respectively. The alpha channel of the image is optional. If it is defined, it determines the attenuation of the ray intensity. The value of the alpha channel is multiplied with the ray intensity during ray tracing, such that a value of `1` means no attenuation and a value of `0` means full attenuation (no light passes).

A LUT camera is simulated in Blender by placing a sphere around a standard camera and defining a shader on that sphere that bends the light rays appropriately. However, this construction means, that you cannot use render layers like the depth map and the movement (vector), as they only regard the first plane a ray intersects. Instead, you need to use the `anytruth` supplied methods for depth, optical flow and label. 

## Camera Usage Constraints

It is also imperative that you consider the following points, before using a LUT camera. If this is not possible for your setup, you can automatically approximate a LUT camera with a Blender Polynomial camera. Details are described below.

### Automatic Scene Transformation
You absolutely **must** use the render setting `bTransformSceneToCameraFrame`, which is set in the render settings configuration. For example,
```json
{
    "sDTI": "/catharsys/blender/render/output-list:1",
	"sId": "${filebasename}",

	"lSettings": [
        {
            "sDTI": "/catharsys/blender/render/settings/main:1",
            "bTransformSceneToCameraFrame": true,
        },
    ],

    "lOutputs": [] // define outputs
}
```
See `image-render-workspace-test/config/anycam/test-01/render/image_v1.json5` for a full example.

This setting transforms the whole scene before rendering, so that the active camera is at the origin and the camera axis align with the world axes. This is needed due to the single floating points precision used by Blender internally.

### Ground Truth Rendering

For the ground truth rendering to work, all materials are replaces with shaders that use an emission shader to generate an appropriate color for the information to be rendered. For Blender each object is therefore a light source and the preparation of the scene can take a long time, or the GPU memory may get exhausted. If that happens, you need to reduce the complexity of your scene. 

## LUT image specification

The LUT image has to be generated to the following specifications:

1. The LUT image must be stored as `RBG` or `RGBA` OpenEXR file, where each color channel is a 32-bit floating point value.
2. The camera coordinate system is assumed to be a Blender coordinate system, i.e. `x`-axis to the right, `y`-axis to the top and `z`-axis points behind the camera. That is, the optical axis goes along the *negative* `z`-axis. The vectors stored in the LUT image are specified in the same coordinate system.
3. The `RGB`-channels of a pixel contain the `(x,y,z)`-coordinates of the projection ray that passes through the **center** of that pixel. Ray directions may also point to positive `z`-directions. However, the ray-directions must vary smoothly for the camera to work. The ray directions should also be normalized to unit length. 
4. The optional alpha channel is multiplied with that ray intensity during rendering. In this way, you can simulate the vignetting of the optical system.
5. The LUT image may be super-sampled. That is, you can generate an integer amount of LUT pixels along each axis, for each image pixel. In the camera configuration file, you need to specify the super-sampling with the parameter `iLutSuperSampling`. By default this value is `1`, which means that there is one LUT pixel per image pixel. If there are `N` by `N` LUT pixels per image pixel, set this parameter to `N`.
6. The LUT image may have a border of LUT pixels that are outside the image. This can be useful to improve the render quality at the image edges. If there is one additional row (column) of LUT pixels, you need to set the parameter `iLutBorderPixel` to `1`. 
7. By default, it is assumed that the camera's optical axis passes through the center of the LUT. If this is not the case, you need to specify the position on the LUT image, where the optical axis passes through. For example, suppose the LUT image has size `6x5` pixel with no super-sampling and no border. Then the default principle point coordinates of the LUT are `2.5` for the column and `2` for the row. This is becuase the coordinates are relative to the pixel center. The column origin is at the left and the row origin at the top. This center position does not change if there are border pixels or super-sampling. The center position coordinates are set with the parameters `fLutCenterRow` and `fLutCenterCol`. 

A LUT projection config has for example the following form:
```json
{
    "sDTI": "/anycam/db/project/lut/std:1.0",

    "sId": "$filebasename",

	"sLutFile": "fisheye-200deg-v1.exr",   
    "iLutBorderPixel": 1,
    "iLutSuperSampling": 1,
    "fLutCenterRow": 500.5,
    "fLutCenterCol": 500.0,
}
```
If the parameter `sLutFile` contains a relative path to an `.exr` file, it is assumed to be relative to the project config JSON file. 

The example `anycam` camera database contains two LUT camera examples. You can either install the camera database with `cathy install asset cameras` or cloning the `image-render-asset-cameras` module.

## Approximating a LUT Camera

You can approximate a LUT camera with a native Blender polynomial fisheye camera. Simply use a projection configuration of the following type:

```json
{
    "sDTI": "/anycam/db/project/pano/poly:1.0",
    "sId": "${filebasename}",

    // relative path to lut config, from which 
    // polynomial is estimated.
    "sLutConfigFile": "../lut/test-fisheye-200deg-v1",

    // You can optionally set the maximal viewing FoV explicitly.
    // fFovMax_deg: 100.0,

}
```

You can find the example file under `image-render-asset-cameras/pano/poly-lut-fisheye-200deg.json5`. The corresponding camera configuration is `image-render-asset-cameras/camera/pano_poly_lut_fisheye_SDTV.json5`.
