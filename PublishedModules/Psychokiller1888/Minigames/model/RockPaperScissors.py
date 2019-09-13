import os
import random

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class RockPaperScissors(MiniGame):

	_INTENT_PLAY_GAME = Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS = Intent('AnswerRockPaperOrScissors', isProtected=True)

	def __init__(self):
		super().__init__()


	@property
	def intents(self) -> list:
		return [
			self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS
		]


	def start(self, session: DialogSession):
		super().start(session)

		SuperManager.getInstance().mqttManager.continueDialog(
			sessionId=session.sessionId,
			text=SuperManager.getInstance().talkManager.randomTalk(talk='rockPaperScissorsStart', module='Minigames'),
			intentFilter=[self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS],
			previousIntent=self._INTENT_PLAY_GAME
		)


	def onMessage(self, intent: str, session: DialogSession):
		if intent == self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS:
			me = random.choice(['rock', 'paper', 'scissors'])

			SuperManager.getInstance().mqttManager.playSound(
				soundFile=os.path.join(commons.rootDir(), 'modules', 'Minigames', 'sounds', 'drum_suspens'),
				siteId=session.siteId,
				absolutePath=True
			)

			redQueen = SuperManager.getInstance().moduleManager.getModuleInstance('RedQueen')
			redQueen.changeRedQueenStat('happiness', 5)
			player = session.slotValue('RockPaperOrScissors')
			# tie
			if player == me:
				result = 'rockPaperScissorsTie'
			# player wins
			elif player == 'rock' and me == 'scissors' or player == 'paper' and me == 'rock' or player == 'scissors' and me == 'paper':
				result = 'rockPaperScissorsWins'
				redQueen.changeRedQueenStat('frustration', 2)
			# alice wins
			else:
				result = 'rockPaperScissorsLooses'
				redQueen.changeRedQueenStat('frustration', -5)
				redQueen.changeRedQueenStat('happiness', 5)

			SuperManager.getInstance().mqttManager.continueDialog(
				sessionId=session.sessionId,
				text=SuperManager.getInstance().talkManager.randomTalk(
					talk=result,
					module='Minigames'
				).format(SuperManager.getInstance().languageManager.getTranslations(module='Minigames', key=me, toLang=SuperManager.getInstance().languageManager.activeLanguage)[0]),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_PLAY_GAME,
				customData={
					'askRetry': True
				}
			)