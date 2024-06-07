# Manifest Configuration

From the overview of the Catharsys system, recall that one of the design principles of Catharsys is, to enable the combination of different partial configurations into a set of full configurations. For example, you may want to vary the camera position, the set of objects in the scene, the ego velocity of the camera, etc. Each of these variations has a configuration type associated with it. In the manifest file you declare which configuration *types* you want to vary, and in the trial file you sepecify a set of actual *configurations* for each type. See also the manifest file documentation [here](manifest-file-info). 


| Tag      | Type       | Description                                     | Value Constraints         | Example           |
| -------- | ---------- | ----------------------------------------------- | ------------------------- | ----------------- |
| sDTI     | string     | DTI of manifest file. Must be this value.       | `/catharsys/manifest:1.1` |                   |
| sId      | string     | Id of manifest file.                            |                           | `${filebasename}` |
| mActions | dictionary | Dictionary of actions. See below for more info. |                           |                   |

## Action Definition

The `mActions` dictionary defines the configuration data expected per action. Note that every action specified in the launch configuration can reference a different trial file and each trial file in turn references a manifest. The manifest specifies what configuration data type is to be expected for a given id and the trial file specifies the lists of configurations per id. 

Every action in the `mActions` dictionary must have this form:

```json
    "[action name]": {
        "sDTI": "manifest/action:1",
        "lConfigs": [
            "{config declaration dictionary 1}",
            "{config declaration dictionary 2}",
            "[...]"
        ],
        "lDeps": ["name of action this action depends on"],
    }
```

The elements of the `lConfigs` list must be dictionaries with the following elements:

| Tag        | Type   | Description                                                      | Value Constraints            | Example  |
| ---------- | ------ | ---------------------------------------------------------------- | ---------------------------- | -------- |
| sId        | string | id name used in trial file to specify list of configurations     | no spaces or special symbals | "render" |
| sDTI       | string | the DTI of the configurations used                               |                              |          |
| sForm      | string | configuration data form                                          | `file/json` or `value`       |          |
| bAddToPath | bool   | indicates whether to add the id of the config to the output path | `true` or `false`            |          |
| bEnabled   | bool   | can be used to filter certain combinations of configs            | `true` or `false`            |          |


The `sForm` element defines the form in which the configuration data is presented. This can either be a json file (`file/json`) or a value (`value`) if the values are given directly in the trial file. Note that when the values are passed directly, the DTI value is not checked. However, the action may require certain DTIs to be available. For example, the Blender render action expects there to be a value element with DTI `camera-name:1` to specify the camera, if no camera set configuration file is given.

The `bEnabled` element can be used to filter certain combinations of configurations. This can be done in conjunction with the configuration `id` dictionary (see also [here](config-id-dict)). For example, suppose you have two sets of configurations that are referenced in the manifest and trial files by `a` and `b`, that is, the `sId` given in the manifest for the two configuration types is `a` and `b`, respectively. By default, if there are a number of configuration files defined in the trial file for `a` and `b`, the configuration compiler will generate combined configurations for all possible combinations. If you only want to use combined combinations if the configuration ids (the `sId` elements in each configuration file) are equal, then you can define the `bEnabled` element in the manifest of configuration `b` as: 

```json
    "bEnabled": "$eq{${id:a:cfg-id}, ${id:b:cfg-id}}"
```

Similarly, you can also place the `bEnabled` element in the top level of any configuration file. In this way, you can define a condition per configuration file and not just per configuration file type, as in the manifest.

The `lDeps` element is a list of action names, the current action depends on. That means, that the current configuration set is combined with all the combinations of parent configuration. 

## Example

Here is an example manifest configuration taken from this [example config](https://github.com/boschresearch/image-render-workspace-examples/blob/main/config/vars/test-04/manifest.json5):

```json
{
    "sDTI": "/catharsys/manifest:1.1",
    "sId": "${filebasename}",

    "mActions": {
        "run": {
            "sDTI": "manifest/action:1",
            "lConfigs": [
                { "sId": "render", "sDTI": "blender/render/output-list:1", "sForm": "file/json", "bAddToPath": false },
                { "sId": "cap", "sDTI": "capture/std:1", "sForm": "file/json", "bAddToPath": false },
                { "sId": "cam", "sDTI": "camera-name:1", "sForm": "value" },
                { "sId": "meta", "sDTI": "meta-test:1", "sForm": "file/json" },
                // The type "vars-test:1" is just an arbitrary typename.
                // However, the json file referenced in the trial config must use this DTI.
                { "sId": "vars", "sDTI": "vars-test:1", "sForm": "file/json", "bAddToPath": true },
            ],
            "lDeps": []
        },
    }
}
```
