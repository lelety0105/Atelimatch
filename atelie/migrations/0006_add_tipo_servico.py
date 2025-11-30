from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atelie', '0005_chatmensagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='tipo_servico',
            field=models.CharField(default='OUTROS', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pedido',
            name='status',
            field=models.CharField(default='AGUARDANDO_ORCAMENTO', max_length=20, choices=[
                ('AGUARDANDO_ORCAMENTO', 'Aguardando Orçamento'),
                ('AGUARDANDO_APROVACAO', 'Aguardando Aprovação'),
                ('ORCAMENTO_REPROVADO', 'Orçamento Reprovado'),
                ('AGUARDANDO_PAGAMENTO', 'Aguardando Pagamento'),
                ('EM_ANDAMENTO', 'Em Andamento'),
                ('AGUARDANDO_RETIRADA', 'Aguardando Retirada'),
                ('FINALIZADO', 'Finalizado'),
                ('CANCELADO', 'Cancelado'),
            ]),
        ),
    ]
