from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QListWidget, QListWidgetItem, QPushButton, QSlider, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt

class ModelLabPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QHBoxLayout(self)
        left = QFrame(); left.setObjectName('Card'); ll = QVBoxLayout(left)
        ll.addWidget(QLabel('Model List'))
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
        cl.addWidget(QLabel('Model Insights'))
        cl.addWidget(QLabel('AUC 0.88  •  Acc 0.82  •  Recall Bad 0.71  •  Precision 0.64  •  F1 0.67  •  Inference 12ms'))
        tabs = QHBoxLayout(); tabs.addWidget(QLabel('ROC Curve')); tabs.addWidget(QLabel('PR Curve')); tabs.addWidget(QLabel('Feature Importance'))
        cl.addLayout(tabs)
        heat = QFrame(); heat.setObjectName('Card'); hl = QVBoxLayout(heat); hl.addWidget(QLabel('Confusion Matrix 2x2'))
        cl.addWidget(heat)
        right = QFrame(); right.setObjectName('Card'); rl = QVBoxLayout(right)
        rl.addWidget(QLabel('Editing & Threshold'))
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
        self.btnTrain = QPushButton('Train Model'); self.btnSaveVer = QPushButton('Save as Version'); self.btnDelete = QPushButton('Delete Model')
        btns.addWidget(self.btnTrain); btns.addWidget(self.btnSaveVer); btns.addWidget(self.btnDelete)
        rl.addLayout(btns)
        rl.addWidget(QLabel('Threshold θ'))
        self.th = QSlider(Qt.Orientation.Horizontal); self.th.setRange(0,100); self.th.setValue(50)
        rl.addWidget(self.th)
        self.policy = QLabel('PD < 0.30 → APPROVE • 0.30–0.50 → REVIEW • PD > 0.50 → REJECT')
        rl.addWidget(self.policy)
        self.btnOpt = QPushButton('Recompute Optimal Threshold'); self.btnApply = QPushButton('Apply Threshold')
        op = QHBoxLayout(); op.addWidget(self.btnOpt); op.addWidget(self.btnApply); rl.addLayout(op)
        root.addWidget(left,1); root.addWidget(center,2); root.addWidget(right,1)

