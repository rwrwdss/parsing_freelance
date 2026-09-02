from .base import SourceHandler, LogEntry
from datetime import datetime, timezone
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FileHandler(SourceHandler):
    """Обработчик логов из файлов"""
    
    def __init__(self, name: str, file_path: str):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.last_position = 0  # Отслеживаем позицию в файле
    
    async def fetch(self) -> list[LogEntry]:
        """Читает новые строки из файла"""
        if not self.file_path.exists():
            logger.error(f"Файл не найден: {self.file_path}")
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # Переходим к последней позиции
                f.seek(self.last_position)
                
                entries = []
                for line in f:
                    line = line.strip()
                    if line:
                        entry = LogEntry(
                            source=self.name,
                            title="Лог",
                            content=line,
                            timestamp=datetime.now(tz=timezone.utc),
                        )
                        entries.append(entry)
                
                # Запоминаем новую позицию
                self.last_position = f.tell()
                
                if entries:
                    logger.info(f"Файл {self.name}: прочитано {len(entries)} строк")
                
                return entries
        
        except Exception as e:
            logger.error(f"Ошибка чтения файла {self.name}: {e}")
            return []
