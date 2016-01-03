import unittest
import factory
import likelihood, path
import score, audio
import numpy as np

class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.factory = factory.Factory({
            "x": lambda: [1,2,3],
            "y": lambda: [4,5,6],
        })
        
    def testCall(self):
        self.failUnlessEqual(self.factory("x"), [1,2,3])
        self.failUnlessEqual(self.factory("y"), [4,5,6])

    def testInvalidKey(self):
        with self.assertRaises(KeyError):
            self.factory("z")

state = score.State().add_note(60).add_note(88)
data = np.ones(audio.num_bins)*0.01
data[194] = data[980] = data[480] = 500
fft = audio.FreqFrame(data)

class LikelihoodTests(unittest.TestCase):
    def testPoisson(self):
        self.failUnlessEqual(round(likelihood.factory("poisson").calculate(fft, state),4),-38.8645)
    def testSpectra(self):
        self.failUnlessEqual(round(likelihood.factory("spectra").calculate(fft, state),4), 0.6796)
    def testPSD(self):
        self.failUnlessEqual(round(likelihood.factory("psd").calculate(fft, state),4), 0.1562)
        
def main():
    unittest.main()

if __name__ == '__main__':
    main()
