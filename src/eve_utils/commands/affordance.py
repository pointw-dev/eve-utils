import os
import click

@click.group(name='affordance', help='Manage link rels that operate on the state of resources.')
def commands():
    pass

@commands.command(name='create', help='(not yet implemented)')
def create():
    click.echo(f'create')


@commands.command(name='list', help='(not yet implemented)')
def list_affordances():
    click.echo('list')


@commands.command(name='remove', help='(not yet implemented)')
def remove():
    click.echo('remove')
