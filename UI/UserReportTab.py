from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from .user_model import User
except Exception:
    from user_model import User
try:
    from .integration import get_db_connector, get_query_service
except Exception:
    from integration import get_db_connector, get_query_service
import json

class UserReportTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.view_mode = 'own_data_only' if self.user.is_user() else 'all'
        self.setup_ui()
    
    def showEvent(self, event):
        """Override showEvent để auto-refresh khi tab được hiển thị"""
        super().showEvent(event)
        print("\n📊 [UserReportTab] Tab được hiển thị, đang refresh data...")
        self.load_recent()  # Auto refresh khi chuyển vào tab

    def setup_ui(self):
        root = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        content = QWidget(); layout = QVBoxLayout(content); layout.setContentsMargins(16,16,16,16); layout.setSpacing(16)
        
        # Thêm thông báo hướng dẫn nếu chưa có dữ liệu
        self.empty_message = QLabel()
        self.empty_message.setText(
            "📊 <b>Chưa có dữ liệu báo cáo</b><br><br>"
            "Để xem báo cáo, bạn cần:<br>"
            "1. Vào tab <b>Dự Báo</b><br>"
            "2. Nhập thông tin khách hàng<br>"
            "3. Tích ✅ <b>\"Lưu vào lịch sử dự báo\"</b><br>"
            "4. Nhấn <b>Dự Báo Rủi Ro</b><br><br>"
            "Sau đó quay lại đây để xem báo cáo!"
        )
        self.empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_message.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 40px;
                color: #6c757d;
                font-size: 14px;
            }
        """)
        self.empty_message.setVisible(False)  # Ẩn ban đầu
        layout.addWidget(self.empty_message)
        
        filters = QHBoxLayout()
        self.cmb_time = QComboBox()
        self.cmb_time.addItems(['Hôm nay', 'Tuần này', 'Tháng này'])
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(['Tất cả', 'Nguy cơ cao', 'Nguy cơ thấp'])
        filters.addWidget(QLabel('Thời gian:'))
        filters.addWidget(self.cmb_time)
        filters.addWidget(QLabel('Trạng thái:'))
        filters.addWidget(self.cmb_status)
        self.btn_export = QPushButton('Export Excel')
        self.btn_export.clicked.connect(self.export_to_excel)
        filters.addStretch()
        filters.addWidget(self.btn_export)
        layout.addLayout(filters)
        stats = QHBoxLayout()
        self.lbl_total = QLabel('Tổng dự báo: 0')
        self.lbl_high = QLabel('Nguy cơ cao: 0')
        self.lbl_low = QLabel('Nguy cơ thấp: 0')
        self.lbl_avg = QLabel('Trung bình: 0%')
        stats.addWidget(self.lbl_total)
        stats.addWidget(self.lbl_high)
        stats.addWidget(self.lbl_low)
        stats.addWidget(self.lbl_avg)
        layout.addLayout(stats)
        self.table = QTableWidget(5, 6)
        self.table.setHorizontalHeaderLabels(['STT', 'Khách hàng', 'Ngày', 'Kết quả', 'Xác suất', 'Thao tác'])
        self.load_recent()
        layout.addWidget(self.table)
        self.info = QLabel()
        self.info.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.info.setText('Chế độ: dữ liệu của tôi' if self.view_mode == 'own_data_only' else 'Chế độ: tất cả')
        layout.addWidget(self.info)
        scroll.setWidget(content)
        root.addWidget(scroll)

    def load_recent(self):
        try:
            print("\n🔄 [UserReportTab] Đang load dữ liệu báo cáo...")
            db = get_db_connector()
            qs = get_query_service(db)
            uid = self.user.id if self.view_mode == 'own_data_only' else None
            print(f"   User ID: {uid}, View mode: {self.view_mode}")
            
            rows = qs.get_predictions_join_customers('Hôm nay', 'Tất cả', limit=20, user_id=uid)
            print(f"   Query 1 returned {len(rows) if rows else 0} rows")
            
            if not rows:
                print("   Thử query dự phòng...")
                rows = qs.get_recent_predictions_join_customers('today', limit=20)
                if uid is not None:
                    rows = [r for r in rows if int(r.get('user_id') or 0) == uid]
                print(f"   Query 2 returned {len(rows)} rows")
            
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                self.table.setItem(i, 1, QTableWidgetItem(str(r.get('customer_name') or r.get('customer_id') or '-')))
                self.table.setItem(i, 2, QTableWidgetItem(str(r.get('created_at'))))
                self.table.setItem(i, 3, QTableWidgetItem('Nguy cơ cao' if int(r.get('predicted_label') or r.get('label') or 0)==1 else 'Nguy cơ thấp'))
                self.table.setItem(i, 4, QTableWidgetItem(f"{float(r.get('probability') or 0.0):.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem('Xem'))
            
            if self.table.rowCount() == 0:
                print("   ⚠️  Không có dữ liệu, hiển thị thông báo hướng dẫn")
                self.table.setVisible(False)
                self.empty_message.setVisible(True)
                # Update stats to 0
                self.lbl_total.setText('Tổng dự báo: 0')
                self.lbl_high.setText('Nguy cơ cao: 0')
                self.lbl_low.setText('Nguy cơ thấp: 0')
                self.lbl_avg.setText('Trung bình: 0%')
            else:
                print(f"   ✓ Đã load {self.table.rowCount()} dòng vào bảng")
                self.table.setVisible(True)
                self.empty_message.setVisible(False)
                # Calculate stats
                high_count = sum(1 for i in range(len(rows)) if int(rows[i].get('predicted_label') or rows[i].get('label') or 0) == 1)
                low_count = len(rows) - high_count
                avg_prob = sum(float(r.get('probability') or 0.0) for r in rows) / len(rows) if rows else 0
                self.lbl_total.setText(f'Tổng dự báo: {len(rows)}')
                self.lbl_high.setText(f'Nguy cơ cao: {high_count}')
                self.lbl_low.setText(f'Nguy cơ thấp: {low_count}')
                self.lbl_avg.setText(f'Trung bình: {avg_prob:.0%}')
            
            db.close()
            print("✓ [UserReportTab] Load dữ liệu thành công\n")
        except Exception as e:
            print(f"✗ [UserReportTab] Lỗi khi load dữ liệu: {e}")
            import traceback
            traceback.print_exc()
            try:
                db.close()
            except Exception:
                pass
    
    def export_to_excel(self):
        """Export dữ liệu báo cáo ra file Excel"""
        try:
            # Check if table has data
            if self.table.rowCount() == 0:
                QMessageBox.warning(self, "Không có dữ liệu", "Chưa có dữ liệu để export!")
                return
            
            # Get save file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"BaoCao_RuiRo_{timestamp}.xlsx"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Lưu file Excel",
                default_filename,
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            print(f"\n📤 [UserReportTab] Đang export dữ liệu ra {file_path}...")
            
            # Collect data from table
            data = []
            headers = []
            for col in range(self.table.columnCount()):
                headers.append(self.table.horizontalHeaderItem(col).text())
            
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else '')
                data.append(row_data)
            
            # Create DataFrame and export to Excel
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(file_path, index=False, sheet_name='Báo Cáo')
            
            print(f"✓ Đã export {len(data)} dòng ra file Excel")
            
            QMessageBox.information(
                self,
                "Export thành công",
                f"Đã xuất {len(data)} dòng dữ liệu ra file:\n{file_path}"
            )
            
        except Exception as e:
            print(f"✗ [UserReportTab] Lỗi khi export: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Lỗi Export",
                f"Không thể export dữ liệu:\n{str(e)}"
            )
