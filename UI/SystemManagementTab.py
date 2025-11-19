from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from pathlib import Path
import datetime

class SystemManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_paths()
        self.setup_ui()

    def _init_paths(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.eval_path = self.project_root / 'outputs' / 'evaluation' / 'evaluation_data.npz'
        # Integration helpers
        try:
            from .integration import get_db_connector, get_query_service
        except Exception:
            from integration import get_db_connector, get_query_service
        self._get_db_connector = get_db_connector
        self._get_query_service = get_query_service
        # Model management
        try:
            from services.model_management_service import ModelManagementService
            self._ModelManagementService = ModelManagementService
        except Exception:
            self._ModelManagementService = None

    def setup_ui(self):
        root = QVBoxLayout()
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); scroll.setWidget(content)
        layout = QVBoxLayout(content)

        # ========== Model Settings ==========
        section0 = QVBoxLayout()
        section0.addWidget(QLabel('Thiết lập mô hình'))
        row0 = QHBoxLayout()
        self.cmbModel = QComboBox(); self.cmbModel.addItems(['XGBoost','LightGBM','LogisticRegression'])
        row0.addWidget(QLabel('Model:'))
        row0.addWidget(self.cmbModel)
        row0.addStretch()
        section0.addLayout(row0)

        # Threshold editor
        row0b = QHBoxLayout()
        row0b.addWidget(QLabel('Ngưỡng rủi ro (threshold):'))
        self.spnThreshold = QDoubleSpinBox(); self.spnThreshold.setRange(0.0,1.0); self.spnThreshold.setSingleStep(0.01)
        self.spnThreshold.setDecimals(2)
        current_thr = self._load_threshold(self.cmbModel.currentText())
        self.spnThreshold.setValue(current_thr)
        row0b.addWidget(self.spnThreshold)
        btnApply = QPushButton('Áp dụng'); btnApply.clicked.connect(self.apply_settings)
        row0b.addWidget(btnApply)
        btnRecompute = QPushButton('Recompute metrics'); btnRecompute.clicked.connect(self.recompute_dashboard_metrics)
        row0b.addWidget(btnRecompute)
        # Active model controls
        if self._ModelManagementService:
            btnSetActive = QPushButton('Set Active Model'); btnSetActive.clicked.connect(self.set_active_model)
            row0b.addWidget(btnSetActive)
            self.lblActive = QLabel('')
            row0b.addWidget(self.lblActive)
        section0.addLayout(row0b)

        # Business Rules overlay
        row0c = QHBoxLayout()
        row0c.addWidget(QLabel('Overlay: α'))
        self.spnAlpha = QDoubleSpinBox(); self.spnAlpha.setRange(0.0, 3.0); self.spnAlpha.setSingleStep(0.05); self.spnAlpha.setDecimals(2)
        row0c.addWidget(self.spnAlpha)
        row0c.addWidget(QLabel('β'))
        self.spnBeta = QDoubleSpinBox(); self.spnBeta.setRange(0.0, 3.0); self.spnBeta.setSingleStep(0.05); self.spnBeta.setDecimals(2)
        row0c.addWidget(self.spnBeta)
        row0c.addWidget(QLabel('Feature'))
        self.cmbOverlayFeature = QComboBox(); self.cmbOverlayFeature.addItems(['NONE','AGE','LIMIT_BAL','PAY_0'])
        row0c.addWidget(self.cmbOverlayFeature)
        self.btnApplyOverlay = QPushButton('Áp dụng Overlay'); self.btnApplyOverlay.clicked.connect(self.apply_overlay)
        row0c.addWidget(self.btnApplyOverlay)
        btnResetOverlay = QPushButton('Reset Overlay'); btnResetOverlay.clicked.connect(self.reset_overlay)
        row0c.addWidget(btnResetOverlay)
        # Load current overlay
        a,b,f,en = self._load_overlay()
        self.spnAlpha.setValue(a); self.spnBeta.setValue(b);
        idx = self.cmbOverlayFeature.findText(f) if f else 0
        self.cmbOverlayFeature.setCurrentIndex(max(idx,0))
        section0.addLayout(row0c)
        layout.addLayout(section0)

        # Models table
        sectionModels = QVBoxLayout()
        sectionModels.addWidget(QLabel('Danh sách mô hình'))
        self.tblModels = QTableWidget(0, 9)
        self.tblModels.setHorizontalHeaderLabels(['Model','Type','Algo','AUC','Acc','F1','Active','Size(MB)','Threshold'])
        self.tblModels.setMinimumHeight(220)
        self.tblModels.setAlternatingRowColors(True)
        sectionModels.addWidget(self.tblModels)
        layout.addLayout(sectionModels)

        # Threshold Audit table
        sectionAudit = QVBoxLayout()
        sectionAudit.addWidget(QLabel('Threshold Audit'))
        self.tblAudit = QTableWidget(0, 4)
        self.tblAudit.setHorizontalHeaderLabels(['Thời điểm','Model','Giá trị','User'])
        self.tblAudit.setMinimumHeight(160)
        self.tblAudit.setAlternatingRowColors(True)
        btnAuditRefresh = QPushButton('Refresh Audit'); btnAuditRefresh.clicked.connect(self._load_threshold_audit)
        sectionAudit.addWidget(self.tblAudit)
        sectionAudit.addWidget(btnAuditRefresh)
        layout.addLayout(sectionAudit)

        section1 = QVBoxLayout()
        section1.addWidget(QLabel('Phát hiện dữ liệu bất thường'))
        row1 = QHBoxLayout()
        method = QComboBox()
        method.addItems(['Isolation Forest'])
        threshold = QSpinBox()
        threshold.setRange(0, 100)
        threshold.setValue(5)
        btn_scan = QPushButton('Scan Database')
        row1.addWidget(QLabel('Method:'))
        row1.addWidget(method)
        row1.addWidget(QLabel('Threshold:'))
        row1.addWidget(threshold)
        row1.addWidget(btn_scan)
        section1.addLayout(row1)
        self.table1 = QTableWidget(0, 5)
        self.table1.setHorizontalHeaderLabels(['☑', 'Cust ID', 'Score', 'Issue', 'Actions'])
        self.table1.setMinimumHeight(420)
        self.table1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        section1.addWidget(self.table1)
        self.table1.setAlternatingRowColors(True)
        row2 = QHBoxLayout()
        btnDelete = QPushButton('Delete Selected'); btnDelete.clicked.connect(self.delete_selected_outliers)
        btnExport = QPushButton('Export Outliers'); btnExport.clicked.connect(self.export_outliers)
        row2.addWidget(btnDelete)
        row2.addWidget(btnExport)
        section1.addLayout(row2)
        layout.addLayout(section1)
        section2 = QVBoxLayout()
        section2.addWidget(QLabel('Phân cụm khách hàng'))
        row3 = QHBoxLayout()
        algo = QComboBox()
        algo.addItems(['K-Means'])
        self.clusters = QSpinBox()
        self.clusters.setRange(2, 10)
        self.clusters.setValue(4)
        row3.addWidget(QLabel('Algorithm:'))
        row3.addWidget(algo)
        row3.addWidget(QLabel('Clusters:'))
        row3.addWidget(self.clusters)
        btn_run = QPushButton('Run')
        btn_scan.clicked.connect(lambda: self.run_outlier_scan(threshold.value()))
        btn_run.clicked.connect(self.run_kmeans)
        row3.addWidget(btn_run)
        section2.addLayout(row3)
        self.cluster_canvas = FigureCanvas(Figure(figsize=(5,3)))
        self.cluster_canvas.setMinimumHeight(320)
        layout.addWidget(self.cluster_canvas)
        layout.addLayout(section2)
        root.addWidget(scroll)
        self.setLayout(root)

        # Events
        self.cmbModel.currentTextChanged.connect(self.on_model_changed)
        self._load_models_table()
        self._load_threshold_audit()

    def load_dataset(self) -> pd.DataFrame:
        try:
            db = self._get_db_connector()
            # Select subset of numeric columns used for detection
            cols = ['ID','LIMIT_BAL','AGE'] + [f'PAY_{i}' for i in [0,2,3,4,5,6]] + \
                   [f'BILL_AMT{i}' for i in range(1,13)] + [f'PAY_AMT{i}' for i in range(1,13)]
            sel = ','.join([c for c in cols if c != 'ID'])
            # Some schemas may not have sequential columns fully; fetch what exists
            rows = db.fetch_all(f"SELECT id, {sel} FROM customers")
            db.close()
            if not rows:
                return pd.DataFrame()
            df = pd.DataFrame(rows, columns=['ID'] + [c for c in cols if c != 'ID'])
            return df
        except Exception as e:
            print(f"✗ Load dataset from DB failed: {e}")
            return pd.DataFrame()

    # ======== Model Settings Helpers ========
    def _load_threshold(self, model_name: str) -> float:
        try:
            import numpy as np
            if not self.eval_path.exists():
                return 0.6
            data = np.load(self.eval_path, allow_pickle=True)
            best = data.get('best_thresholds', None)
            if best is None:
                return 0.6
            thr_dict = best.item() if hasattr(best, 'item') else best
            val = thr_dict.get(model_name, 0.6)
            return float(val)
        except Exception:
            return 0.6

    def _save_threshold(self, model_name: str, value: float) -> bool:
        try:
            import numpy as np
            self.eval_path.parent.mkdir(parents=True, exist_ok=True)
            store = {}
            if self.eval_path.exists():
                data = np.load(self.eval_path, allow_pickle=True)
                for k in data.files:
                    store[k] = data[k]
            # Load previous thresholds robustly
            prev_best = store.get('best_thresholds', None)
            thr_dict = {}
            try:
                if prev_best is not None:
                    if hasattr(prev_best, 'item') and prev_best.ndim == 0:
                        obj = prev_best.item()
                        if isinstance(obj, dict):
                            thr_dict = dict(obj)
                    elif isinstance(prev_best, dict):
                        thr_dict = dict(prev_best)
            except Exception:
                thr_dict = {}
            thr_dict[model_name] = float(value)
            store['best_thresholds'] = np.array(thr_dict, dtype=object)
            # Audit robustly
            prev_audit = store.get('threshold_audit', None)
            audit_list = []
            try:
                if prev_audit is not None:
                    if hasattr(prev_audit, 'item') and getattr(prev_audit, 'ndim', 0) == 0:
                        obj = prev_audit.item()
                        if isinstance(obj, list):
                            audit_list = list(obj)
                    elif isinstance(prev_audit, list):
                        audit_list = list(prev_audit)
            except Exception:
                audit_list = []
            audit_list.append({'model': model_name, 'value': float(value), 'user': 'admin', 'ts': datetime.datetime.now().isoformat()})
            store['threshold_audit'] = np.array(audit_list, dtype=object)
            np.savez(self.eval_path, **store)
            return True
        except Exception as e:
            print(f"✗ Save threshold failed: {e}")
            return False

    def on_model_changed(self, name: str):
        self.spnThreshold.setValue(self._load_threshold(name))

    def apply_settings(self):
        name = self.cmbModel.currentText()
        val = float(self.spnThreshold.value())
        ok = self._save_threshold(name, val)
        if ok:
            QMessageBox.information(self, 'Thành công', f'Đã cập nhật threshold cho {name}: {val:.2f}')
            self._load_models_table()
            self._load_threshold_audit()
        else:
            QMessageBox.critical(self, 'Lỗi', 'Không thể lưu thiết lập. Vui lòng thử lại.')

    def apply_overlay(self):
        a = float(self.spnAlpha.value())
        b = float(self.spnBeta.value())
        f = self.cmbOverlayFeature.currentText()
        ok = self._save_overlay(a,b,f)
        if ok:
            QMessageBox.information(self, 'Thành công', f'Đã cập nhật overlay: α={a:.2f}, β={b:.2f}, feature={f}')
        else:
            QMessageBox.critical(self, 'Lỗi', 'Không thể lưu overlay.')

    def _load_threshold_audit(self):
        try:
            import numpy as np
            self.tblAudit.setRowCount(0)
            if not self.eval_path.exists():
                return
            data = np.load(self.eval_path, allow_pickle=True)
            audit = data.get('threshold_audit', None)
            items = []
            if audit is not None:
                # np.ndarray cases: 0-D object or 1-D list-like
                if isinstance(audit, np.ndarray):
                    if getattr(audit, 'ndim', 0) == 0:
                        obj = audit.item()
                        if isinstance(obj, list):
                            items = obj
                    else:
                        # Convert to list of dicts if available
                        lst = audit.tolist()
                        if isinstance(lst, list):
                            items = [x for x in lst if isinstance(x, dict)]
                elif isinstance(audit, list):
                    items = [x for x in audit if isinstance(x, dict)]
            self.tblAudit.setRowCount(len(items))
            for i, r in enumerate(items[::-1]):
                self.tblAudit.setItem(i,0, QTableWidgetItem(str(r.get('ts',''))))
                self.tblAudit.setItem(i,1, QTableWidgetItem(str(r.get('model',''))))
                self.tblAudit.setItem(i,2, QTableWidgetItem(f"{float(r.get('value',0.0)):.2f}"))
                self.tblAudit.setItem(i,3, QTableWidgetItem(str(r.get('user',''))))
        except Exception as e:
            print(f"✗ Load threshold audit failed: {e}")

    def recompute_dashboard_metrics(self):
        try:
            import numpy as np
            self.eval_path.parent.mkdir(parents=True, exist_ok=True)
            store = {}
            if self.eval_path.exists():
                data = np.load(self.eval_path, allow_pickle=True)
                for k in data.files:
                    store[k] = data[k]
            thr = float(self._load_threshold(self.cmbModel.currentText()))
            store['dashboard_threshold'] = np.array({'value': thr, 'ts': datetime.datetime.now().isoformat(), 'user': 'admin'}, dtype=object)
            np.savez(self.eval_path, **store)
            # Trigger dashboard refresh if available
            try:
                mw = self.window()
                if hasattr(mw, 'dashboard_tab'):
                    mw.dashboard_tab.refresh_dashboard()
            except Exception:
                pass
            QMessageBox.information(self, 'Thành công', f'Đã tái tính theo threshold hiện tại: {thr:.2f}')
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể tái tính: {e}')

    def run_outlier_scan(self, threshold_percent: int):
        df = self.load_dataset()
        if df.empty:
            return
        try:
            from sklearn.ensemble import IsolationForest
        except Exception:
            return
        cols = [c for c in df.columns if c.startswith('BILL_AMT') or c.startswith('PAY_AMT')]
        X = df[cols].fillna(0).values
        iso = IsolationForest(contamination=max(min(threshold_percent/100.0,0.4),0.01), random_state=42)
        scores = -iso.fit_predict(X)
        probs = iso.decision_function(X)
        idx = probs.argsort()[-150:][::-1]
        self.table1.setRowCount(len(idx))
        self._outliers = []
        for i, j in enumerate(idx):
            cust_id = int(df.iloc[j]['ID']) if 'ID' in df.columns else j
            score = float(probs[j])
            self.table1.setItem(i, 0, QTableWidgetItem('☑'))
            self.table1.setItem(i, 1, QTableWidgetItem(str(cust_id)))
            self.table1.setItem(i, 2, QTableWidgetItem(f"{score:.2f}"))
            self.table1.setItem(i, 3, QTableWidgetItem('Outlier'))
            self.table1.setItem(i, 4, QTableWidgetItem('Edit/Delete'))
            self._outliers.append({'customer_id': cust_id, 'score': score})

    def run_kmeans(self):
        df = self.load_dataset()
        if df.empty:
            return
        try:
            from sklearn.cluster import KMeans
        except Exception:
            return
        cols = ['LIMIT_BAL','AGE'] + [c for c in df.columns if c.startswith('PAY_')][:4]
        X = df[cols].fillna(0).values
        k = int(self.clusters.value())
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(X)
        labels = km.labels_
        counts = pd.Series(labels).value_counts().sort_index()
        ax = self.cluster_canvas.figure.subplots()
        ax.clear()
        ax.bar(counts.index.astype(str), counts.values, color='#9b59b6')
        ax.set_title('Phân bổ khách hàng theo cụm')
        ax.set_xlabel('Cụm')
        ax.set_ylabel('Số lượng')
        self.cluster_canvas.draw()

    def export_outliers(self):
        try:
            if not getattr(self, '_outliers', None):
                QMessageBox.information(self, 'Thông báo', 'Chưa có danh sách outliers. Vui lòng Scan trước.')
                return
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            out_dir = self.project_root / 'outputs' / 'evaluation'
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / f'outliers_{ts}.csv'
            pd.DataFrame(self._outliers).to_csv(path, index=False)
            QMessageBox.information(self, 'Thành công', f'Đã export: {path}')
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể export: {e}')

    def delete_selected_outliers(self):
        try:
            if self.table1.rowCount() == 0:
                return
            db = self._get_db_connector()
            count = 0
            for i in range(self.table1.rowCount()):
                cust_id_item = self.table1.item(i,1)
                score_item = self.table1.item(i,2)
                if not cust_id_item:
                    continue
                cust_id = int(float(cust_id_item.text()))
                score = float(score_item.text()) if score_item else 0.0
                notes = f'Outlier score={score:.2f}. Marked by System tab.'
                db.execute_query(
                    """
                    INSERT INTO data_quality_log (record_id, record_type, issue_type, severity, detection_method, action_taken, action_at, action_by, notes)
                    VALUES (%s, 'Customer', 'Outlier', 'High', 'IsolationForest', 'Deleted', NOW(), %s, %s)
                    """,
                    (cust_id, 'admin', notes)
                )
                count += 1
            db.close()
            QMessageBox.information(self, 'Thành công', f'Đã ghi log xóa {count} outliers (soft-delete).')
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể xóa: {e}')

    def set_active_model(self):
        try:
            if not self._ModelManagementService:
                QMessageBox.critical(self, 'Lỗi', 'ModelManagementService không khả dụng')
                return
            db = self._get_db_connector()
            svc = self._ModelManagementService(db)
            name = self.cmbModel.currentText()
            ok = svc.set_active_model(name, 'admin')
            db.close()
            if ok:
                self.lblActive.setText(f'Active: {name}')
                self._load_models_table()
                QMessageBox.information(self, 'Thành công', f'Đã set active model: {name}')
            else:
                QMessageBox.critical(self, 'Lỗi', 'Không thể set active model')
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể set active: {e}')
    def _load_overlay(self):
        try:
            import numpy as np
            if not self.eval_path.exists():
                return (1.0,0.0,'NONE',False)
            data = np.load(self.eval_path, allow_pickle=True)
            cfg = data.get('overlay_config', None)
            if cfg is None:
                return (1.0,0.0,'NONE',False)
            d = cfg.item() if hasattr(cfg, 'item') else cfg
            return (float(d.get('alpha',1.0)), float(d.get('beta',0.0)), str(d.get('feature','NONE')), bool(d.get('enabled',True)))
        except Exception:
            return (1.0,0.0,'NONE',False)

    def _save_overlay(self, alpha: float, beta: float, feature: str) -> bool:
        try:
            import numpy as np
            store = {}
            if self.eval_path.exists():
                data = np.load(self.eval_path, allow_pickle=True)
                for k in data.files:
                    store[k] = data[k]
            store['overlay_config'] = np.array({'alpha': float(alpha), 'beta': float(beta), 'feature': feature, 'enabled': True}, dtype=object)
            np.savez(self.eval_path, **store)
            return True
        except Exception as e:
            print(f"✗ Save overlay failed: {e}")
            return False

    def reset_overlay(self):
        try:
            import numpy as np
            store = {}
            if self.eval_path.exists():
                data = np.load(self.eval_path, allow_pickle=True)
                for k in data.files:
                    store[k] = data[k]
            store['overlay_config'] = np.array({'alpha': 1.0, 'beta': 0.0, 'feature': 'NONE', 'enabled': False}, dtype=object)
            np.savez(self.eval_path, **store)
            self.spnAlpha.setValue(1.0)
            self.spnBeta.setValue(0.0)
            self.cmbOverlayFeature.setCurrentIndex(self.cmbOverlayFeature.findText('NONE'))
            QMessageBox.information(self, 'Thành công', 'Đã reset overlay về mặc định.')
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể reset overlay: {e}')

    def _load_models_table(self):
        try:
            if not self._ModelManagementService:
                return
            db = self._get_db_connector()
            svc = self._ModelManagementService(db)
            models = svc.get_all_models()
            active = svc.get_active_model()
            # Load thresholds mapping
            thr_map = {}
            try:
                import numpy as np
                if self.eval_path.exists():
                    data = np.load(self.eval_path, allow_pickle=True)
                    best = data.get('best_thresholds', None)
                    if best is not None:
                        d = best.item() if hasattr(best, 'item') else best
                        if hasattr(d, 'items'):
                            thr_map = {str(k): float(v) for k, v in d.items()}
            except Exception:
                thr_map = {}

            self.tblModels.setRowCount(len(models))
            for i, m in enumerate(models):
                self.tblModels.setItem(i,0, QTableWidgetItem(str(m.get('model_name',''))))
                self.tblModels.setItem(i,1, QTableWidgetItem(str(m.get('model_type',''))))
                self.tblModels.setItem(i,2, QTableWidgetItem(str(m.get('algorithm',''))))
                self.tblModels.setItem(i,3, QTableWidgetItem(f"{float(m.get('auc_score') or 0):.4f}"))
                self.tblModels.setItem(i,4, QTableWidgetItem(f"{float(m.get('accuracy') or 0):.4f}"))
                self.tblModels.setItem(i,5, QTableWidgetItem(f"{float(m.get('f1_score') or 0):.4f}"))
                self.tblModels.setItem(i,6, QTableWidgetItem('✓' if bool(m.get('is_active')) else ''))
                self.tblModels.setItem(i,7, QTableWidgetItem(f"{float(m.get('model_size_mb') or 0):.2f}"))
                cur_thr = thr_map.get(str(m.get('model_name','')), None)
                self.tblModels.setItem(i,8, QTableWidgetItem(f"{float(cur_thr):.2f}" if cur_thr is not None else '—'))
            if active:
                self.lblActive.setText(f"Active: {active.get('model_name','')}")
            db.close()
        except Exception as e:
            print(f"✗ Load models failed: {e}")
