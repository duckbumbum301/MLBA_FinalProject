from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QSizePolicy, QHeaderView
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
        self.support_path = self.project_root / 'outputs' / 'system' / 'forgot_requests.json'
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
        lblTitleModel = QLabel('Thiết lập mô hình'); lblTitleModel.setObjectName('SectionTitle'); section0.addWidget(lblTitleModel)
        row0 = QHBoxLayout()
        self.cmbModel = QComboBox(); self.cmbModel.addItems(['XGBoost','LightGBM','LogisticRegression'])  # Only 3 trained models exist
        lblModel = QLabel('Model:'); lblModel.setStyleSheet('font-weight:600')
        row0.addWidget(lblModel)
        row0.addWidget(self.cmbModel)
        row0.addStretch()
        section0.addLayout(row0)

        # Threshold editor
        row0b = QHBoxLayout()
        lblThr = QLabel('Ngưỡng rủi ro (threshold):'); lblThr.setStyleSheet('font-weight:600')
        row0b.addWidget(lblThr)
        self.spnThreshold = QDoubleSpinBox(); self.spnThreshold.setRange(0.0,1.0); self.spnThreshold.setSingleStep(0.01)
        self.spnThreshold.setDecimals(2)
        current_thr = self._load_threshold(self.cmbModel.currentText())
        self.spnThreshold.setValue(current_thr)
        row0b.addWidget(self.spnThreshold)
        btnApply = QPushButton('Áp dụng'); btnApply.setObjectName('Primary'); btnApply.clicked.connect(self.apply_settings)
        row0b.addWidget(btnApply)
        btnRecompute = QPushButton('Recompute metrics'); btnRecompute.setObjectName('Primary'); btnRecompute.clicked.connect(self.recompute_dashboard_metrics)
        row0b.addWidget(btnRecompute)
        # Active model controls
        if self._ModelManagementService:
            btnSetActive = QPushButton('Set Active Model'); btnSetActive.setObjectName('Secondary'); btnSetActive.clicked.connect(self.set_active_model)
            row0b.addWidget(btnSetActive)
            self.lblActive = QLabel('')
            row0b.addWidget(self.lblActive)
        section0.addLayout(row0b)

        # Business Rules overlay
        row0c = QHBoxLayout()
        lblAlpha = QLabel('Overlay: α'); lblAlpha.setStyleSheet('font-weight:600')
        row0c.addWidget(lblAlpha)
        self.spnAlpha = QDoubleSpinBox(); self.spnAlpha.setRange(0.0, 3.0); self.spnAlpha.setSingleStep(0.05); self.spnAlpha.setDecimals(2)
        row0c.addWidget(self.spnAlpha)
        lblBeta = QLabel('β'); lblBeta.setStyleSheet('font-weight:600')
        row0c.addWidget(lblBeta)
        self.spnBeta = QDoubleSpinBox(); self.spnBeta.setRange(0.0, 3.0); self.spnBeta.setSingleStep(0.05); self.spnBeta.setDecimals(2)
        row0c.addWidget(self.spnBeta)
        lblFeat = QLabel('Feature'); lblFeat.setStyleSheet('font-weight:600')
        row0c.addWidget(lblFeat)
        self.cmbOverlayFeature = QComboBox(); self.cmbOverlayFeature.addItems(['NONE','AGE','LIMIT_BAL','PAY_0'])
        row0c.addWidget(self.cmbOverlayFeature)
        self.btnApplyOverlay = QPushButton('Áp dụng Overlay'); self.btnApplyOverlay.setObjectName('Primary'); self.btnApplyOverlay.clicked.connect(self.apply_overlay)
        row0c.addWidget(self.btnApplyOverlay)
        btnResetOverlay = QPushButton('Reset Overlay'); btnResetOverlay.setObjectName('Secondary'); btnResetOverlay.clicked.connect(self.reset_overlay)
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
        lblModels = QLabel('Danh sách mô hình'); lblModels.setObjectName('SectionTitle'); sectionModels.addWidget(lblModels)
        self.tblModels = QTableWidget(0, 9)
        self.tblModels.setHorizontalHeaderLabels(['Model','Type','Algo','AUC','Acc','F1','Active','Size(MB)','Threshold'])
        self.tblModels.setMinimumHeight(220)
        self.tblModels.setAlternatingRowColors(True)
        try:
            self.tblModels.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        sectionModels.addWidget(self.tblModels)
        # Add compare models button
        btnCompareModels = QPushButton('So sánh 8 mô hình'); btnCompareModels.setObjectName('Secondary')
        btnCompareModels.clicked.connect(self.show_model_comparison)
        sectionModels.addWidget(btnCompareModels)
        layout.addLayout(sectionModels)

        # Threshold Audit table
        sectionAudit = QVBoxLayout()
        lblAudit = QLabel('Threshold Audit'); lblAudit.setObjectName('SectionTitle'); sectionAudit.addWidget(lblAudit)
        self.tblAudit = QTableWidget(0, 4)
        self.tblAudit.setHorizontalHeaderLabels(['Thời điểm','Model','Giá trị','User'])
        self.tblAudit.setMinimumHeight(160)
        self.tblAudit.setAlternatingRowColors(True)
        try:
            self.tblAudit.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        btnAuditRefresh = QPushButton('Refresh Audit'); btnAuditRefresh.clicked.connect(self._load_threshold_audit)
        btnAuditRefresh.setObjectName('Primary')
        sectionAudit.addWidget(self.tblAudit)
        sectionAudit.addWidget(btnAuditRefresh)
        layout.addLayout(sectionAudit)

        # Support requests section
        sectionSupport = QVBoxLayout()
        lblSupport = QLabel('Yêu cầu hỗ trợ'); lblSupport.setObjectName('SectionTitle'); sectionSupport.addWidget(lblSupport)
        self.lblSupportNotice = QLabel('')
        sectionSupport.addWidget(self.lblSupportNotice)
        self.tblSupport = QTableWidget(0, 4)
        self.tblSupport.setHorizontalHeaderLabels(['Họ tên','Email','User','Thời điểm'])
        self.tblSupport.setMinimumHeight(160)
        try:
            self.tblSupport.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        rowSup = QHBoxLayout()
        btnSupportRefresh = QPushButton('Refresh'); btnSupportRefresh.setObjectName('Secondary'); btnSupportRefresh.clicked.connect(self._load_support_requests)
        btnSupportResolve = QPushButton('Mark Resolved'); btnSupportResolve.setObjectName('Primary'); btnSupportResolve.clicked.connect(self._resolve_selected_support)
        rowSup.addWidget(btnSupportRefresh); rowSup.addWidget(btnSupportResolve)
        sectionSupport.addWidget(self.tblSupport)
        sectionSupport.addLayout(rowSup)
        layout.addLayout(sectionSupport)

        section1 = QVBoxLayout()
        lblOut = QLabel('Phát hiện dữ liệu bất thường'); lblOut.setObjectName('SectionTitle'); section1.addWidget(lblOut)
        row1 = QHBoxLayout()
        method = QComboBox()
        method.addItems(['Isolation Forest'])
        threshold = QSpinBox()
        threshold.setRange(0, 100)
        threshold.setValue(5)
        btn_scan = QPushButton('Scan Database'); btn_scan.setObjectName('Primary')
        lblMethod = QLabel('Method:'); lblMethod.setStyleSheet('font-weight:600')
        row1.addWidget(lblMethod)
        row1.addWidget(method)
        lblThresh2 = QLabel('Threshold:'); lblThresh2.setStyleSheet('font-weight:600')
        row1.addWidget(lblThresh2)
        row1.addWidget(threshold)
        row1.addWidget(btn_scan)
        section1.addLayout(row1)
        self.table1 = QTableWidget(0, 5)
        self.table1.setHorizontalHeaderLabels(['☑', 'Cust ID', 'Score', 'Issue', 'Actions'])
        self.table1.setMinimumHeight(420)
        self.table1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        section1.addWidget(self.table1)
        self.table1.setAlternatingRowColors(True)
        try:
            self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        row2 = QHBoxLayout()
        btnDelete = QPushButton('Delete Selected'); btnDelete.setObjectName('Danger'); btnDelete.clicked.connect(self.delete_selected_outliers)
        btnExport = QPushButton('Export Outliers'); btnExport.setObjectName('Secondary'); btnExport.clicked.connect(self.export_outliers)
        row2.addWidget(btnDelete)
        row2.addWidget(btnExport)
        section1.addLayout(row2)
        layout.addLayout(section1)
        section2 = QVBoxLayout()
        lblCluster = QLabel('Phân cụm khách hàng'); lblCluster.setObjectName('SectionTitle'); section2.addWidget(lblCluster)
        row3 = QHBoxLayout()
        algo = QComboBox()
        algo.addItems(['K-Means'])
        self.clusters = QSpinBox()
        self.clusters.setRange(2, 10)
        self.clusters.setValue(4)
        lblAlgo = QLabel('Algorithm:'); lblAlgo.setStyleSheet('font-weight:600')
        row3.addWidget(lblAlgo)
        row3.addWidget(algo)
        lblClusters = QLabel('Clusters:'); lblClusters.setStyleSheet('font-weight:600')
        row3.addWidget(lblClusters)
        row3.addWidget(self.clusters)
        btn_run = QPushButton('Run'); btn_run.setObjectName('Primary')
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
        self._load_support_requests()
        self._apply_styles()

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
            try:
                db = self._get_db_connector()
                try:
                    qs = self._get_query_service(db)
                except Exception:
                    qs = None
                if qs and hasattr(qs, 'save_model_threshold'):
                    qs.save_model_threshold(name, val, 'admin')
                else:
                    db.execute_query(
                        "INSERT INTO model_thresholds (model_name, threshold, updated_by) VALUES (%s, %s, %s)",
                        (name, val, 'admin')
                    )
                    db.execute_query(
                        "UPDATE model_registry SET threshold = %s WHERE model_name = %s",
                        (val, name)
                    )
                db.close()
            except Exception:
                pass
            self._show_msg(f"Đã cập nhật <b>threshold</b> cho <b>{name}</b>: {val:.2f}", 'Thành công', 'success')
            self._load_models_table()
            self._load_threshold_audit()
        else:
            self._show_msg('Không thể lưu thiết lập. Vui lòng thử lại.', 'Lỗi', 'error')

    def apply_overlay(self):
        a = float(self.spnAlpha.value())
        b = float(self.spnBeta.value())
        f = self.cmbOverlayFeature.currentText()
        ok = self._save_overlay(a,b,f)
        if ok:
            self._show_msg(f"Đã cập nhật <b>overlay</b>: α={a:.2f}, β={b:.2f}, feature=<b>{f}</b>", 'Thành công', 'success')
        else:
            self._show_msg('Không thể lưu overlay.', 'Lỗi', 'error')

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
            self._show_msg(f'Đã tái tính theo <b>threshold</b> hiện tại: {thr:.2f}', 'Thành công', 'success')
        except Exception as e:
            self._show_msg(f'Không thể tái tính: {e}', 'Lỗi', 'error')

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
                self._show_msg('Chưa có danh sách outliers. Vui lòng Scan trước.', 'Thông báo', 'info')
                return
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            out_dir = self.project_root / 'outputs' / 'evaluation'
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / f'outliers_{ts}.csv'
            pd.DataFrame(self._outliers).to_csv(path, index=False)
            self._show_msg(f'Đã export: <b>{path}</b>', 'Thành công', 'success')
        except Exception as e:
            self._show_msg(f'Không thể export: {e}', 'Lỗi', 'error')

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
            self._show_msg(f'Đã ghi <b>log xóa</b> {count} outliers (soft-delete).', 'Thành công', 'success')
        except Exception as e:
            self._show_msg(f'Không thể xóa: {e}', 'Lỗi', 'error')

    def set_active_model(self):
        try:
            if not self._ModelManagementService:
                self._show_msg('ModelManagementService không khả dụng', 'Lỗi', 'error')
                return
            db = self._get_db_connector()
            svc = self._ModelManagementService(db)
            name = self.cmbModel.currentText()
            ok = svc.set_active_model(name, 'admin')
            db.close()
            if ok:
                self.lblActive.setText(f'Active: {name}')
                self._load_models_table()
                self._show_msg(f'Đã set <b>active model</b>: {name}', 'Thành công', 'success')
            else:
                self._show_msg('Không thể set active model', 'Lỗi', 'error')
        except Exception as e:
            self._show_msg(f'Không thể set active: {e}', 'Lỗi', 'error')

    def _apply_styles(self):
        try:
            self.setStyleSheet(
                """
                QLabel#SectionTitle { font-weight: 700; color: #1e2a44; background-color: #00bfff; padding: 6px 10px; border-radius: 8px; border: 1px solid #d7e3ff; }
                QPushButton#Primary { background-color: #2663ea; color: #ffffff; padding: 6px 14px; border-radius: 8px; }
                QPushButton#Primary:hover { background-color: #1e56c9; }
                QPushButton#Secondary { background-color: #f0f4ff; color: #1e2a44; padding: 6px 14px; border-radius: 8px; border: 1px solid #d3d9e8; }
                QPushButton#Secondary:hover { background-color: #e6edff; }
                QPushButton#Danger { background-color: #e74c3c; color: #ffffff; padding: 6px 14px; border-radius: 8px; }
                QPushButton#Danger:hover { background-color: #cf3f30; }
                QTableWidget { background-color: #ffffff; border: 1px solid #e5eaf3; border-radius: 8px; }
                QHeaderView::section { background-color: #f7f9fc; padding: 6px; border: 1px solid #e5eaf3; font-weight: 600; }
                """
            )
        except Exception:
            pass
    
    def show_model_comparison(self):
        """Hiển thị dialog so sánh 8 models với dữ liệu mẫu"""
        print("🟢 SystemManagementTab.show_model_comparison() CALLED!")
        try:
            from .ModelComparisonDialog import ModelComparisonDialog
            print("🟢 Successfully imported ModelComparisonDialog from relative import")
        except Exception as e:
            print(f"🔴 Relative import failed: {e}, trying absolute import")
            from ModelComparisonDialog import ModelComparisonDialog
            print("🟢 Successfully imported ModelComparisonDialog from absolute import")
        
        # Test data mẫu
        test_data = {
            'LIMIT_BAL': 300000,
            'SEX': 1,
            'EDUCATION': 2,
            'MARRIAGE': 1,
            'AGE': 45,
            'PAY_0': 1, 'PAY_2': 1, 'PAY_3': 0, 'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 1,
            'PAY_7': 0, 'PAY_8': 0, 'PAY_9': 0, 'PAY_10': 0, 'PAY_11': 0, 'PAY_12': 0,
            'BILL_AMT1': 10000, 'BILL_AMT2': 10000, 'BILL_AMT3': 10000, 'BILL_AMT4': 10000,
            'BILL_AMT5': 10000, 'BILL_AMT6': 10000, 'BILL_AMT7': 10000, 'BILL_AMT8': 10000,
            'BILL_AMT9': 10000, 'BILL_AMT10': 10000, 'BILL_AMT11': 10000, 'BILL_AMT12': 10000,
            'PAY_AMT1': 5000, 'PAY_AMT2': 5000, 'PAY_AMT3': 5000, 'PAY_AMT4': 5000,
            'PAY_AMT5': 5000, 'PAY_AMT6': 5000, 'PAY_AMT7': 5000, 'PAY_AMT8': 5000,
            'PAY_AMT9': 5000, 'PAY_AMT10': 5000, 'PAY_AMT11': 5000, 'PAY_AMT12': 5000
        }
        
        dialog = ModelComparisonDialog(test_data, self)
        dialog.exec()

    def _show_msg(self, text: str, title: str = 'Thông báo', kind: str = 'info'):
        box = QMessageBox(self)
        if kind == 'success':
            box.setIcon(QMessageBox.Icon.Information)
        elif kind == 'error':
            box.setIcon(QMessageBox.Icon.Critical)
        else:
            box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(title)
        box.setText(f"<div style='font-size:14px; color:#1e2a44'>{text}</div>")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setStyleSheet(
            """
            QMessageBox { background-color: #ffffff; border: 1px solid #e5eaf3; border-radius: 12px; }
            QLabel { color: #1e2a44; font-size: 14px; }
            QPushButton { background-color: #2663ea; color: #ffffff; padding: 6px 16px; border-radius: 8px; min-width: 84px; }
            QPushButton:hover { background-color: #1e56c9; }
            """
        )
        box.exec()

    def _load_support_requests(self):
        try:
            import json
            self.tblSupport.setRowCount(0)
            pending = []
            if self.support_path.exists():
                items = json.loads(self.support_path.read_text(encoding='utf-8'))
                pending = [i for i in items if i.get('status') == 'pending']
            self.lblSupportNotice.setText(f"Có {len(pending)} yêu cầu quên mật khẩu đang chờ duyệt")
            self.tblSupport.setRowCount(len(pending))
            for i, r in enumerate(pending):
                self.tblSupport.setItem(i,0, QTableWidgetItem(str(r.get('full_name',''))))
                self.tblSupport.setItem(i,1, QTableWidgetItem(str(r.get('email',''))))
                self.tblSupport.setItem(i,2, QTableWidgetItem(str(r.get('username',''))))
                self.tblSupport.setItem(i,3, QTableWidgetItem(str(r.get('ts',''))))
        except Exception as e:
            print(f"✗ Load support requests failed: {e}")

    def _resolve_selected_support(self):
        try:
            import json
            row = self.tblSupport.currentRow()
            if row < 0:
                return
            email = self.tblSupport.item(row,1).text()
            name = self.tblSupport.item(row,0).text()
            if not self.support_path.exists():
                return
            items = json.loads(self.support_path.read_text(encoding='utf-8'))
            for i in items:
                if i.get('email') == email and i.get('full_name') == name and i.get('status') == 'pending':
                    i['status'] = 'resolved'
                    break
            self.support_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
            self._load_support_requests()
            self._show_msg('Đã đánh dấu xử lý yêu cầu', 'Thành công', 'success')
        except Exception as e:
            self._show_msg(f'Không thể cập nhật: {e}', 'Lỗi', 'error')
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
            self._show_msg('Đã reset <b>overlay</b> về mặc định.', 'Thành công', 'success')
        except Exception as e:
            self._show_msg(f'Không thể reset overlay: {e}', 'Lỗi', 'error')

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
