from django.test import TestCase
from daisyproducer.documents.models import State, StateError

class StateTestCase(TestCase):
    fixtures = ['state.yaml']

    def setUp(self):
        self.stateNew = State.objects.get(name='new')
        self.stateScanned = State.objects.get(name='scanned')

    def testUnicode(self):
        self.assertEquals(self.stateNew.__unicode__(), 'new')

    def testTransition(self):
        self.assertRaises(TypeError, self.stateNew.transitionTo, self)
        self.assertRaises(StateError, self.stateNew.transitionTo, self.stateNew)
        self.assertEquals(self.stateNew.transitionTo(self.stateScanned), self.stateScanned)
