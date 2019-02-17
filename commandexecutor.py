#!/usr/bin/python3

import subprocess


class CommandExecutor:

    def call(self, command, regex=None, converters=None, ignorenomatch=False, successcodes=0):
        if successcodes == 0:
            successcodes = [0]
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.decode('utf-8').rstrip("\n")
        stderr = result.stderr.decode('utf-8').rstrip("\n")
        if successcodes is not None and result.returncode not in successcodes:
            raise Exception("Command: {0}\nReturn Code: {1}\nStandard Output: {2}\nError Output: {3}".format(command, result.returncode, stdout, stderr))
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

    def getuser(self):
        return self.call("who am i | awk '{print $1}'")
