# Generated by Django 2.2.28 on 2023-07-15 14:07

from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20230713_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='专题名称')),
                ('status', models.CharField(choices=[('not_started', '未开始'), ('ongoing', '连载中'), ('completed', '已完结')], default='not_started', max_length=20, verbose_name='状态')),
                ('description', models.CharField(max_length=250, verbose_name='描述')),
                ('sort_order', models.IntegerField(default=99, help_text='作为专题列表页的排序', verbose_name='排序')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('cover_image', imagekit.models.fields.ProcessedImageField(default='subject/default/default.png', help_text='上传图片大小建议使用5:3的宽高比，为了清晰度原始图片宽度应该超过250px', upload_to='subject/upload/%Y/%m/%d/', verbose_name='封面图')),
            ],
            options={
                'verbose_name': '专题',
                'verbose_name_plural': '专题',
                'ordering': ['-create_date'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='topic_order',
            field=models.IntegerField(blank=True, default=99, help_text='仅作为文章在主题中的排序', null=True, verbose_name='主题中排序'),
        ),
        migrations.AddField(
            model_name='article',
            name='topic_short_title',
            field=models.CharField(blank=True, help_text='专门给Topic使用的短标题', max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='主题名称')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('sort_order', models.IntegerField(default=99, help_text='仅作为主题在专题中的排序，类似目录', verbose_name='排序')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='topics', to='blog.Subject', verbose_name='所属专题')),
            ],
            options={
                'verbose_name': '专题-主题',
                'verbose_name_plural': '专题-主题',
                'ordering': ['-create_date'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='blog.Topic', verbose_name='所属主题'),
        ),
    ]
