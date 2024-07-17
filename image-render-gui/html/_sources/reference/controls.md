# GUI Controls

The following lists the available GUI controls and their parameters with usage examples.

All controls have the following configuration elements:

- `sDTI`: The type of GUI control element. This element is optional, if the type can be deduced from the name as described before. For a full list of availabel control types see {doc}`controls`.
- `sLabel`: The GUI element label. If this element is not given, the name is either deduced from the naming convention or the element name itself is used.
- `sTooltip`: A tooltip for the GUI element. If this element is not given, no tooltip is shown.



## Number Control

The number control is available for integer and floating point numbers with the following type ids:

| Type Id                                   | Description     |
| ----------------------------------------- | --------------- |
| `/catharsys/gui/control/number/int:1.0`   | Integer numbers |
| `/catharsys/gui/control/number/float:1.0` | Float numbers   |


These controls have slightly different available configuration elements.

### Integer Number Control

Type id: `/catharsys/gui/control/number/int:1.0`

| Element   | Type   | Description                                          |
| --------- | ------ | ---------------------------------------------------- |
| `iStep`   | int    | Step size when using the increment/decrement control |
| `iMin`    | int    | The minimal allowed integer value                    |
| `iMax`    | int    | The maximal allowed integer value                    |
| `sPrefix` | string | A prefix to be displayed in front of the value       |
| `sSuffix` | string | A suffix to be displayed after the value             |

Here is a full GUI definition example:

```json
"my_value": 42,
"my_value/gui": {
    "sDTI": "/catharsys/gui/control/number/int:1.0",
    "sLabel": "My Value",
    "sTooltip": "This is my wonderful value",
    "iStep": 2,
    "iMin": 40,
    "iMax": 44,
    "sPrefix": "Magic: ",
    "sSuffix": "m",
}
```

### Float Number Control

Type id: `/catharsys/gui/control/number/float:1.0`

| Element      | Type   | Description                                          |
| ------------ | ------ | ---------------------------------------------------- |
| `fStep`      | float  | Step size when using the increment/decrement control |
| `iPrecision` | int    | Number of decimal places to round value to           |
| `fMin`       | float  | The minimal allowed integer value                    |
| `fMax`       | float  | The maximal allowed integer value                    |
| `sPrefix`    | string | A prefix to be displayed in front of the value       |
| `sSuffix`    | string | A suffix to be displayed after the value             |

Here is a full GUI definition example:

```json
"my_value": 3.1415,
"my_value/gui": {
    "sDTI": "/catharsys/gui/control/number/float:1.0",
    "sLabel": "My Value",
    "sTooltip": "This is my wonderful value",
    "iStep": 0.01,
    "iMin": 1.0,
    "iMax": 4.2,
    "sPrefix": "Magic: ",
    "sSuffix": "cm",
}
```

## Switch Control

This control is meant for boolean values but it also works for integer or float values. 

Type id (`sDTI`): `/catharsys/gui/control/switch:1.0` 

There are no additional parameters apart from the common control parameters available for this control.

## Input Control

This control allows you to input strings.

Type id: `/catharsys/gui/control/switch:1.0`

This control has the following additional parameters.

| Element               | Type | Description                                                    |
| --------------------- | ---- | -------------------------------------------------------------- |
| `bIsPassword`         | bool | If true, the input is only shown as `*` symbols per character  |
| `bTogglePasswordView` | bool | If true, a button is displayed to show the input in clear text |

Here is a full GUI definition example:

```json
"pw": "password",
"pw/gui": {
    "sDTI": "gui/control/input:1",
    "sLabel": "Password",
    "sTooltip": "Enter a password",
    "bIsPassword": true,
    "bTogglePasswordView": true,
}
```

## Select Control

This control allows the user to select one value from a set of values. There are different type ids depending on the data type that is to be selected.

| Type Id                                   | Description     |
| ----------------------------------------- | --------------- |
| `/catharsys/gui/control/select/int:1.0`   | Integer numbers |
| `/catharsys/gui/control/select/float:1.0` | Float numbers   |
| `/catharsys/gui/control/select/str:1.0`   | Strings         |


This control has the following additional parameters.

| Element     | Type | Description                                        |
| ----------- | ---- | -------------------------------------------------- |
| `lOptions`  | list | The list of options for the selection.              |
| `bMultiple` | bool | If true, allows the selection of multiple elements. |

Note that if `bMultiple` is true, the result is always a list, even if only a single or no element is selected.

Here is a full GUI definition example:

```json
"objects": ["cup"],
"objects/gui": {
    "sDTI": "gui/control/select/str:1",
    "sLabel": "Object",
    "sTooltip": "Select a set of objects",
    "lOptions": ["cup", "tree", "spoon"],
    "bMultiple": true,
}
```

 