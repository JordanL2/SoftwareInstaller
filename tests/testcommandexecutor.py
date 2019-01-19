#!/usr/bin/python3


class TestCommandExecutor:

    def __init__(self, cmdmap):
        self.cmdmap = cmdmap
        self.executed = []

    def call(self, command, regex=None, converters=None, ignorenomatch=False, successcodes=0):
        self.executed.append(command)
        stdout = self.cmdmap[command]
        if regex is None:
            return stdout
        response = []
        for line in stdout.splitlines():
            match = regex.match(line)
            if match:
                result_line = match.groups()
                if converters is not None:
                    result_line = [converters[i](r) for i, r in enumerate(result_line)]
                response.append(result_line)
            elif not ignorenomatch:
                raise Exception("Line '{0}' did not match regex".format(line))
        return response
