
# How to debug Blender actions (alternate method)
*by Dirk Rapröger*

Debugging with VS-Code is more or less easy. <br/>
You will find the Debug-Icon in the left Tool Bar. Afterwards, the targets to debug can be choosen and configured
by that drop-down Menue, shown in the image below.

 ![DebugTargets](images/dTargets.png)

 Configurations can be done for your workspace individually in file: `launch.json`

The default debugging is to debug the current file. For that task, the launch.json file may look like:
:::json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Current Python File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "args": [
                "--debug"
            ],
            "cwd": "${workspaceFolder:cws-infra-02}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "subProcess": true
        },
    ]
}
:::

Assuming you work with a workspace, the different folders that are selected inside the explorer view can be used to 
select for example the 'cwd' parameter of that configuration.

Arguments to the python script must be given as a comma-separated-array, here shown in `args`

## Debugging the catharsys script itself

When debugging the cathy tool that runs just before the blender render process, one can define
a configuration like that:

:::json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Cathy Launch Workspace",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder:image-render-setup-develop}/${config:cathy-script}",
            "args": [
                "--log-call",
                "--debug",
                "ws",
                "launch",
                "--config",
                "cs1",
                "--action",
                "render",
            ],
            "cwd": "${workspaceFolder:cws-infra-02}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "subProcess": true
        },
    ]
}
:::

The first debugging argument `--log-call` activate the logging mechanism, that are wrapped around some function
calls. The calling stack is logged into file: `cathy.cal.md`. Opening that file with VS-Code editor can be 
just to 
1) view the calling hierarchy during the catharsys script in some selected functions and suplementary informations
2) navigating directly to the python code with `ctrl-klick` onto the link

The second debug arg `--debug` will show some detatiled information in the unlikely case of failure, 
the catharsys Error-Message Trace for example.

Placing and navigating with breakpoints are the well known features of the python VS-Code environment.

# Debugging the Blender script, that was called by catharsys

In the similiar way as debugging the original python code with the VS-Code launch mechanism, debugging of the Blender-Python
is possible too.

VS-Code is able to attach the Debugger to a process, that can be started in advance.

That means, first a task must be started: the catharsys-script with the 'normal' python script. This script will call the blender
process, and here the debugger must attaches to it.

A configuration may look like this for attaching to a prelaunch task:
:::json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Attach_host-CS1",
            "type": "python",
            "request": "attach",
            "preLaunchTask": "Launch-Debug-CS1",
            "justMyCode": false,
            "host": "localhost",
            "port": 5678
        },
    ]
}
:::
The prelaunch task itself must be defined in a separate VS-Code configuration file `task.json`
This task is similiar to the debug configuration, as you can see it below:
:::json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Launch-Debug-CS1",
            "type": "shell",
            "command": "${workspaceFolder:cws-infra-02}/.catharsys/cathy-task",
            "options": {
                "cwd": "${workspaceFolder:cws-infra-02}",
            },
            "isBackground": true,
            "args": [
                "${workspaceFolder:image-render-setup-develop}/${config:cathy-script}",
                "--log-call",
                "--debug",
                "ws",
                "launch",
                "--config",
                "cs1",
                "--action",
                "render",
                "--script-vars",
                "break=True",
                "__skip-action",
                "background=False",
                "quit-blender=False",
            ],
            "problemMatcher": []
        },
    ]
}
:::

Calling the blender script wil be performed, and a first debug point will be reached automatically. This is important, to synchronize the 
Blender-Python environment with te VS-Code-Debugger. After Sync, you can press `F5` to run your actual blender script and debug your algorithm.

To control the blender script, there are several more arguments following ```--script-args```. 

* `break=True`, that is important because of the mentioned sync mechanism of the debugger. (set to False, the blender script will not acceptd your following breakpoints)
* `skip-action`, may be, you want develop some action/ operators or other stuff inside blender itself, and you need only a starting point for debugging. Than catharsys only configure
the action and prepare the blend file, but will not perform the action automatically. You can call your scripts by every blender operator you want, and if you have placed a breakpoint 
in the corresponding script, VS-Code will stop. (In this example the argument is 'commented out' by `__`)
* `background=False`, normally blender will run in background mode, but when you will interactively change something, it is possible to start blender
with normal GUI interface
* `quit-blender`, normally blender will quit its process after finishing the script, but if desired for further steps, you can allow blender to live longer. 
(until you quit blender interactively, this only makes sense in windows system and not when running in batch-mode)

# Settings by `project.code-workspace`

It is a common method, to organize all the settings inside a `project.code-workspace` file to bind your settings onto that special project that you are working for.
Unfortunately, the described debugging and prelaunch tasks must be separated into that special files and must not be integrated into your project settings.
This is a described bug of VS-Code. 
