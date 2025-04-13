import unittest
from handlers import commands, questions, settings, admin, feedback
from utils import tts
import keyboards

class TestImports(unittest.TestCase):
    def test_imports(self):
        self.assertIsNotNone(commands)
        self.assertIsNotNone(questions)
        self.assertIsNotNone(settings)
        self.assertIsNotNone(admin)
        self.assertIsNotNone(feedback)
        self.assertIsNotNone(tts)
        self.assertIsNotNone(keyboards)

if __name__ == '__main__':
    unittest.main()
