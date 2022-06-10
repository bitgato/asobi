from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from .models import *


class StartGameForm(forms.Form):
    # here, gc = game_code
    gc = forms.CharField(
        max_length=Game.GC_LEN,
        label='Game code',
        required=False,
        help_text='Leave empty to create new game'
    )

    def __init__(self, *args, **kwargs):
        super(StartGameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class StartTicTacToeForm(StartGameForm):
    n = forms.IntegerField(
        min_value=3,
        label='Rows',
        required=False,
        help_text='Leave empty to create 3x3 box',
    )

    class Meta:
        fields = ['gc', 'n']

    def __init__(self, *args, **kwargs):
        super(StartTicTacToeForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div('gc', css_class='col-sm-8'),
                Div('n', css_class='col-sm-4'),
                css_class='row'
            ),
        )


class StartObstructionForm(StartGameForm):
    rows = forms.IntegerField(
        min_value=6,
        label='Rows',
        required=False,
        help_text='Leave empty for 6 rows',
    )
    cols = forms.IntegerField(
        min_value=6,
        label='Columns',
        required=False,
        help_text='Leave empty for 6 columns',
    )

    class Meta:
        fields = ['gc', 'rows', 'cols']

    def __init__(self, *args, **kwargs):
        super(StartObstructionForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div('gc', css_class='col-sm-8'),
                Div('rows', css_class='col-sm-2'),
                Div('cols', css_class='col-sm-2'),
                css_class='row'
            ),
        )


class StartLudoForm(StartGameForm):
    players = forms.IntegerField(
        min_value=2,
        max_value=4,
        label='Number of players',
        required=False,
        help_text='Leave empty for 4 players'
    )

    class Meta:
        fields = ['gc', 'players']

    def __init__(self, *args, **kwargs):
        super(StartLudoForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div('gc', css_class='col-sm-8'),
                Div('players', css_class='col-sm-4'),
                css_class='row'
            ),
        )


class StartBattleShipForm(StartGameForm):
    pass


class StartConnect4Form(StartGameForm):
    CHOICES = [
        ('7x6', '7x6'),
        ('5x4', '5x4'),
        ('6x5', '6x5'),
        ('8x7', '8x7'),
        ('9x7', '9x7'),
        ('10x7', '10x7'),
        ('8x8', '8x8'),
    ]
    size = forms.ChoiceField(choices=CHOICES)

    class Meta:
        fields = ['gc', 'size']

    def __init__(self, *args, **kwargs):
        super(StartConnect4Form, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div('gc', css_class='col-sm-8'),
                Div(Field('size', css_class='form-control'), css_class='col-sm-4'),
                css_class='row'
            )
        )


class StartOthelloForm(StartGameForm):
    pass
