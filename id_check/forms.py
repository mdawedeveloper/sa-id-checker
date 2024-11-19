import datetime
from django import forms

class IDForm(forms.Form):
    id_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your SA ID Number'}),
    )

    def clean_id_number(self):
        id_number = str(self.cleaned_data['id_number']).strip()  # Ensure it's a string
        
        # 1. Checking if the ID number is numeric and has 13 digits
        if not id_number.isdigit() or len(id_number) != 13:
            raise forms.ValidationError("Invalid ID number. Must be 13 numeric digits.")
        
        # 2. Extracting and validating the date of birth (first 6 digits)
        dob = id_number[:6]  # YYMMDD
        try:
            # Ensuring that dob is a valid string and formatted as date (YYMMDD)
            birth_date = datetime.datetime.strptime(dob, "%y%m%d").date()
        except ValueError:
            raise forms.ValidationError("Invalid date of birth in ID number.")
        
        # Ensuring birth date is not in the future
        if birth_date > datetime.date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        
        # 3. Extracting gender from the SSSS digits (7th-10th digits)
        gender_code = int(id_number[6:10])
        gender = "Female" if gender_code < 5000 else "Male"
        
        # 4. Extracting SA citizenship status (11th digit)
        citizenship_code = id_number[10]
        citizenship_status = (
            "SA Citizen" if citizenship_code == "0" else "Permanent Resident"
        )
        
        # 5. Validating checksum using the Luhn algorithm
        if not self.is_valid_luhn(id_number):
            raise forms.ValidationError("Invalid checksum in ID number.")
        
        # Returning cleaned data with additional info for use in views
        return {
            "id_number": id_number,
            "birth_date": birth_date,
            "gender": gender,
            "citizenship_status": citizenship_status,
        }

    def is_valid_luhn(self, id_number):
        """
        Validates an ID number using the Luhn algorithm.

        Args:
          id_number (str): The ID number to validate.

        Returns:
          bool: True if the ID number is valid, False otherwise.
        """
        # Removing all non-numeric characters and make sure it's a string.
        digits = "".join([char for char in str(id_number) if char.isdigit()])

        # Checking for empty or invalid input.
        if not digits or len(digits) != 13:
            return False

        # Double every other digit, starting from the second-to-last.
        doubled_digits = [int(digit) * 2 if i % 2 else int(digit) for i, digit in enumerate(digits[::-1])]

        # Subtracting 9 from any digit greater than 9.
        doubled_digits = [digit - 9 if digit > 9 else digit for digit in doubled_digits]

        # Sum all the digits.
        sum_of_digits = sum(doubled_digits)

        # Checking if the sum is a multiple of 10.
        return sum_of_digits % 10 == 0





