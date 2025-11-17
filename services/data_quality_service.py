"""
Data Quality Service
Service kiểm tra chất lượng dữ liệu và phân cụm khách hàng
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from scipy import stats

from database.connector import DatabaseConnector


class DataQualityService:
    """
    Service phân tích chất lượng dữ liệu
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db = db_connector
    
    def detect_outliers(
        self,
        method: str = 'IsolationForest',
        contamination: float = 0.05,
        customer_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Phát hiện outliers trong dữ liệu khách hàng
        
        Args:
            method: 'IsolationForest', 'LOF', hoặc 'ZScore'
            contamination: Tỷ lệ outliers dự kiến (0.01-0.5)
            customer_ids: List ID khách hàng cần check (None = tất cả)
        
        Returns:
            Dict chứa outlier indices, scores, và issue descriptions
        """
        # Load customer data
        if customer_ids:
            query = f"""
                SELECT * FROM customers 
                WHERE id IN ({','.join(map(str, customer_ids))})
            """
        else:
            query = "SELECT * FROM customers LIMIT 5000"  # Limit để tránh quá tải
        
        results = self.db.fetch_all(query)
        
        if not results:
            return {'error': 'No data found'}
        
        # Convert to DataFrame
        columns = [
            'id', 'customer_name', 'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
            'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
            'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12',
            'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
            'BILL_AMT7', 'BILL_AMT8', 'BILL_AMT9', 'BILL_AMT10', 'BILL_AMT11', 'BILL_AMT12',
            'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6',
            'PAY_AMT7', 'PAY_AMT8', 'PAY_AMT9', 'PAY_AMT10', 'PAY_AMT11', 'PAY_AMT12'
        ]
        
        df = pd.DataFrame(results, columns=columns)
        
        # Features for outlier detection (numeric only)
        feature_cols = [col for col in columns if col not in ['id', 'customer_name']]
        X = df[feature_cols].values
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Detect outliers
        if method == 'IsolationForest':
            detector = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_jobs=-1
            )
            predictions = detector.fit_predict(X_scaled)
            scores = detector.score_samples(X_scaled)
        
        elif method == 'LOF':
            detector = LocalOutlierFactor(
                contamination=contamination,
                n_jobs=-1
            )
            predictions = detector.fit_predict(X_scaled)
            scores = detector.negative_outlier_factor_
        
        elif method == 'ZScore':
            # Z-score based outlier detection
            z_scores = np.abs(stats.zscore(X_scaled, axis=0))
            predictions = np.where(np.max(z_scores, axis=1) > 3, -1, 1)
            scores = -np.max(z_scores, axis=1)  # Negative for consistency
        
        else:
            return {'error': f'Unknown method: {method}'}
        
        # Find outliers
        outlier_mask = predictions == -1
        outlier_indices = np.where(outlier_mask)[0]
        
        outliers = []
        for idx in outlier_indices:
            customer_id = int(df.iloc[idx]['id'])
            customer_name = df.iloc[idx]['customer_name']
            score = float(scores[idx])
            
            # Analyze issues
            issues = self._analyze_customer_issues(df.iloc[idx])
            
            outliers.append({
                'customer_id': customer_id,
                'customer_name': customer_name,
                'score': score,
                'issues': issues,
                'severity': 'High' if score < -0.5 else 'Medium'
            })
        
        # Sort by score (most anomalous first)
        outliers.sort(key=lambda x: x['score'])
        
        return {
            'method': method,
            'total_checked': len(df),
            'outliers_found': len(outliers),
            'outliers': outliers
        }
    
    def _analyze_customer_issues(self, customer_row: pd.Series) -> List[str]:
        """Phân tích vấn đề cụ thể của khách hàng"""
        issues = []
        
        # Check extreme values
        if customer_row['LIMIT_BAL'] > 800000:
            issues.append('Hạn mức cực cao (>800k)')
        
        if customer_row['AGE'] < 21 or customer_row['AGE'] > 70:
            issues.append(f'Tuổi bất thường ({customer_row["AGE"]})')
        
        # Check payment history
        pay_cols = [f'PAY_{i}' for i in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
        pay_values = [customer_row[col] for col in pay_cols if col in customer_row.index]
        
        if all(v >= 2 for v in pay_values):
            issues.append('Trễ thanh toán liên tục 12 tháng')
        
        # Check bill amounts
        bill_cols = [f'BILL_AMT{i}' for i in range(1, 13)]
        bill_values = [customer_row[col] for col in bill_cols if col in customer_row.index]
        
        if max(bill_values) > 500000:
            issues.append(f'Hóa đơn cực cao (max: {max(bill_values):,.0f})')
        
        # Check payment amounts
        pay_amt_cols = [f'PAY_AMT{i}' for i in range(1, 13)]
        pay_amt_values = [customer_row[col] for col in pay_amt_cols if col in customer_row.index]
        
        avg_bill = np.mean(bill_values)
        avg_pay = np.mean(pay_amt_values)
        
        if avg_bill > 0 and avg_pay / avg_bill < 0.1:
            issues.append(f'Tỷ lệ thanh toán cực thấp ({avg_pay/avg_bill*100:.1f}%)')
        
        if not issues:
            issues.append('Bất thường tổng thể')
        
        return issues
    
    def log_outlier(
        self,
        customer_id: int,
        issue_type: str,
        severity: str,
        method: str,
        detected_by: str
    ):
        """Ghi log outlier vào database"""
        query = """
            INSERT INTO data_quality_log 
            (record_id, record_type, issue_type, severity, detection_method, detected_by)
            VALUES (%s, 'Customer', %s, %s, %s, %s)
        """
        self.db.execute_query(query, (customer_id, issue_type, severity, method, detected_by))
    
    def delete_customer(self, customer_id: int, username: str) -> bool:
        """Xóa customer và log action"""
        try:
            # Update log
            query = """
                UPDATE data_quality_log 
                SET action_taken = 'Deleted', action_by = %s, action_at = NOW()
                WHERE record_id = %s AND record_type = 'Customer'
            """
            self.db.execute_query(query, (username, customer_id))
            
            # Delete customer
            self.db.execute_query("DELETE FROM customers WHERE id = %s", (customer_id,))
            
            return True
        except Exception as e:
            print(f"✗ Failed to delete customer: {e}")
            return False
    
    def cluster_customers(
        self,
        algorithm: str = 'KMeans',
        n_clusters: int = 4,
        customer_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Phân cụm khách hàng
        
        Args:
            algorithm: 'KMeans' hoặc 'DBSCAN'
            n_clusters: Số clusters (cho KMeans)
            customer_ids: List ID khách hàng (None = tất cả)
        
        Returns:
            Dict chứa cluster assignments và statistics
        """
        # Load data
        if customer_ids:
            query = f"""
                SELECT * FROM customers 
                WHERE id IN ({','.join(map(str, customer_ids))})
            """
        else:
            query = "SELECT * FROM customers LIMIT 5000"
        
        results = self.db.fetch_all(query)
        
        if not results:
            return {'error': 'No data found'}
        
        # Convert to DataFrame
        columns = [
            'id', 'customer_name', 'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
            'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
            'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12',
            'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
            'BILL_AMT7', 'BILL_AMT8', 'BILL_AMT9', 'BILL_AMT10', 'BILL_AMT11', 'BILL_AMT12',
            'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6',
            'PAY_AMT7', 'PAY_AMT8', 'PAY_AMT9', 'PAY_AMT10', 'PAY_AMT11', 'PAY_AMT12'
        ]
        
        df = pd.DataFrame(results, columns=columns)
        
        # Features
        feature_cols = [col for col in columns if col not in ['id', 'customer_name']]
        X = df[feature_cols].values
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Clustering
        if algorithm == 'KMeans':
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = clusterer.fit_predict(X_scaled)
            
            # Calculate distances to cluster centers
            distances = np.min(clusterer.transform(X_scaled), axis=1)
        
        elif algorithm == 'DBSCAN':
            clusterer = DBSCAN(eps=0.5, min_samples=10)
            clusters = clusterer.fit_predict(X_scaled)
            distances = np.zeros(len(clusters))  # DBSCAN doesn't have distances
            n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        
        else:
            return {'error': f'Unknown algorithm: {algorithm}'}
        
        # Map clusters to risk levels
        risk_mapping = self._map_clusters_to_risk(df, clusters, n_clusters)
        
        # Save to database
        for idx, cluster_id in enumerate(clusters):
            customer_id = int(df.iloc[idx]['id'])
            risk_level = risk_mapping.get(cluster_id, 'Unknown')
            distance = float(distances[idx])
            
            query = """
                INSERT INTO customer_clusters 
                (customer_id, cluster_id, risk_level, cluster_center_distance)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                cluster_id = VALUES(cluster_id),
                risk_level = VALUES(risk_level),
                cluster_center_distance = VALUES(cluster_center_distance),
                clustered_at = CURRENT_TIMESTAMP
            """
            
            self.db.execute_query(query, (customer_id, int(cluster_id), risk_level, distance))
        
        # Statistics
        cluster_stats = []
        for cluster_id in range(n_clusters):
            mask = clusters == cluster_id
            cluster_size = np.sum(mask)
            
            # Calculate risk indicators
            cluster_data = df[mask]
            avg_pay_delay = cluster_data[[f'PAY_{i}' for i in [0, 2, 3, 4, 5, 6]]].mean().mean()
            
            cluster_stats.append({
                'cluster_id': int(cluster_id),
                'size': int(cluster_size),
                'percentage': float(cluster_size / len(df) * 100),
                'risk_level': risk_mapping.get(cluster_id, 'Unknown'),
                'avg_payment_delay': float(avg_pay_delay)
            })
        
        # PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        return {
            'algorithm': algorithm,
            'n_clusters': n_clusters,
            'total_customers': len(df),
            'cluster_stats': cluster_stats,
            'pca_data': {
                'x': X_pca[:, 0].tolist(),
                'y': X_pca[:, 1].tolist(),
                'clusters': clusters.tolist(),
                'explained_variance': pca.explained_variance_ratio_.tolist()
            }
        }
    
    def _map_clusters_to_risk(
        self,
        df: pd.DataFrame,
        clusters: np.ndarray,
        n_clusters: int
    ) -> Dict[int, str]:
        """Map cluster IDs to risk levels based on payment behavior"""
        risk_mapping = {}
        
        for cluster_id in range(n_clusters):
            mask = clusters == cluster_id
            cluster_data = df[mask]
            
            # Calculate average payment delay
            pay_cols = [f'PAY_{i}' for i in [0, 2, 3, 4, 5, 6]]
            avg_delay = cluster_data[pay_cols].mean().mean()
            
            # Map to risk level
            if avg_delay < -0.5:
                risk_mapping[cluster_id] = 'Low'
            elif avg_delay < 0.5:
                risk_mapping[cluster_id] = 'Medium'
            elif avg_delay < 1.5:
                risk_mapping[cluster_id] = 'High'
            else:
                risk_mapping[cluster_id] = 'Critical'
        
        return risk_mapping
    
    def get_cluster_statistics(self) -> List[Dict[str, Any]]:
        """Lấy thống kê clusters từ database"""
        query = """
            SELECT cluster_id, risk_level, COUNT(*) as count
            FROM customer_clusters
            GROUP BY cluster_id, risk_level
            ORDER BY cluster_id
        """
        
        results = self.db.fetch_all(query)
        
        stats = []
        for row in results:
            stats.append({
                'cluster_id': row[0],
                'risk_level': row[1],
                'count': row[2]
            })
        
        return stats
