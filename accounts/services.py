from decimal import Decimal

def convert_to_metric(weight, weight_unit, height_cm=None, height_feet=None, height_inches=None, height_unit='cm'):
    """
    Converts weight to kg and height to cm if input in imperial units.
    """
    weight_kg = Decimal('0.0')
    if weight is not None:
        if weight_unit == 'lb':
            weight_kg = Decimal(str(weight)) * Decimal('0.45359237')
        else:
            weight_kg = Decimal(str(weight))
            
    height_final_cm = Decimal('0.0')
    if height_unit == 'ft_in':
        feet = Decimal(str(height_feet or 0))
        inches = Decimal(str(height_inches or 0))
        total_inches = (feet * Decimal('12')) + inches
        height_final_cm = total_inches * Decimal('2.54')
    else:
        if height_cm is not None:
            height_final_cm = Decimal(str(height_cm))
            
    return weight_kg, height_final_cm

def calculate_daily_targets(profile):
    """
    Calculates standard calorie and macro targets using Mifflin-St Jeor and activity levels.
    """
    if not profile.age or not profile.weight or (profile.height_unit == 'cm' and not profile.height) or (profile.height_unit == 'ft_in' and profile.height_feet is None):
        return {
            'bmr': 0,
            'tdee': 0,
            'calories': 2000,
            'protein': 150,
            'carbs': 250,
            'fat': 70
        }
        
    # 1. Convert to metric
    weight_kg, height_cm = convert_to_metric(
        weight=profile.weight,
        weight_unit=profile.weight_unit,
        height_cm=profile.height,
        height_feet=profile.height_feet,
        height_inches=profile.height_inches,
        height_unit=profile.height_unit
    )
    
    age = profile.age
    gender = profile.gender
    
    # 2. Calculate BMR (Mifflin-St Jeor)
    if gender == 'Male':
        bmr = Decimal('10') * weight_kg + Decimal('6.25') * height_cm - Decimal('5') * Decimal(str(age)) + Decimal('5')
    elif gender == 'Female':
        bmr = Decimal('10') * weight_kg + Decimal('6.25') * height_cm - Decimal('5') * Decimal(str(age)) - Decimal('161')
    else: # Other/Prefer not to say: average of male and female formula
        bmr = Decimal('10') * weight_kg + Decimal('6.25') * height_cm - Decimal('5') * Decimal(str(age)) - Decimal('78')
        
    # 3. Calculate target (multiplier = 1.0 as activity level is removed)
    tdee = bmr
    
    # 4. Adjust calories based on goal
    if profile.goal == 'Lose weight':
        calories = tdee - Decimal('500')
    elif profile.goal == 'Gain weight':
        calories = tdee + Decimal('500')
    else: # Maintain weight
        calories = tdee
        
    # Ensure calories is sensible
    calories = max(Decimal('1200'), calories)
    
    # 5. Distribute Macros (Standard Ratio: 30% Protein, 45% Carbs, 25% Fat)
    # Calories: Protein (4 kcal/g), Carbs (4 kcal/g), Fat (9 kcal/g)
    protein_g = (calories * Decimal('0.30')) / Decimal('4')
    carbs_g = (calories * Decimal('0.45')) / Decimal('4')
    fat_g = (calories * Decimal('0.25')) / Decimal('9')
    
    return {
        'bmr': int(round(bmr)),
        'tdee': int(round(tdee)),
        'calories': int(round(calories)),
        'protein': int(round(protein_g)),
        'carbs': int(round(carbs_g)),
        'fat': int(round(fat_g))
    }
