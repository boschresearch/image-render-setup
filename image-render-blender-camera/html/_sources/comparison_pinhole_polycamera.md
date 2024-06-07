<!--
# File: /comparison_pinhole_polycamera.md
# Created Date: Monday, December 13th 2021
# Author: Peter Seitz
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Blender Camera add-on module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
###
-->

# Comparison of cameras modeled with the pinhole / poly camera model

*Author: Peter Seitz*

The assumption is, that while more generic, the poly camera model should be able to reproduce the pinhole camera model.
The comparison is done on a lens/image combination modeled after the Sony IMX252 imager and the Schneider-Kreuznach Cingeon 16mm f=1.8 lens.
The parameters are set based on the values in the datasheet of the [lens](https://schneiderkreuznach.com/application/files/1915/4114/9084/1001482_Cinegon_1-8_16.pdf) and the [sensor](https://www.sony-semicon.co.jp/products/common/pdf/IMX250_252_Flyer.pdf) .

## Geometry

### Pinhole

The pinhole camera is characterized by the opening angle for the imager/lens combination.
Evaluating this for the width of the sensor (pixel number times size: $2064 px \times 3.45\mu m = 7.1208 mm$) and the focal length $f = 16.43mm$, the field of view is given by $\Theta = 2 \times atan(sensorwidth / (2 \times f)) = 24.4540 \degree$

The corresponding pinhole camera definition looks like:

    {
        "sDTI": "/anycam/db/project/pinhole:1.0",
        "sId": "${filebasename}",
        "lFov_deg": [24.4540, 0]
    }

### Poly Camera

`fNormLength_mm` is set to the width of the sensor given by the pixel number times size: $2064 px \times 3.45\mu m = 7.1208 mm$.

The optical center is set to [0,0].  

The polynomial coefficients are set to an expansion of `atan(Theta)` :
For an ideal flat-field lens the distance from the optical axis scales with $f \times tan(\Theta)$. Denoting the distance from the optical axis as $r$ we get $r = f \times tan(\Theta)$. Solving for $\Theta$: $\Theta = atan(\frac{r}{f})$. With f the focal length (here f = 16.43 mm).  
To approximate the atan, it's series expansion is used: $atan(x) = x - \frac{x^3}{3} + \frac{x^5}{5} - \frac{x^7}{7} + \frac{x^9}{9} - O(x^{11})$ - even exponents are zero.

As the `SInputType` setting requires normalized coefficients, the coefficients are scaled by sensor_width / focal length: 7.1208 mm / 16.43 mm.  

The complete optics definition is given by:

    {
        "sDTI": "/anycam/db/project/poly/radial:1.0",
        "sId": "${filebasename}",
        "sInputType": "radius/normalized/fixed/mm",
        "sOutputType": "angle/rad",
        "lCoef": [
            0.4334023128423615,
            0.0,
            -0.027136411671025203,
            0.0,
            0.0030583424910446827,
            0.0,
            -0.0004103368612658486,
            0.0,
            5.994852636769042e-05
        ],
        "lCenter_mm": [
            0.0,
            0.0
        ],
        "fNormLength_mm": 7.1208,
        "fMaxAngle_deg": 51.0,
        "_datasheet": "https://schneiderkreuznach.com/application/files/1915/4114/9084/1001482_Cinegon_1-8_16.pdf"
    }

## Results

For the tests a pinhole and a poly camera with the parameters above where created at position (0, 0, 0).
A plane in xy was placed at z = -1m and textured using a checker pattern with a scaling of 50.

Comparison of the lens described by the pinhole model only using the opening angle and the poly model shows only minor differences regarding the area viewed.

The resulting image from the pinhole camera:

<img src="images/SonyIMX252_SchneiderKreuznach16mm_pin_NoVignetting.png" width="500" />

The poly model result:

<img src="images/SonyIMX252_SchneiderKreuznach16mm_poly_Vignetting.png" width="500" />

The refraction plane of the poly camera is placed at z= + sensor_width in this case (refraction plane at z = 0, effective pinhole camera at z= + sensor_width).
Shifting the poly camera assembly by -focal length + sensor_width results in having the same view with poly camera and pinhole camera.

<img src="images/SonyIMX252_SchneiderKreuznach16mm_poly_NoVignetting_z-f+senswidth.png" width="500" />

Resulting in an almost identical difference image where only statistical fluctuations occur at the edges of the checker pattern (only visible in difference image, not shown).

## Conclusion

The implementation of the poly camera creates images almost identical to a pure pinhole camera.  

To compensate for the remaining differences, the position of the poly camera has to be shifted relative to the pinhole camera. More precise by placing the poly camera at $\Delta$ z = - focal_length + sensor_width w.r.t. the pinhole camera compared to the current offset of $\Delta$ z = + sensor_width.

