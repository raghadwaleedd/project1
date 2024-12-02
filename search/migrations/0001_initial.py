# Generated by Django 5.1.2 on 2024-11-29 12:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Search",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("query_text", models.TextField()),
                ("query_time", models.DateTimeField(auto_now_add=True)),
                ("response_time", models.DurationField(blank=True, null=True)),
                ("response_text", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="searches",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Search",
                "verbose_name_plural": "User Searches",
                "db_table": "user_searches",
                "ordering": ["-query_time"],
                "permissions": [("can_view_all_searches", "Can view all searches")],
                "indexes": [
                    models.Index(
                        fields=["user", "query_time"],
                        name="user_search_user_id_4cbf35_idx",
                    )
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("query_time__isnull", False)),
                        name="query_time_present",
                    )
                ],
                "unique_together": {("user", "query_text")},
            },
        ),
    ]
