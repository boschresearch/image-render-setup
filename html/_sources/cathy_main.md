
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Setup module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
# Command-Line Tool `cathy`

The command line tool `cathy` is the 'command center' to perform various tasks. The basic syntax is:

```{admonition} Shell
`cathy [--debug] [command [sub-command]] [option [...]]`
```

The set of available commands and sub-commands depends on the Catharsys modules that are installed. Each module can define its' own commands and sub-commands.

## Getting help

To get help for any `cathy` command, use the `-h` or `--help` option as in:

```{admonition} Shell
`cathy [command [sub-command]] -h`
```

To see the HTML documentation in a web browser, run:

```{admonition} Shell
`cathy --docs`
```

There is currently no option to open specifig HTML documentation for a command.

## List of Commands

Here is a list of the commands that are available by default.


| Command | Sub-Command | Description | See also |
| ------- | ----------- | ----------- | -------- |
| `install` | `system`  | Installs the Catharsys system | {doc}`setup` |
|         | `workspace` | Installs a pre-packaged workspace that comes with the setup package | | 
| **ToDo** | *other commands* | | |



## Debugging

If a command returns with an error and you think it's a bug, or you do not understand where the error is comming from, run the command again with the `--debug` option. This should show a trace, where in the code the error occurred. Note, that the option `--debug` must be the first element after `cathy` for any command. For example,

```{admonition} Shell
`cathy --debug [command [sub-command]] [option [...]]`
```

