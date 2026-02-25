from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('atelie', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, verbose_name='Descricao')),
                ('preco_base', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Preco Base')),
                ('duracao_estimada', models.IntegerField(blank=True, help_text='Informe em minutos (opcional)', null=True, verbose_name='Duracao Estimada (minutos)')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Servico',
                'verbose_name_plural': 'Servicos',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.AddField(
            model_name='pedido',
            name='data_agendada',
            field=models.DateField(blank=True, null=True, verbose_name='Data do Agendamento'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='hora_agendada',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora do Agendamento'),
        ),
        migrations.AlterField(
            model_name='itempedido',
            name='produto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='itens_pedido', to='atelie.produto', verbose_name='Produto'),
        ),
        migrations.AddField(
            model_name='itempedido',
            name='servico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='itens_servico', to='atelie.servico', verbose_name='Servico'),
        ),
    ]
