from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QListWidget, QListWidgetItem, QPushButton, QSlider, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt

class ModelLabPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QHBoxLayout(self)
        left = QFrame(); left.setObjectName('Card'); ll = QVBoxLayout(left)
        ll.addWidget(QLabel('Danh sách mô hình'))
        self.list = QListWidget()
        for name, group, active in [
            ('XGBoost_v3','CORE',True),('LightGBM_v2','CORE',False),('Logistic_v1','CORE',False),
            ('CatBoost_v1','ADV',False),('RandomForest_v1','ADV',False),('NeuralNet_v1','ADV',False),('Voting Ensemble','ADV',False),('Stacking Ensemble','ADV',False)
        ]:
            item = QListWidgetItem(('🟢 ' if active else '')+name)
            item.setData(Qt.ItemDataRole.UserRole, {'group':group,'active':active})
            self.list.addItem(item)
        ll.addWidget(self.list)
        center = QFrame(); center.setObjectName('Card'); cl = QVBoxLayout(center)
        cl.addWidget(QLabel('Thông tin mô hình'))
        cl.addWidget(QLabel('AUC 0.88  •  Acc 0.82  •  Recall Bad 0.71  •  Precision 0.64  •  F1 0.67  •  Inference 12ms'))
        tabs = QHBoxLayout(); tabs.addWidget(QLabel('Đường cong ROC')); tabs.addWidget(QLabel('Đường cong PR')); tabs.addWidget(QLabel('Tầm quan trọng đặc trưng'))
        cl.addLayout(tabs)
        heat = QFrame(); heat.setObjectName('Card'); hl = QVBoxLayout(heat); hl.addWidget(QLabel('Ma trận nhầm lẫn 2x2'))
        cl.addWidget(heat)
        right = QFrame(); right.setObjectName('Card'); rl = QVBoxLayout(right)
        rl.addWidget(QLabel('Chỉnh sửa & Ngưỡng'))
        self.lr = QDoubleSpinBox(); self.lr.setRange(0.0001, 1.0); self.lr.setValue(0.05)
        self.depth = QSpinBox(); self.depth.setRange(1, 16); self.depth.setValue(6)
        self.est = QSpinBox(); self.est.setRange(10, 5000); self.est.setValue(1000)
        self.subs = QDoubleSpinBox(); self.subs.setRange(0.1,1.0); self.subs.setSingleStep(0.05); self.subs.setValue(0.8)
        self.cols = QDoubleSpinBox(); self.cols.setRange(0.1,1.0); self.cols.setSingleStep(0.05); self.cols.setValue(0.8)
        rl.addWidget(QLabel('learning_rate')); rl.addWidget(self.lr)
        rl.addWidget(QLabel('depth')); rl.addWidget(self.depth)
        rl.addWidget(QLabel('estimators')); rl.addWidget(self.est)
        rl.addWidget(QLabel('subsample')); rl.addWidget(self.subs)
        rl.addWidget(QLabel('colsample_bytree')); rl.addWidget(self.cols)
        btns = QHBoxLayout();
        self.btnTrain = QPushButton('Huấn luyện mô hình'); self.btnSaveVer = QPushButton('Lưu thành phiên bản'); self.btnDelete = QPushButton('Xóa mô hình')
        btns.addWidget(self.btnTrain); btns.addWidget(self.btnSaveVer); btns.addWidget(self.btnDelete)
        rl.addLayout(btns)
        rl.addWidget(QLabel('Ngưỡng θ'))
        self.th = QSlider(Qt.Orientation.Horizontal); self.th.setRange(0,100); self.th.setValue(50)
        rl.addWidget(self.th)
        self.policy = QLabel('PD < 0,30 → PHÊ DUYỆT • 0,30–0,50 → XEM XÉT • PD > 0,50 → TỪ CHỐI')
        rl.addWidget(self.policy)
        self.btnOpt = QPushButton('Tính lại ngưỡng tối ưu'); self.btnApply = QPushButton('Áp dụng ngưỡng')
        op = QHBoxLayout(); op.addWidget(self.btnOpt); op.addWidget(self.btnApply); rl.addLayout(op)
        root.addWidget(left,1); root.addWidget(center,2); root.addWidget(right,1)

