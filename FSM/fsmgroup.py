from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command


from database import Posts
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def kb_hashtags():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Подарки')
    keyboard.button(text='Здоровье')
    keyboard.button(text='Спорт')
    keyboard.button(text='Животные')
    keyboard.button(text='Дом и сад')
    keyboard.button(text='Электроника')
    keyboard.button(text='Продукты питания')
    keyboard.button(text='Детям')
    keyboard.button(text='Мужчинам')
    keyboard.button(text='Женщинам')
    keyboard.adjust(2, 2, 2, 2, 2, 2, 2, 2)
    return keyboard.as_markup(resize_keyboard=True)


def kb_service():
    kb_service = InlineKeyboardBuilder()
    kb_service.button(text='Правила Сервиса', callback_data='rules')
    kb_service.adjust(1)
    return kb_service


def kb_cancel():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Отмена')
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_continue():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Продолжить')
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_cancel_or_accept():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Отмена')
    keyboard.button(text='Перейти к оплате')
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_start():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Вернуться к истокам')
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_pay():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Оплатить')
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


class Post(StatesGroup):
    Hashtag = State()
    name = State()
    Description = State()
    link = State()
    photo_id = State()
    id = State()
    chat_id = State()
    payment = State()
    confirmation = State()


cancel_fsm_router = Router()
FoeTracer = Router()






@cancel_fsm_router.message(F.text.casefold() == 'Отмена' or 'Продолжить' or 'Вернуться к истокам')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Post.Hashtag)
    if message.text == 'Вернуться к истокам':
        await message.answer('Вы вернулись к истокам. Создайте свой пост. Возможно, очередной...', reply_markup=kb_start())
    elif message.text == 'Отмена':
        await message.answer('Действие отменено. Выберите категорию', reply_markup=kb_hashtags())


@FoeTracer.message(Command('start'))
async def hashtag(message: Message, state: FSMContext):
    await message.answer('Приветствую вас в Авангарде. Давайте создадим ваше предложение... Но для начала вам кое-что расскажем...', reply_markup=kb_continue())
    await message.answer('Ознакомьтесь с правилами пользования, если вы ещё их не читали', reply_markup=kb_service().as_markup())
    await state.set_state(Post.Hashtag)


@FoeTracer.callback_query(F.data == 'rules')
async def handle_callback_query(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.data == 'rules':
        await bot.send_message(chat_id=callback.from_user.id, text="""
        В нашем сервисе нельзя загружать посты 18+, спамить посты без оплаты, загружать нецензурные материалы, .
        Отклонённые посты лежат в закрытом канале до выяснения причин между модераторами и создателем.
        Если вашего поста нет в течении 48 часов, значит он был отклонён окончательно и вы нарушили правила сообщества
        Посты выкладываются в течении 24 часов, за редким исключением могут быть задержки. В большинстве случаев это происходит в течении часа..
        """, reply_markup=kb_continue())
        await state.set_state(Post.Hashtag)
        await callback.answer()


@FoeTracer.message(Post.Hashtag)
async def name(message: Message, state: FSMContext):
    ms = message.text
    if ms in ['Подарки', 'Здоровье', 'Спорт', 'Животные', 'Дом и сад', 'Электроника', 'Продукты питания', 'Детям', 'Мужчинам', 'Женщинам']:
        await state.update_data(hashtag="#" + message.text)
        await state.update_data(id=message.from_user.id)
        await state.update_data(chat_id=message.chat.id)
        await message.answer('Сколько стоит ваш товар?\n(Укажите цену цифрой без букв, например 763 или 1299)', reply_markup=kb_cancel())
        await state.set_state(Post.name)
    else:
        await message.answer('Пожалуйста, выберите одну из категорий', reply_markup=kb_hashtags())
        await state.set_state(Post.Hashtag)


@FoeTracer.message(Post.name)
async def description(message: Message, state: FSMContext):
    await state.update_data(name=message.text + ' Rub.')
    await message.answer('Введите описание вашего продукта', reply_markup=kb_cancel())
    await state.set_state(Post.Description)


@FoeTracer.message(Post.Description)
async def link(message: Message, state: FSMContext):
    await state.update_data(Description=message.text)
    await message.answer('Ссылка на ваш продукт...', reply_markup=kb_cancel())
    await state.set_state(Post.link)


@FoeTracer.message(Post.link)
async def photo(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    if not message.text.startswith('http://') and not message.text.startswith('https://'):
        await message.answer('Ссылка должна начинаться с http:// или https://')
        return
    else:
        await message.answer('Отправьте лицевое фото вашего продукта...', reply_markup=kb_cancel())
        await state.set_state(Post.photo_id)


@FoeTracer.message(Post.photo_id)
async def process_photo(message: Message, state: FSMContext):
    if message.photo is None:
        await message.answer('Пожалуйста, отправьте фото')
        return
    else:
        await state.set_state(Post.id)
        await state.update_data(photo_id=message.photo[-1].file_id)
        our_data = await state.get_data()
        photo = message.photo[-1]
        await message.bot.send_photo(photo=photo.file_id,
                                     caption=f'Ваш пост выглядит так:\n{our_data["hashtag"]}\n{our_data["name"]}\n{our_data["Description"]}\n{our_data["link"]}',
                                     chat_id=message.from_user.id)
        await message.answer('Если всё верно, нажмите "Перейти к оплате"', reply_markup=kb_cancel_or_accept())

        Posts.create(self=Posts(our_data))


@FoeTracer.message(Post.photo_id)
async def process_photo(message: Message, state: FSMContext):
    if message.photo is None:
        await message.answer('Пожалуйста, отправьте фото')
    else:
        await state.set_state(Post.id)
        await state.update_data(photo_id=message.photo[-1].file_id)
        our_data = await state.get_data()
        photo = message.photo[-1]
        await message.bot.send_photo(photo=photo.file_id,
                                     caption=f'Ваш пост выглядит так:\n{our_data["hashtag"]}\n{our_data["name"]}\n{our_data["Description"]}\n{our_data["link"]}',
                                     chat_id=message.from_user.id)
        await message.answer('Если всё верно, нажмите "Перейти к оплате"', reply_markup=kb_cancel_or_accept())
        Posts.create(self=Posts(our_data))


@FoeTracer.message(Post.id)
async def payment_info(message: Message, state: FSMContext):
    await message.answer(
        "Перевод на карту 👇\n"
        "Тинькофф 👑: 2200 7008 7844 6318\n"
        "ВТБ 💎: 2200 2460 0612 8725\n\n"
        "Комментарий не нужен.\n\n"
        "‼️ ВАЖНО: для завершения и отправки заказа сделайте ответ [Reply] на ЭТО СООБЩЕНИЕ и прикрепите к нему через 📎 скриншот 🧾 ЧЕКА об оплате.\n\n"
        "Для этого выберите: Сохранить чек.\n\n"
        "‼️ ПРИСЫЛАЙТЕ ИМЕННО ЧЕК, СКРИН О ПЕРЕВОДЕ НЕ ПОДТВЕРЖДАЕТ ПЛАТЕЖ\n\n"
        "За нарушение правил сообщества вас ждёт перманентная блокировка. Просим вас помнить о наших правилах.",
        reply_markup=kb_cancel()
    )
    await state.set_state(Post.confirmation)


@FoeTracer.message(Post.confirmation)
async def confirm_payment(message: Message, bot: Bot, state: FSMContext):
    if message.photo:
        our_data = await state.get_data()
        name = message.from_user.first_name
        username = message.from_user.username
        inline_keyboard = [
            [InlineKeyboardButton(text="Принять", callback_data="accept"),
             InlineKeyboardButton(text="Отклонить", callback_data="reject")]
        ]
        await bot.send_photo(photo=our_data["photo_id"],
                             caption=f'\n{our_data["hashtag"]}\n{our_data["name"]}\n{our_data["Description"]}\n{our_data["link"]}\n\n',
                             chat_id=-1002105581775, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
        await bot.send_photo(photo=message.photo[-1].file_id, caption=f'Чек об оплате пользователя {name}  @{username}', chat_id=-1002105581775)

        await state.set_state(Post.Hashtag)
        await message.answer('Ваш пост отправлен на модерацию. Если он не нарушает правила сообщества, он будет опубликован в течении 24 часов. Пока можете приступить к созданию нового поста.', reply_markup=kb_start())
    else:
        await message.answer('Пожалуйста, отправьте фото чека об оплате.')


@FoeTracer.callback_query()
async def accept(callback: CallbackQuery, state: FSMContext, bot: Bot):
    our_data = await state.get_data()

    if callback.data == 'accept':
        await bot.forward_message(chat_id=-1002012902708, from_chat_id=-1002105581775, message_id=callback.message.message_id, disable_notification=True)
        await bot.delete_message(chat_id=-1002105581775, message_id=callback.message.message_id)
    elif callback.data == 'reject':
        await bot.forward_message(chat_id=-1002003559111, from_chat_id=-1002105581775, message_id=callback.message.message_id, disable_notification=True)
        await bot.delete_message(chat_id=-1002105581775, message_id=callback.message.message_id)

    await callback.answer()
    await state.clear()
