
## Programming Style Guide

### Linter & Autoformatter

Use `black` as auto formatter and `flake8` as linter. For `flake8` set the following paramters:

| Parameter       | Value |
| --------------- | ----- |
| max-line-length | 120   |
| ignore          | E203  |
|                 |       |

For `black` set the following parameters:

| Parameter   | Value |
| ----------- | ----- |
| line-length | 120   |
|             |       |

In VS-Code use the following settings:
:::json
"python.formatting.provider": "black",
"python.formatting.blackArgs": [
    "--line-length",
    "120"
],
"editor.formatOnSave": true,
"python.linting.flake8Enabled": true,
"python.linting.pylintEnabled": false,
"python.linting.enabled": true,
"python.linting.flake8Args": [
  "--max-line-length=120",
  "--ignore=E203"
],
:::

### Variable Conventions

Variable names need to start with a lower-case letter indicating the variable type. This helps other programmers to understand your code more easily. For example, a variable of type `dict` must start with `dic`, as in `dicValues`. The first letter of descriptive name must start with a capital letter. If there are mulitple words, use camel-case, as in `dicHouseHeights`.

*Ideally*, variable names should read from the general to the specific. For example, `iCameraCount` first gives the variable type, then the object it describes an aspect of and lastly what specific parameter it contains.


| Type         | Prefix | Example     |
| ------------ | ------ | ----------- |
| `int`        | `i`    | `iIdx`      |
| `float`      | `f`    | `fAngle`    |
| `bool`       | `b`    | `bIsValid`  |
| `str`        | `s`    | `sName`     |
| `dict`       | `dic`  | `dicValues` |
| `list`       | `l`    | `lValues`   |
| `enum class` | `e`    | `eType`     |
| other        | `x`    | `xMyClass`  |
|              |        |             |

If you know that a variable can have more than one type and you know which types, then list them after an `x` at the beginning of the variable name. For example, a variable that can be list or integer is named `xilValue`. For dictionaries, just use `d` in this case, as in `xidValue` for a variable that can be integer or dictionary. Variables that can be anything start with an `x`.

Regarding **class instances**, if the meaning of your class can be abbreviated well, then use this as prefix for a variable. For example, a variable of type `pathlib.Path` should be written `pathFile`. 

**Blender variable types**:

| Type        | Prefix | Example      |
| ----------- | ------ | ------------ |
| objects     | `obj`  | `objCube`    |
| collections | `cln`  | `clnCameras` |
|             |        |              |

Variables of variable type or complex types like classes, must start with an `x`.

If it is not clear for the linter of what type a variable is from the variable initialization, then declare its' type.

### Function Conventions

Function names start with a capital letter and use camel-case for multiple words, as in `MyWonderfulFunction`. This distinguishes them from variable names.

*Ideally*, use type attributes whereever possible. You may need to import the `typing` module to achieve this. For example,

:::python
from typing import Optional

def Run(*,
        _sWsName: str, 
        _sPathTrg: Optional[str] = None,
        _bForce: bool = False,
        _bDoList: bool = False
) -> bool:
:::

**Function interface argument** names must start with an underscore (as in the example above), so that there is a distinction between interface variables and local variables in the function body.

### Classes

- *Ideally*, each class should be defined in its own python file. 
- The filename *must* start with `cls_` as in `cls_complex.py`. 
- The class typenames *must* start with a capital `C`, as in `CWorkspace`. This clearly differentiates a class instance initialization from a function call.
- Classes derived from type `enum.Enum` must have a name that starts with a capital `E`, as in `EMyEnum`. 


### Block-end Comments

All ends of indented block that are required by Python need a `# end[command] [comment]` line at the end. For example, `if`, `for`, `while`, `with`, `def`, `class`, etc. require you to indent the containing code. These blocks must be ended like this:
:::python
def MyFunc():
    while bA is True:
        MyCode()
        if iA > 2:
            RunNow()
            with pathA.open("w") as xFile:
                WriteToFile(xFile)
            # endwith
        # endif iA > 2
        MoreWork()
    # endwhile bA is True
# enddef MyFunc()
:::

*Ideally*, for long code blocks, there is a comment behind the `# end[...]`, so that you can immediately see what this end belongs to.
