import sys

std_in, std_out, std_err = sys.stdin, sys.stdout, sys.stderr
reload(sys)
sys.setdefaultencoding('utf-8')

sys.stdin, sys.stdout, sys.stderr = std_in, std_out, std_err
