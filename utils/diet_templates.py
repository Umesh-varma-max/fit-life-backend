# utils/diet_templates.py
"""
Pre-defined meal templates per goal and food preference.
Keys: low_cal, high_protein, balanced
Sub-keys: non-veg, veg, vegan
Each meal: {meal: name, kcal: calories}
"""

DIET_TEMPLATES = {
    'low_cal': {
        'non-veg': {
            'breakfast': {'meal': 'Oats with banana + green tea', 'kcal': 380},
            'lunch':     {'meal': 'Grilled chicken salad + whole wheat roti', 'kcal': 550},
            'snack':     {'meal': 'Mixed nuts + apple', 'kcal': 180},
            'dinner':    {'meal': 'Steamed fish + stir-fried vegetables', 'kcal': 450}
        },
        'veg': {
            'breakfast': {'meal': 'Upma + green tea', 'kcal': 320},
            'lunch':     {'meal': 'Dal + brown rice + salad', 'kcal': 500},
            'snack':     {'meal': 'Sprout chaat', 'kcal': 160},
            'dinner':    {'meal': 'Vegetable soup + whole wheat bread', 'kcal': 380}
        },
        'vegan': {
            'breakfast': {'meal': 'Smoothie bowl (oat milk + berries)', 'kcal': 340},
            'lunch':     {'meal': 'Quinoa salad + chickpeas', 'kcal': 480},
            'snack':     {'meal': 'Apple + almond butter', 'kcal': 190},
            'dinner':    {'meal': 'Lentil soup + rye bread', 'kcal': 400}
        },
        'keto': {
            'breakfast': {'meal': 'Scrambled eggs + avocado', 'kcal': 400},
            'lunch':     {'meal': 'Grilled paneer + cucumber salad', 'kcal': 450},
            'snack':     {'meal': 'Cheese cubes + walnuts', 'kcal': 200},
            'dinner':    {'meal': 'Butter chicken (no rice) + salad', 'kcal': 480}
        },
        'paleo': {
            'breakfast': {'meal': 'Boiled eggs + sweet potato', 'kcal': 360},
            'lunch':     {'meal': 'Grilled chicken + mixed vegetables', 'kcal': 520},
            'snack':     {'meal': 'Fresh fruits + almonds', 'kcal': 170},
            'dinner':    {'meal': 'Baked fish + roasted veggies', 'kcal': 440}
        }
    },
    'high_protein': {
        'non-veg': {
            'breakfast': {'meal': 'Egg white omelette + whole wheat toast', 'kcal': 420},
            'lunch':     {'meal': 'Chicken breast + sweet potato + broccoli', 'kcal': 650},
            'snack':     {'meal': 'Protein shake + banana', 'kcal': 300},
            'dinner':    {'meal': 'Salmon + brown rice + asparagus', 'kcal': 680}
        },
        'veg': {
            'breakfast': {'meal': 'Paneer scramble + multigrain toast', 'kcal': 440},
            'lunch':     {'meal': 'Rajma + brown rice + curd', 'kcal': 620},
            'snack':     {'meal': 'Roasted chana + nuts', 'kcal': 280},
            'dinner':    {'meal': 'Tofu stir-fry + quinoa', 'kcal': 580}
        },
        'vegan': {
            'breakfast': {'meal': 'Soy milk smoothie + oats + seeds', 'kcal': 400},
            'lunch':     {'meal': 'Chickpea curry + brown rice', 'kcal': 600},
            'snack':     {'meal': 'Edamame + mixed nuts', 'kcal': 260},
            'dinner':    {'meal': 'Lentil dal + quinoa + greens', 'kcal': 550}
        },
        'keto': {
            'breakfast': {'meal': '3-egg omelette + cheese + spinach', 'kcal': 480},
            'lunch':     {'meal': 'Tandoori chicken + raita', 'kcal': 600},
            'snack':     {'meal': 'Protein shake (unsweetened)', 'kcal': 250},
            'dinner':    {'meal': 'Mutton curry + cauliflower rice', 'kcal': 620}
        },
        'paleo': {
            'breakfast': {'meal': 'Eggs + turkey bacon + avocado', 'kcal': 500},
            'lunch':     {'meal': 'Grilled fish + baked sweet potato', 'kcal': 620},
            'snack':     {'meal': 'Beef jerky + macadamia nuts', 'kcal': 280},
            'dinner':    {'meal': 'Roasted chicken + roasted vegetables', 'kcal': 650}
        }
    },
    'balanced': {
        'non-veg': {
            'breakfast': {'meal': 'Poha + boiled egg + tea', 'kcal': 400},
            'lunch':     {'meal': 'Chicken curry + rice + salad', 'kcal': 600},
            'snack':     {'meal': 'Fruit bowl + yogurt', 'kcal': 200},
            'dinner':    {'meal': 'Dal + roti + sautéed veggies', 'kcal': 550}
        },
        'veg': {
            'breakfast': {'meal': 'Idli + sambar + coconut chutney', 'kcal': 350},
            'lunch':     {'meal': 'Mixed dal + rice + papad + salad', 'kcal': 560},
            'snack':     {'meal': 'Makhana + green tea', 'kcal': 150},
            'dinner':    {'meal': 'Paneer curry + roti', 'kcal': 520}
        },
        'vegan': {
            'breakfast': {'meal': 'Poha + coconut milk tea', 'kcal': 340},
            'lunch':     {'meal': 'Rajma + rice + salad', 'kcal': 550},
            'snack':     {'meal': 'Fruit smoothie (oat milk)', 'kcal': 180},
            'dinner':    {'meal': 'Mixed vegetable curry + roti', 'kcal': 480}
        },
        'keto': {
            'breakfast': {'meal': 'Cheese omelette + bulletproof coffee', 'kcal': 450},
            'lunch':     {'meal': 'Grilled fish + salad + olive oil dressing', 'kcal': 550},
            'snack':     {'meal': 'Dark chocolate + almonds', 'kcal': 200},
            'dinner':    {'meal': 'Palak paneer + cauliflower rice', 'kcal': 500}
        },
        'paleo': {
            'breakfast': {'meal': 'Scrambled eggs + fruit plate', 'kcal': 380},
            'lunch':     {'meal': 'Grilled chicken + sweet potato mash', 'kcal': 580},
            'snack':     {'meal': 'Trail mix (no peanuts)', 'kcal': 200},
            'dinner':    {'meal': 'Baked fish + steamed vegetables', 'kcal': 500}
        }
    }
}
