"""Telegram bot implementation with all handlers and logic."""

import logging
import re
from typing import Optional, List, Dict, Any

import telebot
from telebot import types
from telebot.types import Message, CallbackQuery

from config import Config
from db import Database
from states import StateManager, UserState


logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot class with all handlers and logic."""
    
    def __init__(self, config: Config, database: Database):
        """Initialize bot with config and database."""
        self.config = config
        self.db = database
        self.bot = telebot.TeleBot(config.telegram_bot_token)
        self.state_manager = StateManager()
        
        # Register all handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register all message and callback handlers."""
        # Command handlers
        self.bot.message_handler(commands=['start'])(self.handle_start)
        self.bot.message_handler(commands=['help'])(self.handle_help)
        self.bot.message_handler(commands=['events'])(self.handle_events)
        self.bot.message_handler(commands=['book'])(self.handle_book)
        self.bot.message_handler(commands=['mybookings'])(self.handle_my_bookings)
        self.bot.message_handler(commands=['feedback'])(self.handle_feedback)
        self.bot.message_handler(commands=['cancel'])(self.handle_cancel)
        
        # Admin commands
        self.bot.message_handler(commands=['admin_bookings'])(self.handle_admin_bookings)
        self.bot.message_handler(commands=['admin_events'])(self.handle_admin_events)
        self.bot.message_handler(commands=['event_feedback'])(self.handle_event_feedback)
        
        # Text message handlers for different states
        self.bot.message_handler(func=lambda message: True)(self.handle_text_message)
        
        # Callback query handlers
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback_query)
    
    def start_polling(self) -> None:
        """Start bot polling."""
        logger.info("Bot started polling...")
        self.bot.infinity_polling()
    
    # Utility methods
    def _get_main_menu_keyboard(self) -> types.ReplyKeyboardMarkup:
        """Create main menu keyboard."""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(
            types.KeyboardButton("📅 Расписание"),
            types.KeyboardButton("🎫 Забронировать")
        )
        keyboard.add(
            types.KeyboardButton("📋 Мои брони"),
            types.KeyboardButton("💬 Оставить отзыв")
        )
        return keyboard
    
    def _format_event(self, event: Dict[str, Any], show_book_button: bool = True) -> str:
        """Format event information for display."""
        category_emoji = {
            'concert': '🎵',
            'movie': '🎬',
            'play': '🎭'
        }
        
        emoji = category_emoji.get(event['category'], '🎪')
        time_str = f" в {event['time']}" if event['time'] else ""
        
        text = (f"{emoji} {event['title']}\n"
                f"📅 {event['date']}{time_str}\n"
                f"🏷️ Категория: {event['category']}\n"
                f"💰 Цена: {event['base_ticket_price']:.0f} ₽")
        
        return text
    
    def _format_booking(self, booking: Dict[str, Any]) -> str:
        """Format booking information for display."""
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'cancelled': '❌'
        }
        
        emoji = status_emoji.get(booking['status'], '❓')
        time_str = f" в {booking['time']}" if booking['time'] else ""
        
        return (f"{emoji} Бронь #{booking['id']}\n"
                f"🎪 {booking['title']}\n"
                f"📅 {booking['date']}{time_str}\n"
                f"🎫 Билетов: {booking['tickets_count']}\n"
                f"💰 Сумма: {booking['total_price']:.0f} ₽\n"
                f"📊 Статус: {booking['status']}")
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return self.config.is_admin(user_id)
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        # Simple validation: starts with +7 or 8, has 10-11 digits
        pattern = r'^(\+7|8)\d{10}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    # Command handlers
    def handle_start(self, message: Message) -> None:
        """Handle /start command."""
        self.state_manager.clear_session(message.from_user.id)
        
        welcome_text = (
            "🎪 Добро пожаловать в бот бронирования билетов!\n\n"
            "Здесь вы можете:\n"
            "📅 Посмотреть расписание мероприятий\n"
            "🎫 Забронировать билеты\n"
            "📋 Управлять своими бронями\n"
            "💬 Оставить отзыв о посещенных событиях\n\n"
            "Используйте меню ниже или команды:\n"
            "/events - расписание\n"
            "/book - забронировать\n"
            "/mybookings - мои брони\n"
            "/feedback - оставить отзыв\n"
            "/help - помощь"
        )
        
        self.bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=self._get_main_menu_keyboard()
        )
    
    def handle_help(self, message: Message) -> None:
        """Handle /help command."""
        help_text = (
            "🆘 Помощь по использованию бота\n\n"
            "📋 Основные команды:\n"
            "/events - посмотреть расписание мероприятий\n"
            "/book - забронировать билеты\n"
            "/mybookings - посмотреть свои брони\n"
            "/feedback - оставить отзыв\n"
            "/cancel - отменить текущее действие\n\n"
            "🎫 Процесс бронирования:\n"
            "1. Выберите мероприятие\n"
            "2. Укажите количество билетов\n"
            "3. Добавьте пожелания (необязательно)\n"
            "4. Введите имя и телефон\n"
            "5. Выберите способ оплаты\n"
            "6. Подтвердите бронь\n\n"
            "❓ Если возникли вопросы, обратитесь к организаторам."
        )
        
        self.bot.send_message(message.chat.id, help_text)
    
    def handle_events(self, message: Message) -> None:
        """Handle /events command - show event schedule."""
        events = self.db.get_events()
        
        if not events:
            self.bot.send_message(
                message.chat.id,
                "📅 Пока нет запланированных мероприятий."
            )
            return
        
        # Create category filter keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🎵 Концерты", callback_data="filter_concert"),
            types.InlineKeyboardButton("🎬 Фильмы", callback_data="filter_movie")
        )
        keyboard.add(
            types.InlineKeyboardButton("🎭 Спектакли", callback_data="filter_play"),
            types.InlineKeyboardButton("🎪 Все", callback_data="filter_all")
        )
        
        self.bot.send_message(
            message.chat.id,
            "📅 Расписание мероприятий\n\nВыберите категорию:",
            reply_markup=keyboard
        )
    
    def handle_book(self, message: Message) -> None:
        """Handle /book command - start booking flow."""
        self.state_manager.clear_session(message.from_user.id)
        self._show_events_for_booking(message.chat.id)
    
    def handle_my_bookings(self, message: Message) -> None:
        """Handle /mybookings command - show user's bookings."""
        bookings = self.db.get_bookings_by_user(message.from_user.id)
        
        if not bookings:
            self.bot.send_message(
                message.chat.id,
                "📋 У вас пока нет броней."
            )
            return
        
        for booking in bookings:
            text = self._format_booking(booking)
            
            keyboard = types.InlineKeyboardMarkup()
            if booking['status'] == 'pending':
                keyboard.add(
                    types.InlineKeyboardButton(
                        "❌ Отменить бронь",
                        callback_data=f"cancel_booking_{booking['id']}"
                    )
                )
            
            self.bot.send_message(
                message.chat.id,
                text,
                reply_markup=keyboard if keyboard.keyboard else None
            )
    
    def handle_feedback(self, message: Message) -> None:
        """Handle /feedback command - start feedback flow."""
        self.state_manager.clear_session(message.from_user.id)
        
        # Get events user attended
        attended_events = self.db.get_user_attended_events(message.from_user.id)
        
        if not attended_events:
            self.bot.send_message(
                message.chat.id,
                "💬 У вас пока нет посещенных мероприятий для отзыва."
            )
            return
        
        self.state_manager.set_state(message.from_user.id, UserState.FEEDBACK_SELECT_EVENT)
        
        keyboard = types.InlineKeyboardMarkup()
        for event in attended_events:
            keyboard.add(
                types.InlineKeyboardButton(
                    f"{event['title']} ({event['date']})",
                    callback_data=f"feedback_event_{event['id']}"
                )
            )
        
        self.bot.send_message(
            message.chat.id,
            "💬 Выберите мероприятие для отзыва:",
            reply_markup=keyboard
        )
    
    def handle_cancel(self, message: Message) -> None:
        """Handle /cancel command - cancel current operation."""
        self.state_manager.clear_session(message.from_user.id)
        self.bot.send_message(
            message.chat.id,
            "❌ Операция отменена.",
            reply_markup=self._get_main_menu_keyboard()
        )
    
    # Admin handlers
    def handle_admin_bookings(self, message: Message) -> None:
        """Handle /admin_bookings command."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Недостаточно прав.")
            return
        
        bookings = self.db.get_recent_bookings(20)
        
        if not bookings:
            self.bot.send_message(message.chat.id, "📋 Нет броней.")
            return
        
        for booking in bookings:
            text = (f"🎫 Бронь #{booking['id']}\n"
                   f"🎪 {booking['title']}\n"
                   f"📅 {booking['date']}\n"
                   f"👤 {booking['customer_name']}\n"
                   f"📞 {booking['customer_phone']}\n"
                   f"🎫 Билетов: {booking['tickets_count']}\n"
                   f"💰 Сумма: {booking['total_price']:.0f} ₽\n"
                   f"📊 Статус: {booking['status']}\n"
                   f"📝 Пожелания: {booking['notes'] or 'Нет'}")
            
            keyboard = types.InlineKeyboardMarkup()
            if booking['status'] == 'pending':
                keyboard.add(
                    types.InlineKeyboardButton(
                        "✅ Подтвердить",
                        callback_data=f"admin_confirm_{booking['id']}"
                    ),
                    types.InlineKeyboardButton(
                        "❌ Отменить",
                        callback_data=f"admin_cancel_{booking['id']}"
                    )
                )
            
            self.bot.send_message(
                message.chat.id,
                text,
                reply_markup=keyboard if keyboard.keyboard else None
            )
    
    def handle_admin_events(self, message: Message) -> None:
        """Handle /admin_events command."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Недостаточно прав.")
            return
        
        events = self.db.get_all_events()
        
        if not events:
            self.bot.send_message(message.chat.id, "📅 Нет мероприятий.")
            return
        
        text = "📅 Все мероприятия:\n\n"
        for event in events:
            text += f"ID: {event['id']} | {self._format_event(event, False)}\n\n"
        
        # Split long messages
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for part in parts:
                self.bot.send_message(message.chat.id, part)
        else:
            self.bot.send_message(message.chat.id, text)
    
    def handle_event_feedback(self, message: Message) -> None:
        """Handle /event_feedback <event_id> command."""
        if not self._is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Недостаточно прав.")
            return
        
        try:
            event_id = int(message.text.split()[1])
        except (IndexError, ValueError):
            self.bot.send_message(
                message.chat.id,
                "❌ Использование: /event_feedback <event_id>"
            )
            return
        
        feedback_list = self.db.get_feedback_by_event(event_id)
        
        if not feedback_list:
            self.bot.send_message(
                message.chat.id,
                f"💬 Нет отзывов для мероприятия ID {event_id}."
            )
            return
        
        text = f"💬 Отзывы для мероприятия ID {event_id}:\n\n"
        for feedback in feedback_list:
            rating_str = f" (⭐ {feedback['rating']})" if feedback['rating'] else ""
            text += (f"👤 User ID: {feedback['user_id']}{rating_str}\n"
                    f"💬 {feedback['text']}\n"
                    f"📅 {feedback['created_at'][:10]}\n\n")
        
        self.bot.send_message(message.chat.id, text)
    
    # Text message handler
    def handle_text_message(self, message: Message) -> None:
        """Handle text messages based on current state."""
        user_id = message.from_user.id
        state = self.state_manager.get_state(user_id)
        text = message.text.strip()
        
        # Handle menu buttons
        if text == "📅 Расписание":
            self.handle_events(message)
            return
        elif text == "🎫 Забронировать":
            self.handle_book(message)
            return
        elif text == "📋 Мои брони":
            self.handle_my_bookings(message)
            return
        elif text == "💬 Оставить отзыв":
            self.handle_feedback(message)
            return
        
        # Handle state-specific input
        if state == UserState.BOOKING_ENTER_TICKETS:
            self._handle_booking_tickets_input(message)
        elif state == UserState.BOOKING_ENTER_NOTES:
            self._handle_booking_notes_input(message)
        elif state == UserState.BOOKING_ENTER_NAME:
            self._handle_booking_name_input(message)
        elif state == UserState.BOOKING_ENTER_PHONE:
            self._handle_booking_phone_input(message)
        elif state == UserState.FEEDBACK_ENTER_TEXT:
            self._handle_feedback_text_input(message)
        else:
            # Default response for unrecognized input
            self.bot.send_message(
                message.chat.id,
                "❓ Не понимаю. Используйте меню или команды.",
                reply_markup=self._get_main_menu_keyboard()
            )
    
    # Callback query handler
    def handle_callback_query(self, call: CallbackQuery) -> None:
        """Handle inline keyboard button presses."""
        user_id = call.from_user.id
        data = call.data
        
        try:
            # Event filtering
            if data.startswith("filter_"):
                category = data.split("_")[1]
                self._show_filtered_events(call.message.chat.id, category, call.message.message_id)
            
            # Event booking
            elif data.startswith("book_event_"):
                event_id = int(data.split("_")[2])
                self._start_booking_flow(call.message.chat.id, user_id, event_id)
            
            # Feedback event selection
            elif data.startswith("feedback_event_"):
                event_id = int(data.split("_")[2])
                self._start_feedback_flow(call.message.chat.id, user_id, event_id)
            
            # Booking management
            elif data.startswith("cancel_booking_"):
                booking_id = int(data.split("_")[2])
                self._cancel_user_booking(call.message.chat.id, user_id, booking_id)
            
            # Payment method selection
            elif data.startswith("payment_"):
                payment_method = data.split("_")[1]
                self._handle_payment_selection(call.message.chat.id, user_id, payment_method)
            
            # Skip notes
            elif data == "skip_notes":
                self._handle_skip_notes(call.message.chat.id, user_id)
            
            # Feedback rating
            elif data.startswith("rating_"):
                rating = int(data.split("_")[1])
                self._handle_feedback_rating(call.message.chat.id, user_id, rating)
            
            # Admin actions
            elif data.startswith("admin_confirm_"):
                booking_id = int(data.split("_")[2])
                self._admin_confirm_booking(call.message.chat.id, user_id, booking_id)
            
            elif data.startswith("admin_cancel_"):
                booking_id = int(data.split("_")[2])
                self._admin_cancel_booking(call.message.chat.id, user_id, booking_id)
            
            # Answer callback to remove loading state
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    # Event display methods
    def _show_filtered_events(self, chat_id: int, category: str, message_id: int) -> None:
        """Show events filtered by category."""
        if category == "all":
            events = self.db.get_events()
        else:
            events = self.db.get_events(category)
        
        if not events:
            text = "📅 Нет мероприятий в выбранной категории."
            keyboard = None
        else:
            text = f"📅 Мероприятия ({category if category != 'all' else 'все категории'}):\n\n"
            keyboard = types.InlineKeyboardMarkup()
            
            for event in events:
                text += self._format_event(event, False) + "\n\n"
                keyboard.add(
                    types.InlineKeyboardButton(
                        f"🎫 Забронировать: {event['title'][:30]}...",
                        callback_data=f"book_event_{event['id']}"
                    )
                )
        
        try:
            self.bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=keyboard
            )
        except Exception:
            # If edit fails, send new message
            self.bot.send_message(chat_id, text, reply_markup=keyboard)
    
    def _show_events_for_booking(self, chat_id: int) -> None:
        """Show events for booking selection."""
        events = self.db.get_events()
        
        if not events:
            self.bot.send_message(chat_id, "📅 Пока нет доступных мероприятий для бронирования.")
            return
        
        self.state_manager.set_state(chat_id, UserState.BOOKING_SELECT_EVENT)
        
        keyboard = types.InlineKeyboardMarkup()
        for event in events:
            keyboard.add(
                types.InlineKeyboardButton(
                    f"{event['title']} - {event['date']} ({event['base_ticket_price']:.0f}₽)",
                    callback_data=f"book_event_{event['id']}"
                )
            )
        
        self.bot.send_message(
            chat_id,
            "🎫 Выберите мероприятие для бронирования:",
            reply_markup=keyboard
        )
    
    # Booking flow methods
    def _start_booking_flow(self, chat_id: int, user_id: int, event_id: int) -> None:
        """Start booking flow for selected event."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.bot.send_message(chat_id, "❌ Мероприятие не найдено.")
            return
        
        # Store event in booking data
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.event_id = event_id
        
        # Set state and ask for tickets count
        self.state_manager.set_state(user_id, UserState.BOOKING_ENTER_TICKETS)
        
        text = (f"🎫 Бронирование: {event['title']}\n"
                f"📅 {event['date']}\n"
                f"💰 Цена за билет: {event['base_ticket_price']:.0f} ₽\n\n"
                f"Сколько билетов вы хотите забронировать? (введите число)")
        
        self.bot.send_message(chat_id, text)
    
    def _handle_booking_tickets_input(self, message: Message) -> None:
        """Handle tickets count input."""
        user_id = message.from_user.id
        
        try:
            tickets_count = int(message.text.strip())
            if tickets_count <= 0:
                raise ValueError("Invalid count")
        except ValueError:
            self.bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите корректное количество билетов (положительное число)."
            )
            return
        
        # Store tickets count
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.tickets_count = tickets_count
        
        # Calculate total price
        event = self.db.get_event_by_id(booking_data.event_id)
        total_price = event['base_ticket_price'] * tickets_count
        
        # Ask for notes
        self.state_manager.set_state(user_id, UserState.BOOKING_ENTER_NOTES)
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_notes"))
        
        text = (f"🎫 Билетов: {tickets_count}\n"
                f"💰 Общая стоимость: {total_price:.0f} ₽\n\n"
                f"Есть ли у вас особые пожелания или комментарии? "
                f"(напишите текст или нажмите 'Пропустить')")
        
        self.bot.send_message(message.chat.id, text, reply_markup=keyboard)
    
    def _handle_booking_notes_input(self, message: Message) -> None:
        """Handle notes input."""
        user_id = message.from_user.id
        notes = message.text.strip()
        
        # Store notes
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.notes = notes if notes else None
        
        self._ask_for_customer_name(message.chat.id, user_id)
    
    def _handle_skip_notes(self, chat_id: int, user_id: int) -> None:
        """Handle skip notes button."""
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.notes = None
        
        self._ask_for_customer_name(chat_id, user_id)
    
    def _ask_for_customer_name(self, chat_id: int, user_id: int) -> None:
        """Ask for customer name."""
        self.state_manager.set_state(user_id, UserState.BOOKING_ENTER_NAME)
        
        self.bot.send_message(
            chat_id,
            "👤 Введите ваше имя и фамилию:"
        )
    
    def _handle_booking_name_input(self, message: Message) -> None:
        """Handle customer name input."""
        user_id = message.from_user.id
        name = message.text.strip()
        
        if len(name) < 2:
            self.bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите корректное имя (минимум 2 символа)."
            )
            return
        
        # Store name
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.customer_name = name
        
        # Ask for phone
        self.state_manager.set_state(user_id, UserState.BOOKING_ENTER_PHONE)
        
        self.bot.send_message(
            message.chat.id,
            "📞 Введите ваш номер телефона (например: +79991234567):"
        )
    
    def _handle_booking_phone_input(self, message: Message) -> None:
        """Handle phone number input."""
        user_id = message.from_user.id
        phone = message.text.strip()
        
        if not self._validate_phone(phone):
            self.bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите корректный номер телефона (начинается с +7 или 8)."
            )
            return
        
        # Store phone
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.customer_phone = phone
        
        # Ask for payment method
        self._ask_for_payment_method(message.chat.id, user_id)
    
    def _ask_for_payment_method(self, chat_id: int, user_id: int) -> None:
        """Ask for payment method selection."""
        self.state_manager.set_state(user_id, UserState.BOOKING_SELECT_PAYMENT)
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("💳 Онлайн (заглушка)", callback_data="payment_online_stub"),
            types.InlineKeyboardButton("💵 Наличными на месте", callback_data="payment_cash")
        )
        
        self.bot.send_message(
            chat_id,
            "💳 Выберите способ оплаты:",
            reply_markup=keyboard
        )
    
    def _handle_payment_selection(self, chat_id: int, user_id: int, payment_method: str) -> None:
        """Handle payment method selection and complete booking."""
        booking_data = self.state_manager.get_booking_data(user_id)
        booking_data.payment_method = payment_method
        
        # Get event details
        event = self.db.get_event_by_id(booking_data.event_id)
        total_price = event['base_ticket_price'] * booking_data.tickets_count
        
        # Create booking in database
        try:
            booking_id = self.db.create_booking(
                event_id=booking_data.event_id,
                user_id=user_id,
                username=getattr(self.bot.get_chat(user_id), 'username', None),
                customer_name=booking_data.customer_name,
                customer_phone=booking_data.customer_phone,
                tickets_count=booking_data.tickets_count,
                notes=booking_data.notes,
                payment_method=payment_method,
                total_price=total_price
            )
            
            # Send confirmation
            payment_text = "Онлайн (заглушка)" if payment_method == "online_stub" else "Наличными на месте"
            
            confirmation_text = (
                f"✅ Ваша заявка на бронирование принята!\n\n"
                f"🎫 Номер заявки: #{booking_id}\n"
                f"🎪 Мероприятие: {event['title']}\n"
                f"📅 Дата: {event['date']}\n"
                f"👤 Имя: {booking_data.customer_name}\n"
                f"📞 Телефон: {booking_data.customer_phone}\n"
                f"🎫 Билетов: {booking_data.tickets_count}\n"
                f"💰 Сумма: {total_price:.0f} ₽\n"
                f"💳 Оплата: {payment_text}\n"
                f"📝 Пожелания: {booking_data.notes or 'Нет'}\n\n"
                f"📊 Статус: Ожидает подтверждения организатором\n\n"
                f"⚠️ Оплата не производится в боте. "
                f"Вы выбрали способ оплаты: {payment_text}"
            )
            
            self.bot.send_message(
                chat_id,
                confirmation_text,
                reply_markup=self._get_main_menu_keyboard()
            )
            
            # Clear session
            self.state_manager.clear_session(user_id)
            
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            self.bot.send_message(
                chat_id,
                "❌ Произошла ошибка при создании брони. Попробуйте еще раз."
            )
    
    # Feedback flow methods
    def _start_feedback_flow(self, chat_id: int, user_id: int, event_id: int) -> None:
        """Start feedback flow for selected event."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.bot.send_message(chat_id, "❌ Мероприятие не найдено.")
            return
        
        # Store event in feedback data
        feedback_data = self.state_manager.get_feedback_data(user_id)
        feedback_data.event_id = event_id
        
        # Ask for feedback text
        self.state_manager.set_state(user_id, UserState.FEEDBACK_ENTER_TEXT)
        
        text = (f"💬 Отзыв о мероприятии: {event['title']}\n"
                f"📅 {event['date']}\n\n"
                f"Напишите ваш отзыв (1-500 символов):")
        
        self.bot.send_message(chat_id, text)
    
    def _handle_feedback_text_input(self, message: Message) -> None:
        """Handle feedback text input."""
        user_id = message.from_user.id
        text = message.text.strip()
        
        if len(text) < 1 or len(text) > 500:
            self.bot.send_message(
                message.chat.id,
                "❌ Отзыв должен содержать от 1 до 500 символов."
            )
            return
        
        # Store feedback text
        feedback_data = self.state_manager.get_feedback_data(user_id)
        feedback_data.text = text
        
        # Ask for rating
        self.state_manager.set_state(user_id, UserState.FEEDBACK_ENTER_RATING)
        
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        keyboard.add(*[
            types.InlineKeyboardButton(f"{i}⭐", callback_data=f"rating_{i}")
            for i in range(1, 6)
        ])
        
        self.bot.send_message(
            message.chat.id,
            "⭐ Оцените мероприятие от 1 до 5 звезд:",
            reply_markup=keyboard
        )
    
    def _handle_feedback_rating(self, chat_id: int, user_id: int, rating: int) -> None:
        """Handle feedback rating selection and save feedback."""
        feedback_data = self.state_manager.get_feedback_data(user_id)
        feedback_data.rating = rating
        
        # Save feedback to database
        try:
            feedback_id = self.db.create_feedback(
                event_id=feedback_data.event_id,
                user_id=user_id,
                text=feedback_data.text,
                rating=rating
            )
            
            self.bot.send_message(
                chat_id,
                f"✅ Спасибо за отзыв! Ваш отзыв сохранен под номером #{feedback_id}",
                reply_markup=self._get_main_menu_keyboard()
            )
            
            # Clear session
            self.state_manager.clear_session(user_id)
            
        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            self.bot.send_message(
                chat_id,
                "❌ Произошла ошибка при сохранении отзыва. Попробуйте еще раз."
            )
    
    # Booking management methods
    def _cancel_user_booking(self, chat_id: int, user_id: int, booking_id: int) -> None:
        """Cancel user's booking."""
        # Verify booking belongs to user
        booking = self.db.get_booking_by_id(booking_id)
        if not booking or booking['user_id'] != user_id:
            self.bot.send_message(chat_id, "❌ Бронь не найдена.")
            return
        
        if booking['status'] != 'pending':
            self.bot.send_message(chat_id, "❌ Можно отменить только ожидающие брони.")
            return
        
        # Update booking status
        if self.db.update_booking_status(booking_id, 'cancelled'):
            self.bot.send_message(chat_id, f"✅ Бронь #{booking_id} отменена.")
        else:
            self.bot.send_message(chat_id, "❌ Ошибка при отмене брони.")
    
    # Admin methods
    def _admin_confirm_booking(self, chat_id: int, user_id: int, booking_id: int) -> None:
        """Admin confirm booking."""
        if not self._is_admin(user_id):
            self.bot.send_message(chat_id, "❌ Недостаточно прав.")
            return
        
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            self.bot.send_message(chat_id, "❌ Бронь не найдена.")
            return
        
        if self.db.update_booking_status(booking_id, 'confirmed'):
            self.bot.send_message(chat_id, f"✅ Бронь #{booking_id} подтверждена.")
            
            # Notify user
            try:
                self.bot.send_message(
                    booking['user_id'],
                    f"✅ Ваша бронь #{booking_id} подтверждена организатором!"
                )
            except Exception as e:
                logger.error(f"Failed to notify user {booking['user_id']}: {e}")
        else:
            self.bot.send_message(chat_id, "❌ Ошибка при подтверждении брони.")
    
    def _admin_cancel_booking(self, chat_id: int, user_id: int, booking_id: int) -> None:
        """Admin cancel booking."""
        if not self._is_admin(user_id):
            self.bot.send_message(chat_id, "❌ Недостаточно прав.")
            return
        
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            self.bot.send_message(chat_id, "❌ Бронь не найдена.")
            return
        
        if self.db.update_booking_status(booking_id, 'cancelled'):
            self.bot.send_message(chat_id, f"❌ Бронь #{booking_id} отменена администратором.")
            
            # Notify user
            try:
                self.bot.send_message(
                    booking['user_id'],
                    f"❌ Ваша бронь #{booking_id} была отменена организатором."
                )
            except Exception as e:
                logger.error(f"Failed to notify user {booking['user_id']}: {e}")
        else:
            self.bot.send_message(chat_id, "❌ Ошибка при отмене брони.")