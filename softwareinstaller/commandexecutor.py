#!/usr/bin/python3

import subprocess
import os
import fcntl


def non_blocking_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.readline()
    except:
        return ""


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
        #print(command)
        while proc.poll() is None:
            line = non_blocking_read(proc.stdout)
            #print(line.rstrip("\n"))
            stdout_result += line
            if stdout is not None:
                print(line.rstrip("\n"), file=stdout)
            
            line = non_blocking_read(proc.stderr)
            stderr_result += line
            if stderr is not None:
                print(line.rstrip("\n"), file=stderr)
        result_code = proc.poll()
        #print(result_code)

        stdout_result = stdout_result.rstrip("\n")
        stderr_result = stderr_result.rstrip("\n")

        return stdout_result, stderr_result, result_code

    def call(self, command, regex=None, converters=None, ignorenomatch=False, successcodes=0, stdout=None, stderr=None):
        if successcodes == 0:
            successcodes = [0]

        stdout_result, stderr_result, result_code = self.execute_proc(command, stdout, stderr)
        
        if successcodes is not None and result_code not in successcodes:
            raise Exception("Command: {0}\nReturn Code: {1}\nStandard Output: {2}\nError Output: {3}".format(command, result.returncode, stdout_result, stderr_result))
        
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
                raise Exception("Line '{0}' did not match regex".format(line))
        return response

    def getuser(self):
        return self.call("logname")
