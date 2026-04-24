# Generated manually to fix database schema

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='target_weight',
            field=models.FloatField(blank=True, help_text='Target weight in kg', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='activity_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('sedentary', 'Sedentary (little or no exercise)'),
                    ('light', 'Light (1-3 days/week)'),
                    ('moderate', 'Moderate (3-5 days/week)'),
                    ('active', 'Active (6-7 days/week)'),
                    ('very_active', 'Very Active (twice per day)')
                ],
                max_length=50,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='workout_duration',
            field=models.IntegerField(blank=True, help_text='Preferred workout duration in minutes', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='workout_types',
            field=models.JSONField(blank=True, help_text='List of preferred workout types', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='dietary_preferences',
            field=models.JSONField(blank=True, help_text='List of dietary preferences', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='allergies',
            field=models.JSONField(blank=True, help_text='List of food allergies', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='medical_conditions',
            field=models.JSONField(blank=True, help_text='List of medical conditions', null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(
                blank=True,
                choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                max_length=10,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='onboarding_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='onboarding_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
            ]
