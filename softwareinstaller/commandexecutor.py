#!/usr/bin/python3

import fcntl
import os
import subprocess
import time


def set_non_blocking(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

def non_blocking_read(output):
    try:
        return output.readlines()
    except:
        return []


class CommandExecutor:

    def execute_proc(self, command, stdout=None, stderr=None):
        proc = subprocess.Popen(command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1)

        stdout_result = ''
        stderr_result = ''
        result_code = None

        set_non_blocking(proc.stdout)
        set_non_blocking(proc.stderr)

        while True:
            lines = non_blocking_read(proc.stdout)
            for line in lines:
                stdout_result += line
                if stdout is not None:
                    print(line, end='', file=stdout)

            lines = non_blocking_read(proc.stderr)
            for line in lines:
                stderr_result += line
                if stderr is not None:
                    print(line, end='', file=stderr)

            if result_code is not None:
                break
            result_code = proc.poll()

            # This fixes a weird bug causing output not to be read correctly
            time.sleep(0.000001)

        stdout_result = stdout_result.rstrip("\n")
        stderr_result = stderr_result.rstrip("\n")

        return stdout_result, stderr_result, result_code

    def call(self, command, regex=None, converters=None, ignorenomatch=False, successcodes=0, stdout=None, stderr=None):
        if successcodes == 0:
            successcodes = [0]

        stdout_result, stderr_result, result_code = self.execute_proc(command, stdout, stderr)

        if successcodes is not None and result_code not in successcodes:
            raise Exception("Command: {0}\nReturn Code: {1}\nStandard Output: {2}\nError Output: {3}".format(command, result_code, stdout_result, stderr_result))

        if regex is None:
            return stdout_result

        response = []
        for line in stdout_result.splitlines():
            match = regex.match(line)
            if match:
                result_line = match.groups()
                if converters is not None:
                    result_line = [converters[i](r) for i, r in enumerate(result_line)]
                response.append(result_line)
            elif not ignorenomatch:
                raise Exception("Line '{0}' did not match regex (command: {1})".format(line, command))
        return response

    def getuser(self):
        return self.call("logname")
