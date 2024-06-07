
# How to debug Blender addons
*by Christian Perwass*

To debug Blender addons developed for the Catharsys system, the following steps are needed:

1. Blender must be started with an appropriate catharsys project configuration.
2. Blender has to run a script starting `debugpy` and waiting for a debugger connection.
3. Once the `debugpy` debug server has been started, the VS Code debugger has to be attached.

All of these steps can be achieved with a `cathy` command and some VSCode configurations. All of the following examples use the configuration `anycam/test-01` in the workspace `image-render-workspace-test`. For more information on how to debug python code in VS Code see this [page](https://code.visualstudio.com/docs/python/debugging).


## Two Step Approach

In this approach you start Blender manually with a `cathy` command and then attach the VSCode debugger. 
To start Blender in debug mode in a Catharsys environment use the command:

```{admonition} Shell
`cathy blender debug -c anycam/test-01 --port 5678 -w 10`
```

The options have the following meaning:

- `-c`: specifies the Catharsys configuration to use.
- `-w` or `--wait`: (optional) sets the time in seconds, for how long to wait for the debug server to start. Defaults to `10`. 
- `--port`: (optional) sets the debug port. Defaults to `5678`.

When the debugger server is up and running you should see the text `Blender debug port open at [...]` in the shell. You can then attach the VSCode debugger. To do this you need to create a launch configuration either in a separate `launch.json` file or in your current `.code-workspace` file. 

```json
"launch": {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Blender",
            "type": "python",
            "request": "attach",
            "justMyCode": false,
            "host": "localhost",
            "port": 5678,
        }
    ]
}
```

You should then see the debug option `Python: Debug Blender` in the VS Code debug tab. Start the debugger and the editor should jump to a line in the file `run-blender-debug.py`, which you can find in the module `image-render-actions-std-blender` in the folder `src/catharsys/plugins/std/blender/scripts`. Just press `F5` to run past the current breakpoint. Now you can use and debug Catharsys Blender addons. Note that `print()` outputs of any scripts run in Blender are **not** shown in the shell but can be found in the `DEBUG CONSOLE` in VS Code.

## Single Step Approach

In this approach everything is started directly from VS Code. For this setup you need to add a task to the `.code-workspace` file or a separate `tasks.json` file. The JSON block for the task looks like this:

```json
"tasks": {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Launch-Debug-Blender",
            "type": "shell",
            "options": {
                "cwd": "${workspaceFolder:image-render-workspace-test}",
            },
            "isBackground": true,
            "command": "cathy 'blender debug -c anycam/test-01 --port 5678 --wait 10'",
            "problemMatcher": {
                "pattern": {
                    "regexp": "^ERROR.+"
                },
                "background": {
                    "activeOnStart": true,
                    "beginsPattern": "^Starting Catharsys debugging.+",
                    "endsPattern": "^Catharsys debug port open.+"
                }
            },
            "presentation": {
                "reveal": "always"
            },
        },
        {
            "label": "Terminate All Tasks",
            "command": "echo ${input:terminate}",
            "type": "shell",
            "problemMatcher": []
        }
    ],
    "inputs": [
        {
            "id": "terminate",
            "type": "command",
            "command": "workbench.action.tasks.terminate",
            "args": "terminateAll"
        }
    ]
}
```

The task `Launch-Debug-Blender` sets the current working directory to the folder of the Catharsys project. If you are in a multi-workspace environment you can use the approach as shown above. In a single workspace environment just use `${workspaceFolder}`. Note that the arguments of `cathy` in the `command` element need to be enclosed in `''`. The `problemMatcher` defines in the `background/endsPattern` the regular expression to look for, when the task is finished. In this case, when the debug server is running. 

The additional task `Terminate All Tasks` does what is says, and will be executed as a post debug task.

The full launch configuration now looks like this:
```json
"launch": {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Blender",
            "type": "python",
            "request": "attach",
            "justMyCode": false,
            "host": "localhost",
            "port": 5678,
            "preLaunchTask": "Launch-Debug-Blender",
            "postDebugTask": "Terminate All Tasks"
        }
    ]
}
```

The `Launch-Debug-Blender` task is executed before VS Code tries to attach the debugger. Therefore, this task must only return, when the debug server is actually running. The post debug task closes all task terminals. Without it, the debug task terminal will stay open until you close it manually. Restarting the debug launch configuration while the debug task terminal is still open from a previous launch, causes an error.
