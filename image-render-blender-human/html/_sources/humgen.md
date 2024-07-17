
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Blender Human add-on module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
<!---
	Copyright (c) 2009, 2018 Robert Bosch GmbH and its subsidiaries.
-->
## How to generate a human <a name="generate-anyhumans"></a>
Generation of anyhumans is based on a configuration dictionary (see [configuration](#anyhuman-configuration)).
Since it is cumbersome to specify the whole configuration each time a different anyhuman is needed, there exist several parameter generator functions to help with the process.
These are described below.

It is also possible to overwrite a parameter that has been produced by a generator.

The following carthasys snippit will generate a person using the persona parameter generator. The configuration will be based on the persona 'bob', but the hair lightness will be set in a way that Bobs dark brown hair is replaced by black hair.

```json
{
    "sDTI": "/catharsys/blender/generate/object/hum-gen-3d:1.0",
    "sId": "Bob",
    "xSeed": "1",
    "sMode": "PERSONA",
    "mParamConfig":
    {
        "sPersonaId": "bob"
    },
    "mOverwrite": {
      "hair" : {
        "lightness": 0.0
      }
    },
    "lCollectionHierarchy": ["Persons"],
    "lModifiers":
    [
        // ...
    ]
}
```

### 1. Persona

Predefined settings can be loaded for several available personas. 
They are specified by the .json files in the `./personas/` folder. 
The currently available personas are
- alice
- bob

Example generator snippit for catharsys:

```json
{
    "sDTI": "/catharsys/blender/generate/object/hum-gen-3d:1.0",
    "sId": "Bob",
    "xSeed": "1",
    "sMode": "PERSONA",
    "mParamConfig":
    {
        "sPersonaId": "bob"
    },            
    "lCollectionHierarchy": ["Persons"],
    "lModifiers":
    [
        // ...
    ]
}
```
### 2. Fully Random:

For domain randomization, it is reasonable to create completely random anyhumans. The parameters of the human will be varied over the whole range of valid values, resulting sometimes in funny and questionable configurations. However, even if these anyhumans probably will not have a correspondace in reality, it is expected that this is benefitial for AI training.

```json
{
    "sDTI": "/catharsys/blender/generate/object/hum-gen-3d:1.0",
    "sId": "Armature.001",
    "xSeed": "1",
    "sMode": "RANDOM_FULL",
    "mParamConfig":
    {
        "gender": "female", // optional
        "additional_clothes_to_ignore": [...] // list of str, optional
    },            
    "lCollectionHierarchy": ["Persons"],
    "lModifiers":
    [
        // ...
    ]
}
```
### 3. Realistic Random:

Similar to fully random parameter generation. However, the parameters are to be expected in a more realistic range and the generated humans are supposed to be believable. 
```json
{
    "sDTI": "/catharsys/blender/generate/object/hum-gen-3d:1.0",
    "sId": "Armature.001",
    "xSeed": "1",
    "sMode": "RANDOM_REALISTIC",
    "mParamConfig":
    {
        "gender": "male", // optional
        "additional_clothes_to_ignore": [...] // list of str, optional
    },            
    "lCollectionHierarchy": ["Persons"],
    "lModifiers":
    [
        // ...
    ]
}
```

### 3. Zwicky Box:

**REMARK: NOT FULLY IMPLEMENTED YET**

Using this setting, it is easily possible to specify an anyhuman by means of a Zwicky box.
The current implementation of has the following dimensions:


| dimension | values |
|-----------|--------|
| gender    |  male, female      |
| age       |  young, adult, senior |
| type      |  asian, black, caucasian      |
| bodytype  |  thin, athletic, average, corpulent, obese |
| bodyheight    |  short, average, tall      |
| skin_tone |  dark, average, bright |
| hair_legnth      |  bald, short, average, long |
| hair_color | black, dark, average, light |
| eye_color | blue, green, brown |
| clothing | casual, business |
| clothing_color | mixed, bright, dark |

For the generation, indiviual dimensions can be specified or ommitted.
If ommitted, they will be choosen randomly from the available values. For each of the values,
the resulting configuration will be drawn from a normal distribution around representive values.

The following will generate an average sized caucasian male with short hair (all other dimensions are randomized):

```json
{
    "sDTI": "/catharsys/blender/generate/object/hum-gen-3d:1.0",
    "sId": "Charlie",
    "xSeed": "1",
    "sMode": "ZWICKY",
    "mParamConfig":
    {
        "gender": "male",
        "type": "caucasian",
        "bodyheight": "average",
        "hair_length": "short"
    },            
    "lCollectionHierarchy": ["Persons"],
    "lModifiers":
    [
        // ...
    ]
}
```

### 5. File:

**REMARK: NOT IMPLEMENTED YET**

Also, anyhuman configurations can be loaded from a json file:

```json
{
    "sDTI": "/catharsys/blender/generate/object/hum-gen-3d:1.0",
    "sId": "Dave",
    "xSeed": "1",
    "sMode": "FILE",
    "mParamConfig":
    {
        "filepath": "./personas/dave.json"
    },            
    "lCollectionHierarchy": ["Persons"],
    "lModifiers":
    [
        // ...
    ]
}
```
## Anyhuman configuration  <a name="anyhuman-configuration"></a>

```json
{
    "gender": "male", // "male" or "female"
    "body": "Caucasian 1.json", // from the list of available body types
    "muscular": 0.1, // [0, 1]
    "overweight": 0.1,  // [0, 1]
    "skinny": 0.1,  // [0, 1]
    "height": 177.6, // height in cm
    "face": XXX, // specification of the face, see below
    "skin": XXX, // see below
    "eyes": XXX, // see below
    "hair": XXX, // see below
    "beard": XXX, // see below
    "outfit": XXX, // see below
    "footwear": XXX, // see below
    "expression": "\\expressions\\Base Shapekeys\\Smile.txt", // from the file of available expresions
    "posefilename": null // from the file of available poses
}
```

### Specifying the body of the human

if "gender" is "male", "body" can be one of the following list:
```json
    "Asian 1.json"
    // ..
    "Asian 8.json"

    "Caucasian 1.json"
    // ..
    "Caucasian 5.json"
    "Black 1.json"
    // ..
    "Black 5.json"
    "Hispanic 1.json"
```

if "gender" is "female", "body" can be one of the following list:
```json
    "Asian 1.json"
    // ..
    "Asian 7.json"

    "Caucasian 1.json"
    // ..
    "Caucasian 5.json"
    "Black 1.json"
    // ..
    "Black 5.json"
    "Hispanic.json"
```


### Specifying the face of the human
The face of the human can be described by various means.

1. Completely random:
```json
{
    "face": "random" // completeley random face
}
```
2. use one of the available variations
```json
{
    "face": "variation_7" // completeley random face
}
```

"face" can be one of the following list:
```json
    "asian",
    "black",
    "caucasion",
    "variation_1",
    // ..
    "variation_11"
```

3. full specification (not implement yet)

### Specifying the hair and beard

"hair_style" for female anyhumans can be on of this list:
```json
Afro Dreads
Afro
Curls High Top Fade
Curly Afro
Dreadlocks
Bob Bangs
Bob Long
Bob Short
Bun Bangs
Bun
Medium Center Part
Medium Side Part
Ponytail Short
Ponytail
Undercut
Wavy Bob Bangs
Bowl
Combed Stylized
Flat top
Mohawk
Pixie Messy
Pixie
Slicked Back Side Part
Slicked Back
Spiked Up
Buzzcut Curly Fade
Buzzcut Fade
Short Combed
Short Curly Fade
Short Side Part
```

"hair_style" for male anyhumans can be on of this list:
```json
Afro Dreads
Afro
Curls High Top Fade
Curly Afro
Dreadlocks
Bob Long
Bun
Medium Center Part
Medium Side Part
Ponytail Short
Ponytail
Undercut
Wavy Bob Bangs
Bowl
Combed Stylized
Flat top
Mohawk
Pixie Messy
Pixie
Slicked Back Side Part
Slicked Back
Spiked Up
Buzzcut Curly Fade
Buzzcut Fade
Short Combed
Short Curly Fade
Short Side Part
```

"beard_style" can be one of the following:
```json
Full_Beard_1
Goatee
Groomed_Beard_1
Handlebar_Mustache
Large_Mustache_[Full]
Large_Mustache_[Short]
Stubble_Mustache_1
Stubble_Long
Stubble_Short
```

### Specifying the outfit

```json
"outfit": {
    "outfit_style": XXX,
    "outfit_pattern": XXX,
    "outfit_color_value_modifier": XXX,
    "outfit_brightness": XXX,
    "outfit_saturation": XXX,
    "outfit_contrast": XXX,
},
```

"outfit_style" can be either "random" or from the list:
```json
// female outfit styles
Casual/Skinny_Look
Casual/Smart_Casual
Casual/Stylish_Casual
Casual/Weekend_Warrior
Office/New_Intern
Office/Open_Suit
Office/Pantsuit
Office/Relaxed_Dresscode
Office/Stock_Exchange
Office/Summer_Lawyer
Summer/BBQ_Barbara
Summer/Beach_Day
Summer/Office_Excursion
Winter/Frosty_Evening
Extra Outfits Pack/CEO
Extra Outfits Pack/Dress
Extra Outfits Pack/Flight Suit
Extra Outfits Pack/Kimono
Extra Outfits Pack/Lab Tech
Extra Outfits Pack/Pirate
Extra Outfits Pack/Presentation
Extra Outfits Pack/Springtime
Extra Outfits Pack/Tip Top

// male outfit styles
Casual/Casual_Weekday
Casual/Relaxed_Office
Casual/Skinny_Look
Casual/Smart_Casual
Casual/Stylish_Casual
Casual/Weekend_Warrior
Office/New_Intern
Office/Open_Suit
Office/Relaxed_Dresscode
Office/Stock_Exchange
Office/Suit_N_Tie
Office/Summer_Lawyer
Summer/BBQ_Barry
Summer/Beach_Day
Summer/Office_Excursion
Winter/Frosty_Evening
Extra Outfits Pack/Bomber look
Extra Outfits Pack/Flight Suit
Extra Outfits Pack/Golf Day
Extra Outfits Pack/Lab Tech
Extra Outfits Pack/On the road
Extra Outfits Pack/Pirate
Extra Outfits Pack/Relaxed Fit
```

To pattern and color the output, use either a constant value, a list, or a dictionary for the remaining outfit values.
Using a constant value, the provided value will be applied to all clothing items.
Using a list, the values in the list will be appliedt to clothing items in a consecutive manner.
Using a dictionary, the keys will be used for lookup of the items to apply to.

Example:

```json
"outfit": {
    "outfit_style": "Casual/Relaxed_Weekday",
    "outfit_pattern": "random",
    "outfit_color": {
      "TSHIRT": "green",
      "Jeans": "gray"
    },
    "outfit_color_value_modifier": {
      "TSHIRT": 1.0,
      "Jeans": 0.5
    },
    "outfit_brightness": [1.0, 0.5, 2.5],
    "outfit_saturation": 1.1,
}
```

### Others
Documentation of other values will be added in the future.
