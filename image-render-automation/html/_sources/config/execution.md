# The Execution Configuration File

The main purpose of the execution file is to specify *how* to execute an action. Typically an action is a python script. The execution file now defines whether this script is executed with a Python process directly, is run inside Blender or is started as a job in a job distribution system like LSF. How a script is executed is determined by the DTI string in the `sDTI` element of the execution file. The currently available execution types are:

- Blender on the local machine: `/catharsys/exec/blender/std:2.1`
- Blender on a LSF system: `/catharsys/exec/blender/lsf:2.1`
- Python process on the local machine: `/catharsys/exec/python/std:2.0`
- Python process on a LSF system: `/catharsys/exec/python/lsf:2.0`

Each of these execution types has their own set of parameters.

## Blender local execution

- `sDTI`: `/catharsys/exec/blender/std:2.1`
- `mBlender`: dictionary with Blender parameters described below.

## Blender LSF execution

- `sDTI`: `/catharsys/exec/blender/lsf:2.1`
- `mBlender`: dictionary with Blender parameters described below.

Additional LSF parameters, which are the same for Blender and Python execution. See below.

## Python local execution

- `sDTI`: `/catharsys/exec/python/std:2.0`
- `mPython`: *optional* dictionary specifying the Python parser to use. This is the same for local and LSF executeion. (see below)

## Python LSF execution

- `sDTI`: `/catharsys/exec/python/lsf:2.0`
- `mPython`: *optional* dictionary specifying the Python parser to use. This is the same for local and LSF executeion. (see below)

Additional LSF parameters, which are the same for Blender and Python execution. See below.

## Blender parameters `mBlender`

The dictionary `mBlender` has the following elements in version 1.0.

- `sDTI`: `/catharsys/blender:1.0`
- `sVersion`: The Blender version to use. Expects string with major and minor version, e.g. `"3.3"`.
- `mSettings`: An *optional* dictionary with DTI `/catharsys/blender/settings:1.0`, defining Blender settings to use.

The `mSettings` dictionary has the following elements.

- `sDTI`: `/catharsys/blender/settings:1.0`
- `lAddOns`: a list of Blender addons to register with Blender
- `mPreferences`: a list of Blender preferences to set

### Specifying AddOns

The `lAddOns` element is a list of dictionaries, where each dictionary describes one Blender addon to use. Each dictionary has at least the following two elements:

- `sName`: The name of the addon
- `sType`: Has to be either `MODULE` or `FOLDER`. If it is `MODULE` the addon must be a module installed in the current Conda environment. If it is `FOLDER` it references an addon installed in some folder on the local machine. 

If the `sType` element is `FOLDER`, the following additional parameters are available.

- `sPath`: The absolute path to the Blender addon.
- `mPreferences`: Am *optional* dictionary of preferences to set for the addon. The key values are the parameter names as used by the addon and the values are the values you want to set. This depends on the actual addon.

:::{note}
Note that Blender addons are simply zip files at the top level. To use an addon in Catharsys, simply unzip it to some folder and reference it in the `lAddOns` list.
:::

### Specifying Preferences

The `mPreferences` dictionary in the `mSettings` dictionary, defines preferences to be set in Blender. The key is the name of the preference in Blender and the value the value you want to set. For example, if you want to enable that zooming in Blender zooms to the mouse pointer, you need to write,

```json
"mPreferences": {
    "inputs": {
        "use_zoom_to_mouse": true,
    }
}
```

