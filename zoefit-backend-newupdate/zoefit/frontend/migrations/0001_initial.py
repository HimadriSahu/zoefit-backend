"""
Initial migration for frontend module.

This migration creates all the database tables for the frontend module:
- WorkoutSession: Tracks actual workout completions
- ExerciseLog: Detailed exercise performance data
- ProgressSnapshot: Time-based progress measurements
- Streak: Various fitness streak tracking
- MealLog: User meal consumption tracking
- Achievement: Achievement and milestone tracking

Generated: 2026-03-02 21:45:00
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(help_text='When the workout session started')),
                ('end_time', models.DateTimeField(blank=True, help_text='When the workout session ended', null=True)),
                ('duration', models.DurationField(blank=True, help_text='Total duration of the workout session', null=True)),
                ('completed', models.BooleanField(default=False, help_text='Whether the workout was completed as planned')),
                ('exercises_completed', models.JSONField(default=list, help_text='List of exercises completed with their details')),
                ('calories_burned', models.IntegerField(default=0, help_text='Estimated calories burned during the session', validators=[django.core.validators.MinValueValidator(0)])),
                ('user_notes', models.TextField(blank=True, help_text="User's notes about the workout session")),
                ('difficulty_rating', models.IntegerField(blank=True, help_text="User's rating of workout difficulty (1-5)", null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workout_sessions', to=settings.AUTH_USER_MODEL)),
                ('workout_plan', models.ForeignKey(blank=True, help_text='The AI-generated workout plan this session follows', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actual_sessions', to='workout.WorkoutPlan')),
            ],
            options={
                'verbose_name': 'Workout Session',
                'verbose_name_plural': 'Workout Sessions',
                'db_table': 'frontend_workout_sessions',
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='ProgressSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Date of the progress snapshot')),
                ('weight', models.FloatField(blank=True, help_text='Weight in kg', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('body_fat_percentage', models.FloatField(blank=True, help_text='Body fat percentage', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('muscle_mass', models.FloatField(blank=True, help_text='Muscle mass in kg', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('measurements', models.JSONField(default=dict, help_text='Body measurements in cm (chest, waist, arms, thighs, etc.)')),
                ('progress_photos', models.JSONField(default=list, help_text='URLs to progress photos')),
                ('notes', models.TextField(blank=True, help_text='User notes about this progress snapshot')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_snapshots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Progress Snapshot',
                'verbose_name_plural': 'Progress Snapshots',
                'db_table': 'frontend_progress_snapshots',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Streak',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('streak_type', models.CharField(choices=[('workout', 'Workout Streak'), ('calorie', 'Calorie Logging Streak'), ('water', 'Water Intake Streak'), ('steps', 'Steps Goal Streak'), ('meal_plan', 'Meal Plan Adherence Streak')], help_text='Type of streak being tracked', max_length=50)),
                ('current_count', models.IntegerField(default=0, help_text='Current streak count', validators=[django.core.validators.MinValueValidator(0)])),
                ('longest_count', models.IntegerField(default=0, help_text='Longest streak achieved', validators=[django.core.validators.MinValueValidator(0)])),
                ('last_activity_date', models.DateField(help_text='Date of last activity for this streak')),
                ('start_date', models.DateField(help_text='Date when the current streak started')),
                ('is_active', models.BooleanField(default=True, help_text='Whether the streak is currently active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='streaks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Streak',
                'verbose_name_plural': 'Streaks',
                'db_table': 'frontend_streaks',
            },
        ),
        migrations.CreateModel(
            name='MealLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_type', models.CharField(choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('snack', 'Snack')], help_text='Type of meal', max_length=20)),
                ('food_items', models.JSONField(default=list, help_text='List of food items with quantities and nutritional info')),
                ('total_calories', models.IntegerField(default=0, help_text='Total calories in the meal', validators=[django.core.validators.MinValueValidator(0)])),
                ('protein', models.FloatField(default=0, help_text='Protein content in grams', validators=[django.core.validators.MinValueValidator(0)])),
                ('carbs', models.FloatField(default=0, help_text='Carbohydrate content in grams', validators=[django.core.validators.MinValueValidator(0)])),
                ('fat', models.FloatField(default=0, help_text='Fat content in grams', validators=[django.core.validators.MinValueValidator(0)])),
                ('meal_time', models.DateTimeField(default=django.utils.timezone.now, help_text='When the meal was consumed')),
                ('photo_url', models.URLField(blank=True, help_text='URL to meal photo')),
                ('notes', models.TextField(blank=True, help_text='User notes about the meal')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Meal Log',
                'verbose_name_plural': 'Meal Logs',
                'db_table': 'frontend_meal_logs',
                'ordering': ['-meal_time'],
            },
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievement_type', models.CharField(help_text='Type of achievement', max_length=50)),
                ('title', models.CharField(help_text='Achievement title', max_length=100)),
                ('description', models.TextField(help_text='Achievement description')),
                ('badge_icon', models.CharField(help_text='Icon identifier for the achievement badge', max_length=50)),
                ('points_awarded', models.IntegerField(default=0, help_text='Points awarded for this achievement', validators=[django.core.validators.MinValueValidator(0)])),
                ('earned_date', models.DateTimeField(auto_now_add=True, help_text='When the achievement was earned')),
                ('is_displayed', models.BooleanField(default=True, help_text='Whether to display this achievement on profile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Achievement',
                'verbose_name_plural': 'Achievements',
                'db_table': 'frontend_achievements',
                'ordering': ['-earned_date'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise_name', models.CharField(help_text='Name of the exercise performed', max_length=100)),
                ('sets_completed', models.IntegerField(help_text='Number of sets completed', validators=[django.core.validators.MinValueValidator(1)])),
                ('reps_per_set', models.JSONField(help_text='List of reps completed for each set')),
                ('weight_used', models.FloatField(blank=True, help_text='Weight used in kg', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('rest_time', models.DurationField(blank=True, help_text='Rest time between sets', null=True)),
                ('form_rating', models.IntegerField(blank=True, help_text="User's rating of exercise form (1-5)", null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('notes', models.TextField(blank=True, help_text='Notes about this specific exercise')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('workout_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_logs', to='frontend.workoutsession')),
            ],
            options={
                'verbose_name': 'Exercise Log',
                'verbose_name_plural': 'Exercise Logs',
                'db_table': 'frontend_exercise_logs',
                'ordering': ['workout_session', 'id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='progresssnapshot',
            unique_together={('user', 'date')},
        ),
        migrations.AlterUniqueTogether(
            name='streak',
            unique_together={('user', 'streak_type')},
        ),
        migrations.AddIndex(
            model_name='workoutsession',
            index=models.Index(fields=['user', '-start_time'], name='frontend_work_user_id_8f4a9a_idx'),
        ),
        migrations.AddIndex(
            model_name='workoutsession',
            index=models.Index(fields=['user', 'completed'], name='frontend_work_user_id_4b5f3b_idx'),
        ),
        migrations.AddIndex(
            model_name='workoutsession',
            index=models.Index(fields=['-created_at'], name='frontend_work__created_1e4a2c_idx'),
        ),
        migrations.AddIndex(
            model_name='exerciselog',
            index=models.Index(fields=['workout_session', 'exercise_name'], name='frontend_exer_workout_s_7c3d5e_idx'),
        ),
        migrations.AddIndex(
            model_name='exerciselog',
            index=models.Index(fields=['-created_at'], name='frontend_exer__created_5f8b9a_idx'),
        ),
        migrations.AddIndex(
            model_name='progresssnapshot',
            index=models.Index(fields=['user', '-date'], name='frontend_prog_user_id__a2c4d6_idx'),
        ),
        migrations.AddIndex(
            model_name='progresssnapshot',
            index=models.Index(fields=['-created_at'], name='frontend_prog__created_3e7f8b_idx'),
        ),
        migrations.AddIndex(
            model_name='streak',
            index=models.Index(fields=['user', 'streak_type'], name='frontend_stre_user_id__9c2d5e_idx'),
        ),
        migrations.AddIndex(
            model_name='streak',
            index=models.Index(fields=['user', 'is_active'], name='frontend_stre_user_id_6f8a3b_idx'),
        ),
        migrations.AddIndex(
            model_name='streak',
            index=models.Index(fields=['-updated_at'], name='frontend_stre__updated_2c7e9a_idx'),
        ),
        migrations.AddIndex(
            model_name='meallog',
            index=models.Index(fields=['user', '-meal_time'], name='frontend_meal_user_id__4e8c7f_idx'),
        ),
        migrations.AddIndex(
            model_name='meallog',
            index=models.Index(fields=['user', 'meal_type'], name='frontend_meal_user_id_7a3d2b_idx'),
        ),
        migrations.AddIndex(
            model_name='meallog',
            index=models.Index(fields=['-created_at'], name='frontend_meal__created_9f5e8c_idx'),
        ),
        migrations.AddIndex(
            model_name='achievement',
            index=models.Index(fields=['user', '-earned_date'], name='frontend_achi_user_id__2b6e9a_idx'),
        ),
        migrations.AddIndex(
            model_name='achievement',
            index=models.Index(fields=['achievement_type'], name='frontend_achi_achievem_8c3f5d_idx'),
        ),
    ]
