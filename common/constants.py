# common/constants.py

# ===== Длины полей =====
# Пользователь
MAX_LENGTH_NAME = 124
MAX_LENGTH_SURNAME = 124
MAX_LENGTH_PHONE = 12
MAX_LENGTH_ABOUT = 256

# Проект
MAX_LENGTH_PROJECT_NAME = 200
MAX_LENGTH_PROJECT_STATUS = 6

# Навыки
MAX_LENGTH_SKILL_NAME = 124

# ===== Статусы проектов =====
PROJECT_STATUS_OPEN = 'open'
PROJECT_STATUS_CLOSED = 'closed'

# ===== GitHub =====
GITHUB_DOMAIN = 'github.com'

# ===== Пагинация =====
ITEMS_PER_PAGE = 12

# ===== Регулярные выражения =====
PHONE_REGEX = r'^\+7\d{10}$'

# ===== Аватары =====
AVATAR_SIZE = 200
AVATAR_BG_COLOR_MIN = 100
AVATAR_BG_COLOR_MAX = 200
AVATAR_TEXT_COLOR = 'white'
AVATAR_FONT_SIZE = 100
AVATAR_FONT_PATH = "arial.ttf"
AVATAR_ANCHOR_OFFSET = 0

# ===== Лимиты для API =====
SKILLS_AUTOCOMPLETE_LIMIT = 10
