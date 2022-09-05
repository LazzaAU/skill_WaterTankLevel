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
		device = self.DeviceManager.getDeviceByName("grey water tank 1")
		self._AliceDev.logPrint(f"Device is {device}")
		if not device:
			return
		# If grey water reporting is enabled in the skill
		if self.getConfig(key='greyWaterReporting'):
			# and user is not sleeping and low level sensor is on...
			if device.getParam('Switch1') == 'ON' and not self.UserManager.checkIfAllUser('sleeping'):
				# If only the first and second sensors are on, , say its a quarter full
				if device.getParam('Switch2') == 'ON' and device.getParam('Switch3') == 'OFF' and device.getParam('Switch4') == 'OFF':
					self.say(
						text='Your grey water tank is a quarter full. Time to keep a eye on it'
					)
					# Else if the second and third sensors are on, say its 3 quarters full
				elif device.getParam('Switch2') == 'ON' and device.getParam('Switch3') == 'ON' and device.getParam('Switch4') == 'OFF':
					self.say(
						text='Your grey water tank is three quarters full. Is the valve open ?'
					)
					# Else if all sensors are on, say its full
				else:
					self.say(
						text='Your grey water is full. It NEEDS attention now'
					)
	@IntentHandler('disableGreywaterMonitoring')
	def greywaterSetting(self):
		if self.getConfig(key='greyWaterReporting'):
			self.say(
				text="Turning off Grey water monitoring"
			)
			self.updateConfig(key='greyWaterReporting', value=False)
		else:
			self.say(
				text="Turning on Grey water monitoring"
			)
			self.updateConfig(key='greyWaterReporting', value=True)

	@IntentHandler('disableRainMonitoring')
	def disableMonitoring(self):
		homeAssistant = HomeAssistant.HomeAssistant()

		device = self.DeviceManager.getDeviceByName('rainwater hose connected')
		homeAssistant.deviceClicked(uid=device.uid)
		self._AliceDev.logPrint(f"device is hopefully rainwater hose ->> {device}")
		if device.getParam('state') == 'on':
			pump = self.DeviceManager.getDeviceByName('rain water pump')
			if pump.getParam('state') == 'on':
				homeAssistant.deviceClicked(uid=pump.uid)

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
			self._AliceDev.logPrint(f"That device doesnt exist")
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

