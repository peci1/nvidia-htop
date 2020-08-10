import subprocess
import unittest


class TestNvidiaHtop(unittest.TestCase):
    def do_test(self, stdin, stdout, fake_ps='FAKE_PS', call_args=None):
        if call_args is None:
            call_args = list()
        with open(stdin, 'r') as fake_stdin:
            test_call = subprocess.run(["../nvidia-htop.py", "--fake-ps", fake_ps] + call_args, stdin=fake_stdin, stdout=subprocess.PIPE)
            self.assertEqual(test_call.returncode, 0)
            with open(stdout, 'r') as desired_stdout:
                out = desired_stdout.read()
                self.assertEqual(out, test_call.stdout.decode())

    def test_with_processes(self):
        self.do_test('FAKE_STDIN', 'DESIRED_STDOUT')

    def test_new_format(self):
        self.do_test('FAKE_STDIN_NEW_FORMAT', 'DESIRED_STDOUT_NEW_FORMAT')

    def test_with_processes_color(self):
        self.do_test('FAKE_STDIN', 'DESIRED_STDOUT_COLOR', call_args=["-c"])

    def test_with_processes_long(self):
        self.do_test('FAKE_STDIN', 'DESIRED_STDOUT_L', call_args=["-l"])

    def test_with_processes_very_long(self):
        self.do_test('FAKE_STDIN', 'DESIRED_STDOUT_L150', call_args=["-l", "150"])

    def test_no_processes(self):
        self.do_test('FAKE_STDIN_NO_PROCESSES', 'DESIRED_STDOUT_NO_PROCESSES')

    def test_no_processes_docker(self):
        self.do_test('FAKE_STDIN_NO_PROCESSES_DOCKER', 'DESIRED_STDOUT_NO_PROCESSES_DOCKER')


if __name__ == '__main__':
    unittest.main()
