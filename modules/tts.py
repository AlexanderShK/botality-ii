from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile
from providers.tts_provider import tts, remote_tts, convert_to_ogg, so_vits_svc
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
from utils import download_audio
import asyncio
import tempfile

class TextToSpeechModule:
  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.tts_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    
    so_vits_svc_voices = list(v['voice'].lower().replace('-','') for v in config.tts_so_vits_svc_voices)
    all_voices = [*config.tts_voices, *so_vits_svc_voices]
    @dp.message(Command(commands=["tts", *config.tts_voices, *so_vits_svc_voices]), flags={"long_operation": "record_audio"})
    async def command_tts_handler(message: Message, command: CommandObject) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          #show helper message if no voice is selected
          if command.command == "tts" or not command.args or str(command.args).strip() == "" or ('-help' in str(command.args)):
            return await message.answer(f"usage: {' '.join(['/' + x for x in all_voices])} text, /revoice [recording]\nUse the commands like /command@botname \n{config.tts_credits}")
          voice = command.command
          text = str(command.args)
          task_function = remote_tts if config.tts_mode != 'local' else tts
          wrapped_runner = semaphore_wrapper(self.semaphore, task_function)
          error, data = await wrapped_runner(voice, text)
          if error:
            return await message.answer(f"Error, <b>{error}</b>")
          else:
            audio = BufferedInputFile(convert_to_ogg(data), 'tts.ogg')
            return await message.answer_voice(voice=audio)
    
    if config.tts_enable_so_vits_svc:
      @dp.message(Command(commands=["revoice", "sts"]), flags={"long_operation": "record_audio"})
      async def revoice(message: Message, command: CommandObject) -> None:
        voice = str(command.args).split(' ')[0] if command.args else so_vits_svc_voices[0]
        voice = voice if voice in so_vits_svc_voices else None
        if not voice:
          return await message.answer("<b>Voice not found</b>, available speech-to-speech voices: " +
           ", ".join(so_vits_svc_voices))
        if message.reply_to_message:
          if message.reply_to_message.voice:
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
              await download_audio(bot, message.reply_to_message.voice.file_id, temp_file.name)
              wrapped_runner = semaphore_wrapper(self.semaphore, so_vits_svc)
              error, data = await wrapped_runner(voice, None, temp_file.name)
              if error:
                return await message.answer(f"Error, <b>{error}</b>")
              else:
                audio = BufferedInputFile(convert_to_ogg(data), 'tts.ogg')
                return await message.answer_voice(voice=audio)
        return await message.answer("No audio found. Use this command replying to voice messages")

    bot.reply_tts = command_tts_handler



















