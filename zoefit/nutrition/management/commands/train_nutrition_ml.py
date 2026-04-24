"""
Django management command to train nutrition ML models.

Usage:
    python manage.py train_nutrition_ml --dataset path/to/dataset.csv
    python manage.py train_nutrition_ml --from-db
    python manage.py train_nutrition_ml --evaluate --test-data path/to/test.csv
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Train nutrition ML models with provided dataset'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            help='Path to training dataset file (CSV, JSON, or Excel)'
        )
        parser.add_argument(
            '--from-db',
            action='store_true',
            help='Train models using database data'
        )
        parser.add_argument(
            '--test-data',
            type=str,
            help='Path to test dataset for evaluation'
        )
        parser.add_argument(
            '--evaluate-only',
            action='store_true',
            help='Only evaluate existing models'
        )
        parser.add_argument(
            '--no-augment',
            action='store_true',
            help='Skip data augmentation'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file for training report'
        )
    
    def handle(self, *args, **options):
        from nutrition.ml.train_models import NutritionModelTrainer
        
        trainer = NutritionModelTrainer()
        
        self.stdout.write(self.style.SUCCESS('Starting Nutrition ML Training...'))
        
        try:
            if options['evaluate_only']:
                if not options['test_data']:
                    self.stdout.write(self.style.ERROR('--test-data required for evaluation'))
                    return
                
                self.stdout.write('Evaluating existing models...')
                results = trainer.evaluate_models(options['test_data'])
                
            else:
                if options['from_db']:
                    self.stdout.write('Training from database data...')
                    results = trainer.train_from_database(augment_data=not options['no_augment'])
                elif options['dataset']:
                    self.stdout.write(f'Training from dataset: {options["dataset"]}')
                    results = trainer.train_from_dataset(options['dataset'], augment_data=not options['no_augment'])
                else:
                    self.stdout.write(self.style.ERROR('Either --dataset or --from-db required'))
                    return
                
                # Evaluate if test data provided
                if options['test_data'] and 'error' not in results:
                    self.stdout.write('Running evaluation...')
                    evaluation_results = trainer.evaluate_models(options['test_data'])
                    results['evaluation'] = evaluation_results
            
            # Output results
            if options['output']:
                with open(options['output'], 'w') as f:
                    json.dump(results, f, indent=2)
                self.stdout.write(self.style.SUCCESS(f'Results saved to {options["output"]}'))
            
            # Display summary
            self._display_results(results)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Training failed: {e}'))
    
    def _display_results(self, results):
        """Display training results summary"""
        if 'error' in results:
            self.stdout.write(self.style.ERROR(f"Error: {results['error']}"))
            return
        
        self.stdout.write(self.style.SUCCESS('\n=== TRAINING RESULTS ==='))
        self.stdout.write(f"Status: {results.get('status', 'unknown')}")
        self.stdout.write(f"Date: {results.get('training_date', 'unknown')}")
        
        if 'data_quality' in results:
            dq = results['data_quality']
            self.stdout.write(f"\nData Quality:")
            self.stdout.write(f"  Total samples: {dq.get('total_samples', 0)}")
            self.stdout.write(f"  Missing values: {dq.get('missing_values', 0)}")
            self.stdout.write(f"  Duplicate rows: {dq.get('duplicate_rows', 0)}")
        
        if 'model_performance' in results:
            mp = results['model_performance']
            self.stdout.write(f"\nModel Performance:")
            
            if 'macro_prediction' in mp:
                macro = mp['macro_prediction']
                self.stdout.write(f"  Macro Prediction:")
                self.stdout.write(f"    MSE: {macro.get('mse', 0):.4f}")
                self.stdout.write(f"    R² Score: {macro.get('r2_score', 0):.4f}")
            
            if 'meal_recommendation' in mp:
                meal = mp['meal_recommendation']
                self.stdout.write(f"  Meal Recommendation:")
                self.stdout.write(f"    MSE: {meal.get('mse', 0):.4f}")
                self.stdout.write(f"    R² Score: {meal.get('r2_score', 0):.4f}")
        
        if 'evaluation' in results:
            eval_results = results['evaluation']
            self.stdout.write(f"\nEvaluation Results:")
            
            if 'macro_prediction' in eval_results:
                macro = eval_results['macro_prediction']
                self.stdout.write(f"  Macro Prediction:")
                self.stdout.write(f"    MSE: {macro.get('mse', 0):.4f}")
                self.stdout.write(f"    MAE: {macro.get('mae', 0):.4f}")
                self.stdout.write(f"    R² Score: {macro.get('r2_score', 0):.4f}")
            
            if 'meal_recommendation' in eval_results:
                meal = eval_results['meal_recommendation']
                self.stdout.write(f"  Meal Recommendation:")
                self.stdout.write(f"    MSE: {meal.get('mse', 0):.4f}")
                self.stdout.write(f"    MAE: {meal.get('mae', 0):.4f}")
                self.stdout.write(f"    R² Score: {meal.get('r2_score', 0):.4f}")
        
        self.stdout.write(self.style.SUCCESS('\nTraining completed successfully!'))
