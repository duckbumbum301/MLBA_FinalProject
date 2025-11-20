"""
AI Assistant Widget  
Tab chat với Gemini AI
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QLineEdit,
    QPushButton, QLabel, QComboBox, QMessageBox, QScrollArea, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QUrl, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QGuiApplication, QPixmap, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.user import User
from services.gemini_service import GeminiService
from database.connector import DatabaseConnector


class AIAssistantWidget(QWidget):
    """
    Widget cho Tab AI Trợ Lý
    Chat interface với Gemini AI
    """
    
    class ChatWorker(QThread):
        finished_text = pyqtSignal(str)
        error_text = pyqtSignal(str)

        def __init__(self, service: GeminiService, message: str, context: dict, context_type: str):
            super().__init__()
            self._service = service
            self._message = message
            self._context = context
            self._context_type = context_type

        def run(self):
            try:
                resp = self._service.send_message(
                    message=self._message,
                    context=self._context,
                    context_type=self._context_type
                )
                self.finished_text.emit(resp)
            except Exception as e:
                self.error_text.emit(str(e))

    def __init__(self, user: User, db_connector: DatabaseConnector):
        super().__init__()
        self.user = user
        self.db = db_connector
        
        # Initialize Gemini Service
        try:
            self.gemini_service = GeminiService(db_connector, user.id)
            self.gemini_available = self.gemini_service.is_available()
        except Exception as e:
            print(f"⚠ Gemini Service initialization failed: {e}")
            self.gemini_service = None
            self.gemini_available = False
        
        self.setup_ui()
        self._chat_log = []
        self._last_ai_text = None
        self._typing_timer = None
        self._typing_id = None
        self._current_worker = None
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 16)
        
        # Title
        title = QLabel("TRỢ LÝ AI TOP 1 VN - NYTDT")
        title.setObjectName('Heading3')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(38, 99, 234, 90))
        title.setGraphicsEffect(shadow)
        header = QVBoxLayout()
        header.setSpacing(6)
        header.setContentsMargins(0,0,0,0)
        header.addWidget(title)
        underline = QFrame()
        underline.setFixedHeight(4)
        underline.setMaximumWidth(80)
        underline.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #2663ea, stop:1 #27ae60); border-radius: 2px;")
        header.addWidget(underline, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(header)
        anim = QPropertyAnimation(underline, b"maximumWidth")
        anim.setDuration(1200)
        anim.setStartValue(80)
        anim.setEndValue(520)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._underline_anim = anim
        self._underline_anim.start()
        logo_path = project_root / 'UI' / 'images' / 'logo.png'
        if logo_path.exists():
            logo = QLabel('')
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pm = QPixmap(str(logo_path))
            try:
                logo.setPixmap(pm.scaledToHeight(56))
            except Exception:
                logo.setPixmap(pm)
            layout.addWidget(logo)
        
        # Status indicator removed theo yêu cầu
        
        context_layout = QHBoxLayout()
        lbl_ctx = QLabel("Ngữ cảnh:")
        context_layout.addWidget(lbl_ctx)
        self.context_selector = QComboBox()
        self.context_selector.addItems([
            "Hỏi chung về Credit Risk",
            "Giải thích dự báo vừa rồi",
            "So sánh các models",
            "Tư vấn chiến lược"
        ])
        self.context_selector.setMinimumWidth(240)
        context_layout.addWidget(self.context_selector)
        context_layout.addStretch()
        layout.addLayout(context_layout)
        
        chat_card = QFrame()
        chat_card.setObjectName('Card')
        chat_card_layout = QVBoxLayout(chat_card)
        chat_card_layout.setContentsMargins(16, 16, 16, 16)
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenLinks(False)
        self.chat_display.anchorClicked.connect(self.on_anchor_clicked)
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 11))
        self.chat_display.setStyleSheet("QTextBrowser { background-color: #eef6ff; border: 1px solid #dfe6ee; border-radius: 12px; padding: 12px; }")
        self.chat_display.setMinimumHeight(420)
        chat_card_layout.addWidget(self.chat_display)
        layout.addWidget(chat_card)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Nhập câu hỏi của bạn...")
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.textChanged.connect(self.update_send_state)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Gửi")
        self.send_button.setObjectName('Primary')
        self.send_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Quick actions (không label, canh phải)
        self.quick_layout = QHBoxLayout()
        self.quick_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.quick_layout.addStretch()
        layout.addLayout(self.quick_layout)
        self.context_selector.currentTextChanged.connect(self.update_quick_actions)
        self.update_quick_actions(self.context_selector.currentText())
        
        # Clear button
        clear_btn = QPushButton("Xóa lịch sử chat")
        clear_btn.setObjectName('Danger')
        clear_btn.clicked.connect(self.clear_chat)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        
        # Load chat history
        self.load_chat_history()
        
        # Disable if not available
        if not self.gemini_available:
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
        else:
            self.update_send_state()
    
    def send_message(self):
        """Gửi message tới Gemini"""
        message = self.input_field.text().strip()
        
        if not message:
            return
        
        if not self.gemini_available:
            QMessageBox.warning(
                self,
                "AI Không Khả Dụng",
                "Vui lòng cấu hình Gemini API key trong config/gemini_config.py"
            )
            return
        
        self.send_button.setEnabled(False)
        self.send_button.setText("Đang xử lý...")
        
        self.add_user_message(message)
        typing_id = self.show_typing_indicator()
        
        # Clear input
        self.input_field.clear()
        
        try:
            ctx_choice = self.context_selector.currentText()
            if ctx_choice.startswith("Hỏi chung"):
                context = None
            else:
                if self.user.is_admin():
                    context = self.get_admin_context()
                else:
                    context = self.get_user_context()

            worker = AIAssistantWidget.ChatWorker(
                self.gemini_service,
                message,
                context,
                self.context_selector.currentText()
            )
            self._current_worker = worker
            worker.finished_text.connect(lambda resp: self._on_worker_done(typing_id, resp))
            worker.error_text.connect(lambda err: self._on_worker_error(typing_id, err))
            worker.finished_text.connect(lambda _: (self._restore_input_state(), setattr(self, '_current_worker', None)))
            worker.error_text.connect(lambda _: (self._restore_input_state(), setattr(self, '_current_worker', None)))
            worker.start()
        except Exception as e:
            self._on_worker_error(typing_id, str(e))
            self._restore_input_state()

    def update_send_state(self):
        text = self.input_field.text().strip()
        enabled = bool(text) and self.gemini_available
        self.send_button.setEnabled(enabled)

    def _restore_input_state(self):
        self.send_button.setEnabled(True)
        self.send_button.setText("Gửi")
        self.input_field.setFocus()
    
    def quick_ask(self, question: str):
        """Gửi câu hỏi nhanh"""
        self.input_field.setText(question)
        # Hiển thị ngay câu hỏi bên phải và tạo typing
        self.add_user_message(question)
        typing_id = self.show_typing_indicator()
        # Gửi nền
        try:
            ctx_choice = self.context_selector.currentText()
            if ctx_choice.startswith("Hỏi chung"):
                context = None
            else:
                context = self.get_admin_context() if self.user.is_admin() else self.get_user_context()
            worker = AIAssistantWidget.ChatWorker(
                self.gemini_service,
                question,
                context,
                self.context_selector.currentText()
            )
            self._current_worker = worker
            worker.finished_text.connect(lambda resp: self._on_worker_done(typing_id, resp))
            worker.error_text.connect(lambda err: self._on_worker_error(typing_id, err))
            worker.finished_text.connect(lambda _: setattr(self, '_current_worker', None))
            worker.error_text.connect(lambda _: setattr(self, '_current_worker', None))
            worker.start()
        except Exception as e:
            self._on_worker_error(typing_id, str(e))
    
    def add_user_message(self, text: str):
        mid = f"u_{int(datetime.now().timestamp()*1000)}"
        self._chat_log.append({'id': mid, 'sender': '👤 Bạn', 'text': text, 'time': datetime.now().strftime('%H:%M'), 'type': 'user'})
        self._render_chat_html()

    def show_typing_indicator(self):
        mid = f"t_{int(datetime.now().timestamp()*1000)}"
        self._chat_log.append({'id': mid, 'sender': '🤖 AI', 'text': 'Đang tạo phản hồi...', 'time': datetime.now().strftime('%H:%M'), 'type': 'typing'})
        self._render_chat_html()
        self._start_typing_animation(mid)
        return mid

    def replace_typing_with_ai(self, typing_id: str, text: str, is_error: bool = False):
        for item in self._chat_log:
            if item.get('id') == typing_id:
                item['type'] = 'ai'
                item['text'] = text
                item['sender'] = '🤖 AI' if not is_error else '⚠️ Hệ thống'
                break
        self._render_chat_html()
        self._stop_typing_animation()

    def _on_worker_done(self, typing_id: str, response: str):
        self.replace_typing_with_ai(typing_id, response)
        self._last_ai_text = response

    def _on_worker_error(self, typing_id: str, error: str):
        self.replace_typing_with_ai(typing_id, f"❌ Lỗi: {error}", is_error=True)

    def _render_content_html(self, text: str, as_markdown: bool) -> str:
        if as_markdown:
            try:
                import markdown
                html = markdown.markdown(text, extensions=['fenced_code', 'tables'])
                return html
            except Exception:
                pass
        safe = text.replace('<', '&lt;').replace('>', '&gt;')
        return safe.replace(chr(10), '<br>')

    def copy_last_ai_response(self):
        if not self._last_ai_text:
            return
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._last_ai_text)
        self._chat_log.append({'id': f"sys_{int(datetime.now().timestamp()*1000)}", 'sender': '✅ Hệ thống', 'text': 'Đã sao chép phản hồi AI vào clipboard', 'time': datetime.now().strftime('%H:%M'), 'type': 'system'})
        self._render_chat_html()

    def export_chat(self):
        if not self._chat_log:
            return
        default_name = datetime.now().strftime('chat_%Y%m%d_%H%M%S.md')
        path, _ = QFileDialog.getSaveFileName(self, 'Xuất hội thoại', default_name, 'Markdown (*.md);;Text (*.txt)')
        if not path:
            return
        try:
            lines = []
            for item in self._chat_log:
                lines.append(f"### {item['sender']} ({item['time']})\n\n{item['text']}\n")
            content = '\n'.join(lines)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._chat_log.append({'id': f"sys_{int(datetime.now().timestamp()*1000)}", 'sender': '✅ Hệ thống', 'text': f'Đã xuất hội thoại ra file: {path}', 'time': datetime.now().strftime('%H:%M'), 'type': 'system'})
            self._render_chat_html()
        except Exception as e:
            self._chat_log.append({'id': f"sys_{int(datetime.now().timestamp()*1000)}", 'sender': '❌ Hệ thống', 'text': f'Lỗi khi xuất hội thoại: {e}', 'time': datetime.now().strftime('%H:%M'), 'type': 'system'})
            self._render_chat_html()

    def on_anchor_clicked(self, url: QUrl):
        action = url.toString()
        if action.startswith('copy:'):
            mid = action.split(':', 1)[1]
            for item in self._chat_log:
                if item.get('id') == mid and item.get('type') in ('ai', 'system'):
                    QGuiApplication.clipboard().setText(item.get('text',''))
                    break
        elif action.startswith('export:'):
            mid = action.split(':', 1)[1]
            for item in self._chat_log:
                if item.get('id') == mid:
                    default_name = datetime.now().strftime(f"reply_{mid}_%Y%m%d_%H%M%S.md")
                    path, _ = QFileDialog.getSaveFileName(self, 'Xuất phản hồi', default_name, 'Markdown (*.md);;Text (*.txt)')
                    if path:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(item.get('text',''))
                    break

    def _render_chat_html(self):
        parts = []
        for item in self._chat_log:
            sender = item.get('sender','')
            text = item.get('text','')
            ts = item.get('time','')
            is_ai = item.get('type') in ('ai','typing') and sender.startswith('🤖')
            align = 'right' if item.get('type') == 'user' else 'left'
            if item.get('type') == 'user':
                color = '#2663ea'
                bubble_bg = '#2663ea'
                text_color = '#ffffff'
                border = '#2663ea'
            elif item.get('type') == 'typing':
                color = '#27ae60'
                bubble_bg = '#ffffff'
                text_color = '#10151A'
                border = '#27ae60'
            elif item.get('type') == 'ai':
                color = '#27ae60'
                bubble_bg = '#ffffff'
                text_color = '#10151A'
                border = '#27ae60'
            else:
                color = '#95a5a6'
                bubble_bg = '#ffffff'
                text_color = '#10151A'
                border = '#95a5a6'
            content_html = self._render_content_html(text, is_ai)
            actions_html = ''
            if item.get('type') == 'ai':
                mid = item.get('id','')
                actions_html = f"<div style='margin-top:8px; font-size:13px; color:#7f8c8d;'>" \
                                f"<a href='copy:{mid}' style='text-decoration:none; color:#2663ea; font-weight:600;'>Sao chép</a> · " \
                                f"<a href='export:{mid}' style='text-decoration:none; color:#2663ea; font-weight:600;'>Xuất</a>" \
                                f"</div>"
            bubble_align_extra = 'display:block; margin-left:auto;' if item.get('type')=='user' else 'display:block; margin-right:auto;'
            html = (
                f"<div style='margin:8px 0 16px 0; text-align:{align};'>"
                f"<div style='color:{color}; font-size:12px; display:inline-block;'>"
                f"<b>{sender}</b> <span style='color:#7f8c8d'>{ts}</span></div>"
                f"<div style='max-width:80%; padding:12px; background-color:{bubble_bg}; "
                f"border:2px solid {border}; border-radius:14px; margin-top:6px; text-align:left; color:{text_color}; "
                f"{'font-weight:700;' if item.get('type')=='user' else ''}; {bubble_align_extra}'>"
                f"{content_html}{actions_html}</div></div>"
            )
            parts.append(html)
        html_all = ''.join(parts)
        self.chat_display.setHtml(html_all)
        try:
            self._persist_local_chat()
        except Exception:
            pass
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_quick_actions(self, ctx_text: str):
        # Clear existing buttons except label and stretch
        while self.quick_layout.count() > 1:
            item = self.quick_layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        # Suggestions per context
        if ctx_text.startswith("Hỏi chung"):
            items = [
                "Credit risk là gì?",
                "Top 3 yếu tố rủi ro",
                "Cách giảm rủi ro"
            ]
        elif ctx_text.startswith("Giải thích"):
            items = [
                "Giải thích dự báo vừa rồi",
                "Yếu tố ảnh hưởng",
                "Khuyến nghị hành động"
            ]
        elif ctx_text.startswith("So sánh"):
            items = [
                "So sánh XGBoost vs LightGBM",
                "Ưu nhược điểm từng model",
                "Khi nào dùng CatBoost"
            ]
        else:
            items = [
                "Chiến lược giảm rủi ro",
                "Thiết lập ngưỡng tín dụng",
                "Theo dõi cảnh báo"
            ]
        for t in items:
            btn = QPushButton(t)
            btn.setObjectName('Secondary')
            btn.clicked.connect(lambda _, q=t: self.quick_ask(q))
            self.quick_layout.insertWidget(self.quick_layout.count()-1, btn)

    def closeEvent(self, event):
        # Graceful stop typing animation
        self._stop_typing_animation()
        # Wait for worker to finish to ensure DB history is saved
        try:
            if self._current_worker and self._current_worker.isRunning():
                self._current_worker.wait(5000)
        except Exception:
            pass
        try:
            self._persist_local_chat()
        except Exception:
            pass
        super().closeEvent(event)

    def _persist_local_chat(self):
        from pathlib import Path as _P
        root = _P(__file__).resolve().parents[1] / 'outputs' / 'ai_chat'
        root.mkdir(parents=True, exist_ok=True)
        path = root / f'chat_{self.user.id}.json'
        import json as _json
        with open(path, 'w', encoding='utf-8') as f:
            _json.dump(self._chat_log, f, ensure_ascii=False, indent=2)

    def _load_local_chat(self):
        from pathlib import Path as _P
        path = _P(__file__).resolve().parents[1] / 'outputs' / 'ai_chat' / f'chat_{self.user.id}.json'
        if path.exists():
            import json as _json
            try:
                data = _json.loads(path.read_text(encoding='utf-8'))
                self._chat_log = data
                self._render_chat_html()
            except Exception:
                pass

    def _clear_local_chat(self):
        from pathlib import Path as _P
        path = _P(__file__).resolve().parents[1] / 'outputs' / 'ai_chat' / f'chat_{self.user.id}.json'
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass

    def _start_typing_animation(self, mid: str):
        self._typing_id = mid
        self._typing_dots = 0
        if self._typing_timer:
            self._typing_timer.stop()
        self._typing_timer = QTimer(self)
        self._typing_timer.setInterval(400)
        self._typing_timer.timeout.connect(self._update_typing_text)
        self._typing_timer.start()

    def _stop_typing_animation(self):
        if self._typing_timer:
            self._typing_timer.stop()
            self._typing_timer = None
            self._typing_id = None

    def _update_typing_text(self):
        if not self._typing_id:
            return
        self._typing_dots = (getattr(self, '_typing_dots', 0) + 1) % 4
        dots = '.' * self._typing_dots
        for item in self._chat_log:
            if item.get('id') == self._typing_id and item.get('type') == 'typing':
                item['text'] = f"Đang tạo phản hồi{dots}"
                break
        self._render_chat_html()
    
    def append_message(self, sender: str, message: str, color: str):
        ts = datetime.now().strftime('%H:%M')
        if sender.startswith('👤'):
            mtype = 'user'
        elif sender.startswith('🤖'):
            mtype = 'ai'
        else:
            mtype = 'system'
        self._chat_log.append({'id': f"m_{int(datetime.now().timestamp()*1000)}", 'sender': sender, 'text': message, 'time': ts, 'type': mtype})
        self._render_chat_html()
    
    def load_chat_history(self):
        """Load lịch sử chat từ database"""
        if not self.gemini_available or not self.gemini_service:
            return
        
        try:
            history = self.gemini_service.get_chat_history(limit=10)
            
            if history:
                for item in history:
                    self.append_message("👤 Bạn", item['user_message'], "#3498db")
                    self.append_message("🤖 AI", item['ai_response'], "#27ae60")
            else:
                self._load_local_chat()
        except:
            try:
                self._load_local_chat()
            except Exception:
                pass
    
    def clear_chat(self):
        """Xóa lịch sử chat"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa toàn bộ lịch sử chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            if self.gemini_service:
                self.gemini_service.clear_chat_history()
            try:
                self._clear_local_chat()
            except Exception:
                pass
    
    def get_user_context(self):
        """Get context chỉ từ predictions của user này (User role)"""
        try:
            recent_predictions = self.db.fetch_all("""
                SELECT p.*, c.customer_name, c.customer_id_card
                FROM predictions_log p
                LEFT JOIN customers c ON p.customer_id = c.id
                WHERE p.user_id = %s
                ORDER BY p.created_at DESC
                LIMIT 10
            """, (self.user.id,))
            
            return {
                'user_predictions': recent_predictions,
                'total_predictions': len(recent_predictions) if recent_predictions else 0,
                'role': 'User'
            }
        except Exception as e:
            print(f"⚠ Error getting user context: {e}")
            return {'role': 'User', 'error': str(e)}
    
    def get_admin_context(self):
        """Get context từ toàn bộ database (Admin role)"""
        try:
            # All recent predictions
            all_predictions = self.db.fetch_all("""
                SELECT p.*, c.customer_name, c.customer_id_card, u.username
                FROM predictions_log p
                LEFT JOIN customers c ON p.customer_id = c.id
                LEFT JOIN user u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 50
            """)
            
            # System stats
            stats = self.db.fetch_one("""
                SELECT 
                    COUNT(*) as total_predictions,
                    SUM(CASE WHEN predicted_label = 1 THEN 1 ELSE 0 END) as high_risk_count,
                    AVG(probability) as avg_probability
                FROM predictions_log
            """)
            
            return {
                'all_predictions': all_predictions,
                'system_stats': stats,
                'role': 'Admin'
            }
        except Exception as e:
            print(f"⚠ Error getting admin context: {e}")
            return {'role': 'Admin', 'error': str(e)}
