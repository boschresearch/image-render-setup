# <LICENSE id="Apache-2.0">
#
#   Image-Render Setup module
#   Copyright 2022 Robert Bosch GmbH and its subsidiaries
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# </LICENSE>

from anybase.cls_any_error import CAnyError_Message

g_sCmdDesc = "Displays the registered entry points for a group"


####################################################################
def AddArgParseArguments(_xArgParser):
    _xArgParser.add_argument("group", nargs=1, default=[None])


# enddef


####################################################################
def RunCmd(_xArgs):
    from importlib import metadata

    sGroup: str = None
    try:
        sGroup = _xArgs.group[0]
        if not isinstance(sGroup, str):
            raise CAnyError_Message(sMsg="No entry points group given")
        # endif

        lGrpDti = []
        # print(f"Group: {sGroup}")
        clnEpGrp = metadata.entry_points().select(group=sGroup)
        if len(clnEpGrp) == 0:
            raise CAnyError_Message(sMsg=f"Entry point group '{sGroup}' not available")
        # endif

        print(f"Entry points of group '{sGroup}':")
        for iIdx, epTrgTest in enumerate(clnEpGrp):
            print(
                "[{}]: {}\n  -> {}\n".format(iIdx + 1, epTrgTest.name, epTrgTest.value)
            )
        # endfor
        print("")
    except Exception as xEx:
        raise CAnyError_Message(
            sMsg=f"Error listing entry points for group {sGroup}", xChildEx=xEx
        )
    # endtry


# enddef


####################################################################
def RunCli():
    import sys
    import argparse
    from catharsys.setup import except_util

    global g_sCmdDesc

    try:
        xArgParse = argparse.ArgumentParser(description=g_sCmdDesc)
        xArgParse.add_argument(
            "--debug", dest="debug", action="store_true", default=False
        )
        # Add command specific arguments
        AddArgParseArguments(xArgParse)
        xArgs = xArgParse.parse_args()
    except Exception as xEx:
        print("ERROR parsing runtime arguments:\n{}\n".format(str(xEx)))
        sys.exit(1)
    # endtry

    try:
        print(xArgs.debug)
        RunCmd(xArgs)

    except Exception as xEx:
        except_util.PrintException("Error running install", xEx, bTraceback=xArgs.debug)
        sys.exit(1)
    # endtry

    sys.exit(0)


# enddef


####################################################################
if __name__ == "__main__":
    RunCli()
# endif
