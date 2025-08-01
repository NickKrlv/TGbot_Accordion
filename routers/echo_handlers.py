from aiogram import Router, types, Bot
from routers.message_counter import count_group_messages


router = Router(name=__name__)



@router.message(lambda message: message.chat.type in ["group", "supergroup"])
async def echo(message: types.Message):
    await count_group_messages(message)

    # if message.photo:
    #     await message.reply(f"Алло, я робот. Я нихуя не вижу, чё там на картинке.")

    # if message.from_user.id == 337660143:
    #     try:
    #         await message.bot.set_message_reaction(
    #             chat_id=message.chat.id,
    #             message_id=message.message_id,
    #             reaction=[types.ReactionTypeEmoji(emoji="🤡")]
    #         )
    #     except Exception as e:
    #         print(f"Ошибка при установке реакции: {e}")
