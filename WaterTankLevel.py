from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class WaterTankLevel(AliceSkill):
	"""
	Author: LazzaAU
	Description: Announce water tank levels and states
	"""


	@IntentHandler('MyIntentName')
	def testIntent(self, session: DialogSession, **_kwargs):
		pass


	@IntentHandler('MySecondIntentName')
	def secondTestIntent(self, session: DialogSession, **_kwargs):
		pass