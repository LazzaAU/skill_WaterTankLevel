from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler
import  json


class WaterTankLevel(AliceSkill):
	"""
	Author: LazzaAU
	Description: Announce water tank levels and states
	"""
	def __init__(self):
		self._tank1 = int
		super().__init__()


	def onFullHour(self):
		"""
		On the hour get reminded if the grey water tank is full, and if user is not sleeping
		:return: voice message that the tank is full
		"""
		device = self.DeviceManager.getDeviceByName("grey water tank")
		if not device:
			return
		if device.getParam('Switch2') == 'ON' and not self.UserManager.checkIfAllUser('sleeping'):
			self.say(
				text='Your grey water is full. You might want to empty it'
			)

	@IntentHandler('SayWaterTankLevel')
	def respondTankLevel(self, session: DialogSession, **_kwargs):
		tankType = self.returnTankType(session=session)

		device = self.DeviceManager.getDeviceByName(tankType[0])

		if len(tankType) > 1:
			text1 = self.getTankLevels(device=device)
			device2 = self.DeviceManager.getDeviceByName(tankType[1])
			text2 = self.getTankLevels(device=device2)
			textOutPut = f"{text1} and {text2}"
			if "None" in textOutPut:
				self.logPrint(f'yes none is in {textOutPut}')
				textOutPut.replace("None", "")
		else:
			textOutPut = self.getTankLevels(device=device)
			if "None" in textOutPut:
				textOutPut.replace("None", "")
		self.sayTheLevels(text=textOutPut, session=session)

	@staticmethod
	def returnTankType(session):
		"""Return the type of tank that has been requested"""

		if session.slotValue('WaterTank') == "fresh water":
			return ['fresh water tank 1', 'fresh water tank 2']
		elif session.slotValue('WaterTank') == "rain water":
			return ['rain water tank']
		elif session.slotValue('WaterTank') == "grey water":
			return ['grey water tank 1']

	def getTankLevels(self, device):
		"""
		Return the tank level value
		:param device: The device that was requested
		:return: Returns the string alice will speak
		"""
		if not device:
			self.logWarning(f"that device doesnt exist")
			return

		originalDeviceState = json.loads(device.getParam('state'))
		updatedStates = self.processNumberOfStates(states=originalDeviceState)

		numberOfSwitches = len(updatedStates.items())
		switchNumber = numberOfSwitches

		while switchNumber >= 0:
			if switchNumber == 0:
				return self.randomTalk(text=f'tankLevelEmpty', replace=[device.displayName])

			if updatedStates[f"Switch{switchNumber}"] == 'ON':
				litreage = self.calculateLitresOfTank(switchNumber=switchNumber, tankType=numberOfSwitches, device=device)
				return self.randomTalk(text=f'tankLevel{numberOfSwitches}-{switchNumber}', replace=[device.displayName, litreage])

			switchNumber -= 1


	@staticmethod
	def processNumberOfStates(states: dict) -> dict:
		"""Remove the time stamp leaving just the states"""
		xValue = len(states) - 1
		updatedStates = dict(list(states.items())[0: xValue])
		return updatedStates


	def sayTheLevels(self, session, text: str):

		self.endDialog(
			sessionId=session.sessionId,
			text=text,
			deviceUid=session.deviceUid
		)

	def calculateLitresOfTank(self, switchNumber: int, tankType: int, device):
		"""
		Calculate the approximate water tank levels into litres
		:param switchNumber: the int showing what what number the tank is at
		:param tankType: The type of tank. IE: tanklevel4 etc
		:param device: The current device that is being worked on
		:return:
		"""
		deviceTypes = self.DeviceManager.getDevicesBySkill(skillName='HomeAssistant', deviceType=device.deviceType)
		if str(device.displayName[-1]).isnumeric():
			strippedDeviceName = device.displayName[:-1]
		else:
			strippedDeviceName = device.displayName
		self.logPrint(f"displayname is {strippedDeviceName}")

		tankList = list()
		for item in deviceTypes:
			# if fresh water tank for exampleis in displayname
			if strippedDeviceName in item.displayName:
				tankList.append(item)

		if len(tankList) > 1:
			self.logPrint(f"tank list is {tankList} +2")
			if tankType == 4 and device.displayName == 'fresh water tank 1':
				self._tank1 = 20.5 * switchNumber
			if tankType == 4 and device.displayName == 'fresh water tank 2':
				result = self._tank1 + (20.5 * switchNumber)
				return f"that means {result} litres of fresh water available"


		else:
			if tankType == 4 and device.displayName == 'grey water tank 1':
				result = 20.5 * switchNumber
				return f"that equates to roughly {result} litres "

			if tankType == 3:
				result = 13.3 * switchNumber
				return f"that means approximately {result} litres "

