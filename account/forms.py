from django import forms
from groups.models import Group

class GroupSelectionForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.none(), label="Выберите группу")

    def __init__(self, *args, account=None, **kwargs):
        super().__init__(*args, **kwargs)
        if account:
            self.fields['group'].queryset = Group.objects.filter(account=account)