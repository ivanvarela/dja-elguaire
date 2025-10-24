"""
User Area Forms - Betting forms
"""
from django import forms
from core.models import BetPolla, BetEvento, BetMatch


class BetPollaForm(forms.ModelForm):
    """Form for placing a polla bet"""
    class Meta:
        model = BetPolla
        fields = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6']
        widgets = {
            'c1': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Caballo 1-20'}),
            'c2': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Caballo 1-20'}),
            'c3': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Caballo 1-20'}),
            'c4': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Caballo 1-20'}),
            'c5': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Caballo 1-20'}),
            'c6': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Caballo 1-20'}),
        }
        labels = {
            'c1': 'Carrera 1',
            'c2': 'Carrera 2',
            'c3': 'Carrera 3',
            'c4': 'Carrera 4',
            'c5': 'Carrera 5',
            'c6': 'Carrera 6',
        }


class BetEventoForm(forms.ModelForm):
    """Form for placing an evento bet"""
    class Meta:
        model = BetEvento
        fields = []  # We'll dynamically add match prediction fields

    def __init__(self, *args, **kwargs):
        self.evento = kwargs.pop('evento', None)
        self.matches = kwargs.pop('matches', [])
        super().__init__(*args, **kwargs)

        # Dynamically create fields for each match
        for match in self.matches:
            if self.evento.tipo_juego == 3:
                # NFL - Winner selection
                self.fields[f'match_{match.id}'] = forms.ChoiceField(
                    label=f'{match.team1.nombre} vs {match.team2.nombre}',
                    choices=[
                        ('E1', match.team1.nombre),
                        ('E2', match.team2.nombre),
                    ],
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )
            elif self.evento.tipo_juego in [5, 6]:
                # Soccer - Winner or Tie
                self.fields[f'match_{match.id}'] = forms.ChoiceField(
                    label=f'{match.team1.nombre} vs {match.team2.nombre}',
                    choices=[
                        ('E1', match.team1.nombre),
                        ('TIE', 'Empate'),
                        ('E2', match.team2.nombre),
                    ],
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )
            else:
                # Score prediction
                self.fields[f'match_{match.id}_score1'] = forms.IntegerField(
                    label=match.team1.nombre,
                    min_value=0,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px; display: inline-block;'})
                )
                self.fields[f'match_{match.id}_score2'] = forms.IntegerField(
                    label=match.team2.nombre,
                    min_value=0,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px; display: inline-block;'})
                )

    def save_match_predictions(self, bet):
        """Save match predictions after bet is created"""
        for match in self.matches:
            if self.evento.tipo_juego == 3:
                # NFL - Convert winner selection to scores
                winner = self.cleaned_data.get(f'match_{match.id}')
                if winner == 'E1':
                    score1, score2 = 1, 0
                else:
                    score1, score2 = 0, 1
            elif self.evento.tipo_juego in [5, 6]:
                # Soccer - Convert selection to scores
                result = self.cleaned_data.get(f'match_{match.id}')
                if result == 'E1':
                    score1, score2 = 1, 0
                elif result == 'TIE':
                    score1, score2 = 1, 1
                else:
                    score1, score2 = 0, 1
            else:
                # Direct score entry
                score1 = self.cleaned_data.get(f'match_{match.id}_score1')
                score2 = self.cleaned_data.get(f'match_{match.id}_score2')

            BetMatch.objects.create(
                bet_evento=bet,
                match=match,
                score_team1=score1,
                score_team2=score2
            )
