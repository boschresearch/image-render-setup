#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cathy.py
# Created Date: Thursday, June 2nd 2022, 5:00:15 pm
# Author: Christian Perwass (CR/AEC5)
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
###


####################################################################
from catharsys.setup import args, version


##########################################################################################################
# Main CLI script that distributes workload to specialized scripts
def RunCli():
    import sys

    sys.stdout.write("> Loading modules.")
    sys.stdout.flush()
    import argparse

    sys.stdout.write(".")
    sys.stdout.flush()

    sys.stdout.write(".")
    sys.stdout.flush()
    try:
        import catharsys.decs.decorator_log as logging_dec

        bHasDecorators = True
    except Exception:
        bHasDecorators = False
    # endtry

    try:
        from anybase import logging
        clog = logging.logger
    except Exception:
        logging = None
        clog = None 
    # endtry

    sys.stdout.write(".")
    sys.stdout.flush()

    try:
        from anybase import assertion

        bHasAssertion = True
    except Exception:
        bHasAssertion = False
    # endtry
    sys.stdout.write("done   \r")
    sys.stdout.flush()

    sys.stdout.write("Loading available commands...              \r")
    sys.stdout.flush()

    # ####################################################################################################
    # parse command line and extend sub parser
    try:
        # Print logs for everything above or equal to INFO
        if logging is not None:
            logging.set_logging(logging.LogConfig(stdout_level=3, stdout_format=logging.ELogFormat.SIMPLE))
            clog = logging.logger
        # endif

        sVersion = version.AsString()
        parseMain = argparse.ArgumentParser(
            prog="cathy", description=f"Catharsys v{sVersion} main system command", exit_on_error=False
        )
        parseMain.add_argument("--debug", dest="debug", action="store_true", default=False)
        parseMain.add_argument("--log-call", dest="log_call", action="store_true", default=False)
        parseMain.add_argument("-d", "--docs", dest="show_docs", action="store_true", default=False)

        # Get set of available sub-commands
        xCmdSet = args.CCommandSet("catharsys.commands")

        # Need to separate all arguments until the first sub-command
        # to enable the correct help output for a call like 'cathy repos -h'. Otherwise,
        # the '-h' will be consumed right away and only the global help is shown.
        xCmdArgSplit = args.GetCurrentCmdArgs(_lArgs=sys.argv[1:], _xCmdSet=xCmdSet)

        # ####################################################################################################
        # logging functionality
        # Parse arguments apart from a possible sub-command
        if xCmdArgSplit.bHasSubCommand is True:
            lGlobalArgs = xCmdArgSplit.lArgs[:-1]
        else:
            lGlobalArgs = xCmdArgSplit.lArgs
        # endif

        bShowGlobalHelp = False
        if "-h" in lGlobalArgs:
            bShowGlobalHelp = True
            lGlobalArgs.remove("-h")
        elif "--help" in lGlobalArgs:
            bShowGlobalHelp = True
            lGlobalArgs.remove("--help")
        # endif

        argsGlobal = parseMain.parse_args(lGlobalArgs)

        if bHasDecorators is True and hasattr(logging_dec, "SwitchLoggingOff"):
            logging_dec.SwitchLoggingOff("catharsys")
            if argsGlobal.log_call is True and hasattr(logging_dec, "SwitchLoggingOn"):
                logging_dec.SwitchLoggingOn(pathLogFile=None, sApplication="catharsys")
            # endif logCall
        # endif

        # ####################################################################################################
        # anybase assertion handling
        if bHasAssertion is True:
            assertion.Enable(argsGlobal.debug)
        # endtry

        # ####################################################################################################

        sys.stdout.write("                                                          \r")
        sys.stdout.flush()

    except Exception as xEx:
        if clog is not None:
            clog.error(f"ERROR parsing runtime arguments:\n{xEx!s}\n")
        else:
            print(f"ERROR parsing runtime arguments:\n{xEx!s}\n")
        # endif
        sys.exit(1)
    # endtry

    # ####################################################################################################
    # run functionality
    try:
        argsCmd = None

        if bShowGlobalHelp is True:
            # Register sub-commands as arguments
            args.AddCommandSetArgs(_parseMain=parseMain, _xCmdSet=xCmdSet)
            # Print help with list of availbale commands
            parseMain.print_help()

        elif argsGlobal.show_docs is True:
            try:
                import webbrowser
            except Exception as xEx:
                if clog is not None:
                    clog.error(f"ERROR importing webbrowser module:\n{xEx!s}\n")
                else:
                    print(f"ERROR importing webbrowser module:\n{xEx!s}\n")
                # endif
            # endtry

            import catharsys.setup.version as cathver
            from catharsys.setup import util

            sVersion = cathver.MajorMinorAsString()
            pathCathUser = util.GetCathUserPath(_bCheckExists=True)
            pathDocs = pathCathUser / "docs/html/index.html"
            if not pathDocs.exists():
                if clog is not None:
                    clog.error(f"ERROR: Catharsys HTML documentation cannot be found at: {pathDocs}")
                else:
                    print(f"ERROR: Catharsys HTML documentation cannot be found at: {pathDocs}")
                #endif
            # endif
            webbrowser.open(pathDocs.as_posix())

        elif xCmdArgSplit.bHasSubCommand is True:
            # Register sub-commands as arguments
            args.AddCommandSetArgs(_parseMain=parseMain, _xCmdSet=xCmdSet)

            # Only parse the sub-command as argument.
            argsCmd = parseMain.parse_args([xCmdArgSplit.lArgs[-1]], argsGlobal)

            # Run the sub-command, which will also register any additional arguments
            # for the specific sub-command
            args.RunSubCommand(_argsCmd=argsCmd, _lArgs=xCmdArgSplit.lRemainder)

        else:
            parseMain.print_help()
        # endif

    except Exception as xEx:
        from catharsys.setup import except_util

        if argsCmd is not None:
            if hasattr(argsCmd, "sCmdName") and isinstance(argsCmd.sCmdName, str):
                sMsg = "Error running command '{}'".format(argsCmd.sCmdName)
            else:
                sMsg = "Error running 'cathy'"
            # endif

            if hasattr(argsCmd, "debug") and isinstance(argsCmd.debug, bool):
                bDebug = argsCmd.debug
            else:
                bDebug = True
            # endif
        else:
            sMsg = "Error running 'cathy'"
            bDebug = False
        # endif

        except_util.PrintException(sMsg=sMsg, xEx=xEx, bTraceback=bDebug)
        sys.exit(1)
    # endtry

    sys.exit(0)


# enddef


# ####################################################################################################
if __name__ == "__main__":
    RunCli()
# endif
