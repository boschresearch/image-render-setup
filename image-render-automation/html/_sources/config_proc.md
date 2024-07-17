
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

## File Variables

Whenever a configuration file is processed, a number of varibles are available. For example, when processing the file with absolute path `/home/user/myws/config/anim/test-01/launch.json5`, the variables are defined as follows:

| Variable       | Description                        | Example                                            |
| -------------- | ---------------------------------- | -------------------------------------------------- |
| `filebasename` | The file's basename without suffix | `launch`                                           |
| `filename`     | The filename                       | `launch.json5`                                     |
| `fileext`      | The filename extension             | `.json5`                                           |
| `folder`       | The file's folder name             | `test-01`                                          |
| `parentfolder` | The file's parent folder name      | `anim`                                             |
| `path`         | The path to the file               | `/home/user/myws/config/anim/test-01`              |
| `filepath`     | The full file path                 | `/home/user/myws/config/anim/test-01/launch.json5` |


## Project Variables

Suppose the launch file is in the path ``/home/user/myws/config/anim/test-01/launch.json5``,
and you are executing a render action from the Blender plugin with `iRenderQuality`set to 4.

| Variable                | Description                             | Example                               |
| ----------------------- | --------------------------------------- | ------------------------------------- |
| `path-workspace`        | Main workspace path                     | `/home/user/myws`                     |
| `path-all-configs`      | Main configuration path                 | `/home/user/myws/config`              |
| `path-config`           | The current configuration path          | `/home/user/myws/config/anim/test-01` |
| `path-output`           | The output path                         | `/home/user/myws/_output`             |
| `path-production`       | The main production path                | `/home/user/myws/_render`             |
| `path-actprod`          | The active production path              | `/home/user/myws/_render/rq0004`      |
| `folder-config`         | The current configuration folder        | `test`                                |
| `folder-actprod`        | The top folder of the active production | `rq0004`                              |
| `rel-path-config`       | The relative config path                | `anim/test-01`                        |
| `rel-path-config-child` | The child path of `rel-path-config`     | `test-01`                             |
| `path-render`           | Same as `path-production`               | `/home/user/myws/_render`             |

:::{note}
The variable `path-render` is only available for rendering related actions.
:::

## Configuration Variables

:::{note}
See the configuration `vars/test-01` in the example workspace `image-render-workspace-test` for a demo of using these variables.
:::

| Variable       | Description                                                                             |
| -------------- | --------------------------------------------------------------------------------------- |
| `now`          | The processing data & time in the format `YYYY-MM-DD_HH-MM-SS`                          |
| `trial`        | The contents of the trial configuration file                                            |
| `exec`         | The contents of the execution configuration file                                        |
| `action`       | A dictionary with action information. See below.                                        |
| `rel-path-trg` | The relative target path for this configuration. This may not be the final output path. |
| `path-trg`     | The absolute target path for this configuration.                                        |
| `id`           | A dictionary of all configuration dictionaries, using the trial config id. See below.   |
| `value`        | The currently processed configuration dictionary.                                       |

(var-action)=
### The dictionary `action`

The following variables are members of the `action` dictionary. For example, the variable `name` in the table below, can be accessed via `${action:name}`. As another example, you can access the action parameter `iFrameStart` via `${action:args:iFrameStart}`.

| Variable | Description                                                              |
| -------- | ------------------------------------------------------------------------ |
| `name`   | The action name as specified in the launch file.                         |
| `dti`    | The action dti as specified in the launch file.                          |
| `config` | The action configuration dictionary. These are not the action arguments. |
| `args`   | The action launch arguments.                                             |

(config-id-dict)=
### The dictionary `id`

The following variables are members of the `id` dictionary. The elements of the `id` dictionary are the id names used in the trial file (and declared in the manifest) to specify the configurations. For example, if your trial file specifies the capture configuration to use via the id `cap`, you can access the full capture configuration dictionary via `${id:cap:value}`. The following table gives the elements available per id dictionary element.

| Variable       | Description                                                                                    |
| -------------- | ---------------------------------------------------------------------------------------------- |
| `cfg-id`       | The id string of the configuration.                                                            |
| `rel-path-cfg` | The relative output path for this configuration. This is not necessarily the full output path. |
| `folder`       | The configuration output folder name.                                                          |
| `dti`          | The configuration DTI.                                                                         |
| `value`        | The actual configuration value dictionary.                                                     |
| `parent`       | The configuration defined before this.                                                         |
| `child`        | The configuration defined after this.                                                          |

Instead of accessing the id dictionaries by name, there are three special names:

| Variable  | Description               |
| --------- | ------------------------- |
| `@this`   | The current configuration |
| `@parent` | The parent configuration  |
| `@child`  | The child configuration   |

For example, to access the DTI of the current configuration you can write `${id:@this:dti}`.


