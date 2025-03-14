import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import dropbox
import requests
import atexit
import re
import ttkbootstrap as ttkb

app_key = "YOUR APP KEY HERE"
app_secret = "YOUR APP SECRET HERE"
refresh_token = "YOUR REFRESH TOKEN HERE"
access_token = None

dbx = None
csv_file_path = ""

def refresh_access_token():
    global access_token
    url = 'https://api.dropbox.com/oauth2/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': app_key,
        'client_secret': app_secret,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        print("Access token refreshed successfully!")
        return access_token
    else:
        print(f"Error refreshing token: {response.text}")
        return None

def initialize_dropbox():
    global dbx
    access_token = refresh_access_token()
    if access_token:
        dbx = dropbox.Dropbox(access_token)
    else:
        print("Failed to initialize Dropbox.")

def download_recipes_from_dropbox():
    global csv_file_path
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_dir, 'recipes.csv')
        dbx.files_download_to_file(csv_file_path, '/recipes.csv')
        print("Recipes downloaded successfully from Dropbox.")
    except Exception as e:
        print(f"Error downloading recipes from Dropbox: {e}")

def upload_recipes_to_dropbox():
    try:
        with open(csv_file_path, 'rb') as f:
            dbx.files_upload(f.read(), '/recipes.csv', mode=dropbox.files.WriteMode.overwrite)
        print("Recipes uploaded successfully to Dropbox.")

        os.remove(csv_file_path)
        print("Local recipes.csv file deleted successfully.")
    except Exception as e:
        print(f"Error uploading recipes to Dropbox or deleting local file: {e}")

def open_new_recipe_window():
    new_recipe_window = ttkb.Toplevel(title="Add new recipe")

    ttkb.Label(new_recipe_window, text="Recipe name:").grid(row=0, column=0, padx=10, pady=10)
    recipe_name_entry = ttkb.Entry(new_recipe_window, width=30)
    recipe_name_entry.grid(row=0, column=1, padx=10, pady=10)

    seuraava_button = ttkb.Button(new_recipe_window, text="Next", command=lambda: check_recipe_name(new_recipe_window, recipe_name_entry.get()))
    seuraava_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

def check_recipe_name(new_recipe_window, recipe_name):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csvFile = csv.reader(file)
        next(csvFile)  
        for lines in csvFile:
            if lines[0].lower() == recipe_name.lower():
                messagebox.showerror("Error", "Recipe with name '{0}' already exists.".format(recipe_name))
                return

    ttkb.Label(new_recipe_window, text="Servings:").grid(row=2, column=0, padx=10, pady=10)
    servings_entry = ttkb.Entry(new_recipe_window, width=30)
    servings_entry.grid(row=2, column=1, padx=10, pady=10)
    servings_entry.config(validate="key", validatecommand=(new_recipe_window.register(validate_numeric), "%P"))

    vegaaninen_var = tk.StringVar(value="No")
    laktoositon_var = tk.StringVar(value="No")
    alkuruoka_var = tk.StringVar(value="No")
    paaruoka_var = tk.StringVar(value="No")
    jalkiruoka_var = tk.StringVar(value="No")

    vegaaninen_check = ttkb.Checkbutton(new_recipe_window, text="Vegan", variable=vegaaninen_var, onvalue="Yes", offvalue="No")
    vegaaninen_check.grid(row=3, column=0, padx=10, pady=5)

    laktoositon_check = ttkb.Checkbutton(new_recipe_window, text="Lactose free", variable=laktoositon_var, onvalue="Yes", offvalue="No")
    laktoositon_check.grid(row=3, column=1, padx=10, pady=5)

    alkuruoka_check = ttkb.Checkbutton(new_recipe_window, text="Appetizer", variable=alkuruoka_var, onvalue="Yes", offvalue="No")
    alkuruoka_check.grid(row=4, column=0, padx=10, pady=5)

    paaruoka_check = ttkb.Checkbutton(new_recipe_window, text="Main", variable=paaruoka_var, onvalue="Yes", offvalue="No")
    paaruoka_check.grid(row=4, column=1, padx=10, pady=5)

    jalkiruoka_check = ttkb.Checkbutton(new_recipe_window, text="Dessert", variable=jalkiruoka_var, onvalue="Yes", offvalue="No")
    jalkiruoka_check.grid(row=5, column=0, padx=10, pady=5)

    seuraava_button = ttkb.Button(new_recipe_window, text="Next", command=lambda: add_ingredients(new_recipe_window, recipe_name, servings_entry.get(), vegaaninen_var.get(), laktoositon_var.get(), alkuruoka_var.get(), paaruoka_var.get(), jalkiruoka_var.get()))
    seuraava_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

def validate_numeric(P):
    if P.isdigit() or P == "":
        return True
    else:
        return False

def add_ingredients(new_recipe_window, recipe_name, servings, vegaaninen, laktoositon, alkuruoka, paaruoka, jalkiruoka):
    new_recipe_window.destroy()

    ingredients_window = ttkb.Toplevel(title="Add ingredients")

    ingredient_entries = []
    amount_entries = []

    def add_more_ingredients():
        row = len(ingredient_entries) + 5
        ttkb.Label(ingredients_window, text=f"Ingredient {row-4}:").grid(row=row, column=0, padx=10, pady=5)
        ingredient_entry = ttkb.Entry(ingredients_window, width=30)
        ingredient_entry.grid(row=row, column=1, padx=10, pady=5)
        ingredient_entries.append(ingredient_entry)

        ttkb.Label(ingredients_window, text="Amount:").grid(row=row, column=2, padx=10, pady=5)
        amount_entry = ttkb.Entry(ingredients_window, width=10)
        amount_entry.grid(row=row, column=3, padx=10, pady=5)
        amount_entries.append(amount_entry)

    for i in range(10):  
        ttkb.Label(ingredients_window, text=f"Ingredient {i+1}:").grid(row=i, column=0, padx=10, pady=5)
        ingredient_entry = ttkb.Entry(ingredients_window, width=30)
        ingredient_entry.grid(row=i, column=1, padx=10, pady=5)
        ingredient_entries.append(ingredient_entry)

        ttkb.Label(ingredients_window, text="Amount:").grid(row=i, column=2, padx=10, pady=5)
        amount_entry = ttkb.Entry(ingredients_window, width=10)
        amount_entry.grid(row=i, column=3, padx=10, pady=5)
        amount_entries.append(amount_entry)

    add_more_button = ttkb.Button(ingredients_window, text="Add ingredient", command=add_more_ingredients)
    add_more_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

    tallenna_button = ttkb.Button(ingredients_window, text="Save", command=lambda: save_new_recipe(ingredients_window, recipe_name, servings, ingredient_entries, amount_entries, vegaaninen, laktoositon, alkuruoka, paaruoka, jalkiruoka))
    tallenna_button.grid(row=12, column=0, columnspan=4, padx=10, pady=10)

def save_new_recipe(ingredients_window, recipe_name, servings, ingredient_entries, amount_entries, vegaaninen, laktoositon, alkuruoka, paaruoka, jalkiruoka):
    ingredients = []
    for ingredient_entry, amount_entry in zip(ingredient_entries, amount_entries):
        ingredient = ingredient_entry.get().strip()
        amount = amount_entry.get().strip()
        if ingredient and amount:
            ingredients.append(f"{ingredient}_{amount}")

    ingredients_str = ";".join(ingredients)

    with open(csv_file_path, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([recipe_name, servings, ingredients_str, vegaaninen, laktoositon, alkuruoka, paaruoka, jalkiruoka])

    messagebox.showinfo("Saved", "New recipe saved succesfully!")
    ingredients_window.destroy()

def scale_ingredient(ingredient, scaling_factor):
    match = re.match(r"(.*?)(\d+(\.\d+)?)\s*(.*)", ingredient)
    if match:
        name_part = match.group(1).strip()
        amount_part = float(match.group(2))
        unit_part = match.group(4).strip()

        new_amount = amount_part * scaling_factor
        if new_amount.is_integer():
            new_amount = int(new_amount)
        else:
            new_amount = round(new_amount, 2)

        return f"{name_part}{new_amount} {unit_part}"
    return ingredient

def search_recipes():
    inp = entry.get().lower()
    try:
        desired_servings = int(servings_entry.get())
    except ValueError:
        desired_servings = 0

    reseptit = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csvFile = csv.reader(file)
        next(csvFile)  
        for lines in csvFile:
            matches_vegaaninen = vegaaninen_var.get() == "No" or lines[3].lower() == "yes"
            matches_laktoositon = laktoositon_var.get() == "No" or lines[4].lower() == "yes"
            matches_alkuruoka = alkuruoka_var.get() == "No" or lines[5].lower() == "yes"
            matches_paaruoka = paaruoka_var.get() == "No" or lines[6].lower() == "yes"
            matches_jalkiruoka = jalkiruoka_var.get() == "No" or lines[7].lower() == "yes"
            if (inp in lines[2].lower() or inp in lines[0].lower()) and matches_vegaaninen and matches_laktoositon and matches_alkuruoka and matches_paaruoka and matches_jalkiruoka:
                reseptit.append(lines)

    for widget in result_frame.winfo_children():
        widget.destroy()

    result_text = f"Found {len(reseptit)} recipes\n"
    ttkb.Label(result_frame, text=result_text, font=('Helvetica', 12)).pack(anchor='w')

    for i in reseptit:
        recipe_name = i[0]
        original_servings = int(i[1])
        final_servings = desired_servings if desired_servings > 0 else original_servings
        scaling_factor = final_servings / original_servings
        scaled_ingredients = []

        for ingredient in i[2].split(';'):
            scaled_ingredient = scale_ingredient(ingredient, scaling_factor)
            scaled_ingredients.append(scaled_ingredient)

        recipe_text = f"{recipe_name}\n"
        recipe_text += f"Servings: {final_servings}\n"
        recipe_text += "Ingredients:\n"
        recipe_text += "\n".join([f"- {ingredient.replace('_', ' ')}" for ingredient in scaled_ingredients])

        frame = ttkb.Frame(result_frame)
        frame.pack(anchor='w', pady=5)

        label = ttkb.Label(frame, text=recipe_text, anchor="w", justify="left", font=('Helvetica', 12))
        label.pack(anchor="w")

        copy_button = ttkb.Button(frame, text="Copy", command=lambda rt=recipe_text: copy_to_clipboard(rt))
        copy_button.pack(side='left', padx=5)

        edit_button = ttkb.Button(frame, text="Edit", command=lambda rn=recipe_name: open_edit_recipe_window(rn))
        edit_button.pack(side='left', padx=5)

    result_canvas.update_idletasks()
    result_canvas.config(scrollregion=result_canvas.bbox("all"))

def copy_to_clipboard(recipe_text):
    pyperclip.copy(recipe_text)
    print("Recipe copied to clipboard!")

def on_mouse_wheel(event):
    result_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def open_delete_recipe_window():
    delete_recipe_window = ttkb.Toplevel(title="Delete recipe")

    ttkb.Label(delete_recipe_window, text="Select recipe to delete:").grid(row=0, column=0, padx=10, pady=10)

    recipes = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csvFile = csv.reader(file)
        next(csvFile)  
        for lines in csvFile:
            recipes.append(lines[0])

    if not recipes:
        messagebox.showinfo("Info", "No recipes to delete.")
        delete_recipe_window.destroy()
        return

    selected_recipe = tk.StringVar()
    recipe_dropdown = ttkb.Combobox(delete_recipe_window, textvariable=selected_recipe)
    recipe_dropdown['values'] = recipes
    recipe_dropdown.grid(row=0, column=1, padx=10, pady=10)
    recipe_dropdown.current(0)  

    poista_button = ttkb.Button(delete_recipe_window, text="Delete", command=lambda: delete_recipe(selected_recipe.get(), delete_recipe_window))
    poista_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

def delete_recipe(recipe_name, delete_recipe_window):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csvFile = csv.reader(file)
        lines = list(csvFile)

    found = False
    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for line in lines:
            if line[0].lower() != recipe_name.lower():
                writer.writerow(line)
            else:
                found = True

    if found:
        messagebox.showinfo("Deleted", f"Recipe '{recipe_name}' succesfully deleted!")
    else:
        messagebox.showerror("Error", f"Recipe with the name '{recipe_name}' not found.")

    delete_recipe_window.destroy()

def open_edit_recipe_window(recipe_name):
    edit_recipe_window = ttkb.Toplevel(title="Edit recipe")

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csvFile = csv.reader(file)
        next(csvFile)  
        for lines in csvFile:
            if lines[0].lower() == recipe_name.lower():
                recipe_data = lines
                break

    recipe_name_entry = ttkb.Entry(edit_recipe_window, width=30)
    recipe_name_entry.insert(0, recipe_data[0])
    recipe_name_entry.grid(row=0, column=1, padx=10, pady=10)

    servings_entry = ttkb.Entry(edit_recipe_window, width=30)
    servings_entry.insert(0, recipe_data[1])
    servings_entry.grid(row=1, column=1, padx=10, pady=10)

    vegaaninen_var = tk.StringVar(value=recipe_data[3])
    laktoositon_var = tk.StringVar(value=recipe_data[4])
    alkuruoka_var = tk.StringVar(value=recipe_data[5])
    paaruoka_var = tk.StringVar(value=recipe_data[6])
    jalkiruoka_var = tk.StringVar(value=recipe_data[7])

    vegaaninen_check = ttkb.Checkbutton(edit_recipe_window, text="Vegan", variable=vegaaninen_var, onvalue="Yes", offvalue="No")
    vegaaninen_check.grid(row=2, column=0, padx=10, pady=5)

    laktoositon_check = ttkb.Checkbutton(edit_recipe_window, text="Lactose free", variable=laktoositon_var, onvalue="Yes", offvalue="No")
    laktoositon_check.grid(row=2, column=1, padx=10, pady=5)

    alkuruoka_check = ttkb.Checkbutton(edit_recipe_window, text="Appetizer", variable=alkuruoka_var, onvalue="Yes", offvalue="No")
    alkuruoka_check.grid(row=3, column=0, padx=10, pady=5)

    paaruoka_check = ttkb.Checkbutton(edit_recipe_window, text="Main", variable=paaruoka_var, onvalue="Yes", offvalue="No")
    paaruoka_check.grid(row=3, column=1, padx=10, pady=5)

    jalkiruoka_check = ttkb.Checkbutton(edit_recipe_window, text="Dessert", variable=jalkiruoka_var, onvalue="Yes", offvalue="No")
    jalkiruoka_check.grid(row=4, column=0, padx=10, pady=5)

    ingredient_entries = []
    amount_entries = []

    ingredients = recipe_data[2].split(';')
    for i, ingredient in enumerate(ingredients):
        name, amount = ingredient.split('_')
        ttkb.Label(edit_recipe_window, text=f"Ingredient {i+1}:").grid(row=i+5, column=0, padx=10, pady=5)
        ingredient_entry = ttkb.Entry(edit_recipe_window, width=30)
        ingredient_entry.insert(0, name)
        ingredient_entry.grid(row=i+5, column=1, padx=10, pady=5)
        ingredient_entries.append(ingredient_entry)

        ttkb.Label(edit_recipe_window, text="Amount:").grid(row=i+5, column=2, padx=10, pady=5)
        amount_entry = ttkb.Entry(edit_recipe_window, width=10)
        amount_entry.insert(0, amount)
        amount_entry.grid(row=i+5, column=3, padx=10, pady=5)
        amount_entries.append(amount_entry)

    def add_more_ingredients():
        row = len(ingredient_entries) + 5
        ttkb.Label(edit_recipe_window, text=f"Ingredient {row-4}:").grid(row=row, column=0, padx=10, pady=5)
        ingredient_entry = ttkb.Entry(edit_recipe_window, width=30)
        ingredient_entry.grid(row=row, column=1, padx=10, pady=5)
        ingredient_entries.append(ingredient_entry)

        ttkb.Label(edit_recipe_window, text="Amount:").grid(row=row, column=2, padx=10, pady=5)
        amount_entry = ttkb.Entry(edit_recipe_window, width=10)
        amount_entry.grid(row=row, column=3, padx=10, pady=5)
        amount_entries.append(amount_entry)

    add_more_button = ttkb.Button(edit_recipe_window, text="Add ingredient", command=add_more_ingredients)
    add_more_button.grid(row=len(ingredients)+5, column=0, columnspan=2, padx=10, pady=10)

    tallenna_button = ttkb.Button(edit_recipe_window, text="Save", command=lambda: save_edited_recipe(edit_recipe_window, recipe_name, recipe_name_entry.get(), servings_entry.get(), ingredient_entries, amount_entries, vegaaninen_var.get(), laktoositon_var.get(), alkuruoka_var.get(), paaruoka_var.get(), jalkiruoka_var.get()))
    tallenna_button.grid(row=len(ingredients)+6, column=0, columnspan=4, padx=10, pady=10)

def save_edited_recipe(edit_recipe_window, original_recipe_name, recipe_name, servings, ingredient_entries, amount_entries, vegaaninen, laktoositon, alkuruoka, paaruoka, jalkiruoka):
    ingredients = []
    for ingredient_entry, amount_entry in zip(ingredient_entries, amount_entries):
        ingredient = ingredient_entry.get().strip()
        amount = amount_entry.get().strip()
        if ingredient and amount:
            ingredients.append(f"{ingredient}_{amount}")

    ingredients_str = ";".join(ingredients)

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csvFile = csv.reader(file)
        lines = list(csvFile)

    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for line in lines:
            if line[0].lower() == original_recipe_name.lower():
                writer.writerow([recipe_name, servings, ingredients_str, vegaaninen, laktoositon, alkuruoka, paaruoka, jalkiruoka])
            else:
                writer.writerow(line)

    messagebox.showinfo("Saved", "Recipe saved succesfully!")
    edit_recipe_window.destroy()

initialize_dropbox()
download_recipes_from_dropbox()

atexit.register(upload_recipes_to_dropbox)

root = ttkb.Window(themename="darkly")
root.title("Recipe List")

entry_label = ttkb.Label(root, text="Search:")
entry_label.grid(row=0, column=0, padx=10, pady=10)
entry = ttkb.Entry(root, width=30)
entry.grid(row=0, column=1, padx=10, pady=10)

servings_label = ttkb.Label(root, text="Amount:")
servings_label.grid(row=1, column=0, padx=10, pady=10)
servings_entry = ttkb.Entry(root, width=30)
servings_entry.grid(row=1, column=1, padx=10, pady=10)

vegaaninen_var = tk.StringVar(value="No")
laktoositon_var = tk.StringVar(value="No")
alkuruoka_var = tk.StringVar(value="No")
paaruoka_var = tk.StringVar(value="No")
jalkiruoka_var = tk.StringVar(value="No")

vegaaninen_check = ttkb.Checkbutton(root, text="Vegan", variable=vegaaninen_var, onvalue="Yes", offvalue="No")
vegaaninen_check.grid(row=2, column=0, padx=10, pady=5)

laktoositon_check = ttkb.Checkbutton(root, text="Lactose free", variable=laktoositon_var, onvalue="Yes", offvalue="No")
laktoositon_check.grid(row=2, column=1, padx=10, pady=5)

alkuruoka_check = ttkb.Checkbutton(root, text="Appetizer", variable=alkuruoka_var, onvalue="Yes", offvalue="No")
alkuruoka_check.grid(row=3, column=0, padx=10, pady=5)

paaruoka_check = ttkb.Checkbutton(root, text="Main", variable=paaruoka_var, onvalue="Yes", offvalue="No")
paaruoka_check.grid(row=3, column=1, padx=10, pady=5)

jalkiruoka_check = ttkb.Checkbutton(root, text="Dessert", variable=jalkiruoka_var, onvalue="Yes", offvalue="No")
jalkiruoka_check.grid(row=4, column=0, padx=10, pady=5)

delete_recipe_button = ttkb.Button(root, text="Delete recipe", command=open_delete_recipe_window)
delete_recipe_button.grid(row=5, column=0, padx=10, pady=10)

add_recipe_button = ttkb.Button(root, text="Add recipe", command=open_new_recipe_window)
add_recipe_button.grid(row=5, column=1, padx=10, pady=10)

search_button = ttkb.Button(root, text="Search", command=search_recipes)
search_button.grid(row=5, column=2, padx=10, pady=10)

result_canvas = tk.Canvas(root, width=600, height=400)
result_canvas.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

scrollbar = ttkb.Scrollbar(root, orient="vertical", command=result_canvas.yview)
scrollbar.grid(row=6, column=3, sticky="ns")

result_canvas.config(yscrollcommand=scrollbar.set)

result_frame = ttkb.Frame(result_canvas)

result_canvas.create_window((300, 0), window=result_frame, anchor="n")

result_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

root.grid_rowconfigure(6, weight=1)

root.mainloop()
