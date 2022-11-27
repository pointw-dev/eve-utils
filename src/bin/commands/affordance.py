import os
import click

@click.group(name='affordance')
def commands():
    pass

@commands.command(name='create')
def create():
    click.echo(f'create')


@commands.command(name='list')
def list():
    click.echo('list')


@commands.command(name='remove')
def remove():
    click.echo('remove')
