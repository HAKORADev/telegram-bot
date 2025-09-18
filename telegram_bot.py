from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import g4f
import json
import os
import re
import time
from datetime import datetime, timedelta
import logging
import copy
import asyncio
import psutil
import platform
import threading
import atexit
import sys

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if not os.path.exists("token.json"):
    print("token.json not found. Please create token.json, set your token inside, and try again.")
    input("Press Enter to exit...")
    sys.exit(1)

with open("token.json", "r") as f:
    try:
        TELEGRAM_TOKEN = json.load(f).get("token", "").strip()
    except:
        TELEGRAM_TOKEN = ""

if not TELEGRAM_TOKEN:
    print("No token found in token.json. Please set your token and try again.")
    input("Press Enter to exit...")
    sys.exit(1)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "sp": "Español",
    "fr": "Français",
    "ru": "Русский",
    "ar": "العربية"
}
DEFAULT_LANGUAGE = "en"

def get_default_persona(language):
    personas = {
        "en": "You are a helpful assistant who speaks English. Be friendly and helpful in your responses.",
        "sp": "Eres un asistente útil que habla español. Sé amable y servicial en tus respuestas.",
        "fr": "Vous êtes un assistant utile qui parle français. Soyez amical et serviable dans vos réponses.",
        "ru": "Вы полезный помощник, который говорит на русском языке. Будьте дружелюбны и полезны в своих ответах.",
        "ar": "أنت مساعد مفيد يتحدث اللغة العربية. كن لطيفًا ومفيدًا في ردودك."
    }
    return personas.get(language, personas["en"])

LANGUAGE_STRINGS = {
    "start_message": {
        "en": """🎯 **Available Bot Commands:**
/start - Start conversation
/help - Show all commands
/clear - Clear conversation memory
/think - Deep thinking on specific text
/think_full - Analyze last 10 messages
/customize - Customize bot personality
/mystats - Show your statistics
/web - Internet search
/users_info - User statistics
/feedback - Send your opinion about the bot
/credits - Developer information
/server_info - Server information
🌐 **Language Settings:**
/en - Set language to English
/sp - Set language to Spanish
/fr - Set language to French
/ru - Set language to Russian
/ar - Set language to Arabic
💡 **Bot Features:**
- Remembers your previous conversation (for 2 days)
- Saves up to 100 messages in conversation
- Excellent language support
- Deep thinking mode for accurate responses
- Customize bot personality as you wish
- Advanced processing system (10 analysis stages)
- Preset system for saving custom personalities
- Advanced internet search
- Permanent data storage system
- Rating and feedback system
- Server monitoring and automatic downtime detection""",
        "sp": """🎯 **Comandos disponibles:**
/start - Iniciar conversación
/help - Mostrar todos los comandos
/clear - Borrar historial de conversación
/think - Pensamiento profundo sobre texto específico
/think_full - Analizar los últimos 10 mensajes
/customize - Personalizar personalidad del bot
/mystats - Mostrar tus estadísticas
/web - Búsqueda en internet
/users_info - Estadísticas de usuarios
/feedback - Enviar tu opinión sobre el bot
/credits - Información del desarrollador
/server_info - Información del servidor
🌐 **Configuración de idioma:**
/en - Establecer idioma a inglés
/sp - Establecer idioma a español
/fr - Establecer idioma a francés
/ru - Establecer idioma a ruso
/ar - Establecer idioma a árabe
💡 **Características del bot:**
- Recuerda tu conversación anterior (por 2 días)
- Guarda hasta 100 mensajes en la conversación
- Soporte excelente para varios idiomas
- Modo de pensamiento profundo para respuestas precisas
- Personaliza la personalidad del bot como desees
- Sistema de procesamiento avanzado (10 etapas de análisis)
- Sistema de preajustes para guardar personalidades personalizadas
- Búsqueda avanzada en internet
- Sistema de almacenamiento permanente
- Sistema de calificación y comentarios
- Monitoreo del servidor y detección automática de caídas""",
        "fr": """🎯 **Commandes disponibles :**
/start - Démarrer la conversation
/help - Afficher toutes les commandes
/clear - Effacer l'historique de conversation
/think - Réflexion approfondie sur un texte spécifique
/think_full - Analyser les 10 derniers messages
/customize - Personnaliser la personnalité du bot
/mystats - Afficher vos statistiques
/web - Recherche sur Internet
/users_info - Statistiques des utilisateurs
/feedback - Envoyer votre avis sur le bot
/credits - Informations sur le développeur
/server_info - Informations sur le serveur
🌐 **Paramètres de langue :**
/en - Définir la langue sur l'anglais
/sp - Définir la langue sur l'espagnol
/fr - Définir la langue sur le français
/ru - Définir la langue sur le russe
/ar - Définir la langue sur l'arabe
💡 **Fonctionnalités du bot :**
- Se souvient de votre conversation précédente (pendant 2 jours)
- Enregistre jusqu'à 100 messages dans la conversation
- Excellent support multilingue
- Mode de réflexion approfondie pour des réponses précises
- Personnalisez la personnalité du bot comme vous le souhaitez
- Système de traitement avancé (10 étapes d'analyse)
- Système de préréglages pour enregistrer des personnalités personnalisées
- Recherche Internet avancée
- Système de stockage permanent
- Système d'évaluation et de commentaires
- Surveillance du serveur et détection automatique des pannes""",
        "ru": """🎯 **Доступные команды бота:**
/start - Начать разговор
/help - Показать все команды
/clear - Очистить историю разговора
/think - Глубокое осмысление конкретного текста
/think_full - Проанализировать последние 10 сообщений
/customize - Настроить личность бота
/mystats - Показать вашу статистику
/web - Поиск в интернете
/users_info - Статистика пользователей
/feedback - Отправить ваше мнение о боте
/credits - Информация о разработчике
/server_info - Информация о сервере
🌐 **Настройки языка:**
/en - Установить язык на английский
/sp - Установить язык на испанский
/fr - Установить язык на французский
/ru - Установить язык на русский
/ar - Установить язык на арабский
💡 **Функции бота:**
- Запоминает ваш предыдущий разговор (на 2 дня)
- Сохраняет до 100 сообщений в разговоре
- Отличная поддержка нескольких языков
- Режим глубокого осмысления для точных ответов
- Настройте личность бота по вашему желанию
- Расширенная система обработки (10 этапов анализа)
- Система предустановок для сохранения пользовательских личностей
- Расширенный поиск в интернете
- Постоянная система хранения данных
- Система рейтинга и обратной связи
- Мониторинг сервера и автоматическое обнаружение простоев""",
        "ar": """🎯 **الاوامر المتاحة:**
/start - بدء المحادثة
/help - اظهار جميع الاوامر
/clear - مسح ذاكرة المحادثة
/think - تفكير عميق في نص محدد
/think_full - تحليل اخر 10 رسائل
/customize - تخصيص شخصية البوت
/mystats - اظهار احصائياتك
/web - بحث في الانترنت
/users_info - احصائيات المستخدمين
/feedback - ارسل رأيك عن البوت
/credits - معلومات المطور
/server_info - معلومات السيرفر
🌐 **اعدادات اللغة:**
/en - تغيير اللغة إلى الانجليزية
/sp - تغيير اللغة إلى الاسبانية
/fr - تغيير اللغة إلى الفرنسية
/ru - تغيير اللغة إلى الروسية
/ar - تغيير اللغة إلى العربية
💡 **مميزات البوت:**
- يتذكر محادثتك السابقة (لمدة يومين)
- يحفظ حتى 100 رسالة في المحادثة
- دعم ممتاز لعدة لغات
- وضع التفكير العميق للحصول على ردود دقيقة
- تخصيص شخصية البوت كما تشاء
- نظام معالجة متقدم (10 مراحل تحليل)
- نظام الـ Presets لحفظ الشخصيات المخصصة
- بحث متقدم في الانترنت
- نظام تخزين دائم
- نظام تقييم وارسال ملاحظات
- مراقبة السيرفر وكشف فترات التوقف تلقائياً"""
    },
    "help_message": {
        "en": """🎯 **Available Bot Commands:**
/start - Start conversation
/help - Show all commands
/clear - Clear conversation memory
🤔 **Advanced Thinking Features:**
/think [text] - Deep thinking on specific text (generates 10 responses and merges them)
/think_full - Analyze last 10 messages and respond point by point
🎭 **Personality Customization:**
/customize - Customize bot personality and save as preset
/customize /s - Save current customization as preset
/customize /t [title] - Add title to preset
/customize /list - Show all saved presets
🔍 **Internet Search:**
/web [query] - Search in more than 20 reliable sources
🌐 **Language Settings:**
/en - Set language to English
/sp - Set language to Spanish
/fr - Set language to French
/ru - Set language to Russian
/ar - Set language to Arabic
📊 **Statistics:**
/mystats - Show your statistics
/users_info - General user statistics
/server_info - Server and performance information
⭐ **Rating and Feedback:**
/feedback [your opinion] - Send your opinion about the bot (once every 5 days)
/credits - Developer information
💾 **Memory Features:**
- Remembers 100 complete messages
- Saves conversation for 2 days
- Learns from your preferences
- Saves up to 10 custom personalities
- Permanent data storage system""",
        "sp": """🎯 **Comandos disponibles:**
/start - Iniciar conversación
/help - Mostrar todos los comandos
/clear - Borrar historial de conversación
🤔 **Características avanzadas de pensamiento:**
/think [texto] - Pensamiento profundo sobre texto específico (genera 10 respuestas y las fusiona)
/think_full - Analizar los últimos 10 mensajes y responder punto por punto
🎭 **Personalización de personalidad:**
/customize - Personalizar personalidad del bot y guardar como preajuste
/customize /s - Guardar personalización actual como preajuste
/customize /t [título] - Agregar título al preajuste
/customize /list - Mostrar todos los preajustes guardados
🔍 **Búsqueda en Internet:**
/web [consulta] - Buscar en más de 20 fuentes confiables
🌐 **Configuración de idioma:**
/en - Establecer idioma a inglés
/sp - Establecer idioma a español
/fr - Establecer idioma a francés
/ru - Establecer idioma a ruso
/ar - Establecer idioma a árabe
📊 **Estadísticas:**
/mystats - Mostrar tus estadísticas
/users_info - Estadísticas generales de usuarios
/server_info - Información del servidor y rendimiento
⭐ **Calificación y comentarios:**
/feedback [tu opinión] - Enviar tu opinión sobre el bot (una vez cada 5 días)
/credits - Información del desarrollador
💾 **Características de memoria:**
- Recuerda 100 mensajes completos
- Guarda la conversación durante 2 días
- Aprende de tus preferencias
- Guarda hasta 10 personalidades personalizadas
- Sistema de almacenamiento permanente""",
        "fr": """🎯 **Commandes disponibles :**
/start - Démarrer la conversation
/help - Afficher toutes les commandes
/clear - Effacer l'historique de conversation
🤔 **Fonctionnalités avancées de réflexion :**
/think [texte] - Réflexion approfondie sur un texte spécifique (génère 10 réponses et les fusionne)
/think_full - Analyser les 10 derniers messages et répondre point par point
🎭 **Personnalisation de la personnalité :**
/customize - Personnaliser la personnalité du bot et enregistrer comme préréglage
/customize /s - Enregistrer la personnalisation actuelle comme préréglage
/customize /t [titre] - Ajouter un titre au préréglage
/customize /list - Afficher tous les préréglages enregistrés
🔍 **Recherche sur Internet :**
/web [requête] - Rechercher dans plus de 20 sources fiables
🌐 **Paramètres de langue :**
/en - Définir la langue sur l'anglais
/sp - Définir la langue sur l'espagnol
/fr - Définir la langue sur le français
/ru - Définir la langue sur le russe
/ar - Définir la langue sur l'arabe
📊 **Statistiques :**
/mystats - Afficher vos statistiques
/users_info - Statistiques générales des utilisateurs
/server_info - Informations sur le serveur et les performances
⭐ **Évaluation et commentaires :**
/feedback [votre avis] - Envoyer votre avis sur le bot (une fois tous les 5 jours)
/credits - Informations sur le développeur
💾 **Fonctionnalités de mémoire :**
- Se souvient de 100 messages complets
- Enregistre la conversation pendant 2 jours
- Apprend de vos préférences
- Enregistre jusqu'à 10 personnalités personnalisées
- Système de stockage permanent""",
        "ru": """🎯 **Доступные команды бота:**
/start - Начать разговор
/help - Показать все команды
/clear - Очистить историю разговора
🤔 **Расширенные функции мышления:**
/think [текст] - Глубокое осмысление конкретного текста (генерирует 10 ответов и объединяет их)
/think_full - Проанализировать последние 10 сообщений и ответить по пунктам
🎭 **Настройка личности:**
/customize - Настроить личность бота и сохранить как предустановку
/customize /s - Сохранить текущую настройку как предустановку
/customize /t [название] - Добавить название к предустановке
/customize /list - Показать все сохраненные предустановки
🔍 **Поиск в интернете:**
/web [запрос] - Поиск в более чем 20 надежных источниках
🌐 **Настройки языка:**
/en - Установить язык на английский
/sp - Установить язык на испанский
/fr - Установить язык на французский
/ru - Установить язык на русский
/ar - Установить язык на арабский
📊 **Статистика:**
/mystats - Показать вашу статистику
/users_info - Общая статистика пользователей
/server_info - Информация о сервере и производительности
⭐ **Оценка и отзывы:**
/feedback [ваше мнение] - Отправить ваше мнение о боте (раз в 5 дней)
/credits - Информация о разработчике
💾 **Функции памяти:**
- Запоминает 100 полных сообщений
- Сохраняет разговор на 2 дня
- Учится на ваших предпочтениях
- Сохраняет до 10 пользовательских личностей
- Постоянная система хранения данных""",
        "ar": """🎯 **الاوامر المتاحة:**
/start - بدء المحادثة
/help - اظهار جميع الاوامر
/clear - مسح ذاكرة المحادثة
🤔 **مميزات التفكير المتقدم:**
/think [نص] - تفكير عميق في نص محدد (يولد 10 ردود ويقوم بدمجها)
/think_full - تحليل اخر 10 رسائل والرد نقطة بنقطة
🎭 **تخصيص الشخصية:**
/customize - تخصيص شخصية البوت وحفظها كـ Preset
/customize /s - حفظ التخصيص الحالي كـ Preset
/customize /t [عنوان] - اضافة عنوان للـ Preset
/customize /list - اظهار جميع الـ Presets المحفوظة
🔍 **بحث في الانترنت:**
/web [استعلام] - بحث في اكثر من 20 مصدر موثوق
🌐 **اعدادات اللغة:**
/en - تغيير اللغة إلى الانجليزية
/sp - تغيير اللغة إلى الاسبانية
/fr - تغيير اللغة إلى الفرنسية
/ru - تغيير اللغة إلى الروسية
/ar - تغيير اللغة إلى العربية
📊 **الاحصائيات:**
/mystats - اظهار احصائياتك
/users_info - احصائيات عامة للمستخدمين
/server_info - معلومات السيرفر والاداء
⭐ **التقييم والملاحظات:**
/feedback [رايك] - ارسل رأيك عن البوت (مرة كل 5 ايام)
/credits - معلومات المطور
💾 **مميزات الذاكرة:**
- يتذكر 100 رسالة كاملة
- يحفظ المحادثة لمدة يومين
- يتعلم من تفضيلاتك
- يحفظ حتى 10 شخصيات مخصصة
- نظام تخزين دائم"""
    },
    "clear_message": {
        "en": "✅ **Conversation memory cleared!** We started a new conversation.",
        "sp": "✅ **Historial de conversación borrado!** Hemos comenzado una nueva conversación.",
        "fr": "✅ **Historique de conversation effacé !** Nous avons commencé une nouvelle conversation.",
        "ru": "✅ **История разговора очищена!** Мы начали новый разговор.",
        "ar": "✅ **تم مسح ذاكرة المحادثة!** لقد بدأنا محادثة جديدة."
    },
    "cleanup_message": {
        "en": "🧹 **Conversation cleaned**\n🗑️ Deleted {count} old messages\n💾 Your settings and presets were preserved",
        "sp": "🧹 **Conversación limpiada**\n🗑️ Eliminados {count} mensajes antiguos\n💾 Tus ajustes y preajustes se han conservado",
        "fr": "🧹 **Conversation nettoyée**\n🗑️ {count} anciens messages supprimés\n💾 Vos paramètres et préréglages ont été préservés",
        "ru": "🧹 **Беседа очищена**\n🗑️ Удалено {count} старых сообщений\n💾 Ваши настройки и предустановки сохранены",
        "ar": "🧹 **تم تنظيف المحادثة**\n🗑️ تم حذف {count} رسالة قديمة\n💾 تم الحفاظ على إعداداتك والـ Presets"
    },
    "downtime_message": {
        "en": "🤖 **Bot is currently offline**\n⏰ **Downtime:** {duration}\n📨 All your messages will be answered when the bot returns\n🔔 You will be notified when the bot is back online",
        "sp": "🤖 **El bot está actualmente fuera de línea**\n⏰ **Tiempo fuera:** {duration}\n📨 Todos tus mensajes serán respondidos cuando el bot regrese\n🔔 Serás notificado cuando el bot vuelva a estar en línea",
        "fr": "🤖 **Le bot est actuellement hors ligne**\n⏰ **Temps d'arrêt :** {duration}\n📨 Tous vos messages seront répondus lorsque le bot reviendra\n🔔 Vous serez notifié lorsque le bot sera de retour en ligne",
        "ru": "🤖 **Бот в настоящее время отключен**\n⏰ **Время простоя:** {duration}\n📨 Все ваши сообщения будут ответлены, когда бот вернется\n🔔 Вы будете уведомлены, когда бот снова заработает",
        "ar": "🤖 **البوت غير متصل حالياً**\n⏰ **فترة التوقف:** {duration}\n📨 سيتم الرد على جميع رسائلك عندما يعود البوت\n🔔 سيتم إعلامك عندما يعود البوت إلى الإنترنت"
    },
    "back_online_message": {
        "en": "🤖 Bot is back online!\n⏰ Downtime: {duration}\n📨 All your messages will be processed now",
        "sp": "🤖 ¡El bot está de vuelta en línea!\n⏰ Tiempo fuera: {duration}\n📨 Todos tus mensajes serán procesados ahora",
        "fr": "🤖 Le bot est de retour en ligne !\n⏰ Temps d'arrêt : {duration}\n📨 Tous vos messages seront traités maintenant",
        "ru": "🤖 Бот снова в сети!\n⏰ Время простоя: {duration}\n📨 Все ваши сообщения будут обработаны сейчас",
        "ar": "🤖 البوت عاد إلى الإنترنت!\n⏰ فترة التوقف: {duration}\n📨 سيتم معالجة جميع رسائلك الآن"
    },
    "think_full_analysis": {
        "en": "📊 **Deep analysis of last {count} messages:**\n{response}",
        "sp": "📊 **Análisis profundo de los últimos {count} mensajes:**\n{response}",
        "fr": "📊 **Analyse approfondie des {count} derniers messages :**\n{response}",
        "ru": "📊 **Глубокий анализ последних {count} сообщений:**\n{response}",
        "ar": "📊 **تحليل عميق لأخر {count} رسائل:**\n{response}"
    },
    "no_messages_to_analyze": {
        "en": "❌ No recent messages to analyze.",
        "sp": "❌ No hay mensajes recientes para analizar.",
        "fr": "❌ Aucun message récent à analyser.",
        "ru": "❌ Нет недавних сообщений для анализа.",
        "ar": "❌ لا توجد رسائل حديثة لتحليلها."
    },
    "deep_thinking": {
        "en": "🤔 **Deep thinking... {progress}%** (This may take up to 2 minutes)",
        "sp": "🤔 **Pensamiento profundo... {progress}%** (Esto puede tardar hasta 2 minutos)",
        "fr": "🤔 **Réflexion approfondie... {progress}%** (Cela peut prendre jusqu'à 2 minutes)",
        "ru": "🤔 **Глубокое осмысление... {progress}%** (Это может занять до 2 минут)",
        "ar": "🤔 **تفكير عميق... {progress}%** (قد يستغرق حتى دقيقتين)"
    },
    "deep_thinking_result": {
        "en": "💭 **Deep thinking result (10 perspectives):**\n{response}",
        "sp": "💭 **Resultado del pensamiento profundo (10 perspectivas):**\n{response}",
        "fr": "💭 **Résultat de la réflexion approfondie (10 perspectives) :**\n{response}",
        "ru": "💭 **Результат глубокого осмысления (10 перспектив):**\n{response}",
        "ar": "💭 **نتيجة التفكير العميق (10 وجهات نظر):**\n{response}"
    },
    "web_searching": {
        "en": "🔍 **Searching the internet...**",
        "sp": "🔍 **Buscando en internet...**",
        "fr": "🔍 **Recherche sur Internet...**",
        "ru": "🔍 **Поиск в интернете...**",
        "ar": "🔍 **جاري البحث في الانترنت...**"
    },
    "web_results": {
        "en": "🌐 **Search results for: '{query}'**\n{response}",
        "sp": "🌐 **Resultados de búsqueda para: '{query}'**\n{response}",
        "fr": "🌐 **Résultats de recherche pour : '{query}'**\n{response}",
        "ru": "🌐 **Результаты поиска для: '{query}'**\n{response}",
        "ar": "🌐 **نتائج البحث عن: '{query}'**\n{response}"
    },
    "customization_start": {
        "en": "🎭 **Bot Personality Customization**\nSend /customize followed by the new personality description.\nExample: /customize You are a chemistry doctor specialized in medical analysis\nOr choose from the options below:",
        "sp": "🎭 **Personalización de la personalidad del bot**\nEnvía /customize seguido de la nueva descripción de personalidad.\nEjemplo: /customize Eres un doctor en química especializado en análisis médicos\nO elige una de las opciones a continuación:",
        "fr": "🎭 **Personnalisation de la personnalité du bot**\nEnvoyez /customize suivi de la nouvelle description de personnalité.\nExemple : /customize Vous êtes un docteur en chimie spécialisé dans l'analyse médicale\nOu choisissez parmi les options ci-dessous :",
        "ru": "🎭 **Настройка личности бота**\nОтправьте /customize с новым описанием личности.\nПример: /customize Вы - доктор химии, специализирующийся на медицинском анализе\nИли выберите из вариантов ниже:",
        "ar": "🎭 **تخصيص شخصية البوت**\nأرسل /customize متبوعاً بوصف الشخصية الجديدة.\nمثال: /customize أنت دكتور كيمياء متخصص في التحليلات الطبية\nأو اختر من الخيارات أدناه:"
    },
    "customization_saved": {
        "en": "✅ **Current customization saved as new preset!**\n**Title:** {title}\nYou can change the title using /customize /t [new title]",
        "sp": "✅ **¡Personalización actual guardada como nuevo preajuste!**\n**Título:** {title}\nPuedes cambiar el título usando /customize /t [nuevo título]",
        "fr": "✅ **Personnalisation actuelle enregistrée comme nouveau préréglage !**\n**Titre :** {title}\nVous pouvez changer le titre en utilisant /customize /t [nouveau titre]",
        "ru": "✅ **Текущая настройка сохранена как новая предустановка!**\n**Название:** {title}\nВы можете изменить название с помощью /customize /t [новое название]",
        "ar": "✅ **تم حفظ التخصيص الحالي كـ Preset جديد!**\n**العنوان:** {title}\nيمكنك تغيير العنوان باستخدام /customize /t [عنوان جديد]"
    },
    "no_customization_to_save": {
        "en": "❌ No current customization to save.",
        "sp": "❌ No hay personalización actual para guardar.",
        "fr": "❌ Aucune personnalisation actuelle à enregistrer.",
        "ru": "❌ Нет текущей настройки для сохранения.",
        "ar": "❌ لا يوجد تخصيص حالي لحفظه."
    },
    "max_presets_reached": {
        "en": "❌ Maximum presets reached (10). Please delete one first.",
        "sp": "❌ Se alcanzó el máximo de preajustes (10). Por favor, elimina uno primero.",
        "fr": "❌ Nombre maximum de préréglages atteint (10). Veuillez d'abord en supprimer un.",
        "ru": "❌ Достигнуто максимальное количество предустановок (10). Пожалуйста, сначала удалите одну.",
        "ar": "❌ تم الوصول إلى الحد الأقصى للـ Presets (10). يرجى حذف واحد أولاً."
    },
    "preset_title_updated": {
        "en": "✅ **Preset title updated to:** {title}",
        "sp": "✅ **Título del preajuste actualizado a:** {title}",
        "fr": "✅ **Titre du préréglage mis à jour vers :** {title}",
        "ru": "✅ **Название предустановки обновлено на:** {title}",
        "ar": "✅ **تم تحديث عنوان الـ Preset إلى:** {title}"
    },
    "no_presets": {
        "en": "❌ No saved presets.",
        "sp": "❌ No hay preajustes guardados.",
        "fr": "❌ Aucun préréglage enregistré.",
        "ru": "❌ Нет сохраненных предустановок.",
        "ar": "❌ لا توجد Presets محفوظة."
    },
    "saved_presets": {
        "en": "📋 **Saved presets:**\n{list}\n\n💡 Use /customize /use [number] to activate a specific preset.",
        "sp": "📋 **Preajustes guardados:**\n{list}\n\n💡 Usa /customize /use [número] para activar un preajuste específico.",
        "fr": "📋 **Préréglages enregistrés :**\n{list}\n\n💡 Utilisez /customize /use [numéro] pour activer un préréglage spécifique.",
        "ru": "📋 **Сохраненные предустановки:**\n{list}\n\n💡 Используйте /customize /use [номер] для активации конкретной предустановки.",
        "ar": "📋 **الـ Presets المحفوظة:**\n{list}\n\n💡 استخدم /customize /use [رقم] لتفعيل الـ Preset المحدد."
    },
    "preset_activated": {
        "en": "✅ **Preset activated:** {title}",
        "sp": "✅ **¡Preajuste activado!** {title}",
        "fr": "✅ **Préréglage activé :** {title}",
        "ru": "✅ **Предустановка активирована:** {title}",
        "ar": "✅ **تم تفعيل الـ Preset:** {title}"
    },
    "invalid_preset_number": {
        "en": "❌ Invalid preset number.",
        "sp": "❌ Número de preajuste inválido.",
        "fr": "❌ Numéro de préréglage invalide.",
        "ru": "❌ Неверный номер предустановки.",
        "ar": "❌ رقم الـ Preset غير صالح."
    },
    "preset_deleted": {
        "en": "✅ **Preset deleted:** {title}",
        "sp": "✅ **¡Preajuste eliminado!** {title}",
        "fr": "✅ **Préréglage supprimé :** {title}",
        "ru": "✅ **Предустановка удалена:** {title}",
        "ar": "✅ **تم حذف الـ Preset:** {title}"
    },
    "personality_customized": {
        "en": "✅ **Bot personality customized successfully!**\n**New personality:** {personality}\nWould you like to save this customization as a preset for later use?",
        "sp": "✅ **¡Personalidad del bot personalizada con éxito!**\n**Nueva personalidad:** {personality}\n¿Te gustaría guardar esta personalización como preajuste para usarla más tarde?",
        "fr": "✅ **Personnalité du bot personnalisée avec succès !**\n**Nouvelle personnalité :** {personality}\nSouhaitez-vous enregistrer cette personnalisation comme préréglage pour une utilisation ultérieure ?",
        "ru": "✅ **Личность бота успешно настроена!**\n**Новая личность:** {personality}\nХотите сохранить эту настройку как предустановку для дальнейшего использования?",
        "ar": "✅ **تم تخصيص شخصية البوت بنجاح!**\n**الشخصية الجديدة:** {personality}\nهل ترغب في حفظ هذا التخصيص كـ Preset لاستخدامه لاحقاً؟"
    },
    "reset_to_default": {
        "en": "✅ **Bot personality reset to default settings.**",
        "sp": "✅ **¡Personalidad del bot restablecida a la configuración predeterminada!**",
        "fr": "✅ **Personnalité du bot réinitialisée aux paramètres par défaut.**",
        "ru": "✅ **Личность бота сброшена к настройкам по умолчанию.**",
        "ar": "✅ **تم إعادة تعيين شخصية البوت إلى الإعدادات الافتراضية.**"
    },
    "preset_save_skipped": {
        "en": "✅ **Preset save skipped.**",
        "sp": "✅ **¡Guardado del preajuste omitido!**",
        "fr": "✅ **Enregistrement du préréglage ignoré.**",
        "ru": "✅ **Сохранение предустановки пропущено.**",
        "ar": "✅ **تم تخطي حفظ الـ Preset.**"
    },
    "customization_cancelled": {
        "en": "✅ **Customization cancelled.**",
        "sp": "✅ **¡Personalización cancelada!**",
        "fr": "✅ **Personnalisation annulée.**",
        "ru": "✅ **Настройка отменена.**",
        "ar": "✅ **تم إلغاء التخصيص.**"
    },
    "customization_options_closed": {
        "en": "Customization options closed.",
        "sp": "Opciones de personalización cerradas.",
        "fr": "Options de personnalisation fermées.",
        "ru": "Опции настройки закрыты.",
        "ar": "تم إغلاق خيارات التخصيص."
    },
    "user_stats": {
        "en": """📊 **Your Personal Statistics:**
📨 Messages sent: {messages_sent}
📩 Messages received: {messages_received}
🤔 Thinking sessions (/think): {think}
📋 Full analyses (/think_full): {think_full}
🎭 Customizations: {customizations}
📁 Presets saved: {presets_created}
🔧 Presets used: {presets_used}
🌐 Internet searches: {web_searches}
⭐ Feedbacks submitted: {feedbacks_submitted}
💾 **Memory status:**
📝 Messages saved: {messages_saved}
🕐 Oldest message saved: {oldest_days} days ago
🎭 Custom personality: {custom_personality}
📋 Number of presets: {presets_count}/10""",
        "sp": """📊 **Tus estadísticas personales:**
📨 Mensajes enviados: {messages_sent}
📩 Mensajes recibidos: {messages_received}
🤔 Sesiones de pensamiento (/think): {think}
📋 Análisis completos (/think_full): {think_full}
🎭 Personalizaciones: {customizations}
📁 Preajustes guardados: {presets_created}
🔧 Preajustes usados: {presets_used}
🌐 Búsquedas en internet: {web_searches}
⭐ Comentarios enviados: {feedbacks_submitted}
💾 **Estado de la memoria:**
📝 Mensajes guardados: {messages_saved}
🕐 Mensaje más antiguo guardado: hace {oldest_days} días
🎭 Personalidad personalizada: {custom_personality}
📋 Número de preajustes: {presets_count}/10""",
        "fr": """📊 **Vos statistiques personnelles :**
📨 Messages envoyés : {messages_sent}
📩 Messages reçus : {messages_received}
🤔 Sessions de réflexion (/think) : {think}
📋 Analyses complètes (/think_full) : {think_full}
🎭 Personnalisations : {customizations}
📁 Préréglages enregistrés : {presets_created}
🔧 Préréglages utilisés : {presets_used}
🌐 Recherches sur Internet : {web_searches}
⭐ Commentaires soumis : {feedbacks_submitted}
💾 **État de la mémoire :**
📝 Messages enregistrés : {messages_saved}
🕐 Message le plus ancien enregistré : il y a {oldest_days} jours
🎭 Personnalité personnalisée : {custom_personality}
📋 Nombre de préréglages : {presets_count}/10""",
        "ru": """📊 **Ваши личные статистические данные:**
📨 Отправленные сообщения: {messages_sent}
📩 Полученные сообщения: {messages_received}
🤔 Сессии размышления (/think): {think}
📋 Полные анализы (/think_full): {think_full}
🎭 Настройки: {customizations}
📁 Сохраненные предустановки: {presets_created}
🔧 Использованные предустановки: {presets_used}
🌐 Поисковые запросы: {web_searches}
⭐ Отправленные отзывы: {feedbacks_submitted}
💾 **Состояние памяти:**
📝 Сохраненные сообщения: {messages_saved}
🕐 Самое старое сообщение: {oldest_days} дней назад
🎭 Пользовательская личность: {custom_personality}
📋 Количество предустановок: {presets_count}/10""",
        "ar": """📊 **احصائياتك الشخصية:**
📨 الرسائل المرسلة: {messages_sent}
📩 الرسائل المستلمة: {messages_received}
🤔 جلسات التفكير (/think): {think}
📋 التحليلات الكاملة (/think_full): {think_full}
🎭 التخصيصات: {customizations}
📁 الـ Presets المحفوظة: {presets_created}
🔧 الـ Presets المستخدمة: {presets_used}
🌐 عمليات البحث: {web_searches}
⭐ الملاحظات المرسلة: {feedbacks_submitted}
💾 **حالة الذاكرة:**
📝 الرسائل المحفوظة: {messages_saved}
🕐 أقدم رسالة محفوظة: منذ {oldest_days} يوم
🎭 شخصية مخصصة: {custom_personality}
📋 عدد الـ Presets: {presets_count}/10"""
    },
    "no_stats": {
        "en": "📊 No statistics yet.",
        "sp": "📊 Todavía no hay estadísticas.",
        "fr": "📊 Aucune statistique pour le moment.",
        "ru": "📊 Статистика еще не собрана.",
        "ar": "📊 لا توجد احصائيات حتى الآن."
    },
    "general_user_stats": {
        "en": """📈 **General User Statistics:**
👥 Total users: {total_users}
✅ Active users (less than 1 day): {awake_users}
💤 Sleeping users (2-6 days): {sleeping_users}
❌ Inactive users (more than 7 days): {dead_users}
⭐ Total feedbacks: {total_feedbacks}
⏰ Last update: {last_updated}
💡 **Notes:**
- Active user: Interaction within last 24 hours
- Sleeping user: Interaction 2-6 days ago  
- Inactive user: No interaction for more than 7 days
📝 **Recent feedbacks:**{feedbacks}
Use /feedback [your opinion] to send your feedback about the bot!""",
        "sp": """📈 **Estadísticas generales de usuarios:**
👥 Total de usuarios: {total_users}
✅ Usuarios activos (menos de 1 día): {awake_users}
💤 Usuarios dormidos (2-6 días): {sleeping_users}
❌ Usuarios inactivos (más de 7 días): {dead_users}
⭐ Total de comentarios: {total_feedbacks}
⏰ Última actualización: {last_updated}
💡 **Notas:**
- Usuario activo: Interacción en las últimas 24 horas
- Usuario dormido: Interacción hace 2-6 días  
- Usuario inactivo: Sin interacción durante más de 7 días
📝 **Comentarios recientes:**{feedbacks}
¡Usa /feedback [tu opinión] para enviar tu comentario sobre el bot!""",
        "fr": """📈 **Statistiques générales des utilisateurs :**
👥 Utilisateurs totaux : {total_users}
✅ Utilisateurs actifs (moins de 1 jour) : {awake_users}
💤 Utilisateurs dormant (2-6 jours) : {sleeping_users}
❌ Utilisateurs inactifs (plus de 7 jours) : {dead_users}
⭐ Commentaires totaux : {total_feedbacks}
⏰ Dernière mise à jour : {last_updated}
💡 **Notes :**
- Utilisateur actif : Interaction dans les dernières 24 heures
- Utilisateur dormant : Interaction il y a 2-6 jours  
- Utilisateur inactif : Aucune interaction depuis plus de 7 jours
📝 **Commentaires récents :**{feedbacks}
Utilisez /feedback [votre avis] pour envoyer votre avis sur le bot !""",
        "ru": """📈 **Общая статистика пользователей:**
👥 Всего пользователей: {total_users}
✅ Активные пользователи (менее 1 дня): {awake_users}
💤 Спящие пользователи (2-6 дней): {sleeping_users}
❌ Неактивные пользователи (более 7 дней): {dead_users}
⭐ Всего отзывов: {total_feedbacks}
⏰ Последнее обновление: {last_updated}
💡 **Примечания:**
- Активный пользователь: Взаимодействие в последние 24 часа
- Спящий пользователь: Взаимодействие 2-6 дней назад  
- Неактивный пользователь: Нет взаимодействия более 7 дней
📝 **Недавние отзывы:**{feedbacks}
Используйте /feedback [ваше мнение], чтобы отправить отзыв о боте!""",
        "ar": """📈 **احصائيات عامة للمستخدمين:**
👥 إجمالي المستخدمين: {total_users}
✅ المستخدمين النشطين (أقل من يوم): {awake_users}
💤 المستخدمين النائمين (2-6 أيام): {sleeping_users}
❌ المستخدمين غير النشطين (أكثر من 7 أيام): {dead_users}
⭐ إجمالي الملاحظات: {total_feedbacks}
⏰ آخر تحديث: {last_updated}
💡 **ملاحظات:**
- المستخدم النشط: تفاعل في آخر 24 ساعة
- المستخدم النائم: تفاعل منذ 2-6 أيام  
- المستخدم غير النشط: لا يوجد تفاعل منذ أكثر من 7 أيام
📝 **الملاحظات الحديثة:**{feedbacks}
استخدم /feedback [رايك] لإرسال ملاحظتك عن البوت!"""
    },
    "no_recent_feedbacks": {
        "en": "\nNo recent feedbacks.",
        "sp": "\nNo hay comentarios recientes.",
        "fr": "\nAucun commentaire récent.",
        "ru": "\nНет недавних отзывов.",
        "ar": "\nلا توجد ملاحظات حديثة."
    },
    "feedback_sent": {
        "en": """⭐ **Thank you for your feedback!**
We greatly appreciate user opinions to improve and develop the bot.
Your feedback will be read carefully and your notes will be taken into consideration.
You can send new feedback {days_left} days from now.""",
        "sp": """⭐ **¡Gracias por tu comentario!**
Apreciamos mucho las opiniones de los usuarios para mejorar y desarrollar el bot.
Tu comentario será leído cuidadosamente y tus notas serán tomadas en consideración.
Puedes enviar nuevos comentarios en {days_left} días.""",
        "fr": """⭐ **Merci pour votre avis !**
Nous apprécions grandement les opinions des utilisateurs pour améliorer et développer le bot.
Votre avis sera lu attentivement et vos remarques seront prises en compte.
Vous pouvez envoyer un nouvel avis dans {days_left} jours.""",
        "ru": """⭐ **Спасибо за ваш отзыв!**
Мы очень ценим мнения пользователей для улучшения и развития бота.
Ваш отзыв будет внимательно изучен, и ваши замечания будут учтены.
Вы можете отправить новый отзыв через {days_left} дней.""",
        "ar": """⭐ **شكراً لملاحظتك!**
نحن نقدر آراء المستخدمين لتحسين وتطوير البوت.
سيتم قراءة ملاحظتك بعناية وستؤخذ ملاحظاتك في الاعتبار.
يمكنك إرسال ملاحظة جديدة بعد {days_left} يوم."""
    },
    "feedback_waiting": {
        "en": "⏳ You can send new feedback after {days} day/s. Thank you for your interest!",
        "sp": "⏳ Puedes enviar nuevos comentarios después de {days} día/s. ¡Gracias por tu interés!",
        "fr": "⏳ Vous pouvez envoyer de nouveaux commentaires après {days} jour(s). Merci pour votre intérêt !",
        "ru": "⏳ Вы можете отправить новый отзыв через {days} день(ей). Спасибо за ваш интерес!",
        "ar": "⏳ يمكنك إرسال ملاحظة جديدة بعد {days} يوم/أيام. شكراً لاهتمامك!"
    },
    "developer_info": {
        "en": """👨‍💻 **Developer Information:**
**Bot Developer:** HAKORA
**Twitter:** https://x.com/HAKORAdev/""",
        "sp": """👨‍💻 **Información del desarrollador:**
**Desarrollador del bot:** HAKORA
**Twitter:** https://x.com/HAKORAdev/""",
        "fr": """👨‍💻 **Informations sur le développeur :**
**Développeur du bot :** HAKORA
**Twitter :** https://x.com/HAKORAdev/""",
        "ru": """👨‍💻 **Информация о разработчике:**
**Разработчик бота:** HAKORA
**Twitter:** https://x.com/HAKORAdev/""",
        "ar": """👨‍💻 **معلومات المطور:**
**مطور البوت:** HAKORA
**تويتر:** https://x.com/HAKORAdev/"""
    },
    "server_info": {
        "en": """🖥️ **Server and Performance Information:**
⏰ **Uptime:** {uptime}
🔧 **CPU Information:**
- Current usage: {cpu_percent}%
- Core count: {cpu_count}
- Current frequency: {cpu_freq_current} MHz
- Max frequency: {cpu_freq_max} MHz
💾 **Memory Information (RAM):**
- Total: {memory_total:.2f} GB
- Used: {memory_used:.2f} GB
- Percentage: {memory_percent}%
💿 **Storage Information (Disk):**
- Total: {disk_total:.2f} GB
- Used: {disk_used:.2f} GB
- Percentage: {disk_percent}%
📊 **Bot Statistics:**
- Total messages processed: {total_messages}
- Messages today: {messages_today}
- Messages this week: {messages_week}
- Messages this month: {messages_month}
- Active users today: {users_today}
- Active users this week: {users_week}
- Active users this month: {users_month}
🔄 **Bot Status:**
{bot_status}""",
        "sp": """🖥️ **Información del servidor y rendimiento:**
⏰ **Tiempo activo:** {uptime}
🔧 **Información de CPU:**
- Uso actual: {cpu_percent}%
- Número de núcleos: {cpu_count}
- Frecuencia actual: {cpu_freq_current} MHz
- Frecuencia máxima: {cpu_freq_max} MHz
💾 **Información de memoria (RAM):**
- Total: {memory_total:.2f} GB
- Usado: {memory_used:.2f} GB
- Porcentaje: {memory_percent}%
💿 **Información de almacenamiento (Disco):**
- Total: {disk_total:.2f} GB
- Usado: {disk_used:.2f} GB
- Porcentaje: {disk_percent}%
📊 **Estadísticas del bot:**
- Total de mensajes procesados: {total_messages}
- Mensajes hoy: {messages_today}
- Mensajes esta semana: {messages_week}
- Mensajes este mes: {messages_month}
- Usuarios activos hoy: {users_today}
- Usuarios activos esta semana: {users_week}
- Usuarios activos este mes: {users_month}
🔄 **Estado del bot:**
{bot_status}""",
        "fr": """🖥️ **Informations sur le serveur et les performances :**
⏰ **Temps d'activité :** {uptime}
🔧 **Informations sur le CPU :**
- Utilisation actuelle : {cpu_percent}%
- Nombre de cœurs : {cpu_count}
- Fréquence actuelle : {cpu_freq_current} MHz
- Fréquence maximale : {cpu_freq_max} MHz
💾 **Informations sur la mémoire (RAM) :**
- Total : {memory_total:.2f} GB
- Utilisé : {memory_used:.2f} GB
- Pourcentage : {memory_percent}%
💿 **Informations sur le stockage (Disque) :**
- Total : {disk_total:.2f} GB
- Utilisé : {disk_used:.2f} GB
- Pourcentage : {disk_percent}%
📊 **Statistiques du bot :**
- Total des messages traités : {total_messages}
- Messages aujourd'hui : {messages_today}
- Messages cette semaine : {messages_week}
- Messages ce mois : {messages_month}
- Utilisateurs actifs aujourd'hui : {users_today}
- Utilisateurs actifs cette semaine : {users_week}
- Utilisateurs actifs ce mois : {users_month}
🔄 **État du bot :**
{bot_status}""",
        "ru": """🖥️ **Информация о сервере и производительности:**
⏰ **Время работы:** {uptime}
🔧 **Информация о CPU:**
- Текущее использование: {cpu_percent}%
- Количество ядер: {cpu_count}
- Текущая частота: {cpu_freq_current} МГц
- Максимальная частота: {cpu_freq_max} МГц
💾 **Информация о памяти (RAM):**
- Всего: {memory_total:.2f} ГБ
- Использовано: {memory_used:.2f} ГБ
- Процент: {memory_percent}%
💿 **Информация о хранилище (Диск):**
- Всего: {disk_total:.2f} ГБ
- Использовано: {disk_used:.2f} ГБ
- Процент: {disk_percent}%
📊 **Статистика бота:**
- Всего обработанных сообщений: {total_messages}
- Сообщений сегодня: {messages_today}
- Сообщений на этой неделе: {messages_week}
- Сообщений в этом месяце: {messages_month}
- Активных пользователей сегодня: {users_today}
- Активных пользователей на этой неделе: {users_week}
- Активных пользователей в этом месяце: {users_month}
🔄 **Состояние бота:**
{bot_status}""",
        "ar": """🖥️ **معلومات السيرفر والأداء:**
⏰ **وقت التشغيل:** {uptime}
🔧 **معلومات المعالج:**
- الاستخدام الحالي: {cpu_percent}%
- عدد النوى: {cpu_count}
- التردد الحالي: {cpu_freq_current} ميجا هيرتز
- التردد الأقصى: {cpu_freq_max} ميجا هيرتز
💾 **معلومات الذاكرة (RAM):**
- الإجمالي: {memory_total:.2f} جيجا بايت
- المستخدم: {memory_used:.2f} جيجا بايت
- النسبة: {memory_percent}%
💿 **معلومات التخزين (القرص):**
- الإجمالي: {disk_total:.2f} جيجا بايت
- المستخدم: {disk_used:.2f} جيجا بايت
- النسبة: {disk_percent}%
📊 **احصائيات البوت:**
- إجمالي الرسائل المعالجة: {total_messages}
- الرسائل اليوم: {messages_today}
- الرسائل هذا الأسبوع: {messages_week}
- الرسائل هذا الشهر: {messages_month}
- المستخدمين النشطين اليوم: {users_today}
- المستخدمين النشطين هذا الأسبوع: {users_week}
- المستخدمين النشطين هذا الشهر: {users_month}
🔄 **حالة البوت:**
{bot_status}"""
    },
    "bot_status_online": {
        "en": "✅ Bot operating normally",
        "sp": "✅ Bot operando normalmente",
        "fr": "✅ Bot fonctionne normalement",
        "ru": "✅ Бот работает нормально",
        "ar": "✅ البوت يعمل بشكل طبيعي"
    },
    "bot_status_offline": {
        "en": "⏸️ Bot offline since: {duration}",
        "sp": "⏸️ Bot fuera de línea desde: {duration}",
        "fr": "⏸️ Bot hors ligne depuis : {duration}",
        "ru": "⏸️ Бот отключен с: {duration}",
        "ar": "⏸️ البوت غير متصل منذ: {duration}"
    },
    "error_processing": {
        "en": "Sorry, an error occurred during processing. Please try later.",
        "sp": "Lo sentimos, ocurrió un error durante el procesamiento. Por favor, inténtalo más tarde.",
        "fr": "Désolé, une erreur s'est produite lors du traitement. Veuillez réessayer plus tard.",
        "ru": "Извините, произошла ошибка при обработке. Пожалуйста, попробуйте позже.",
        "ar": "عذراً، حدث خطأ أثناء المعالجة. يرجى المحاولة لاحقاً."
    },
    "error_command": {
        "en": "Sorry, an error occurred processing the command. Please try later.",
        "sp": "Lo sentimos, ocurrió un error al procesar el comando. Por favor, inténtalo más tarde.",
        "fr": "Désolé, une erreur s'est produite lors du traitement de la commande. Veuillez réessayer plus tard.",
        "ru": "Извините, произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.",
        "ar": "عذراً، حدث خطأ أثناء معالجة الأمر. يرجى المحاولة لاحقاً."
    },
    "error_showing_stats": {
        "en": "Sorry, an error occurred showing statistics. Please try later.",
        "sp": "Lo sentimos, ocurrió un error al mostrar las estadísticas. Por favor, inténtalo más tarde.",
        "fr": "Désolé, une erreur s'est produite lors de l'affichage des statistiques. Veuillez réessayer plus tard.",
        "ru": "Извините, произошла ошибка при отображении статистики. Пожалуйста, попробуйте позже.",
        "ar": "عذراً، حدث خطأ أثناء عرض الاحصائيات. يرجى المحاولة لاحقاً."
    },
    "error_sending_feedback": {
        "en": "Sorry, an error occurred sending feedback. Please try later.",
        "sp": "Lo sentimos, ocurrió un error al enviar el comentario. Por favor, inténtalo más tarde.",
        "fr": "Désolé, une erreur s'est produite lors de l'envoi du commentaire. Veuillez réessayer plus tard.",
        "ru": "Извините, произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже.",
        "ar": "عذراً، حدث خطأ أثناء إرسال الملاحظة. يرجى المحاولة لاحقاً."
    },
    "error_showing_credits": {
        "en": "Sorry, an error occurred showing credits. Please try later.",
        "sp": "Lo sentimos, ocurrió un error al mostrar los créditos. Por favor, inténtalo más tarde.",
        "fr": "Désolé, une erreur s'est produite lors de l'affichage des crédits. Veuillez réessayer plus tard.",
        "ru": "Извините, произошла ошибка при отображении информации о разработчике. Пожалуйста, попробуйте позже.",
        "ar": "عذراً، حدث خطأ أثناء عرض معلومات المطور. يرجى المحاولة لاحقاً."
    },
    "error_showing_server_info": {
        "en": "Sorry, an error occurred showing server information. Please try later.",
        "sp": "Lo sentimos, ocurrió un error al mostrar la información del servidor. Por favor, inténtalo más tarde.",
        "fr": "Désolé, une erreur s'est produite lors de l'affichage des informations sur le serveur. Veuillez réessayer plus tard.",
        "ru": "Извините, произошла ошибка при отображении информации о сервере. Пожалуйста, попробуйте позже.",
        "ar": "عذراً، حدث خطأ أثناء عرض معلومات السيرفر. يرجى المحاولة لاحقاً."
    },
    "language_changed": {
        "en": "✅ Language changed to {language}!",
        "sp": "✅ ¡Idioma cambiado a {language}!",
        "fr": "✅ Langue changée en {language} !",
        "ru": "✅ Язык изменен на {language}!",
        "ar": "✅ تم تغيير اللغة إلى {language}!"
    },
    "unsupported_language": {
        "en": "❌ Unsupported language code. Supported codes: {codes}",
        "sp": "❌ Código de idioma no soportado. Códigos soportados: {codes}",
        "fr": "❌ Code de langue non pris en charge. Codes pris en charge : {codes}",
        "ru": "❌ Неподдерживаемый код языка. Поддерживаемые коды: {codes}",
        "ar": "❌ رمز لغة غير مدعوم. الرموز المدعومة: {codes}"
    },
    "enter_search_query": {
        "en": "⚠️ Please send search query after the command. Example: /web Gold price today in Egypt",
        "sp": "⚠️ Por favor, envía la consulta de búsqueda después del comando. Ejemplo: /web Precio del oro hoy en Egipto",
        "fr": "⚠️ Veuillez envoyer la requête de recherche après la commande. Exemple : /web Prix de l'or aujourd'hui en Égypte",
        "ru": "⚠️ Пожалуйста, отправьте поисковый запрос после команды. Пример: /web Цена золота сегодня в Египте",
        "ar": "⚠️ يرجى إرسال استعلام البحث بعد الأمر. مثال: /web سعر الذهب اليوم في مصر"
    },
    "enter_think_query": {
        "en": "⚠️ Please send text to think about after the command. Example: /think What is the meaning of life?",
        "sp": "⚠️ Por favor, envía el texto para reflexionar después del comando. Ejemplo: /think ¿Cuál es el significado de la vida?",
        "fr": "⚠️ Veuillez envoyer le texte à réfléchir après la commande. Exemple : /think Quel est le sens de la vie ?",
        "ru": "⚠️ Пожалуйста, отправьте текст для размышления после команды. Пример: /think Каков смысл жизни?",
        "ar": "⚠️ يرجى إرسال النص للتفكير فيه بعد الأمر. مثال: /think ما هو معنى الحياة؟"
    },
    "error_analysis": {
        "en": "❌ Error during analysis. Please try again later.",
        "sp": "❌ Error durante el análisis. Por favor, inténtalo de nuevo más tarde.",
        "fr": "❌ Erreur lors de l'analyse. Veuillez réessayer plus tard.",
        "ru": "❌ Ошибка во время анализа. Пожалуйста, попробуйте позже.",
        "ar": "❌ خطأ أثناء التحليل. يرجى المحاولة لاحقاً."
    },
    "error_search": {
        "en": "❌ Error during search. Please try again later.",
        "sp": "❌ Error durante la búsqueda. Por favor, inténtalo de nuevo más tarde.",
        "fr": "❌ Erreur lors de la recherche. Veuillez réessayer plus tard.",
        "ru": "❌ Ошибка во время поиска. Пожалуйста, попробуйте позже.",
        "ar": "❌ خطأ أثناء البحث. يرجى المحاولة لاحقاً."
    },
    "error_thinking": {
        "en": "❌ Error during deep thinking. Please try again later.",
        "sp": "❌ Error durante el pensamiento profundo. Por favor, inténtalo de nuevo más tarde.",
        "fr": "❌ Erreur lors de la réflexion approfondie. Veuillez réessayer plus tard.",
        "ru": "❌ Ошибка во время глубокого осмысления. Пожалуйста, попробуйте позже.",
        "ar": "❌ خطأ أثناء التفكير العميق. يرجى المحاولة لاحقاً."
    },
    "error_merging": {
        "en": "⚠️ Could not merge all perspectives due to content length. Showing first 3 perspectives only.",
        "sp": "⚠️ No se pudieron fusionar todas las perspectivas debido a la longitud del contenido. Mostrando solo las primeras 3 perspectivas.",
        "fr": "⚠️ Impossible de fusionner toutes les perspectives en raison de la longueur du contenu. Affichage des 3 premières perspectives uniquement.",
        "ru": "⚠️ Не удалось объединить все перспективы из-за длины содержимого. Отображаются только первые 3 перспективы.",
        "ar": "⚠️ لا يمكن دمج جميع وجهات النظر بسبب طول المحتوى. عرض أول 3 وجهات نظر فقط."
    }
}

DEFAULT_USER_STATS = {
    "messages_sent": 0,
    "messages_received": 0,
    "deep_thoughts": 0,
    "customizations": 0,
    "think_full": 0,
    "think": 0,
    "presets_created": 0,
    "presets_used": 0,
    "web_searches": 0,
    "feedbacks_submitted": 0
}

user_conversations = {}
user_stats = {}
user_feedbacks = {}
bot_stats = {
    "start_time": datetime.now().isoformat(),
    "total_messages_processed": 0,
    "messages_today": 0,
    "messages_week": 0,
    "messages_month": 0,
    "last_message_time": None,
    "downtime_start": None,
    "downtime_periods": [],
    "users_today": set(),
    "users_week": set(),
    "users_month": set()
}
last_save_time = 0
save_lock = threading.Lock()

def get_translation(user_id, key, **kwargs):
    try:
        user_memory = get_user_memory(user_id)
        language = user_memory.get("language", DEFAULT_LANGUAGE)
        text = LANGUAGE_STRINGS[key][language]
        return text.format(**kwargs)
    except Exception as e:
        logger.error(f"Error in get_translation: {e}")
        try:
            return LANGUAGE_STRINGS[key]["en"].format(**kwargs)
        except:
            return "Translation error"

def load_data():
    global user_conversations, user_stats, user_feedbacks, bot_stats
    try:
        if os.path.exists('conversations.json'):
            with open('conversations.json', 'r', encoding='utf-8') as f:
                user_conversations = json.load(f)
            for user_id, data in user_conversations.items():
                if "messages" not in data:
                    data["messages"] = []
                if "last_active" not in data:
                    data["last_active"] = datetime.now().isoformat()
                if "custom_persona" not in data:
                    language = data.get("language", DEFAULT_LANGUAGE)
                    data["custom_persona"] = get_default_persona(language)
                if "presets" not in data:
                    data["presets"] = []
                if "active_preset" not in data:
                    data["active_preset"] = None
                if "last_feedback" not in data:
                    data["last_feedback"] = None
                if "language" not in data:
                    data["language"] = DEFAULT_LANGUAGE
                for msg in data["messages"]:
                    if "timestamp" not in msg:
                        msg["timestamp"] = datetime.now().isoformat()
    except Exception as e:
        logger.error(f"Error loading conversations: {e}")
        user_conversations = {}
    try:
        if os.path.exists('user_stats.json'):
            with open('user_stats.json', 'r', encoding='utf-8') as f:
                user_stats = json.load(f)
            for user_id, stats in user_stats.items():
                for key, value in DEFAULT_USER_STATS.items():
                    if key not in stats:
                        stats[key] = value
    except Exception as e:
        logger.error(f"Error loading statistics: {e}")
        user_stats = {}
    try:
        if os.path.exists('user_feedbacks.json'):
            with open('user_feedbacks.json', 'r', encoding='utf-8') as f:
                user_feedbacks = json.load(f)
    except Exception as e:
        logger.error(f"Error loading feedbacks: {e}")
        user_feedbacks = {}
    try:
        if os.path.exists('bot_stats.json'):
            with open('bot_stats.json', 'r', encoding='utf-8') as f:
                saved_bot_stats = json.load(f)
                for key, value in saved_bot_stats.items():
                    if key in bot_stats:
                        if key in ["users_today", "users_week", "users_month"]:
                            bot_stats[key] = set(value)
                        else:
                            bot_stats[key] = value
    except Exception as e:
        logger.error(f"Error loading bot statistics: {e}")
    load_permanent_data()
    update_users_info()

def load_permanent_data():
    try:
        if os.path.exists('conversations_save.json'):
            with open('conversations_save.json', 'r', encoding='utf-8') as f:
                conversations_save = json.load(f)
            for user_id, data in conversations_save.items():
                if user_id not in user_conversations:
                    user_conversations[user_id] = data
                else:
                    if "language" not in user_conversations[user_id]:
                        user_conversations[user_id]["language"] = DEFAULT_LANGUAGE
        if os.path.exists('user_stats_save.json'):
            with open('user_stats_save.json', 'r', encoding='utf-8') as f:
                user_stats_save = json.load(f)
            for user_id, stats in user_stats_save.items():
                if user_id not in user_stats:
                    user_stats[user_id] = stats
        if os.path.exists('user_feedbacks_save.json'):
            with open('user_feedbacks_save.json', 'r', encoding='utf-8') as f:
                user_feedbacks_save = json.load(f)
            for user_id, feedback in user_feedbacks_save.items():
                if user_id not in user_feedbacks:
                    user_feedbacks[user_id] = feedback
    except Exception as e:
        logger.error(f"Error loading permanent data: {e}")

def save_data():
    global last_save_time
    current_time = time.time()
    if current_time - last_save_time < 5:
        return
    with save_lock:
        try:
            with open('conversations.json', 'w', encoding='utf-8') as f:
                json.dump(user_conversations, f, ensure_ascii=False, indent=2)
            with open('user_stats.json', 'w', encoding='utf-8') as f:
                json.dump(user_stats, f, ensure_ascii=False, indent=2)
            with open('user_feedbacks.json', 'w', encoding='utf-8') as f:
                json.dump(user_feedbacks, f, ensure_ascii=False, indent=2)
            bot_stats_to_save = bot_stats.copy()
            for key in ["users_today", "users_week", "users_month"]:
                if key in bot_stats_to_save:
                    bot_stats_to_save[key] = list(bot_stats_to_save[key])
            with open('bot_stats.json', 'w', encoding='utf-8') as f:
                json.dump(bot_stats_to_save, f, ensure_ascii=False, indent=2)
            save_permanent_data()
            last_save_time = current_time
        except Exception as e:
            logger.error(f"Error saving data: {e}")

def save_permanent_data():
    try:
        with open('conversations_save.json', 'w', encoding='utf-8') as f:
            json.dump(user_conversations, f, ensure_ascii=False, indent=2)
        with open('user_stats_save.json', 'w', encoding='utf-8') as f:
            json.dump(user_stats, f, ensure_ascii=False, indent=2)
        with open('user_feedbacks_save.json', 'w', encoding='utf-8') as f:
            json.dump(user_feedbacks, f, ensure_ascii=False, indent=2)
        update_users_info()
    except Exception as e:
        logger.error(f"Error saving permanent data: {e}")

def update_bot_stats(message_count=0, user_id=None):
    try:
        current_time = datetime.now()
        bot_stats["last_message_time"] = current_time.isoformat()
        if message_count > 0:
            bot_stats["total_messages_processed"] += message_count
            if is_today(current_time):
                bot_stats["messages_today"] += message_count
            if is_this_week(current_time):
                bot_stats["messages_week"] += message_count
            if is_this_month(current_time):
                bot_stats["messages_month"] += message_count
            if user_id:
                if is_today(current_time):
                    bot_stats["users_today"].add(user_id)
                if is_this_week(current_time):
                    bot_stats["users_week"].add(user_id)
                if is_this_month(current_time):
                    bot_stats["users_month"].add(user_id)
        if bot_stats["total_messages_processed"] % 10 == 0:
            save_data()
    except Exception as e:
        logger.error(f"Error updating bot statistics: {e}")

def is_today(timestamp):
    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        return timestamp.date() == datetime.now().date()
    except:
        return False

def is_this_week(timestamp):
    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        return timestamp.date() >= start_of_week.date()
    except:
        return False

def is_this_month(timestamp):
    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        now = datetime.now()
        return timestamp.month == now.month and timestamp.year == now.year
    except:
        return False

def get_uptime():
    try:
        start_time = datetime.fromisoformat(bot_stats["start_time"])
        uptime = datetime.now() - start_time
        return uptime
    except:
        return timedelta(0)

def format_uptime(uptime):
    try:
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            return f"{days} days, {hours} hours, {minutes} minutes"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes, {seconds} seconds"
        else:
            return f"{minutes} minutes, {seconds} seconds"
    except:
        return "Not available"

def get_server_info():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else "N/A"
        cpu_freq_max = cpu_freq.max if cpu_freq else "N/A"
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024 ** 3)
        memory_used = memory.used / (1024 ** 3)
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_total = disk.total / (1024 ** 3)
        disk_used = disk.used / (1024 ** 3)
        disk_percent = disk.percent
        system_info = platform.platform()
        processor = platform.processor()
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "freq_current": cpu_freq_current,
                "freq_max": cpu_freq_max
            },
            "memory": {
                "total": memory_total,
                "used": memory_used,
                "percent": memory_percent
            },
            "disk": {
                "total": disk_total,
                "used": disk_used,
                "percent": disk_percent
            },
            "system": {
                "platform": system_info,
                "processor": processor
            }
        }
    except Exception as e:
        logger.error(f"Error getting server info: {e}")
        return None

async def check_bot_status(application):
    while True:
        try:
            current_time = datetime.now()
            last_message_time = bot_stats.get("last_message_time")
            if last_message_time:
                last_time = datetime.fromisoformat(last_message_time)
                downtime = current_time - last_time
                if downtime.total_seconds() > 300 and not bot_stats.get("downtime_start"):
                    bot_stats["downtime_start"] = last_time.isoformat()
                    logger.warning(f"Bot stopped since: {last_time}")
                elif bot_stats.get("downtime_start") and downtime.total_seconds() <= 300:
                    downtime_start = datetime.fromisoformat(bot_stats["downtime_start"])
                    downtime_period = current_time - downtime_start
                    bot_stats["downtime_periods"].append({
                        "start": downtime_start.isoformat(),
                        "end": current_time.isoformat(),
                        "duration_seconds": downtime_period.total_seconds()
                    })
                    bot_stats["downtime_start"] = None
                    active_users = get_active_users(24)
                    for user_id in active_users:
                        try:
                            user_memory = get_user_memory(user_id)
                            language = user_memory.get("language", DEFAULT_LANGUAGE)
                            duration_text = format_downtime(downtime_period)
                            message = LANGUAGE_STRINGS["back_online_message"][language].format(duration=duration_text)
                            await application.bot.send_message(
                                chat_id=user_id,
                                text=message
                            )
                        except Exception as e:
                            logger.error(f"Error sending notification to user {user_id}: {e}")
                    logger.info(f"Bot back online after: {format_downtime(downtime_period)}")
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error checking bot status: {e}")
            await asyncio.sleep(60)

def format_downtime(downtime):
    try:
        days = downtime.days
        hours, remainder = divmod(downtime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            return f"{days} days, {hours} hours, {minutes} minutes"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes, {seconds} seconds"
        else:
            return f"{minutes} minutes, {seconds} seconds"
    except:
        return "Unknown period"

def get_active_users(hours=24):
    try:
        active_users = set()
        threshold = datetime.now() - timedelta(hours=hours)
        for user_id, data in user_conversations.items():
            if "last_active" in data:
                last_active = datetime.fromisoformat(data["last_active"])
                if last_active >= threshold:
                    active_users.add(user_id)
        return active_users
    except Exception as e:
        logger.error(f"Error getting active users: {e}")
        return set()

def update_users_info():
    try:
        awake_users = 0
        sleeping_users = 0
        dead_users = 0
        total_feedbacks = len(user_feedbacks)
        current_time = datetime.now()
        for user_id, data in user_conversations.items():
            if "last_active" in data:
                last_active = datetime.fromisoformat(data["last_active"])
                days_inactive = (current_time - last_active).days
                if days_inactive <= 1:
                    awake_users += 1
                elif 2 <= days_inactive <= 6:
                    sleeping_users += 1
                else:
                    dead_users += 1
        users_info = {
            "awake_users": awake_users,
            "sleeping_users": sleeping_users,
            "dead_users": dead_users,
            "total_feedbacks": total_feedbacks,
            "last_updated": current_time.isoformat(),
            "total_users": len(user_conversations),
            "recent_feedbacks": get_recent_feedbacks(5)
        }
        with open('users_info.json', 'w', encoding='utf-8') as f:
            json.dump(users_info, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error updating user info: {e}")

def get_recent_feedbacks(limit=5):
    try:
        recent_feedbacks = []
        for user_id, feedback_data in user_feedbacks.items():
            if len(recent_feedbacks) >= limit:
                break
            recent_feedbacks.append({
                "user_id": user_id,
                "feedback": feedback_data.get("feedback", ""),
                "timestamp": feedback_data.get("timestamp", ""),
                "rating": feedback_data.get("rating", "Not specified")
            })
        return recent_feedbacks
    except Exception as e:
        logger.error(f"Error getting recent feedbacks: {e}")
        return []

def cleanup_old_conversations():
    try:
        current_time = datetime.now()
        two_days_ago = current_time - timedelta(days=2)
        deleted_count = 0
        for user_id, data in user_conversations.items():
            if "last_active" in data:
                last_active = datetime.fromisoformat(data["last_active"])
                if last_active < two_days_ago:
                    old_msg_count = len(data.get("messages", []))
                    custom_persona = data.get("custom_persona", get_default_persona(data.get("language", DEFAULT_LANGUAGE)))
                    presets = data.get("presets", [])
                    active_preset = data.get("active_preset", None)
                    last_feedback = data.get("last_feedback", None)
                    user_conversations[user_id] = {
                        "messages": [
                            {
                                "role": "system", 
                                "content": custom_persona,
                                "timestamp": datetime.now().isoformat()
                            }
                        ],
                        "last_active": datetime.now().isoformat(),
                        "custom_persona": custom_persona,
                        "presets": presets,
                        "active_preset": active_preset,
                        "last_feedback": last_feedback,
                        "language": data.get("language", DEFAULT_LANGUAGE),
                        "last_cleanup_notification": datetime.now().isoformat()
                    }
                    deleted_count += 1
                    user_conversations[user_id]["show_cleanup_message"] = True
                    user_conversations[user_id]["deleted_messages_count"] = old_msg_count - 1
        if deleted_count > 0:
            logger.info(f"Cleaned conversations for {deleted_count} users due to inactivity")
        save_permanent_data()
    except Exception as e:
        logger.error(f"Error cleaning old conversations: {e}")

def update_user_stats(user_id, stat_type):
    try:
        if user_id not in user_stats:
            user_stats[user_id] = copy.deepcopy(DEFAULT_USER_STATS)
        if stat_type not in user_stats[user_id]:
            user_stats[user_id][stat_type] = 0
        user_stats[user_id][stat_type] += 1
        save_data()
    except Exception as e:
        logger.error(f"Error updating statistics: {e}")

def get_user_memory(user_id):
    try:
        if user_id not in user_conversations:
            default_persona = get_default_persona(DEFAULT_LANGUAGE)
            user_conversations[user_id] = {
                "messages": [
                    {
                        "role": "system", 
                        "content": default_persona,
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "last_active": datetime.now().isoformat(),
                "custom_persona": default_persona,
                "presets": [],
                "active_preset": None,
                "last_feedback": None,
                "language": DEFAULT_LANGUAGE
            }
        else:
            user_data = user_conversations[user_id]
            if "presets" not in user_data:
                user_data["presets"] = []
            if "active_preset" not in user_data:
                user_data["active_preset"] = None
            if "custom_persona" not in user_data:
                language = user_data.get("language", DEFAULT_LANGUAGE)
                user_data["custom_persona"] = get_default_persona(language)
            if "last_feedback" not in user_data:
                user_data["last_feedback"] = None
            if "language" not in user_data:
                user_data["language"] = DEFAULT_LANGUAGE
            if user_data["messages"] and user_data["messages"][0]["role"] == "system":
                user_data["messages"][0]["content"] = user_data["custom_persona"]
        return user_conversations[user_id]
    except Exception as e:
        logger.error(f"Error getting user memory: {e}")
        default_persona = get_default_persona(DEFAULT_LANGUAGE)
        return {
            "messages": [
                {
                    "role": "system", 
                    "content": default_persona,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "last_active": datetime.now().isoformat(),
            "custom_persona": default_persona,
            "presets": [],
            "active_preset": None,
            "last_feedback": None,
            "language": DEFAULT_LANGUAGE
        }

def clean_response(response):
    try:
        if not response:
            return "Sorry, I couldn't generate a response. Please try again."
        response = re.sub(r'\?\?+$', '', response)
        response = re.sub(r'[^\w\s\u0600-\u06FF\.\,\!\"\'\-\؟]$', '', response)
        return response.strip()
    except Exception as e:
        logger.error(f"Error cleaning response: {e}")
        return "Sorry, an error occurred while processing the response."

def advanced_processing(messages, custom_persona=None):
    try:
        processed_messages = copy.deepcopy(messages)
        system_message = custom_persona if custom_persona else "You are a helpful assistant who speaks English. Be friendly and helpful in your responses."
        context = extract_conversation_context(processed_messages)
        intent = analyze_user_intent(processed_messages[-1]["content"] if processed_messages else "")
        sentiment = analyze_sentiment(processed_messages)
        keywords = extract_keywords(processed_messages)
        detail_level = determine_detail_level(processed_messages)
        direct_questions = identify_direct_questions(processed_messages)
        timeline = analyze_conversation_timeline(processed_messages)
        priorities = determine_response_priorities(processed_messages)
        patterns = analyze_conversation_patterns(processed_messages)
        enhanced_system_message = build_enhanced_system_message(
            system_message, context, intent, sentiment, keywords,
            detail_level, direct_questions, timeline, priorities, patterns
        )
        if processed_messages and processed_messages[0]["role"] == "system":
            processed_messages[0]["content"] = enhanced_system_message
        else:
            processed_messages.insert(0, {"role": "system", "content": enhanced_system_message})
        return processed_messages
    except Exception as e:
        logger.error(f"Error in advanced processing: {e}")
        return messages

def extract_conversation_context(messages):
    try:
        if len(messages) <= 2:
            return "New conversation, not much context"
        recent_messages = messages[-5:]
        context = "Recent conversation context: "
        for msg in recent_messages:
            if msg["role"] == "user":
                context += f"User: {msg['content'][:50]}... "
            elif msg["role"] == "assistant":
                context += f"Assistant: {msg['content'][:30]}... "
        return context
    except:
        return "Cannot extract context due to error"

def analyze_user_intent(user_message):
    try:
        user_message = user_message.lower()
        if any(word in user_message for word in ["how", "method", "steps"]):
            return "User requests explanation or instructions"
        elif any(word in user_message for word in ["why", "reason", "cause"]):
            return "User requests explanation or reasons"
        elif any(word in user_message for word in ["what is", "definition"]):
            return "User requests definition or concept explanation"
        elif any(word in user_message for word in ["want", "need", "search for"]):
            return "User requests help finding something"
        else:
            return "General intent - normal conversation or inquiry"
    except:
        return "Undefined intent"

def analyze_sentiment(messages):
    try:
        if not messages:
            return "Neutral"
        last_user_message = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), "")
        last_user_message = last_user_message.lower()
        positive_words = ["thanks", "excellent", "great", "beautiful", "well done"]
        negative_words = ["angry", "bad", "annoying", "wrong", "why"]
        if any(word in last_user_message for word in positive_words):
            return "Positive"
        elif any(word in last_user_message for word in negative_words):
            return "Negative"
        else:
            return "Neutral"
    except:
        return "Neutral"

def extract_keywords(messages):
    try:
        if not messages:
            return "No keywords"
        all_text = " ".join([msg["content"] for msg in messages if "content" in msg])
        stop_words = ["in", "from", "on", "to", "that", "he", "she", "is", "what", "not"]
        words = re.findall(r'\b[\u0600-\u06FF]{3,}\b', all_text)
        keywords = [word for word in words if word not in stop_words]
        return ", ".join(list(set(keywords))[:5])
    except:
        return "No keywords"

def determine_detail_level(messages):
    try:
        if not messages:
            return "Medium"
        last_user_message = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), "")
        if any(word in last_user_message for word in ["briefly", "quickly", "summarize"]):
            return "Low"
        elif any(word in last_user_message for word in ["in detail", "detailed explanation", "detailed"]):
            return "High"
        else:
            return "Medium"
    except:
        return "Medium"

def identify_direct_questions(messages):
    try:
        if not messages:
            return "No direct questions"
        questions = []
        for msg in messages[-3:]:
            if msg["role"] == "user" and any(mark in msg["content"] for mark in ["؟", "?", "what is", "how"]):
                questions.append(msg["content"][:50] + "...")
        return ", ".join(questions) if questions else "No recent direct questions"
    except:
        return "No direct questions"

def analyze_conversation_timeline(messages):
    try:
        if len(messages) < 3:
            return "New conversation, no long timeline"
        user_msg_count = sum(1 for msg in messages if msg["role"] == "user")
        assistant_msg_count = sum(1 for msg in messages if msg["role"] == "assistant")
        return f"Conversation has {user_msg_count} user messages and {assistant_msg_count} responses"
    except:
        return "Cannot analyze timeline"

def determine_response_priorities(messages):
    try:
        if not messages:
            return "Respond to current message only"
        last_user_message = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), "")
        if any(word in last_user_message for word in ["important", "urgent", "critical"]):
            return "High priority - respond urgently and directly"
        elif any(word in last_user_message for word in ["curiosity", "know", "understand"]):
            return "Medium priority - detailed explanation"
        else:
            return "Normal priority - usual response"
    except:
        return "Normal priority - usual response"

def analyze_conversation_patterns(messages):
    try:
        if len(messages) < 5:
            return "No clear patterns yet (short conversation)"
        roles = [msg["role"] for msg in messages]
        user_streak = 0
        max_user_streak = 0
        for role in roles:
            if role == "user":
                user_streak += 1
                max_user_streak = max(max_user_streak, user_streak)
            else:
                user_streak = 0
        if max_user_streak >= 2:
            return "Pattern: User sends multiple consecutive messages (may be excited or need urgent help)"
        else:
            return "Pattern: Normal alternation between user and assistant"
    except:
        return "Cannot analyze patterns"

def build_enhanced_system_message(base_message, context, intent, sentiment, keywords,
                                 detail_level, direct_questions, timeline, priorities, patterns):
    try:
        enhanced_message = f"""
{base_message}
**Advanced Conversation Analysis:**
- **Context:** {context}
- **Intent:** {intent}
- **Sentiment:** {sentiment}
- **Keywords:** {keywords}
- **Detail Level:** {detail_level}
- **Direct Questions:** {direct_questions}
- **Timeline:** {timeline}
- **Priorities:** {priorities}
- **Patterns:** {patterns}
**Response Guidelines:**
- Focus on answering direct questions first
- Adapt detail level according to request
- Notice user sentiment state
- Use keywords in your response
- Follow the specified priorities
"""
        return enhanced_message
    except:
        return base_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_memory = get_user_memory(user_id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        if bot_stats.get("downtime_start"):
            downtime_start = datetime.fromisoformat(bot_stats["downtime_start"])
            downtime = datetime.now() - downtime_start
            duration_text = format_downtime(downtime)
            downtime_message = get_translation(user_id, "downtime_message", duration=duration_text)
            await update.message.reply_text(downtime_message)
            return
        
        if user_memory.get("show_cleanup_message"):
            deleted_count = user_memory.get("deleted_messages_count", 0)
            if deleted_count > 0:
                cleanup_message = get_translation(user_id, "cleanup_message", count=deleted_count)
                await update.message.reply_text(cleanup_message)
            user_memory["show_cleanup_message"] = False
            save_data()
        
        help_text = get_translation(user_id, "start_message")
        await update.message.reply_text(help_text)
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        error_message = get_translation(user_id, "error_command")
        await update.message.reply_text(error_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        help_text = get_translation(user_id, "help_message")
        await update.message.reply_text(help_text)
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        error_message = get_translation(user_id, "error_command")
        await update.message.reply_text(error_message)

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_memory = get_user_memory(user_id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        custom_persona = user_memory.get("custom_persona", get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE)))
        presets = user_memory.get("presets", [])
        active_preset = user_memory.get("active_preset", None)
        last_feedback = user_memory.get("last_feedback", None)
        user_memory["messages"] = [
            {
                "role": "system", 
                "content": custom_persona,
                "timestamp": datetime.now().isoformat()
            }
        ]
        user_memory["last_active"] = datetime.now().isoformat()
        user_memory["presets"] = presets
        user_memory["active_preset"] = active_preset
        user_memory["last_feedback"] = last_feedback
        save_data()
        clear_message = get_translation(user_id, "clear_message")
        await update.message.reply_text(clear_message)
    except Exception as e:
        logger.error(f"Error in clear command: {e}")
        error_message = get_translation(user_id, "error_command")
        await update.message.reply_text(error_message)

async def think_full_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_memory = get_user_memory(user_id)
        update_user_stats(user_id, "think_full")
        update_bot_stats(1, user_id)
        thinking_msg = await update.message.reply_text(get_translation(user_id, "deep_thinking", progress=0))
        last_10_messages = user_memory["messages"][-10:] if len(user_memory["messages"]) > 10 else user_memory["messages"]
        if not last_10_messages:
            no_messages = get_translation(user_id, "no_messages_to_analyze")
            await thinking_msg.edit_text(no_messages)
            return
        
        analysis_messages = [
            {
                "role": "system",
                "content": "You are an expert conversation analyst. Comprehensively analyze the last 10 messages in the conversation."
            }
        ]
        for i, msg in enumerate(last_10_messages):
            if msg["role"] == "user":
                analysis_messages.append({"role": "user", "content": f"Message {i+1} from user: {msg['content']}"})
            elif msg["role"] == "assistant":
                analysis_messages.append({"role": "user", "content": f"Response {i+1} from assistant: {msg['content']}"})
        
        response = g4f.ChatCompletion.create(
            model="gpt-4o",
            provider=g4f.Provider.MetaAI,
            messages=analysis_messages,
            stream=False,
        )
        cleaned_response = clean_response(response)
        analysis_text = get_translation(user_id, "think_full_analysis", count=len(last_10_messages), response=cleaned_response)
        await thinking_msg.edit_text(analysis_text)
    except Exception as e:
        logger.error(f"Error in think_full command: {e}")
        try:
            error_message = get_translation(user_id, "error_analysis")
            await thinking_msg.edit_text(error_message)
        except:
            error_message = get_translation(user_id, "error_analysis")
            await update.message.reply_text(error_message)

async def update_progress(thinking_msg, progress, user_id):
    try:
        progress_text = get_translation(user_id, "deep_thinking", progress=progress)
        await thinking_msg.edit_text(progress_text)
    except:
        pass

async def think_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_memory = get_user_memory(user_id)
    update_user_stats(user_id, "think")
    update_bot_stats(1, user_id)
    if not context.args:
        no_query = get_translation(user_id, "enter_think_query")
        await update.message.reply_text(no_query)
        return
    
    query = " ".join(context.args)
    thinking_msg = await update.message.reply_text(get_translation(user_id, "deep_thinking", progress=0))
    try:
        responses = []
        perspectives = [
            "Deep philosophical analysis",
            "Accurate scientific analysis",
            "Practical application perspective",
            "Psychological and emotional analysis",
            "Historical perspective",
            "Future vision and prediction",
            "Economic analysis",
            "Social and cultural perspective",
            "Creative innovative analysis",
            "Comprehensive integrated vision"
        ]
        for i, perspective in enumerate(perspectives):
            try:
                progress = (i + 1) * 10
                await update_progress(thinking_msg, progress, user_id)
                response = g4f.ChatCompletion.create(
                    model="gpt-4o",
                    provider=g4f.Provider.MetaAI,
                    messages=[
                        {"role": "system", "content": f"Provide a deep and comprehensive analysis from perspective: {perspective}. Be accurate and detailed."},
                        {"role": "user", "content": query}
                    ],
                    stream=False,
                )
                cleaned_response = clean_response(response)
                if len(cleaned_response.split('\n')) > 25:
                    lines = cleaned_response.split('\n')
                    cleaned_response = '\n'.join(lines[:25]) + "\n... (Analysis shortened for focus)"
                responses.append(f"## Perspective {i+1}: {perspective}\n{cleaned_response}\n")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error generating response from perspective {i+1}: {e}")
                continue
        
        if not responses:
            error_message = get_translation(user_id, "error_thinking")
            await thinking_msg.edit_text(error_message)
            return
        
        await update_progress(thinking_msg, 95, user_id)
        try:
            all_responses_text = "\n".join(responses)
            if len(all_responses_text) > 4000:
                shortened_responses = []
                for response in responses:
                    lines = response.split('\n')
                    if len(lines) > 10:
                        shortened = '\n'.join(lines[:10]) + "\n... (Analysis shortened)"
                        shortened_responses.append(shortened)
                    else:
                        shortened_responses.append(response)
                all_responses_text = "\n".join(shortened_responses)
            
            merge_prompt = f"""
            Merge the following analyses from ten different perspectives into one integrated, comprehensive, and organized response:
            {all_responses_text}
            Merge instructions:
            1. Provide a final response that integrates all these insights coherently
            2. Organize content in a logical and organized manner
            3. Add subheadings for each main section
            4. Ensure comprehensive and accurate response
            5. Delete any unnecessary repetition
            6. Arrange ideas in logical sequential order
            7. Write in clear language of the user
            8. Add conclusion summarizing main points
            9. Do not exceed 100-150 lines
            The final response should be a comprehensive analysis covering all aspects presented.
            """
            merged_response = g4f.ChatCompletion.create(
                model="gpt-4o",
                provider=g4f.Provider.MetaAI,
                messages=[
                    {"role": "system", "content": "You are an expert in merging multiple analyses. Provide a final response that integrates all perspectives coherently and organized while maintaining depth and accuracy."},
                    {"role": "user", "content": merge_prompt}
                ],
                stream=False,
            )
            cleaned_response = clean_response(merged_response)
            if len(cleaned_response.split('\n')) > 150:
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[:150]) + "\n... (Final analysis shortened for focus)"
            
            user_memory["messages"].extend([
                {"role": "user", "content": f"/think {query}", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": cleaned_response, "timestamp": datetime.now().isoformat()}
            ])
            save_data()
            result_text = get_translation(user_id, "deep_thinking_result", response=cleaned_response)
            await thinking_msg.edit_text(result_text)
        except Exception as merge_error:
            logger.error(f"Error merging responses: {merge_error}")
            fallback_response = get_translation(user_id, "deep_thinking_result", response="")
            for i, response in enumerate(responses[:3]):
                fallback_response += f"\n{response}\n{'='*50}\n"
            fallback_response += "\n" + get_translation(user_id, "error_merging")
            user_memory["messages"].extend([
                {"role": "user", "content": f"/think {query}", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": fallback_response, "timestamp": datetime.now().isoformat()}
            ])
            save_data()
            await thinking_msg.edit_text(fallback_response)
    except Exception as e:
        logger.error(f"Error in think command: {e}")
        try:
            error_message = get_translation(user_id, "error_thinking")
            await thinking_msg.edit_text(error_message)
        except:
            error_message = get_translation(user_id, "error_thinking")
            await update.message.reply_text(error_message)

async def web_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_memory = get_user_memory(user_id)
    update_user_stats(user_id, "web_searches")
    update_bot_stats(1, user_id)
    if not context.args:
        no_query = get_translation(user_id, "enter_search_query")
        await update.message.reply_text(no_query)
        return
    
    query = " ".join(context.args)
    search_msg = await update.message.reply_text(get_translation(user_id, "web_searching"))
    try:
        search_prompt = f"""
        You are an advanced search assistant. Search for the following information through the internet focusing on reliable and recent sources.
        Search query: {query}
        Search instructions:
        1. Search in more than 20 different reliable sources
        2. Focus on recent sources (last 6 months)
        3. Verify information accuracy from multiple sources
        4. Compare between different sources
        5. Exclude unreliable or old information
        6. Provide comprehensive answer covering all aspects of the query
        7. Add information sources if possible
        8. Organize response in clear and logical manner
        The answer should be accurate, comprehensive and reliable, focusing on the latest available information.
        """
        response = g4f.ChatCompletion.create(
            model="gpt-4o",
            provider=g4f.Provider.MetaAI,
            messages=[
                {"role": "system", "content": "You are a specialized search assistant. Your task is to search for information through the internet from reliable and multiple sources. Provide accurate and comprehensive answers focusing on recent and reliable sources."},
                {"role": "user", "content": search_prompt}
            ],
            stream=False,
        )
        cleaned_response = clean_response(response)
        user_memory["messages"].extend([
            {"role": "user", "content": f"/web {query}", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": cleaned_response, "timestamp": datetime.now().isoformat()}
        ])
        save_data()
        results_text = get_translation(user_id, "web_results", query=query, response=cleaned_response)
        await search_msg.edit_text(results_text)
    except Exception as e:
        logger.error(f"Error in web command: {e}")
        try:
            error_message = get_translation(user_id, "error_search")
            await search_msg.edit_text(error_message)
        except:
            error_message = get_translation(user_id, "error_search")
            await update.message.reply_text(error_message)

async def customize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_memory = get_user_memory(user_id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        if context.args and context.args[0] == "/s":
            if not user_memory["custom_persona"] or user_memory["custom_persona"] == get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE)):
                no_customization = get_translation(user_id, "no_customization_to_save")
                await update.message.reply_text(no_customization)
                return
            if len(user_memory["presets"]) >= 10:
                max_presets = get_translation(user_id, "max_presets_reached")
                await update.message.reply_text(max_presets)
                return
            new_preset = {
                "id": len(user_memory["presets"]),
                "persona": user_memory["custom_persona"],
                "title": get_translation(user_id, "preset_title_default", number=len(user_memory['presets']) + 1),
                "created_at": datetime.now().isoformat()
            }
            user_memory["presets"].append(new_preset)
            update_user_stats(user_id, "presets_created")
            save_data()
            saved_message = get_translation(user_id, "customization_saved", title=new_preset['title'])
            await update.message.reply_text(saved_message)
            return
        elif context.args and context.args[0] == "/t" and len(context.args) > 1:
            if not user_memory["presets"]:
                no_presets = get_translation(user_id, "no_presets")
                await update.message.reply_text(no_presets)
                return
            new_title = " ".join(context.args[1:])
            user_memory["presets"][-1]["title"] = new_title
            save_data()
            updated_message = get_translation(user_id, "preset_title_updated", title=new_title)
            await update.message.reply_text(updated_message)
            return
        elif context.args and context.args[0] == "/list":
            if not user_memory["presets"]:
                no_presets = get_translation(user_id, "no_presets")
                await update.message.reply_text(no_presets)
                return
            presets_list = ""
            for i, preset in enumerate(user_memory["presets"]):
                active_indicator = " ✅" if user_memory.get("active_preset") == preset["id"] else ""
                presets_list += f"{i+1}. {preset['title']}{active_indicator}\n"
            presets_text = get_translation(user_id, "saved_presets", list=presets_list)
            await update.message.reply_text(presets_text)
            return
        elif context.args and context.args[0] == "/use" and len(context.args) > 1:
            try:
                preset_id = int(context.args[1]) - 1
                if preset_id < 0 or preset_id >= len(user_memory["presets"]):
                    invalid_number = get_translation(user_id, "invalid_preset_number")
                    await update.message.reply_text(invalid_number)
                    return
                preset = user_memory["presets"][preset_id]
                user_memory["custom_persona"] = preset["persona"]
                user_memory["active_preset"] = preset["id"]
                if user_memory["messages"] and user_memory["messages"][0]["role"] == "system":
                    user_memory["messages"][0]["content"] = preset["persona"]
                update_user_stats(user_id, "presets_used")
                save_data()
                activated_message = get_translation(user_id, "preset_activated", title=preset['title'])
                await update.message.reply_text(activated_message)
                return
            except ValueError:
                invalid_number = get_translation(user_id, "invalid_preset_number")
                await update.message.reply_text(invalid_number)
                return
        elif context.args and context.args[0] == "/delete" and len(context.args) > 1:
            try:
                preset_id = int(context.args[1]) - 1
                if preset_id < 0 or preset_id >= len(user_memory["presets"]):
                    invalid_number = get_translation(user_id, "invalid_preset_number")
                    await update.message.reply_text(invalid_number)
                    return
                deleted_preset = user_memory["presets"].pop(preset_id)
                for i, preset in enumerate(user_memory["presets"]):
                    preset["id"] = i
                if user_memory.get("active_preset") == preset_id:
                    user_memory["active_preset"] = None
                    user_memory["custom_persona"] = get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE))
                    if user_memory["messages"] and user_memory["messages"][0]["role"] == "system":
                        user_memory["messages"][0]["content"] = get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE))
                save_data()
                deleted_message = get_translation(user_id, "preset_deleted", title=deleted_preset['title'])
                await update.message.reply_text(deleted_message)
                return
            except ValueError:
                invalid_number = get_translation(user_id, "invalid_preset_number")
                await update.message.reply_text(invalid_number)
                return
        if not context.args:
            keyboard_options = [
                [get_translation(user_id, "reset_to_default")],
                [get_translation(user_id, "save_as_preset"), get_translation(user_id, "show_presets")],
                [get_translation(user_id, "cancel")]
            ]
            reply_markup = {
                "keyboard": keyboard_options,
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
            customization_text = get_translation(user_id, "customization_start")
            await update.message.reply_text(
                customization_text,
                reply_markup=reply_markup
            )
            return
        new_persona = " ".join(context.args)
        user_memory["custom_persona"] = new_persona
        user_memory["active_preset"] = None
        if user_memory["messages"] and user_memory["messages"][0]["role"] == "system":
            user_memory["messages"][0]["content"] = new_persona
        update_user_stats(user_id, "customizations")
        save_data()
        keyboard_options = [
            [get_translation(user_id, "save_as_preset")],
            [get_translation(user_id, "skip")]
        ]
        reply_markup = {
            "keyboard": keyboard_options,
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        personality_text = get_translation(user_id, "personality_customized", personality=new_persona)
        await update.message.reply_text(
            personality_text,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in customize command: {e}")
        error_message = get_translation(user_id, "error_command")
        await update.message.reply_text(error_message)

async def handle_customization_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        user_memory = get_user_memory(user_id)
        
        reset_text = get_translation(user_id, "reset_to_default")
        save_preset_text = get_translation(user_id, "save_as_preset")
        show_presets_text = get_translation(user_id, "show_presets")
        skip_text = get_translation(user_id, "skip")
        cancel_text = get_translation(user_id, "cancel")
        
        if user_message == reset_text:
            default_persona = get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE))
            user_memory["custom_persona"] = default_persona
            user_memory["active_preset"] = None
            if user_memory["messages"] and user_memory["messages"][0]["role"] == "system":
                user_memory["messages"][0]["content"] = default_persona
            save_data()
            reset_message = get_translation(user_id, "reset_to_default")
            await update.message.reply_text(reset_message)
        elif user_message == save_preset_text:
            if not user_memory["custom_persona"] or user_memory["custom_persona"] == get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE)):
                no_customization = get_translation(user_id, "no_customization_to_save")
                await update.message.reply_text(no_customization)
                return
            if len(user_memory["presets"]) >= 10:
                max_presets = get_translation(user_id, "max_presets_reached")
                await update.message.reply_text(max_presets)
                return
            new_preset = {
                "id": len(user_memory["presets"]),
                "persona": user_memory["custom_persona"],
                "title": get_translation(user_id, "preset_title_default", number=len(user_memory['presets']) + 1),
                "created_at": datetime.now().isoformat()
            }
            user_memory["presets"].append(new_preset)
            update_user_stats(user_id, "presets_created")
            save_data()
            saved_message = get_translation(user_id, "customization_saved", title=new_preset['title'])
            await update.message.reply_text(saved_message)
        elif user_message == show_presets_text:
            if not user_memory["presets"]:
                no_presets = get_translation(user_id, "no_presets")
                await update.message.reply_text(no_presets)
                return
            presets_list = ""
            for i, preset in enumerate(user_memory["presets"]):
                active_indicator = " ✅" if user_memory.get("active_preset") == preset["id"] else ""
                presets_list += f"{i+1}. {preset['title']}{active_indicator}\n"
            presets_text = get_translation(user_id, "saved_presets", list=presets_list)
            await update.message.reply_text(presets_text)
        elif user_message == skip_text:
            skip_message = get_translation(user_id, "preset_save_skipped")
            await update.message.reply_text(skip_message)
        elif user_message == cancel_text:
            cancel_message = get_translation(user_id, "customization_cancelled")
            await update.message.reply_text(cancel_message)
        
        remove_keyboard = {"remove_keyboard": True}
        options_closed = get_translation(user_id, "customization_options_closed")
        await update.message.reply_text(options_closed, reply_markup=remove_keyboard)
    except Exception as e:
        logger.error(f"Error in handle_customization_choice: {e}")
        error_message = get_translation(user_id, "error_command")
        await update.message.reply_text(error_message)

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        if user_id not in user_stats:
            no_stats = get_translation(user_id, "no_stats")
            await update.message.reply_text(no_stats)
            return
        
        stats = user_stats[user_id]
        user_memory = get_user_memory(user_id)
        oldest_msg_days = 0
        if user_memory["messages"] and len(user_memory["messages"]) > 1:
            try:
                oldest_msg_time = min(
                    datetime.fromisoformat(msg["timestamp"]) 
                    for msg in user_memory["messages"] 
                    if "timestamp" in msg
                )
                oldest_msg_days = (datetime.now() - oldest_msg_time).days
            except:
                oldest_msg_days = 0
        
        custom_personality = "✅" if user_memory.get('custom_persona') != get_default_persona(user_memory.get("language", DEFAULT_LANGUAGE)) else "❌"
        
        stats_text = get_translation(user_id, "user_stats", 
            messages_sent=stats.get('messages_sent', 0),
            messages_received=stats.get('messages_received', 0),
            think=stats.get('think', 0),
            think_full=stats.get('think_full', 0),
            customizations=stats.get('customizations', 0),
            presets_created=stats.get('presets_created', 0),
            presets_used=stats.get('presets_used', 0),
            web_searches=stats.get('web_searches', 0),
            feedbacks_submitted=stats.get('feedbacks_submitted', 0),
            messages_saved=len(user_memory['messages']),
            oldest_days=max(1, oldest_msg_days),
            custom_personality=custom_personality,
            presets_count=len(user_memory.get('presets', []))
        )
        await update.message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"Error in mystats command: {e}")
        error_message = get_translation(user_id, "error_showing_stats")
        await update.message.reply_text(error_message)

async def users_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        update_users_info()
        try:
            with open('users_info.json', 'r', encoding='utf-8') as f:
                users_info = json.load(f)
        except:
            users_info = {
                "awake_users": 0,
                "sleeping_users": 0,
                "dead_users": 0,
                "total_users": 0,
                "total_feedbacks": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        feedbacks_text = ""
        recent_feedbacks = users_info.get('recent_feedbacks', [])
        if recent_feedbacks:
            for i, feedback in enumerate(recent_feedbacks[:3]):
                user_id_short = feedback.get('user_id', '')[:8] + '...' if feedback.get('user_id') else 'Unknown'
                feedback_text = feedback.get('feedback', '')[:50] + '...' if len(feedback.get('feedback', '')) > 50 else feedback.get('feedback', '')
                feedbacks_text += f"\n{i+1}. User {user_id_short}: {feedback_text}"
        else:
            feedbacks_text = get_translation(user_id, "no_recent_feedbacks")
        
        last_updated = datetime.fromisoformat(users_info.get('last_updated', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')
        
        info_text = get_translation(user_id, "general_user_stats", 
            total_users=users_info.get('total_users', 0),
            awake_users=users_info.get('awake_users', 0),
            sleeping_users=users_info.get('sleeping_users', 0),
            dead_users=users_info.get('dead_users', 0),
            total_feedbacks=users_info.get('total_feedbacks', 0),
            last_updated=last_updated,
            feedbacks=feedbacks_text
        )
        await update.message.reply_text(info_text)
    except Exception as e:
        logger.error(f"Error in users_info command: {e}")
        error_message = get_translation(user_id, "error_showing_stats")
        await update.message.reply_text(error_message)

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_memory = get_user_memory(user_id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        if not context.args:
            await update.message.reply_text(get_translation(user_id, "enter_feedback_query"))
            return
        
        if user_memory.get("last_feedback"):
            last_feedback_time = datetime.fromisoformat(user_memory["last_feedback"])
            time_since_last = datetime.now() - last_feedback_time
            if time_since_last.days < 5:
                days_left = 5 - time_since_last.days
                waiting_message = get_translation(user_id, "feedback_waiting", days=days_left)
                await update.message.reply_text(waiting_message)
                return
        
        feedback_text = " ".join(context.args)
        user_feedbacks[user_id] = {
            "feedback": feedback_text,
            "timestamp": datetime.now().isoformat(),
            "username": update.effective_user.username or "Unknown",
            "first_name": update.effective_user.first_name or "Unknown"
        }
        user_memory["last_feedback"] = datetime.now().isoformat()
        update_user_stats(user_id, "feedbacks_submitted")
        save_data()
        feedback_sent = get_translation(user_id, "feedback_sent", days_left=5)
        await update.message.reply_text(feedback_sent)
    except Exception as e:
        logger.error(f"Error in feedback command: {e}")
        error_message = get_translation(user_id, "error_sending_feedback")
        await update.message.reply_text(error_message)

async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        credits_text = get_translation(user_id, "developer_info")
        await update.message.reply_text(credits_text)
    except Exception as e:
        logger.error(f"Error in credits command: {e}")
        error_message = get_translation(user_id, "error_showing_credits")
        await update.message.reply_text(error_message)

async def server_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        server_info = get_server_info()
        if not server_info:
            error_message = get_translation(user_id, "error_showing_server_info")
            await update.message.reply_text(error_message)
            return
        
        uptime = get_uptime()
        formatted_uptime = format_uptime(uptime)
        
        if bot_stats.get("downtime_start"):
            downtime_start = datetime.fromisoformat(bot_stats["downtime_start"])
            downtime = datetime.now() - downtime_start
            bot_status = get_translation(user_id, "bot_status_offline", duration=format_downtime(downtime))
        else:
            bot_status = get_translation(user_id, "bot_status_online")
        
        info_text = get_translation(user_id, "server_info",
            uptime=formatted_uptime,
            cpu_percent=server_info['cpu']['percent'],
            cpu_count=server_info['cpu']['count'],
            cpu_freq_current=server_info['cpu']['freq_current'],
            cpu_freq_max=server_info['cpu']['freq_max'],
            memory_total=server_info['memory']['total'],
            memory_used=server_info['memory']['used'],
            memory_percent=server_info['memory']['percent'],
            disk_total=server_info['disk']['total'],
            disk_used=server_info['disk']['used'],
            disk_percent=server_info['disk']['percent'],
            total_messages=bot_stats['total_messages_processed'],
            messages_today=bot_stats['messages_today'],
            messages_week=bot_stats['messages_week'],
            messages_month=bot_stats['messages_month'],
            users_today=len(bot_stats['users_today']),
            users_week=len(bot_stats['users_week']),
            users_month=len(bot_stats['users_month']),
            bot_status=bot_status
        )
        await update.message.reply_text(info_text)
    except Exception as e:
        logger.error(f"Error in server_info command: {e}")
        error_message = get_translation(user_id, "error_showing_server_info")
        await update.message.reply_text(error_message)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, lang_code):
    user_id = str(update.effective_user.id)
    user_memory = get_user_memory(user_id)
    
    if lang_code not in SUPPORTED_LANGUAGES:
        supported_codes = ", ".join(SUPPORTED_LANGUAGES.keys())
        error_message = get_translation(user_id, "unsupported_language", codes=supported_codes)
        await update.message.reply_text(error_message)
        return
    
    user_memory["language"] = lang_code
    default_persona = get_default_persona(lang_code)
    user_memory["custom_persona"] = default_persona
    if user_memory["messages"] and user_memory["messages"][0]["role"] == "system":
        user_memory["messages"][0]["content"] = default_persona
    
    save_data()
    
    language_name = SUPPORTED_LANGUAGES[lang_code]
    success_message = get_translation(user_id, "language_changed", language=language_name)
    await update.message.reply_text(success_message)

async def set_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_language(update, context, "en")

async def set_spanish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_language(update, context, "sp")

async def set_french(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_language(update, context, "fr")

async def set_russian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_language(update, context, "ru")

async def set_arabic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_language(update, context, "ar")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        user_message = update.message.text
        user_memory = get_user_memory(user_id)
        if bot_stats.get("downtime_start"):
            downtime_start = datetime.fromisoformat(bot_stats["downtime_start"])
            downtime = datetime.now() - downtime_start
            duration_text = format_downtime(downtime)
            downtime_message = get_translation(user_id, "downtime_message", duration=duration_text)
            await update.message.reply_text(downtime_message)
            return
        
        if user_memory.get("show_cleanup_message"):
            deleted_count = user_memory.get("deleted_messages_count", 0)
            if deleted_count > 0:
                cleanup_message = get_translation(user_id, "cleanup_message", count=deleted_count)
                await update.message.reply_text(cleanup_message)
            user_memory["show_cleanup_message"] = False
            save_data()
        
        update_user_stats(user_id, "messages_received")
        update_bot_stats(1, user_id)
        
        reset_text = get_translation(user_id, "reset_to_default")
        save_preset_text = get_translation(user_id, "save_as_preset")
        show_presets_text = get_translation(user_id, "show_presets")
        skip_text = get_translation(user_id, "skip")
        cancel_text = get_translation(user_id, "cancel")
        
        if user_message in [reset_text, save_preset_text, show_presets_text, skip_text, cancel_text]:
            await handle_customization_choice(update, context)
            return
        
        user_memory["messages"].append({
            "role": "user", 
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        user_memory["last_active"] = datetime.now().isoformat()
        
        if len(user_memory["messages"]) > 100:
            system_message = user_memory["messages"][0]
            other_messages = user_memory["messages"][1:]
            user_memory["messages"] = [system_message] + other_messages[-99:]
        
        processed_messages = advanced_processing(
            [{k: v for k, v in msg.items() if k != "timestamp"} for msg in user_memory["messages"]],
            user_memory.get("custom_persona")
        )
        
        response = g4f.ChatCompletion.create(
            model="gpt-4o",
            provider=g4f.Provider.MetaAI,
            messages=processed_messages,
            stream=False,
        )
        cleaned_response = clean_response(response)
        
        user_memory["messages"].append({
            "role": "assistant", 
            "content": cleaned_response,
            "timestamp": datetime.now().isoformat()
        })
        
        await update.message.reply_text(cleaned_response)
        update_user_stats(user_id, "messages_sent")
        save_data()
        
        if len(user_memory["messages"]) % 10 == 0:
            cleanup_old_conversations()
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        user_id = str(update.effective_user.id)
        error_message = get_translation(user_id, "error_processing")
        await update.message.reply_text(error_message)

def cleanup_resources():
    try:
        import aiohttp
        if 'session' in globals():
            asyncio.get_event_loop().run_until_complete(session.close())
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def check_memory_usage():
    try:
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024
        if memory_usage > 500:
            logger.warning(f"High memory usage: {memory_usage:.2f}MB")
            import gc
            gc.collect()
            return True
    except Exception as e:
        logger.error(f"Memory check error: {e}")
    return False

async def main():
    atexit.register(cleanup_resources)
    load_data()
    try:
        cleanup_old_conversations()
    except Exception as e:
        logger.error(f"Error cleaning old conversations: {e}")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_memory))
    application.add_handler(CommandHandler("think", think_command))
    application.add_handler(CommandHandler("think_full", think_full_command))
    application.add_handler(CommandHandler("customize", customize_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    application.add_handler(CommandHandler("web", web_search_command))
    application.add_handler(CommandHandler("users_info", users_info_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CommandHandler("credits", credits_command))
    application.add_handler(CommandHandler("server_info", server_info_command))
    
    application.add_handler(CommandHandler("en", set_english))
    application.add_handler(CommandHandler("sp", set_spanish))
    application.add_handler(CommandHandler("fr", set_french))
    application.add_handler(CommandHandler("ru", set_russian))
    application.add_handler(CommandHandler("ar", set_arabic))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await application.initialize()
    
    asyncio.create_task(check_bot_status(application))
    
    await application.start()
    await application.updater.start_polling()
    
    print("Bot started successfully")
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        if sys.version_info < (3, 7):
            raise RuntimeError("This bot requires Python 3.7 or higher")
        
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Critical error starting bot: {e}", exc_info=True)
        print(f"Failed to start bot: {e}")
        sys.exit(1)