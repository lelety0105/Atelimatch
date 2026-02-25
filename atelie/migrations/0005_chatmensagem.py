from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atelie', '0004_alter_servico_options_alter_itempedido_servico_and_more'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMensagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conteudo', models.TextField(verbose_name='Mensagem')),
                ('lida_por_cliente', models.BooleanField(default=False, verbose_name='Lida pelo cliente')),
                ('lida_por_atelie', models.BooleanField(default=False, verbose_name='Lida pelo ateliê')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens', to='usuarios.customuser', verbose_name='Autor')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens', to='atelie.pedido', verbose_name='Pedido')),
            ],
            options={
                'verbose_name': 'Mensagem de Chat',
                'verbose_name_plural': 'Mensagens de Chat',
                'ordering': ['-criado_em'],
            },
        ),
    ]
