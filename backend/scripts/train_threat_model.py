"""
Model Training Script for Threat Analysis
=============================================

This script trains a machine learning model to classify threat levels
based on document and behavioral indicators.

Dependencies:
    - scikit-learn
    - pandas
    - numpy
    - pickle

Usage:
    python train_threat_model.py --dataset data/threat_data.csv --output models/threat_analysis.pkl
    python train_threat_model.py --dataset data/threats.csv --model-type gradient_boosting --test-size 0.2
"""

import logging
import pickle
import json
from pathlib import Path
from typing import Tuple, Dict, List, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score
)
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ThreatModelTrainer:
    """Trainer for threat analysis classification model"""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize threat model trainer
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.target_names = None
        self.metrics = {}
        
        logger.info("ThreatModelTrainer initialized")
    
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load training data from CSV
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            DataFrame with training data
        """
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} samples from {csv_path}")
            logger.info(f"Columns: {list(df.columns)}")
            logger.info(f"Data shape: {df.shape}")
            
            # Display data info
            logger.info(f"\nData Info:\n{df.info()}")
            logger.info(f"\nData Statistics:\n{df.describe()}")
            
            return df
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def preprocess_data(self, df: pd.DataFrame, target_column: str = 'threat_level') -> Tuple:
        """
        Preprocess training data
        
        Args:
            df: Input DataFrame
            target_column: Name of target column
            
        Returns:
            Tuple of (X, y)
        """
        try:
            # Separate features and target
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")
            
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Handle categorical features
            categorical_columns = X.select_dtypes(include=['object']).columns
            logger.info(f"Categorical features: {list(categorical_columns)}")
            
            for col in categorical_columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.label_encoders[col] = le
                logger.info(f"Encoded {col}: {len(le.classes_)} classes")
            
            # Handle missing values
            X = X.fillna(X.mean(numeric_only=True))
            y = y.fillna('UNKNOWN')
            
            # Encode target variable
            if y.dtype == 'object':
                le_target = LabelEncoder()
                y = le_target.fit_transform(y)
                self.target_names = le_target.classes_
                logger.info(f"Target classes: {list(self.target_names)}")
            
            self.feature_names = list(X.columns)
            logger.info(f"Features: {self.feature_names}")
            logger.info(f"Feature count: {len(self.feature_names)}")
            
            return X, y
        
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
    
    def train(self, X: np.ndarray, y: np.ndarray, 
              model_type: str = 'random_forest', test_size: float = 0.2) -> Dict:
        """
        Train threat analysis model
        
        Args:
            X: Feature matrix
            y: Target vector
            model_type: Type of model ('random_forest' or 'gradient_boosting')
            test_size: Test set size fraction
            
        Returns:
            Dictionary with training metrics
        """
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state, stratify=y
            )
            
            logger.info(f"Training set size: {len(X_train)}")
            logger.info(f"Test set size: {len(X_test)}")
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            logger.info(f"Training {model_type} model...")
            
            if model_type == 'random_forest':
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=15,
                    min_samples_split=10,
                    min_samples_leaf=5,
                    random_state=self.random_state,
                    n_jobs=-1,
                    verbose=1
                )
            elif model_type == 'gradient_boosting':
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    min_samples_split=10,
                    min_samples_leaf=5,
                    random_state=self.random_state,
                    verbose=1
                )
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            self.model.fit(X_train_scaled, y_train)
            logger.info("Model training completed")
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)
            
            metrics = self._evaluate_model(y_test, y_pred, y_pred_proba)
            self.metrics = metrics
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def _evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray, 
                       y_pred_proba: np.ndarray) -> Dict:
        """
        Evaluate model performance
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities
            
        Returns:
            Dictionary with metrics
        """
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        try:
            if len(np.unique(y_true)) == 2:
                roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1])
            else:
                roc_auc = roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average='weighted')
        except:
            roc_auc = None
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc) if roc_auc else None,
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
            'classification_report': classification_report(
                y_true, y_pred, 
                target_names=self.target_names if self.target_names else None,
                output_dict=True
            )
        }
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Model Evaluation Metrics")
        logger.info(f"{'='*50}")
        logger.info(f"Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall:    {metrics['recall']:.4f}")
        logger.info(f"F1-Score:  {metrics['f1_score']:.4f}")
        if roc_auc:
            logger.info(f"ROC-AUC:   {roc_auc:.4f}")
        logger.info(f"\nConfusion Matrix:\n{metrics['confusion_matrix']}")
        
        return metrics
    
    def get_feature_importance(self, top_n: int = 10) -> List[Tuple]:
        """
        Get feature importance from model
        
        Args:
            top_n: Top N features to return
            
        Returns:
            List of (feature_name, importance) tuples
        """
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            logger.warning("Model or feature importances not available")
            return []
        
        importances = self.model.feature_importances_
        feature_importance = list(zip(self.feature_names, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"\nTop {top_n} Important Features:")
        for i, (feature, importance) in enumerate(feature_importance[:top_n], 1):
            logger.info(f"{i}. {feature}: {importance:.4f}")
        
        return feature_importance[:top_n]
    
    def save_model(self, output_path: str, include_metadata: bool = True):
        """
        Save trained model and metadata
        
        Args:
            output_path: Path to save model
            include_metadata: Whether to save metadata
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save model
            with open(output_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {output_path}")
            
            # Save metadata
            if include_metadata:
                metadata = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'feature_names': self.feature_names,
                    'target_names': self.target_names,
                    'metrics': self.metrics,
                    'scaler_mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else None,
                    'scaler_scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else None
                }
                
                metadata_path = output_path.replace('.pkl', '_metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
                logger.info(f"Metadata saved to {metadata_path}")
        
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, model_path: str):
        """
        Load trained model
        
        Args:
            model_path: Path to model file
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {model_path}")
        
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise


def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(description='Train threat analysis model')
    parser.add_argument('--dataset', type=str, required=True, 
                       help='Path to training dataset (CSV)')
    parser.add_argument('--output', type=str, default='models/threat_analysis.pkl',
                       help='Path to save model')
    parser.add_argument('--model-type', type=str, default='random_forest',
                       choices=['random_forest', 'gradient_boosting'],
                       help='Type of model to train')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set size fraction')
    
    args = parser.parse_args()
    
    try:
        # Initialize trainer
        trainer = ThreatModelTrainer()
        
        # Load and preprocess data
        df = trainer.load_data(args.dataset)
        X, y = trainer.preprocess_data(df)
        
        # Train model
        metrics = trainer.train(X, y, model_type=args.model_type, test_size=args.test_size)
        
        # Get feature importance
        trainer.get_feature_importance(top_n=10)
        
        # Save model
        trainer.save_model(args.output)
        
        logger.info(f"\n✅ Training completed successfully!")
        logger.info(f"Model saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
