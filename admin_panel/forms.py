"""
Admin Panel Forms
"""
from django import forms
from core.models import Polla, Evento, Match, Racetrack, League, Team


class PollaForm(forms.ModelForm):
    """Form for creating/editing pollas"""
    class Meta:
        model = Polla
        fields = ['code4', 'racetrack', 'date_race', 'price_entry']
        widgets = {
            'code4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código (ej: GUY123)'}),
            'racetrack': forms.Select(attrs={'class': 'form-select'}),
            'date_race': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'price_entry': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class EventoForm(forms.ModelForm):
    """Form for creating/editing eventos"""
    class Meta:
        model = Evento
        fields = ['code4', 'league', 'name', 'date', 'price_entry', 'tipo_juego']
        widgets = {
            'code4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código (ej: NFL2024)'}),
            'league': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del evento'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'price_entry': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo_juego': forms.Select(attrs={'class': 'form-select'}, choices=[
                (1, 'Predicción de Marcadores'),
                (3, 'NFL - Ganador'),
                (5, 'Soccer - Ganador o Empate'),
                (6, 'Soccer - Ganador o Empate (Alt)'),
            ]),
        }


class MatchForm(forms.ModelForm):
    """Form for adding matches to an evento"""
    class Meta:
        model = Match
        fields = ['team1', 'team2', 'orden_pa', 'date']
        widgets = {
            'team1': forms.Select(attrs={'class': 'form-select'}),
            'team2': forms.Select(attrs={'class': 'form-select'}),
            'orden_pa': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        evento = kwargs.pop('evento', None)
        super().__init__(*args, **kwargs)

        if evento:
            # Filter teams by league
            self.fields['team1'].queryset = Team.objects.filter(league=evento.league)
            self.fields['team2'].queryset = Team.objects.filter(league=evento.league)

            # Set next orden_pa
            last_match = evento.matches.order_by('-orden_pa').first()
            if last_match:
                self.fields['orden_pa'].initial = last_match.orden_pa + 1
            else:
                self.fields['orden_pa'].initial = 1

            self.instance.evento = evento


class ResultPollaForm(forms.ModelForm):
    """Form for entering polla results"""
    class Meta:
        model = Polla
        fields = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6']
        widgets = {
            'f1': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Carrera 1'}),
            'f2': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Carrera 2'}),
            'f3': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Carrera 3'}),
            'f4': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Carrera 4'}),
            'f5': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Carrera 5'}),
            'f6': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Carrera 6'}),
        }
        labels = {
            'f1': 'Ganador Carrera 1',
            'f2': 'Ganador Carrera 2',
            'f3': 'Ganador Carrera 3',
            'f4': 'Ganador Carrera 4',
            'f5': 'Ganador Carrera 5',
            'f6': 'Ganador Carrera 6',
        }


class ResultEventoForm(forms.Form):
    """Form for entering evento match results (dynamically generated)"""
    pass
