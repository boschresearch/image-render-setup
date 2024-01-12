# Change Log

## 2023-12-05 Catharsys Release 3.2.33

To update a develop installation to this version, you need to run `cathy install system --update`. This should clone  new repositories and install all modified modules in the Anaconda environment. You may also have to update the Catharsys installation in Blender using `cathy blender init -c [your config]`.

- **Blender**
  - Blender 4 has some breaking changes in its' Python code. The Catharsys code has been adapted to support Blender 3.x and 4.0.
  - Only the Catharsys modules that are needed in Blender are installed to Blender python now. The list of modules that are installed is given in the file `image-render-actions-std-blender/src/catharsys/plugins/std/blender/data/blender-install.json5`. The module names are actually interpreted as regular expressions.

- **Generative AI Action**
  - A generative AI action repository is now added as `image-render-generative`.
  - The [PowerShell script](https://github.com/boschresearch/image-render-generative/blob/main/scripts/get_takuma_diffusers.ps1) to install the code and download the network weights now contains the correct versions of all modules explicitly.
  - The module `image-render-workspace-examples` has an additional example configuration for using the generative rendering.

- **Miscellaneous**
  - The JSON output of the product analysis is now better suited for further processing. The path to the missing artefacts is now given as tuple, where each part is an element of the path structure given in the production definition.
  - You can now install a Blender modifier template module with the command `cathy install template std-modifier-blender`.
  
- **Web GUI**
  - **Much improved GUI with new split window image viewer**. The image viewer is now activated by simply clicking on an image. The image is then shown in a panel to the right of the main view.
  - Improved visualization with less empty spaces around elements. Long label names are now also broken into a number of lines at spaces, underscores and hyphens.
  - **The GUI now supports annotation of the result data** by categorizing the path structure variables defined in the production definition. Documentation for this feature can be found here ([markdown](https://github.com/boschresearch/image-render-automation/tree/main/docs/source/products/categorize.md)|{external+image-render-automation:doc}`docs <products/categorize>`). An example can be found in the [production](https://github.com/boschresearch/image-render-workspace-examples/blob/main/config/usecase/generative/production.json5) JSON file of the `usecase/generative` configuration of the `image-render-workspace-examples` [module](https://github.com/boschresearch/image-render-workspace-examples/tree/main).
  - The module `nicegui` which is used by Catharsys has had a major version change with breaking changes. The Catharsys code has been adopted accordingly. The Catharsys installer of the web gui module now fixes the nicegui version to 1.4.5.

- **Automation**
  - Whole configuration files can now be enabled/disabled with an element `bEnabled` in the manifest declaration as well as at the top level of the configuration file itself. This is an updated version of the `sFilter` element, which is evaluated as Python string. The `bEnabled` element has to evaluate to a `bool`, `integer` or `float`. Value `true` or values other than zero are regarded as `true`. You can, for example, use this element to only enable certain configurations if another specific configuration is active. 

- **Bug Fixes**
  - Import paths were not always set correctly in the ison parser.
  - A relative configuration path was not processed correctly by the commands `cathy prod [...]`.
  - The logging action is now also enabled for the rolling shutter capture configurations.

## 2023-11-20 Catharsys Release 3.2.32

- **Blender Render Action**
  - Important bug fixes for rolling shutter rendering and post processing.

- **Automation**
  - A new nested loop configuration type has been added with id `/catharsys/manifest/control/loop/nested-range:1.0`. It allows you to specify a nested loop of arbitrary depth in a single configuration. See the configuration `config/usecase/loop-nested` of the module `image-render-workspace-examples` for an example.


## 2023-11-15 Catharsys Release 3.2.31

- **Web GUI**
  - This release adds the module `image-render-gui`, which implements a web GUI for launching Catharsys jobs and viewing created products, like images. See the {external+image-render-gui:doc}`Web GUI Documentation <get_started>` for more information.

- **Blender Render Action**
  - The render action now also applies the render output type modifiers after possible annotation modifications have been applied to the scene. This is done with the apply type "POST_ANNOTATION". This can, for example, be used to set materials created for annotation as arguments to geometry node trees.
  - A modifier can now also specify the apply mode "`*`" in `lApplyModes`, to be run for all apply modes.
  - **Rolling Shutter Rendering** is now working again for 3d-position ground truth rendering. The rolling shutter construction action now supports calculating depth with standard deviation from this data.

- **Example Workspace**
  - The module `image-render-workspace-examples` now includes an example of how to render, construct and tonemap rolling shutting images. You can find it under `config/usecase/rolling-shutter`. This also includes a `production.json5` configuration for the Web GUI, to view the generated images.


## 2023-10-10 Catharsys Release 3.2.30

- **Installation**
  - The module `image-render-setup` now also installs `GitPython`
  - The system install command only demands git, when installing from repositories.

- **Internals**
  - Module `image-render-actions-std` no uses the module `cls_python.py` from anybase.

- **ISON Parser**
  - Bug fix, where some variables were not processed due to caching of processed configs.

- **Blender Render Action**
  - Fixes processing of render type dependent modifiers. These were not give all locals and globals
    from their parent configurations and render variable were not available.

- **AnyCam**
  - The anycam addon now allows you to automatically create compact camera pose paths for camera sets. That is, instead of representing the camera pose by a path, a single camera pose name is created. This can improve the usability.



## 2023-10-06 Catharsys Release 3.2.29

- **ISON Language**
  - Bug fix: the function `$rand.generator{}` now generates consistent seeds from string and float values.
  - The node names in the `__platform__` blocks, now allow for wildcards, i.e. '*' for any number of characters
    and '?' for a single character.
  - The parsing speed has been improved by avoiding some deep copies in the code. For example, local variables are now pushed to a stack when entering nested dictionaries, instead of doing a deep copy.
    
- **Configuration Generation**
  - Bug fix: The variable `${path-trg}` and `${rel-path-trg}` are now generated correctly also for configurations that at a lower manifest loop level.
  - The configuration generation has been sped up by improving the parsing speed itself, as well as the processing of manifest based configuration setups.

- **Ground Truth**
  - Optical flow ground truth estimation has been improved.
  - Optical flow output is now black in background areas for LUT cameras and standard Blender cameras.
  - When generating ground truth label with a LUT camera, the LUT file is now stored at the top level production 
    folder and not with the image file. This reduces the amount of storage space needed.
  - User defined label shader are now adapted automatically to using an emission or diffusion shader depending on the camera used. For example, a LUT camera must use emission shaders, while Blender native cameras can use a diffusion shader.

- **Render Actions**
  - adds support for EEVEE settings via configuration file. You can choose the render engine via the render settings config. In the new EEVEE settings config, the render quality etc. can be set. 

- **Post-Processing Actions**
  - New focus blur action, that uses the depth ground truth to generate a depth-of-field effect.
  - New motion blur action, that uses the flow ground truth to generate a motion blur effect.

- **Modifiers**
  - Modifier `blender/generate/collection/import/folder-type-hierarchy:1` 
    - can now also import `.fbx`, `.glb` and `.gltf` files,
    - has new option `bJoinObjectGroups` to optionally join all objects imported from a file into a single object,
    - has new option `lIncludeFileSuffix` to optionally set a list of file types to import. Default is all file types.

- **System**
  - the command `cathy code init` now also sets the flag `git.alwaysSignOff` to always add a `signed-off-by` text to the commit message.
  - the command `cathy repos release` now adds the 'signed-off-by' text in addition to GPG signing commits.
  - the set of paths used to search for the `conda-hook.ps1` script on windows systems is extended to include the local app data path, and Miniconda3 as well as Anaconda3 installs. If nothing works, you can set the path to the Anaconda install with the new environment variable `CATHARSYS_CONDA_PATH`. If this environment variable is set, it is the
  only path the system looks for the conda hook script.


## 2023-06-21 Catharsys Release 3.2.28

- **Documentation**
  - There is now more information on the {external+image-render-automation:doc}`automation system <index>`. In particular, the first part of a tutorial series on how to work with Catharsys has been added.

- **`cathy` commands**
  - The `cathy code init` command now adds a setting to the VS Code workspace that stops VS Code from activating a conda environment, as this has already been done by the shell script generated by the command.

- **Job Execution**
  - New LSF execution configuration parameters `lJobExcludeHosts` and `lJobHosts`. Both expect lists of strings. The later expects host names or host group names.

- **Actions**
  - *Blender render logging action*
    - now supports additional parameter `bLogCameraSet`. If this is set to `false`, the camera set yaml files will not be written.
  - *Standard render action*
    - In the trial file you can now leave out the "sBlenderFile" parameter in the "mBlender" block, or set it to an empty string. In this case, Blender starts up with an empty Blender Scene. The default box, camera and light are automatically deleted. Note, you still need the "mBlender" block as before.
    - You no longer need to specify a camera configuration. If no camera is specified, no camera will be activated and rendering an image will lead to errors. This is mainly used when generating new Blender files.
    - You no longer need to specify a capture configuration for the standard Blender rendering. If no configuration is specified, the render FPS is the same as the scene FPS set in the Blender file.
    - There is a new render output type "none", which does not output anything. This can be useful for configurations that import assets, modify them and export them again as .obj files.

  - *Modifier* *([modifier examples and documentation](https://github.com/boschresearch/image-render-workspace-examples/tree/main/config/modify/modifier))*
    - Apply object transformations, with sDTI: [`/catharsys/blender/modify/object/apply-transforms:1.0`](https://github.com/boschresearch/image-render-workspace-examples/blob/main/config/modify/modifier/object/apply-transforms.json5)
    - Remesh object with voxel remesh and then bake the original object's texture onto the remeshed object: [`/catharsys/blender/modify/object/voxel-remesh-bake-texture:1.0`](https://github.com/boschresearch/image-render-workspace-examples/blob/main/config/modify/modifier/object/voxel-remesh-bake-texture.json5)
    - Export object as OBJ file: [`/catharsys/blender/modify/object/export/obj:1.0`](https://github.com/boschresearch/image-render-workspace-examples/blob/main/config/modify/modifier/object/export-obj.json5)
    - Fixes bug where python scripts were executed twice in evaluation modifier.
    - Adds option `lRotationEuler_deg` to set the rotation in degrees when [importing objects](https://github.com/boschresearch/image-render-workspace-examples/blob/main/config/modify/modifier/generate/import-object.json5).

- **Functional JSON**
  - To avoid inconsistencies in generating random numbers, the new function `$rand.generator{}` has been added, which returns the reference to a random number generator instance. This reference can then be used as first parameter in all `$rand.*{}` functions. See {external+functional-json:doc}`ISON math function documentation <ipy/ison-functions-math>` for more information and examples.

:::{note}
The root of the random number generation problem was, that we typically seeded the global random number generator of the python instance. This can lead to problems, if the seeding is not done before any random number is generated. However, you cannot in general enforce a process order when defining variables in a Functional JSON file. To solve this problem, you can now create a random number generator instance and reference it from all random number functions. In this way, if it does not already exist, the random number generator is created *before* the first random number is generated. 

Here are some important aspects to keep in mind when generating random numbers:
- DO NOT generate random numbers with `$py{}`. Use the `$rand.*{}` functions with a generator reference instead.
- Pass a randomizing seed to all external functions that generate random numbers.
- Define zwicky boxes in a `__func_globals__` block and instantiate them with `$rand.zwicky{}` and a generator reference.
- Note that some configuration parts may only be fully executable in the Blender context. To ensure consistency, define all random values such that they are generated during the initial configuration compilation.
:::


## 2023-06-06 Catharsys Release 3.2.27

- System
  - Uses git directly to clone all repositories during system installation. This avoids compatibility problems between `vcstool` and `git`.
  - Adds command `cathy repos update`, which pulls `image-render-setup` and all repositories in the `repos` folder in their current branch. This command also clones repos that are in the repo list `repos-main.yaml` but are not in the repos folder.
  
- Functional JSON (ISON)
  - Fixes bug with nested `__includes__` using relative paths.

- image-render-blender-human
  - Fixes bugs with certain randomization modes
  - adds unit tests

- Documentation
  - adds overview documentation
  - adds first two parts of workspace tutorial



## 2023-05-22 Catharsys Release 3.2.26

- Adds repository `image-render-workspace-examples` which contains a number of configuration examples for the `image-render` automation system. You can install this workspace from a distribution install via `cathy install workspace examples`. If you are in a develop install, first run the command `cathy build modules -m image-render-workspace-examples`, or simply look into the cloned repository.
- Bug fixes
  - now executes the render output type modifiers before applying the lable configuration. In this way, you can enable objects just for the label pass, for example.
  - fixes bug where random object distribution could ignore obstacles for first sampled position.
  - fixes handling of shadow catcher for label rendering
  - fixes bug in calculating label 3d boxes for scaled objects
  - stores anycam camera data also for polynomial fisheye cameras when rendering pos3d


## 2023-05-15 Catharsys Release 3.2.25

This is the first release on GitHub. The main changes are:

- Documentation adapted to describe installation from GitHub and contributing via forks and pull-requests.
- Extended `cathy` command functionality to simplify develop installation from fork.
- GitHub workflow to automatically generate documentation. 

## 2023-04-25 Catharsys Release 3.2.19

- Ground Truth
  - Rendering of world coordinates is changed back again to rendering the absolute world coordinates. The offset used internally during rendering is applied directly after rendering. Also, if the scene is transformed to the camera frame during rendering, this transformation is recovered.
  - If the scene is transformed to the camera frame for rendering, this is now done only for the render operation. All scene 3d data and camera data for labelling is stored before this transformation is applied.
  - The world background is now rendered with color (0,0,0,0) in raw pos3d image.
  - Depth post-processing now sets world background pixels to depth 0, as this would mean a point is on the camera's optical center, which should not occur anyway.

- Functional JSON
  - New function `rand.int{a, b}` gives a uniformly distributed integer value within range `[a, b]` including both `a` and `b`.
  - New function `rand.sample_range{a, b, n, unique=[true|false], consec-differ=[true|false]}` samples `n` integers from the range `[a, b]` including both `a` and `b`. If the named parameter `unique` is `true` the sampled values are unique, default is `true`. See the {external+functional-json:doc}`ISON math function documentation <ipy/ison-functions-math>` for more information and examples.
  - The lambda function `$!foreach{}` can now iterate over named parameters. See the {external+functional-json:doc}`ison lambda function documentation <ipy/ison-functions-lambda>`.
  - Bug fix, where empty strings weren't processed properly by the lambda parser.
  - The syntax highlighting of named lambda parameters has been implemented.
  - The use of named parameters has been generalized. For example, the function `$write{}` now accepts its' optional parameters also with the syntax `[name]=[value]`. More functions may use this syntax in the future.
  - When using the function `$*{}` to convert a string to an object, you can now use backward quotes to denote strings, so that you do not have to use escaped double quotes. See the {external+functional-json:doc}`ISON special function documentation <ipy/ison-functions-special>`.
  - The syntax highlighting has been updated to support named argument highlighting and backquote strings.

- Modifier
  - Random random placement modifier: 
    - bug fix: when using the camera FoV, the modifier did not distinguish in front and behind camera. This is fixed now for versions 1 and 2.
    - bug fix: the numpy random number generator was not seeded correctly, so that the randomized scenarios were not deterministically repeatable. 


## 2023-04-20 Catharsys Release 3.2.18

- Rebuild of release package due to inconsistent versioning in previous release.

## 2023-04-18 Catharsys Release 3.2.17

- `cathy` commands
  - New option to only install the system documentation locally with `cathy system install --docs [doc zip file(s)]`. This can be helpful in a develop install, where you only pull the latest changes and do not re-run the module installation. With this new option you can easily install the latest documentation from a zip file to make it available via `cathy --docs`. If you do not specify a documentation zip file, the documentation from last `pip` installed `image-render-setup` module is used.
  - New command to copy a workspace configuration within a workspace: `cathy ws copy config [source config] [target config]`. This is helpful, since a `cathy blender init` adds the folder `_blender` to a configuration, which you shouldn't copy when copying a configuration, as this will copy the source code of all linked Blender addons as well, instead of just copying their links. After copying a configuration you need to run `cathy blender init --addons -c [config name]` for this configuration. If you have a develop install, you need to run `pip install -e .` in the repository folder `image-render-automation` to make this command available.

- Automation System
  - There are two new parameters you can set in the launch file: 
    - `iConfigsPerGroup` specifies the number of configurations per group. If this value is given it takes prevalence over `iConfigGroups`. The number of config groups is instead calculated from `iConfigsPerGroup` so that there is one group for each `iConfigsPerGroup` block. This parameter allows you to keep the number of configurations per job constant while varying the number of jobs generated.
    - `iFramePerGroup` specifies the number frames processed per group. If this value is given, it takes prevalence over `iFrameGroups`, just like the `iConfigsPerGroup` parameter.

- Rendering
  - Bug fix in rendering of 3D world coordinates.

- Templates
  - Adds two new workspace templates that you can install with `cathy install template [template name]`. (For a list of all available templates run `cathy install template --list`).
    - `workspace-just-render`: The most basic workspace if you just want to render a Blender file and use the job distribution system of Catharsys.
    - `workspace-std`: A simple standard workspace.
  

## 2023-04-17 Catharsys Release 3.2.16

- Automation System
  - You can now run multiple jobs in parallel also on your local machine. To do this set the `iConfigGroups` and `iFrameGroups` appropriately in your launch file, so that there are multiple jobs. Then also define the new element `iMaxLocalWorkers` with the maximal number of parallel processes that should run. Now you can run the action as before and the jobs are executed in parallel. If you combine this with execution on an LSF system, only the LSF jobs are registered in parallel. The number of LSF jobs is specified in the execution configuration, as before.
  - The loop control config `/catharsys/manifest/control/loop/range:1.1` has now one additional, optional parameter `lActiveIndices`, which specifies a list of indices. If this list is given, configs will only be generated for indices within the given range, that are also in this list. This can be helpful, if you need to re-run an action for a subset of indices. Using the `bDoOverwrite` flag set to `false` can be too slow if you have a large number of configurations.
  - There is a new loop control config `/catharsys/manifest/control/loop/list:1.0`, which iterates over a list of indices. The list of indices is specified via `lIndices`. There are also the *optional* elements `iMin`, `iMax` and `iStep`, which refer to the index that indexes the index list given by `lIndices`.

- Ground Truth
  - Adds optional evaluation of ideal 2d-boxes for instances. As this can take some time, the evaluation is optional and switched off by default. To enable this, you need to add the element `bEvalBoxes2d: true` to the `anytruth/label` render output configuration. See `image-render-workspace-test/config/anytruth/test-01/render/output/at_label_v1.json5` for an example. 2d-boxes based on the semantic segmentation are evaluated in the label post-processing and stored in a different element, so that both, the ideal and sem-seg based, label are available.

- Configuration parser
  - removes `__runtime_vars__` element after processing it and speeds-up handling of runtime vars internally.
  - bug fix for parsing of function names with a '.'
  - new functions (by Julian Habekost):
    - `$mod{a, b}`: Evaluates modulus `a mod b`.
    - `$len{x}`: Returns number of elements of list `x`.
    - `$circularselect{x, i}`: Selects element at index `i mod len(x)` of list `x`.

- Developer
  - Adds tooltip decorators for `ison` functions, which can be shown by VS Code add-on. (by Jochen Kall)


## 2023-04-04 Catharsys Release 3.2.15

- Bug fix for `cathy install system`: installs again from '.whl' files.
- Bug fix for `cathy build modules`: now also deletes old `.tar.gz` packages.


## 2023-04-04 Catharsys Release 3.2.14

- Cameras (`anycam`)

  - Adds feature to import cameras via camera-set configuration. In this way, cameras can be imported during a render action launch and need not be present in the Blender file. See `image-render-workspace-test/config/anycam/import/camset` folder for an example.
  - Bug fixes for LUT-cameras and Blender Poly cameras.

- Ground Truth (`anytruth`)

  - Rendering of additional raw ground truth data types for all camera types: object index and local position.
  - Fix for rendering 3d position data for all camera types.
  - Evaluation of optical flow ground truth from object index and local position raw renders.

- Modifier

  - Extend Parent to Object modifier by a flag to skip execution of the modifier, if the object to be parented to does not exist, default behaviour unchanged
  - Extend Place Human on seat modifier by a rotation angle around z axis, default behaviour unchanged
  - Adds modfier to add object to collection
  - Adds modifier from replacing shaders for clothing materials of anyhumans

- Configuration Parser (`ison`)

  - Adds new variables type `__runtime_vars__`. Variables declared in such a dictionary block are only available within the parser and are *not* stored in the resultant configuration file. This can be useful, if you want to import large json data files in the configs but only use a small part of them for each config. If this data was in a `__globals__` block, it would be copied to each configuration. An example can be found in `image-render-workspace-test/config/vars/test-01/launch.json5`. There runtime variables declared there are used in the `vars-rt-01.json5` file.
  - Extends ison function `$read{}` to also read in json files.


## 2023-02-09 Catharsys Release 3.2.13

- A number of bug fixes regarding generation of ground truth data, which were introduced when implementing camera dependent label render materials with the LUT cameras.
- A bug fix for importing objects with the generator `catharsys.plugins.std.blender.generate.func.collection_std:LoadCollections`. The previous version read the scene scaling from the Blender file, which had unforeseen consequences for some imports. So now, you have to specify the scale of the Blender file you are importing from explicitly, if it differs from the scene you are importing to. The new argument is called `fMetersPerBlenderUnit`. You can find an example under `image-render-workspace-test/config/generate/generator/collection/load.json5`.
- The treatment of the camera frustums created with most AnyCam cameras has been improved. If your scene is still cluttered with frustums, then press the "refresh" button in the AnyCam addon.

## 2023-01-27 Catharsys Release 3.2.11

- Adds two new types of Cameras (example camera database with `cathy install asset cameras`):

  - A look-up-table (LUT) based camera. For this camera you specify the ray direction per pixel in an OpenEXR file. This camera is based on a Blender fisheye camera and uses a spherical surface with a special refraction shader to "bend" the rays to the specified direction. Since the shader only uses incoming ray directions and not absolution positions, the camera can be freely moved in space, unlike the LFT, OpenCV (pingen/opencv) or older polynomial cameras. See {external+image-render-blender-camera:doc}`special-camera-render` for more information. Labelling with AnyTruth is available apart from optical flow. _A detailed documentation on how to generate the LUT files will follow in one of the next releases_.
  - A polynomial fisheye camera. This differs from the previously implemented polynomial camera by using the polynomial fisheye camera available directly in Blender. This has the advantage that all ground truth rendering, including optical flow, is available. However, this is a radially symmetric camera, unlike the LUT camera above. You can specify this camera either directly via the [polynomial parameters](https://docs.blender.org/manual/en/latest/render/cycles/object_settings/cameras.html), or by referencing a LUT projection of a LUT camera. In this way, you can generate an approximation of a LUT camera that has the advantage of offering optical flow ground truth and faster label rendering in complex scenes.

- For developers:
  - **IMPORTANT**: If you are working with cloned repos, you still need to (re-)run the Catharsys installer for this version, as additional python modules need to be installed. In particular, `psutil` is needed for the general system and `cv2` is needed by `anycam`.
  - Adds new cathy debugging features:
    - Debug Blender AddOns directly with `cathy blender debug -c [configuration] --port [debug port] --wait [timeout]`. This starts Blender in the given configuration and waits for a debugger to attach. See {doc}`develop/debug-vscode-blender-addon` for more information.
    - Debug all Catharsys actions (not just Blender actions) with `cathy ws launch -c [configuration] -a [action] --debug-port [debug port] --debug-timeout [timeout]`. See {doc}`develop/debug-vscode-action` for more information.
  - In the linked documents it is shown how to automate this process, so that you can start the debugging with a single click in VSCode.
  - New anybase modules:
    - `debug.py`: Functions to support debugging via `debugpy` from VSCode
    - `net.py`: Currently only one function to check continually whether a port is open.

## 2022-12-13 Catharsys Release 3.2.10

- Modifier `/catharsys/blender/modify/collection/object-placement/rnd-surf:1.0`

  - Add optional configuration flag `bInstDrawBoundingBoxes` to create bounding box objects which are added to the scene next to the instantiated objects. This can help with debugging.

- Bug Fixes:
  - Fixed book-keeping of animation handlers when cleaning up scene.
  - Fixes bug where bounding box was not rotated after rotating instance
  - Fixes bug in anytruth, where a bounding box's orientation was determined incorrectly.

## 2022-12-08 Catharsys Release 3.2.8

- Modifiers/Generators:

  - You can now add generators to a modifier program. See the configuration `modify/modifier/generate/import-object.json5` in `image-render-workspace-test` for an example.
  - The random placement modifier `blender/modify/collection/object-placement/rnd-surf:1.1` now has additional optional parameters:
    - `bCopyInstanceParentCollection` (`bool`): if true, creates a collection with the same name and labeltype as the parent collection of the instantiated object. This allows you to instantiate objects from a collection and have the instance labelled in the same way as the original. This is particularly useful in combination with the folder type hierarchy import described below.
    - `sParentObject` (`string`): The name of an object the instantiated objects are parented to.
  - There is a new generator `/catharsys/blender/generate/collection/import/folder-type-hierarchy:1.0`, which imports objects from a folder tree and uses the relative paths as label types. It generates a label type JSON file which is stored with the folder tree and loaded into the scene. For an example, see the configuration `modify/modifier/generate/import-type-hierarchy.json5` in `image-render-workspace-test`.
  - There is a new generator `/catharsrys/blender/generate/object/import/obj:1.0`, which uses the Blender `.obj` import to import such files. See the configuration `modify/modifier/generate/import-object.json5` in `image-render-workspace-test` for an example.

- For developers:
  - The revert handler structure is now removed from the modifier/generator code.
  - The module `anyblend` has a new module `object-ops`, which wraps `bpy.ops.object` functions by creating temporary Blender contexts. In this way you do not have to rely on the correct objects being active in the Blender workspace for the functions to work, but you can call them directly for specific objects.

## 2022-11-29 Catharsys Release 3.2.6

- For developers:
  - Improves on `@paramclass` decorator to declare parameter classes used by modifiers. This makes reading parameters from configurations more type safe with autocomplete, and potentially offers a possibility to automatically generate modifier documentation and GUIs. See the `image-render-actions-std-blender/src/catharsys/plugins/std/blender/modify/func/object_transform.py` file for examples of usage.
  - This release adds a new module `image-render-templates` which contains module templates. Currently, only a python action template is available, which you can use as basis for your own render post-processing actions. Templates can be installed with the new command `cathy install template`. See the {external+image-render-templates:doc}`Catharsys Templates documentation <index>` for more information.

## 2022-11-24 Catharsys Release 3.2.5

- Adds feature in anytruth to enable/disable self-occlusion labelling for armatures. This is needed, if semantic labelling of body parts in an armature is needed.

## 2022-11-22 Catharsys Release 3.2.4

- Bug fix in `anytruth` label module.
- Fixes command `cathy --docs`

## 2022-11-17 Catharsys Release 3.2.0

- New minor version 3.2, as there are many new modifiers and other features.
- Fixes problem with Catharsys install on some systems.
- Adds render output type "openGL" (only suitable in actions in `sActionDTI: "/catharsys/action/std/blender/render/std:1.0"`). See example in `image-render-workspace-test/config/anim/test-01` in action `renderGL`. This does **not** work, when running Blender in background mode, which is the default. Therefore, you need to run the action with the following command: `cathy ws launch -c anim\test-01 -a renderGL --script-vars background=False quit-blender=True`.
- Labelling with `anytruth`:
  - You can now create an Empty with the name `AT.Label.Orig.World`, which is then used as the world frame for all 3D-label data. This makes the label origin and orientation independent of the Blender basis.
  - Mesh objects can now have nested child mesh objects at arbitrary depth. All children of a mesh object are regarded as belonging to the same instance.
  - In addition to the `mCamera` dictionary in the label data output, there is now a `mCameraCV` dictionary, which gives camera data and extrinsic calibration in the typical CV orientation. That is, x-axis to the right, y-axis down and z-axis into the scene.
  - If bones defined in a skeleton type are not found, an error is printed. Before, this was silently ignored.
- Modifier:
  - Random placement now changed its arguments. Unfortunately, this includes **breaking changes** and I missed the right time to keep the old Version in parallel to the new. This is also a reason for the minor version change to 3.2. See `image-render-workspace-test/config/modify/modifier/collection/object-placement_rnd-surf.json5` for a full documentation of all new arguments. The main features are that you can not just place a set of objects, but also create new instances which are randomly rotated. The new instances are linked to the meshes of the original objects, so that it's memory efficient.
  - When loading objects from an external blender file with `/catharsys/blender/generate/collection/load:1.0`, the relative scales of the current and the external files are used, to scale the imported objects appropriately. The object scales are then applied to the object meshes.
  - Hide/Show objects if they are inside/outside the bounding box of another object with `/catharsys/blender/modify/object/enable-if/bound-box:1.0`. For documentation and an example see `image-render-workspace-test/config/modify/modifier/object/enable-if_bound-box.json5`.
  - **Rigid Bodies**. See `image-render-workspace-test/config/modify/modifier/rigidbody/ex1.json5` for a full example and documentation.
    - Make an object a rigid body with `/catharsys/blender/modify/object/rigidbody/add:1.0`.
    - Clear the rigid body world of the scene with `/catharsys/blender/modify/scene/rigidbody/clear:1.0`.
    - Bake a rigid body world with `/catharsys/blender/modify/scene/rigidbody/bake:1.0`.
- For developers:
  - adds a decorator `constKeywordNamespace` for defining const strings in class namespace for e.g. adressing dictionaries items
  - adds a field type in `CParamFields` for `paramclass` decorator:
    - `DEPRECATED`: when inside Json the field name should change, but older names are also accepted (a Warning is printed bu no Error execption is thrown)
    - `DISPLAY`: for GUI Usage, when field name is not suitable for displaying in GUIs, this string will be additionally available

## 2022-10-27 Catharsys Release 3.1.17

- Ensures that all Blender scene drivers are updated after modifiers are applied.
- Ensures that changing custom properties of Blender objects triggers updates of all dependent Blender scene drivers.
- Adds error reporting to catharsys user path evaluation.

## 2022-10-24 Catharsys Release 3.1.16

- Extends documentation for "enable" modifier in `image-render-workspace-test`.
- Adds conda environment name to catharsys user path and Blender install path. **You need to re-install Blender** in Catharsys and re-init your configurations with `cathy blender init --all --addons`, before you can render again.
- Adds more features to the asset plane evaluation in anycam.
- Various bug fixes.

## 2022-10-12 Catharsys Release 3.1.15

- Improves tonemapping action. Now allows explicit specification of source image type, in case this differs from the initial render image type.
- Improves anytruth depth render action to support also cameras that have not been created with AnyCam.
- Fixes type annotation in Catharsys install script, so that it can be executed with python versions before 3.10.
- Fixes `cathy` command help, to show available commands when running `cathy -h`.

## 2022-10-11 Catharsys Release 3.1.14

- Changes `cathy code init` to generate workspace files, whose names include the corresponding conda environment name.
- Adapts `cathy code show` to new workspace file naming convention.
- Improves error reporting for `cathy-conda` install script, if conda environment cannot be activated.
- When initializing Blender configs with `cathy blender init --all`, an update check for the installed catharsys modules is only done once and not for all configs. Addons are updated for all configs, of course.
- Fixes bugs when running python actions with LSF job distribution system.

## 2022-10-10 Catharsys Release 3.1.13

- Adds animator for constant translation `/catharsys/blender/animate/object/translate/const:1.0`. Example of use can be found in `image-render-workspace-test/config/anim/test-01`. This animator translates objects with constant speed.

## 2022-10-06 Catharsys Release 3.1.12

- Bug fixes for logging action.

## 2022-10-06 Catharsys Release 3.1.11

- Fixes bug that "anybase.dec" could not be imported.
- Improves syntax highlighting for pure variables in ison, i.e. `$var`.

## 2022-10-06 Catharsys Release 3.1.10

- Asset placement maps can now be generated automatically with the AnyCam addon. This simplifies, for example, the placement of human models in a scene, depending on the camera.
- Adds modifier "/catharsys/blender/modify/object/properties:1.0", which sets custom properties of an object. For example, modifying the attribute `x` of an object `objFoo`, modifies `objFoo.x`. Modifying the property `x` of the same object, modifies `objFoo["x"]`. When you specify custom properties of an object in Blender, these can be accessed via `objFoo["x"]`, where `x` stands for the property name. These properties can in turn be used in drivers in Blender. In this way, the property modifier gives you access to "variables" of a scene, that can be used in some complex way inside the Blender file. There is an example for using this modifier in `image-render-workspace-test` in the `modify` configuration.

## 2022-09-29 Catharsys Release 3.1.6

- Bug fix of `cathy` command, so that `cathy --docs` works again

## 2022-09-28 Catharsys Release 3.1.5

- Additions to ISON parser:
  - Variables can now also be references via `$variable` in addition to `${variable}`. This reduces the number of braces somewhat. The {external+functional-json:doc}`ISON language <language>` documentation is updated accordingly.
  - The VSCode addon for the ISON syntax highlighting is updated to support the new variable reference syntax.
  - All {external+functional-json:doc}`ISON functions <functions>` are now documented with examples.
  - Bug fixes in install script and default VSCode settings.
  - Bug fixes in `cls_paramclass`

## 2022-09-27 Catharsys Release 3.1.4

- Additions to ISON parser:
  - New special tag '**lambda**' to declare dictionaries as lambda functions. See the {external+functional-json:doc}`ison lambda function documentation <ipy/ison-lambda>` for more details.
  - New ison functions `$print{}` and `$set-log-path{}` for printing and logging during parsing of configuration files. Examples can also be found in the {external+functional-json:doc}`ison language documentation <ipy/ison-basics>`

## 2022-09-23 Catharsys Release 3.1.2

- For developers:
  - Applied code formatting with `black` formatter to all files. Updates default workspace VSCode configurations to activate `black` and `flake8`. Also installs necessary python modules when installing in develop mode.
  - Updates coding conventions
  - Adds decorators for logging and specifying functions as modifiers or generators.
  - Adds command `cathy inspect` to search modifiers and generators.
  - Adds possibility to run any `cathy` command in a debugging mode, so that an external python debugger can be attached to the process. Also works with scripts run in Blender.
- Improves execution of `cathy` commands, so that not all modules of all commands are loaded before a command is executed.
- Adds the option `--all` to `cathy blender init`, which initializes all configs in a workspace. For example, to only update all addons for all configurations in a workspace use `cathy blender init --all --addons`.

## 2022-09-06 Catharsys Release 3.1.0

:::{attention}
Since the minor version has changed, you need to install Blender again with `cathy blender install`.
:::

- A much improved ison parser, which can break some Catharsys configs regarding the use of `__globals__` and `__eval_globals__`. Due to this breaking change, the catharsys minor version has been incremented to 1.
  - Basically, all lambda functions should now be declared in a `__func_globals__` or `__func_locals__` block, as variables declared here are only evaluated when used.
  - The `__eval_*` are now deprecated, as `__globals__` and `__locals__` are also processed per dictionary, before the dictionary contents are parsed. This ensures variable consistency.
  - See the {external+functional-json:doc}`ison language documentation <ipy/ison-basics>` for more details.
- There is now additional documentation for
  - the ison language
  - using LFT, LUT and Poly cameras with `anycam`
  - the catharsys automation configuration processing variables
- There is an additional config in `image-render-workspace-test` to demonstrate the use of all configuration processing variables.
- When installing Catharsys in develop mode, the Python module `pytest` is now also installed.
- There is a new `cathy` command `cathy test`, which runs `pytest` on all unit tests of all modules. Unit tests must be located under `src/testing` per module and have to be named `test_*.py`. See the `pytest` documentation for more info. In VS Code the addon **Python Test Explorer for Visual Studio Code**, is quite helpful in running and debugging tests.
- Fixes bug when only `mGlobalArgs` is defined in a launch file.

## 2022-09-01 Catharsys Release 3.0.48

- Bug fix in random object distribution

## 2022-09-01 Catharsys Release 3.0.47

- Improved random distribution of objects on surface.

## 2022-09-01 Catharsys Release 3.0.46

- Improves processing of `__includes__` statements in `__globals__` etc. by making variables available in parsing of include paths.
- Fixes bugs in error reporting.

## 2022-08-30 Catharsys Release 3.0.45

- Fixes bug in config processing of loop ids.

## 2022-08-30 Catharsys Release 3.0.44

- Adds ISON language feature "**includes**", which can be used in any dictionary. This expects a list of (relative/absolute) file paths to json files. The extension can be omitted. The dictionaries of the loaded are JSONs are integrated in the dictionary the include element is in. The "**includes**" element is deleted after processing. If the current dictionary contains elements that are also present in the included JSONs, they are _not_ overwritten.
- Adds scaling modifiers for setting object scale to a specific scale, for scaling reltive to the current object scale, and for scaling w.r.t. the scene unit scale of the current scene.
- Adds error message, when compositor output node does not have output sockets.

## 2022-08-29 Catharsys Release 3.0.43

- Ensures that global variables from launch config are passed on to all modifiers and generators for later processing.
- Improves type conversions of config variables for modifiers and generators

## 2022-08-26 Catharsys Release 3.0.42

- Fixes problem with object parenting

## 2022-08-25 Catharsys Release 3.0.41

- Improves error reporting for modifers and generators, also displaying the source file where an error occured.
- Improves type conversion and checking when parsing parameters from configuration files.
- Improves error reporting in anycam somewhat. Displaying an error in the Blender UI does not work from all contexts.

## 2022-08-24 Catharsys Release 3.0.40

- In the execution config for python based actions, you do not need to specify a python conda environment anymore.
  By default, the conda environment of the calling process is used. When using an LSF job distribution system,
  the environment should be given, as the LSF system does not run in any conda environment.
- Fixes problem with equidistant cameras in AnyCam, where the render resolution could be of a different parity
  than the camera resolution. This could happen, when the maximal FoV degree is set. It is now ensured that
  render resolution and camera resolution are of the same parity.
- It seems that in some installs the metadata of the entry points is listed twice, when using the `importlib.metadata`
  library. This may be a problem with `pip` or with the lib. In any case, when scanning for commands it is now ensured
  that the entries are unique.

## 2022-08-23 Catharsys Release 3.0.39

- There is now a separate install location for Blender for a "develop" install. This allows you to have a develop and a distribution installation of Catharsys (in separate Anaconda Environments), each using separate Blender installs, so that the Catharsys installs in Blender Python are also separate.
- Catharsys installs now from "wheels" by default, which is much faster. You can still switch to an install from the source distribution via a command line option.
- The documentation is packed differently, so that the installation of the setup package is much faster.

> **IMPORTANT**: If you are working with a develop install you need to re-install Blender from your develop environment via "cathy blender install [blender zip]".
