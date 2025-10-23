import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QScrollArea, QFrame, QSlider, QPushButton
)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


tips = {
    "🔥 Храм Огня": [
        {"text": "Класс «Наемник» — обладает парными шашками с самым высоким потенциальным DPS в игре.", "media": "1.jpg", "type": "image"},
        {"text": "В качестве погребального дара рекомендуется выбрать огненный самоцвет: на ранних локациях много врагов, уязвимых к огненному урону (особенно чёрные жижеподобные монстры).", "media": "2.jpg", "type": "image"},
        {"text": "Не бойтесь сражаться с кристальной ящеркой — её стоит убить ради дополнительных душ.", "media": "3.mp4", "type": "video"},
        {"text": "Судью Гундира можно атаковать сразу после извлечения меча из его тела — не обязательно ждать появления полоски здоровья.", "media": "4.mp4", "type": "video"},
        {"text": "Атаки алебардой Гундира можно парировать.", "media": "5.mp4", "type": "video"},
        {"text": "Слева от входа в Храм Огня — полуголый мужчина с катаной. Он может показаться сложным, но его, если постараться, можно сбросить с обрыва. Его катана — отличное оружие как в начале игры, так и вплоть до финала.", "media": "6.png", "type": "image"},
        {"text": "На крыше Храма Огня находятся ценные предметы и дополнительный «торговец». Ключ стоит 20 000 душ, но можно запаркурить на крышу, отпрыгнув от дерева напротив закрытой двери.", "media": "7.mp4", "type": "video"}
    ],
    "🏰 Высокая стена Лотрика": [
        {"text": "Сразу направо от старта локации — небольшая секция стены, где можно найти лук. Он понадобится для того чтобы прогнать виверну.", "media": "1_1.mp4", "type": "video"},
        {"text": "На пути встретится виверна, огнём блокирующая проход. Её дыхание можно спровоцировать, чтобы потом быстро пробежать в башню, где сидит дракон."},
        {"text": "Внутри — есть мимик с Глубинной секирой — одним из немногих оружий с уроном Тьмой на этом этапе. Отлично работает против босса локации."},
        {"text": "После активации следующего костра вернитесь и обстреляйте виверну стрелами — через некоторое время она улетит.", "media": "2_2.mp4", "type": "video"},
        {"text": "В подвале башни с костром находится Серокрыс — новый торговец для Храма Огня. Обязательно пройдите его квест!"},
        {"text": "На локации встречаются Полые, превращающиеся в чёрных монстров (как Гундир). Огненный урон эффективно их оглушает."},
        {"text": "Рыцарей с копьём легко обойти сзади и выполнить бэкстаб."},
        {"text": "После площади с фонтаном — зайдите в закоулок, чтобы открыть лифт-шорткат до первого костра. Это упростит путь к боссу.", "media": "3_3.mp4", "type": "video"},
        {"text": "Рядом со зданием, где сидит старуха, — красноглазый рыцарь. При победе он отдаст изысканный самоцвет."}
    ],
    "❄️ Вордт из Холодной долины": [
        {"text": "Огромный и неповоротливый босс. Уязвим к урону Тьмой. Можно использовать Глубинную секиру найденую ранее, для большего урона."},
        {"text": "Используйте его длинные атаки с дыханием: забегайте за его спину и наносите удары.", "media": "4_4.mp4", "type": "video"}
    ]
}


class VideoPlayerWidget(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(800, 450)
        self.video_widget.setStyleSheet("background-color: #000;")

        self.media_player.setVideoOutput(self.video_widget)

        self.play_button = QPushButton("▶️")
        self.play_button.setFixedWidth(120)
        self.play_button.clicked.connect(self.toggle_playback)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)
        control_layout.addWidget(QLabel("🔊"))
        control_layout.addWidget(self.volume_slider)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)
        self.setLayout(layout)

        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        if os.path.exists(video_path):
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
        else:
            self.play_button.setEnabled(False)
            self.video_widget.setStyleSheet("background-color: #333; color: #ff6666;")
            self.video_widget.setText("⚠️ Видео не найдено")

    @Slot()
    def on_volume_changed(self, value):
        self.audio_output.setVolume(value / 100.0)

    @Slot()
    def toggle_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("▶️")
        else:
            self.media_player.play()
            self.play_button.setText("⏸️")

    @Slot(int)
    def position_changed(self, position):
        self.position_slider.setValue(position)

    @Slot(int)
    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    @Slot(int)
    def set_position(self, position):
        self.media_player.setPosition(position)


class DarkSoulsGuideApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📖 Справочник советов по Dark Souls III")
        self.resize(980, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("Справочник по Dark Souls III")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #f0f0f0; margin: 10px;")
        main_layout.addWidget(title_label)

        location_layout = QHBoxLayout()
        location_label = QLabel("Выберите локацию:")
        location_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        self.location_combo = QComboBox()
        self.location_combo.addItems(tips.keys())
        self.location_combo.currentTextChanged.connect(self.display_content)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_combo)
        location_layout.addStretch()
        main_layout.addLayout(location_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        if tips:
            first_location = list(tips.keys())[0]
            self.location_combo.setCurrentText(first_location)
            self.display_content(first_location)

    def display_content(self, location):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if location in tips:
            for i, item in enumerate(tips[location], 1):
                # Текст
                label = QLabel(f"{i}. {item['text']}")
                label.setWordWrap(True)
                label.setStyleSheet("color: #f0f0f0; font-size: 14px; padding: 8px 0; font-family: 'Segoe UI';")
                self.content_layout.addWidget(label)

                if "media" in item:
                    media_path = item["media"]
                    media_type = item.get("type", "image")
                    if media_type == "image":
                        self._add_image(media_path)
                    elif media_type == "video":
                        self._add_video(media_path)

    def _add_image(self, filename):
        if os.path.exists(filename):
            pixmap = QPixmap(filename)
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(800, Qt.SmoothTransformation)
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setStyleSheet("margin: 10px 0;")
                self.content_layout.addWidget(img_label)
        else:
            warn = QLabel(f"⚠️ Файл {filename} не найден")
            warn.setStyleSheet("color: #ffaa00; font-style: italic; padding: 5px;")
            self.content_layout.addWidget(warn)

    def _add_video(self, filename):
        video_widget = VideoPlayerWidget(filename)
        video_widget.setStyleSheet("margin: 15px 0;")
        self.content_layout.addWidget(video_widget)


def apply_dark_theme(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = DarkSoulsGuideApp()
    window.show()
    sys.exit(app.exec())