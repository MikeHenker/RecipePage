import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter
import requests
import json
import os
import io
import threading
from datetime import datetime, timedelta
import webbrowser
from typing import Dict, List, Optional
import re
import copy

class RecipeSearchApp:
    def __init__(self):
        # Windows 11 Design System Colors
        self.colors = {
            "light": {
                "primary": "#0078D4",  # Windows Blue
                "background": "#FAFAFA",  # Light gray background
                "surface": "#FFFFFF",  # White surface
                "card": "#FFFFFF",  # Card background
                "text": "#323130",  # Dark text
                "text_secondary": "#605E5C",  # Secondary text
                "border": "#EDEBE9",  # Light border
                "accent": "#0078D4",  # Accent color
                "hover": "#F3F2F1",  # Hover state
                "shadow": "rgba(0, 0, 0, 0.1)",
                "success": "#107C10",  # Green
                "warning": "#FF8C00",  # Orange
                "error": "#D83B01"   # Red
            },
            "dark": {
                "primary": "#60CDFF",  # Light Windows Blue
                "background": "#202020",  # Dark background
                "surface": "#2D2D2D",  # Dark surface
                "card": "#323130",  # Card background
                "text": "#FFFFFF",  # Light text
                "text_secondary": "#C8C6C4",  # Secondary text
                "border": "#484644",  # Dark border
                "accent": "#60CDFF",  # Light blue accent
                "hover": "#3E3E3E",  # Dark hover state
                "shadow": "rgba(0, 0, 0, 0.3)",
                "success": "#6FCF97",  # Light green
                "warning": "#F2C94C",  # Light orange
                "error": "#EB5757"   # Light red
            }
        }
        
        # Initialize theme
        self.current_theme = "light"
        ctk.set_appearance_mode(self.current_theme)
        
        # Create main window with Windows 11 styling
        self.root = ctk.CTk()
        self.root.title("🍳 Recipe Kitchen - Modern Recipe Discovery")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configure window colors
        self.root.configure(fg_color=self.colors[self.current_theme]["background"])
        
        # API configuration
        self.api_key = 'b25512cfb12c4c188f5f532e8a1e441c'
        self.base_url = "https://api.spoonacular.com/recipes"
        
        # Application state
        self.ingredients = []
        self.recipes = []
        self.current_recipe = None
        self.favorites = self.load_favorites()
        self.current_view = "search"  # "search", "favorites", "categories", "meal_plan", "shopping_list"
        self.search_history = self.load_search_history()
        self.meal_plan = self.load_meal_plan()
        self.shopping_list = self.load_shopping_list()
        
        # Recipe categories for browsing
        self.recipe_categories = {
            "🌅 Breakfast": "breakfast",
            "🥗 Lunch": "lunch", 
            "🍽️ Dinner": "dinner",
            "🧁 Desserts": "dessert",
            "🥤 Drinks": "beverage",
            "🍲 Soups": "soup",
            "🥙 Snacks": "snack",
            "🍞 Bread": "bread"
        }
        
        # Advanced filters
        self.advanced_filters = {
            "max_ready_time": 60,
            "difficulty": "any",
            "equipment": [],
            "intolerances": [],
            "sort": "max-used-ingredients"
        }
        
        # Load user preferences
        self.load_user_preferences()
        
        self.setup_ui()
        
        # Apply theme after UI setup
        self.apply_theme()
        
    def load_user_preferences(self):
        """Load user preferences from file"""
        try:
            if os.path.exists('user_preferences.json'):
                with open('user_preferences.json', 'r') as f:
                    prefs = json.load(f)
                    self.current_theme = prefs.get('theme', 'light')
                    self.advanced_filters.update(prefs.get('advanced_filters', {}))
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def save_user_preferences(self):
        """Save user preferences to file"""
        try:
            prefs = {
                'theme': self.current_theme,
                'advanced_filters': self.advanced_filters
            }
            with open('user_preferences.json', 'w') as f:
                json.dump(prefs, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        ctk.set_appearance_mode(self.current_theme)
        self.apply_theme()
        self.save_user_preferences()
    
    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        theme_colors = self.colors[self.current_theme]
        self.root.configure(fg_color=theme_colors["background"])
        
        # Update any theme-dependent UI elements here
        # This will be expanded as we create more UI components
    
    def setup_ui(self):
        """Setup the main UI with Windows 11 styling"""
        # Configure main grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create modern sidebar
        self.create_modern_sidebar()
        
        # Create main content area with modern styling
        self.create_modern_main_content()
        
    def create_modern_sidebar(self):
        """Create a modern Windows 11 styled sidebar"""
        theme_colors = self.colors[self.current_theme]
        
        # Main sidebar frame with Windows 11 styling
        self.sidebar_frame = ctk.CTkFrame(
            self.root, 
            width=320, 
            corner_radius=12,
            fg_color=theme_colors["surface"],
            border_width=1,
            border_color=theme_colors["border"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nswe", padx=(15, 8), pady=15)
        self.sidebar_frame.grid_propagate(False)
        
        # Configure sidebar grid
        for i in range(10):
            self.sidebar_frame.grid_rowconfigure(i, weight=0)
        self.sidebar_frame.grid_rowconfigure(10, weight=1)  # Expandable space
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Modern header with theme toggle
        header_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent",
            corner_radius=0
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(25, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # App title with modern styling
        title_label = ctk.CTkLabel(
            header_frame,
            text="🍳 Recipe Kitchen",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=theme_colors["text"]
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Theme toggle button
        theme_icon = "🌙" if self.current_theme == "light" else "☀️"
        self.theme_toggle_btn = ctk.CTkButton(
            header_frame,
            text=theme_icon,
            width=40,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=18),
            fg_color=theme_colors["hover"],
            hover_color=theme_colors["primary"],
            text_color=theme_colors["text"],
            command=self.toggle_theme
        )
        self.theme_toggle_btn.grid(row=0, column=1, sticky="e")
        
        # Navigation tabs with modern styling
        self.create_navigation_tabs()
        
        # Content area based on current view
        self.sidebar_content_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.sidebar_content_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.sidebar_content_frame.grid_columnconfigure(0, weight=1)
        
        # Initially show search interface
        self.show_search_interface()
        
    def create_navigation_tabs(self):
        """Create modern navigation tabs"""
        theme_colors = self.colors[self.current_theme]
        
        nav_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=theme_colors["hover"],
            corner_radius=8,
            height=50
        )
        nav_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        nav_frame.grid_propagate(False)
        nav_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("🔍", "search", "Search"),
            ("❤️", "favorites", "Favorites"),
            ("📅", "meal_plan", "Meal Plan"),
            ("🛍️", "shopping_list", "Shopping")
        ]
        
        for i, (icon, view, tooltip) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_frame,
                text=icon,
                width=60,
                height=40,
                corner_radius=6,
                font=ctk.CTkFont(size=16),
                fg_color="transparent" if view != self.current_view else theme_colors["primary"],
                hover_color=theme_colors["primary"],
                text_color=theme_colors["text"] if view != self.current_view else "white",
                command=lambda v=view: self.switch_view(v)
            )
            btn.grid(row=0, column=i, padx=2, pady=5)
            self.nav_buttons[view] = btn
    
    def switch_view(self, view):
        """Switch between different views"""
        self.current_view = view
        
        # Update navigation button states
        theme_colors = self.colors[self.current_theme]
        for view_name, btn in self.nav_buttons.items():
            if view_name == view:
                btn.configure(
                    fg_color=theme_colors["primary"],
                    text_color="white"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme_colors["text"]
                )
        
        # Clear current content
        for widget in self.sidebar_content_frame.winfo_children():
            widget.destroy()
        
        # Show appropriate interface
        if view == "search":
            self.show_search_interface()
        elif view == "favorites":
            self.show_favorites_interface()
        elif view == "meal_plan":
            self.show_meal_plan_interface()
        elif view == "shopping_list":
            self.show_shopping_list_interface()
        
    def show_search_interface(self):
        """Show the search interface with modern styling"""
        theme_colors = self.colors[self.current_theme]
        
        # Ingredients section
        ingredients_label = ctk.CTkLabel(
            self.sidebar_content_frame,
            text="🥬 Ingredients",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme_colors["text"]
        )
        ingredients_label.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Modern ingredient input
        ingredient_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        ingredient_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ingredient_frame.grid_columnconfigure(0, weight=1)
        
        self.ingredient_entry = ctk.CTkEntry(
            ingredient_frame,
            placeholder_text="Add an ingredient...",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=6,
            border_width=0,
            fg_color="transparent"
        )
        self.ingredient_entry.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        self.ingredient_entry.bind("<Return>", self.add_ingredient)
        
        add_btn = ctk.CTkButton(
            ingredient_frame,
            text="➕",
            width=40,
            height=40,
            corner_radius=6,
            font=ctk.CTkFont(size=16),
            fg_color=theme_colors["primary"],
            hover_color=theme_colors["accent"],
            command=self.add_ingredient
        )
        add_btn.grid(row=0, column=1, padx=(5, 15), pady=10)
        
        # Modern ingredients list
        self.ingredients_list_frame = ctk.CTkScrollableFrame(
            self.sidebar_content_frame,
            height=120,
            corner_radius=8,
            fg_color=theme_colors["card"],
            border_width=1,
            border_color=theme_colors["border"]
        )
        self.ingredients_list_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # Initialize ingredients display
        self.refresh_ingredients_display()
        
        # Recipe categories
        categories_label = ctk.CTkLabel(
            self.sidebar_content_frame,
            text="🏗️ Quick Categories",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme_colors["text"]
        )
        categories_label.grid(row=3, column=0, sticky="w", pady=(15, 10))
        
        self.create_category_buttons()
        
    def create_category_buttons(self):
        """Create quick category access buttons"""
        theme_colors = self.colors[self.current_theme]
        
        # Category buttons grid
        categories_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color="transparent",
            corner_radius=0
        )
        categories_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        categories_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Create category buttons in a 2x4 grid
        categories = list(self.recipe_categories.items())
        for i, (name, category) in enumerate(categories):
            row = i // 2
            col = i % 2
            
            btn = ctk.CTkButton(
                categories_frame,
                text=name,
                height=35,
                corner_radius=6,
                font=ctk.CTkFont(size=12),
                fg_color=theme_colors["hover"],
                hover_color=theme_colors["primary"],
                text_color=theme_colors["text"],
                command=lambda cat=category: self.search_by_category(cat)
            )
            btn.grid(row=row, column=col, padx=3, pady=2, sticky="ew")
        
        # Advanced filters section
        self.create_advanced_filters()
    
    def create_advanced_filters(self):
        """Create advanced search filters"""
        theme_colors = self.colors[self.current_theme]
        
        # Filters header
        filters_label = ctk.CTkLabel(
            self.sidebar_content_frame,
            text="⚙️ Filters",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme_colors["text"]
        )
        filters_label.grid(row=5, column=0, sticky="w", pady=(15, 10))
        
        # Filters frame
        filters_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        filters_frame.grid(row=6, column=0, sticky="ew", pady=(0, 15))
        filters_frame.grid_columnconfigure(0, weight=1)
        
        # Diet filter
        diet_label = ctk.CTkLabel(
            filters_frame,
            text="Diet Type:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme_colors["text_secondary"]
        )
        diet_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.diet_var = ctk.StringVar(value="None")
        self.diet_menu = ctk.CTkOptionMenu(
            filters_frame,
            variable=self.diet_var,
            values=["None", "Vegetarian", "Vegan", "Gluten Free", "Ketogenic", "Paleo"],
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=theme_colors["hover"],
            button_color=theme_colors["primary"],
            button_hover_color=theme_colors["accent"]
        )
        self.diet_menu.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        # Cuisine filter
        cuisine_label = ctk.CTkLabel(
            filters_frame,
            text="Cuisine Type:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme_colors["text_secondary"]
        )
        cuisine_label.grid(row=2, column=0, padx=15, pady=(5, 5), sticky="w")
        
        self.cuisine_var = ctk.StringVar(value="None")
        self.cuisine_menu = ctk.CTkOptionMenu(
            filters_frame,
            variable=self.cuisine_var,
            values=["None", "Italian", "Mexican", "Chinese", "Indian", "French", "Mediterranean", "American", "Asian", "European"],
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=theme_colors["hover"],
            button_color=theme_colors["primary"],
            button_hover_color=theme_colors["accent"]
        )
        self.cuisine_menu.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        # Cooking time filter
        time_label = ctk.CTkLabel(
            filters_frame,
            text="Max Cooking Time:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme_colors["text_secondary"]
        )
        time_label.grid(row=4, column=0, padx=15, pady=(5, 5), sticky="w")
        
        self.time_frame = ctk.CTkFrame(
            filters_frame,
            fg_color="transparent"
        )
        self.time_frame.grid(row=5, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.time_frame.grid_columnconfigure(0, weight=1)
        
        self.time_slider = ctk.CTkSlider(
            self.time_frame,
            from_=15,
            to=180,
            number_of_steps=11,
            command=self.update_time_label
        )
        self.time_slider.set(self.advanced_filters["max_ready_time"])
        self.time_slider.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.time_value_label = ctk.CTkLabel(
            self.time_frame,
            text=f"{int(self.time_slider.get())} minutes",
            font=ctk.CTkFont(size=11),
            text_color=theme_colors["text_secondary"]
        )
        self.time_value_label.grid(row=1, column=0)
        
        # Modern search button
        search_btn = ctk.CTkButton(
            self.sidebar_content_frame,
            text="🔍 Search Recipes",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=8,
            fg_color=theme_colors["primary"],
            hover_color=theme_colors["accent"],
            command=self.search_recipes
        )
        search_btn.grid(row=7, column=0, sticky="ew", pady=(15, 10))
        
        # Quick actions
        actions_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color="transparent"
        )
        actions_frame.grid(row=8, column=0, sticky="ew", pady=(5, 0))
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        clear_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Clear",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["hover"],
            hover_color=theme_colors["error"],
            text_color=theme_colors["text"],
            command=self.clear_ingredients
        )
        clear_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        random_btn = ctk.CTkButton(
            actions_frame,
            text="🎲 Random",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["hover"],
            hover_color=theme_colors["warning"],
            text_color=theme_colors["text"],
            command=self.get_random_recipes
        )
        random_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
    def update_time_label(self, value):
        """Update the time filter label"""
        self.time_value_label.configure(text=f"{int(value)} minutes")
        self.advanced_filters["max_ready_time"] = int(value)
    
    def clear_ingredients(self):
        """Clear all ingredients"""
        self.ingredients.clear()
        self.refresh_ingredients_display()
    
    def get_random_recipes(self):
        """Get random recipes"""
        if not self.api_key:
            messagebox.showerror("Error", "Spoonacular API key not found!")
            return
        
        self.current_view = "search"
        self.results_label.configure(text="Finding random recipes...")
        
        thread = threading.Thread(target=self._get_random_recipes_thread)
        thread.daemon = True
        thread.start()
    
    def _get_random_recipes_thread(self):
        """Get random recipes in background thread"""
        try:
            params = {
                "apiKey": self.api_key,
                "number": 12,
                "tags": "main course"
            }
            
            response = requests.get(f"{self.base_url}/random", params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.recipes = result.get('recipes', [])
                self.root.after(0, self.display_recipes)
            else:
                self.root.after(0, lambda: self.show_error(f"API Error: {response.status_code}"))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error getting random recipes: {str(e)}"))
    
    def search_by_category(self, category):
        """Search recipes by category"""
        if not self.api_key:
            messagebox.showerror("Error", "Spoonacular API key not found!")
            return
        
        self.current_view = "search"
        self.results_label.configure(text=f"Searching {category} recipes...")
        
        thread = threading.Thread(target=self._search_by_category_thread, args=(category,))
        thread.daemon = True
        thread.start()
    
    def _search_by_category_thread(self, category):
        """Search by category in background thread"""
        try:
            params = {
                "apiKey": self.api_key,
                "type": category,
                "number": 12,
                "addRecipeInformation": True
            }
            
            response = requests.get(f"{self.base_url}/complexSearch", params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.recipes = result.get('results', [])
                self.root.after(0, self.display_recipes)
            else:
                self.root.after(0, lambda: self.show_error(f"API Error: {response.status_code}"))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error searching category: {str(e)}"))
    
    def refresh_ingredients_display(self):
        """Refresh the ingredients display"""
        # Clear current widgets
        for widget in self.ingredients_list_frame.winfo_children():
            widget.destroy()
        
        theme_colors = self.colors[self.current_theme]
        
        if not self.ingredients:
            empty_label = ctk.CTkLabel(
                self.ingredients_list_frame,
                text="No ingredients added yet",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"]
            )
            empty_label.pack(pady=20)
            return
        
        # Display ingredients as modern cards
        for i, ingredient in enumerate(self.ingredients):
            ingredient_frame = ctk.CTkFrame(
                self.ingredients_list_frame,
                fg_color=theme_colors["hover"],
                corner_radius=6,
                height=35
            )
            ingredient_frame.pack(fill="x", padx=5, pady=2)
            ingredient_frame.pack_propagate(False)
            
            ingredient_label = ctk.CTkLabel(
                ingredient_frame,
                text=ingredient,
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text"]
            )
            ingredient_label.pack(side="left", padx=10, pady=5)
            
            remove_btn = ctk.CTkButton(
                ingredient_frame,
                text="✕",
                width=25,
                height=25,
                corner_radius=12,
                font=ctk.CTkFont(size=12),
                fg_color=theme_colors["error"],
                hover_color="#B71C1C",
                command=lambda idx=i: self.remove_ingredient_by_index(idx)
            )
            remove_btn.pack(side="right", padx=10, pady=5)
    
    def remove_ingredient_by_index(self, index):
        """Remove ingredient by index"""
        if 0 <= index < len(self.ingredients):
            self.ingredients.pop(index)
            self.refresh_ingredients_display()
    
    def show_favorites_interface(self):
        """Show favorites management interface"""
        theme_colors = self.colors[self.current_theme]
        
        if not self.favorites:
            empty_frame = ctk.CTkFrame(
                self.sidebar_content_frame,
                fg_color=theme_colors["card"],
                corner_radius=8
            )
            empty_frame.pack(fill="both", expand=True, pady=20)
            
            ctk.CTkLabel(
                empty_frame,
                text="💔 No favorites yet",
                font=ctk.CTkFont(size=16),
                text_color=theme_colors["text_secondary"]
            ).pack(pady=30)
            
            ctk.CTkLabel(
                empty_frame,
                text="Star recipes to add them here!",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"]
            ).pack()
        else:
            favorites_btn = ctk.CTkButton(
                self.sidebar_content_frame,
                text=f"❤️ View All Favorites ({len(self.favorites)})",
                height=45,
                corner_radius=8,
                fg_color=theme_colors["primary"],
                hover_color=theme_colors["accent"],
                command=self.show_favorites
            )
            favorites_btn.pack(fill="x", pady=10)
    
    def show_meal_plan_interface(self):
        """Show comprehensive meal planning interface"""
        theme_colors = self.colors[self.current_theme]
        
        # Meal plan header
        header_label = ctk.CTkLabel(
            self.sidebar_content_frame,
            text="📅 Weekly Meal Plan",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=(0, 15))
        
        # Current week navigation
        week_nav_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color=theme_colors["hover"],
            corner_radius=6
        )
        week_nav_frame.pack(fill="x", pady=(0, 15))
        
        week_nav_content = ctk.CTkFrame(
            week_nav_frame,
            fg_color="transparent"
        )
        week_nav_content.pack(fill="x", padx=10, pady=8)
        week_nav_content.grid_columnconfigure(1, weight=1)
        
        # Previous week button
        ctk.CTkButton(
            week_nav_content,
            text="◀",
            width=30,
            height=30,
            corner_radius=4,
            fg_color=theme_colors["primary"],
            command=self.previous_week
        ).grid(row=0, column=0, padx=(0, 5))
        
        # Current week label
        from datetime import datetime, timedelta
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_text = f"Week of {week_start.strftime('%b %d')}"
        
        self.week_label = ctk.CTkLabel(
            week_nav_content,
            text=week_text,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.week_label.grid(row=0, column=1)
        
        # Next week button
        ctk.CTkButton(
            week_nav_content,
            text="▶",
            width=30,
            height=30,
            corner_radius=4,
            fg_color=theme_colors["primary"],
            command=self.next_week
        ).grid(row=0, column=2, padx=(5, 0))
        
        # Meal plan actions
        actions_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color="transparent"
        )
        actions_frame.pack(fill="x", pady=(0, 15))
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        plan_btn = ctk.CTkButton(
            actions_frame,
            text="📈 View Full Plan",
            height=40,
            corner_radius=6,
            fg_color=theme_colors["primary"],
            command=self.show_full_meal_plan
        )
        plan_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        generate_btn = ctk.CTkButton(
            actions_frame,
            text="🤖 Auto Generate",
            height=40,
            corner_radius=6,
            fg_color=theme_colors["success"],
            command=self.auto_generate_meal_plan
        )
        generate_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Quick daily view
        self.create_daily_meal_preview()
    
    def show_shopping_list_interface(self):
        """Show comprehensive shopping list interface"""
        theme_colors = self.colors[self.current_theme]
        
        # Shopping list header
        header_label = ctk.CTkLabel(
            self.sidebar_content_frame,
            text="🛍️ Shopping List",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=(0, 15))
        
        # Shopping list stats
        if self.shopping_list:
            stats_frame = ctk.CTkFrame(
                self.sidebar_content_frame,
                fg_color=theme_colors["hover"],
                corner_radius=6
            )
            stats_frame.pack(fill="x", pady=(0, 15))
            
            total_items = len(self.shopping_list)
            checked_items = sum(1 for item in self.shopping_list if item.get('checked', False))
            
            ctk.CTkLabel(
                stats_frame,
                text=f"📋 {checked_items}/{total_items} items",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=8)
        
        # Shopping list actions
        actions_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color="transparent"
        )
        actions_frame.pack(fill="x", pady=(0, 15))
        actions_frame.grid_columnconfigure(0, weight=1)
        
        generate_favorites_btn = ctk.CTkButton(
            actions_frame,
            text="❤️ From Favorites",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["primary"],
            command=self.generate_shopping_from_favorites
        )
        generate_favorites_btn.grid(row=0, column=0, sticky="ew", pady=2)
        
        generate_meal_plan_btn = ctk.CTkButton(
            actions_frame,
            text="📅 From Meal Plan",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["success"],
            command=self.generate_shopping_from_meal_plan
        )
        generate_meal_plan_btn.grid(row=1, column=0, sticky="ew", pady=2)
        
        view_list_btn = ctk.CTkButton(
            actions_frame,
            text="📋 View Full List",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["hover"],
            text_color=theme_colors["text"],
            command=self.show_full_shopping_list
        )
        view_list_btn.grid(row=2, column=0, sticky="ew", pady=2)
        
        clear_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Clear List",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["error"],
            command=self.clear_shopping_list
        )
        clear_btn.grid(row=3, column=0, sticky="ew", pady=2)
        
        # Manual add item
        self.create_manual_add_item_interface()
    
    def load_search_history(self):
        """Load search history from file"""
        try:
            if os.path.exists('search_history.json'):
                with open('search_history.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def load_meal_plan(self):
        """Load meal plan from file"""
        try:
            if os.path.exists('meal_plan.json'):
                with open('meal_plan.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def load_shopping_list(self):
        """Load shopping list from file"""
        try:
            if os.path.exists('shopping_list.json'):
                with open('shopping_list.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def save_shopping_list(self):
        """Save shopping list to file"""
        try:
            with open('shopping_list.json', 'w') as f:
                json.dump(self.shopping_list, f)
        except Exception as e:
            print(f"Error saving shopping list: {e}")
    
    def save_meal_plan(self):
        """Save meal plan to file"""
        try:
            with open('meal_plan.json', 'w') as f:
                json.dump(self.meal_plan, f)
        except Exception as e:
            print(f"Error saving meal plan: {e}")
    
    def previous_week(self):
        """Navigate to previous week"""
        # Update week navigation (placeholder for now)
        pass
    
    def next_week(self):
        """Navigate to next week"""
        # Update week navigation (placeholder for now)
        pass
    
    def create_daily_meal_preview(self):
        """Create preview of today's meals"""
        theme_colors = self.colors[self.current_theme]
        
        preview_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        preview_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            preview_frame,
            text="🌅 Today's Plan",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Get today's date for meal plan lookup
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        today_meals = self.meal_plan.get(today, {})
        
        if not today_meals:
            ctk.CTkLabel(
                preview_frame,
                text="No meals planned for today",
                font=ctk.CTkFont(size=11),
                text_color=theme_colors["text_secondary"]
            ).pack(pady=(0, 15))
        else:
            for meal_type, recipe_info in today_meals.items():
                meal_frame = ctk.CTkFrame(
                    preview_frame,
                    fg_color=theme_colors["hover"],
                    corner_radius=4,
                    height=30
                )
                meal_frame.pack(fill="x", padx=10, pady=2)
                meal_frame.pack_propagate(False)
                
                ctk.CTkLabel(
                    meal_frame,
                    text=f"{meal_type.title()}: {recipe_info.get('title', 'Unknown')}",
                    font=ctk.CTkFont(size=10),
                    text_color=theme_colors["text"]
                ).pack(expand=True)
        
        # Quick add meal button
        ctk.CTkButton(
            preview_frame,
            text="+ Add Meal",
            height=30,
            corner_radius=6,
            fg_color=theme_colors["primary"],
            command=lambda: self.quick_add_meal(today)
        ).pack(pady=(5, 15))
    
    def create_manual_add_item_interface(self):
        """Create interface for manually adding shopping list items"""
        theme_colors = self.colors[self.current_theme]
        
        manual_frame = ctk.CTkFrame(
            self.sidebar_content_frame,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        manual_frame.pack(fill="x")
        
        ctk.CTkLabel(
            manual_frame,
            text="✏️ Add Item",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Item input
        input_frame = ctk.CTkFrame(
            manual_frame,
            fg_color="transparent"
        )
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.shopping_item_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter item...",
            height=35,
            corner_radius=6
        )
        self.shopping_item_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.shopping_item_entry.bind("<Return>", self.add_shopping_item)
        
        add_item_btn = ctk.CTkButton(
            input_frame,
            text="+",
            width=35,
            height=35,
            corner_radius=6,
            fg_color=theme_colors["primary"],
            command=self.add_shopping_item
        )
        add_item_btn.grid(row=0, column=1)
    
    def show_full_meal_plan(self):
        """Show full meal planning interface"""
        meal_plan_window = ctk.CTkToplevel(self.root)
        meal_plan_window.title("📅 Weekly Meal Planner")
        meal_plan_window.geometry("1000x600")
        meal_plan_window.transient(self.root)
        
        theme_colors = self.colors[self.current_theme]
        meal_plan_window.configure(fg_color=theme_colors["background"])
        
        # Create weekly meal plan grid
        self.create_weekly_meal_plan_grid(meal_plan_window)
    
    def auto_generate_meal_plan(self):
        """Auto-generate meal plan from favorites"""
        if not self.favorites:
            messagebox.showinfo("Info", "Please add some favorite recipes first!")
            return
        
        # Show loading and generate in background
        self.show_loading_screen("Generating your personalized meal plan...")
        
        thread = threading.Thread(target=self._auto_generate_meal_plan_thread)
        thread.daemon = True
        thread.start()
    
    def _auto_generate_meal_plan_thread(self):
        """Generate meal plan in background thread"""
        try:
            # Get favorite recipes details
            if not self.favorites:
                return
            
            # Use bulk API to get favorite recipes
            params = {
                "apiKey": self.api_key,
                "ids": ",".join(map(str, self.favorites[:7])),  # Get up to 7 recipes
                "includeNutrition": False
            }
            
            response = requests.get(f"{self.base_url}/informationBulk", params=params, timeout=10)
            
            if response.status_code == 200:
                recipes = response.json()
                
                # Generate meal plan for the week
                from datetime import datetime, timedelta
                today = datetime.now()
                meal_plan = {}
                
                meal_types = ['breakfast', 'lunch', 'dinner']
                
                for i in range(7):  # 7 days
                    date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
                    daily_meals = {}
                    
                    # Assign recipes to meal types
                    for j, meal_type in enumerate(meal_types):
                        if j < len(recipes):
                            recipe = recipes[j % len(recipes)]
                            daily_meals[meal_type] = {
                                'id': recipe['id'],
                                'title': recipe['title'],
                                'image': recipe.get('image', ''),
                                'readyInMinutes': recipe.get('readyInMinutes', 30)
                            }
                    
                    meal_plan[date] = daily_meals
                
                # Update meal plan
                self.meal_plan.update(meal_plan)
                self.save_meal_plan()
                
                # Update UI
                self.root.after(0, lambda: self.show_meal_plan_success())
            else:
                self.root.after(0, lambda: self.show_error("Failed to generate meal plan"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error generating meal plan: {str(e)}"))
    
    def show_meal_plan_success(self):
        """Show meal plan generation success"""
        messagebox.showinfo("Success", "Meal plan generated successfully!")
        if self.current_view == "meal_plan":
            self.switch_view("meal_plan")  # Refresh the view
    
    def quick_add_meal(self, date):
        """Quick add meal dialog"""
        # Simple implementation - could be enhanced with recipe search
        meal_type = "dinner"  # Default
        if self.recipes and len(self.recipes) > 0:
            # Use first recipe from current search
            recipe = self.recipes[0]
            
            if date not in self.meal_plan:
                self.meal_plan[date] = {}
            
            self.meal_plan[date][meal_type] = {
                'id': recipe['id'],
                'title': recipe['title'],
                'image': recipe.get('image', ''),
                'readyInMinutes': recipe.get('readyInMinutes', 30)
            }
            
            self.save_meal_plan()
            messagebox.showinfo("Success", f"Added {recipe['title']} to {meal_type}!")
            
            if self.current_view == "meal_plan":
                self.switch_view("meal_plan")  # Refresh
        else:
            messagebox.showinfo("Info", "Please search for recipes first!")
    
    def generate_shopping_from_favorites(self):
        """Generate shopping list from favorite recipes"""
        if not self.favorites:
            messagebox.showinfo("Info", "Please add some favorite recipes first!")
            return
        
        self.show_loading_screen("Generating shopping list from your favorites...")
        
        thread = threading.Thread(target=self._generate_shopping_from_favorites_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_shopping_from_favorites_thread(self):
        """Generate shopping list from favorites in background"""
        try:
            # Get favorite recipes with ingredients
            params = {
                "apiKey": self.api_key,
                "ids": ",".join(map(str, self.favorites)),
                "includeNutrition": False
            }
            
            response = requests.get(f"{self.base_url}/informationBulk", params=params, timeout=15)
            
            if response.status_code == 200:
                recipes = response.json()
                
                # Consolidate ingredients
                ingredient_consolidation = {}
                
                for recipe in recipes:
                    for ingredient in recipe.get('extendedIngredients', []):
                        name = ingredient.get('name', '').lower()
                        original = ingredient.get('original', '')
                        
                        if name:
                            if name in ingredient_consolidation:
                                # Combine amounts if possible
                                existing = ingredient_consolidation[name]
                                existing['recipes'].append(recipe['title'])
                                existing['count'] += 1
                            else:
                                ingredient_consolidation[name] = {
                                    'name': ingredient.get('name', ''),
                                    'original': original,
                                    'aisle': ingredient.get('aisle', 'Other'),
                                    'recipes': [recipe['title']],
                                    'count': 1,
                                    'checked': False
                                }
                
                # Convert to shopping list format
                new_shopping_list = list(ingredient_consolidation.values())
                
                # Add to existing shopping list (avoid duplicates)
                existing_names = {item['name'].lower() for item in self.shopping_list}
                
                for item in new_shopping_list:
                    if item['name'].lower() not in existing_names:
                        self.shopping_list.append(item)
                
                self.save_shopping_list()
                
                # Update UI
                self.root.after(0, lambda: self.show_shopping_success(len(new_shopping_list)))
            else:
                self.root.after(0, lambda: self.show_error("Failed to generate shopping list"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error generating shopping list: {str(e)}"))
    
    def generate_shopping_from_meal_plan(self):
        """Generate shopping list from meal plan"""
        if not self.meal_plan:
            messagebox.showinfo("Info", "Please create a meal plan first!")
            return
        
        # Simple implementation - get all recipes from meal plan
        recipe_ids = set()
        for date_meals in self.meal_plan.values():
            for meal_info in date_meals.values():
                if 'id' in meal_info:
                    recipe_ids.add(meal_info['id'])
        
        if not recipe_ids:
            messagebox.showinfo("Info", "No recipes found in meal plan!")
            return
        
        # Use the favorites method but with meal plan recipe IDs
        original_favorites = self.favorites.copy()
        self.favorites = list(recipe_ids)
        
        self._generate_shopping_from_favorites_thread()
        
        # Restore original favorites
        self.favorites = original_favorites
    
    def show_shopping_success(self, item_count):
        """Show shopping list generation success"""
        messagebox.showinfo("Success", f"Added {item_count} items to your shopping list!")
        if self.current_view == "shopping_list":
            self.switch_view("shopping_list")  # Refresh the view
    
    def show_full_shopping_list(self):
        """Show full shopping list interface"""
        shopping_window = ctk.CTkToplevel(self.root)
        shopping_window.title("🛍️ Shopping List")
        shopping_window.geometry("600x500")
        shopping_window.transient(self.root)
        
        theme_colors = self.colors[self.current_theme]
        shopping_window.configure(fg_color=theme_colors["background"])
        
        # Create shopping list interface
        self.create_shopping_list_interface(shopping_window)
    
    def clear_shopping_list(self):
        """Clear the shopping list"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the shopping list?"):
            self.shopping_list.clear()
            self.save_shopping_list()
            messagebox.showinfo("Success", "Shopping list cleared!")
            if self.current_view == "shopping_list":
                self.switch_view("shopping_list")  # Refresh
    
    def add_shopping_item(self, event=None):
        """Add manual shopping item"""
        item_text = self.shopping_item_entry.get().strip()
        if item_text:
            new_item = {
                'name': item_text,
                'original': item_text,
                'aisle': 'Other',
                'recipes': ['Manual Entry'],
                'count': 1,
                'checked': False
            }
            
            self.shopping_list.append(new_item)
            self.save_shopping_list()
            self.shopping_item_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Added '{item_text}' to shopping list!")
    
    def create_weekly_meal_plan_grid(self, window):
        """Create weekly meal plan grid interface"""
        theme_colors = self.colors[self.current_theme]
        
        # Placeholder for full meal plan interface
        ctk.CTkLabel(
            window,
            text="📅 Weekly Meal Planner",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            window,
            text="Drag and drop functionality coming soon!",
            font=ctk.CTkFont(size=16),
            text_color=theme_colors["text_secondary"]
        ).pack(pady=10)
        
        # Show current meal plan if available
        if self.meal_plan:
            plan_frame = ctk.CTkScrollableFrame(window)
            plan_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            for date, meals in sorted(self.meal_plan.items()):
                date_frame = ctk.CTkFrame(
                    plan_frame,
                    fg_color=theme_colors["card"]
                )
                date_frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    date_frame,
                    text=f"📅 {date}",
                    font=ctk.CTkFont(size=16, weight="bold")
                ).pack(pady=10)
                
                for meal_type, recipe_info in meals.items():
                    meal_label = ctk.CTkLabel(
                        date_frame,
                        text=f"{meal_type.title()}: {recipe_info.get('title', 'Unknown')}",
                        font=ctk.CTkFont(size=12)
                    )
                    meal_label.pack(pady=2)
    
    def create_shopping_list_interface(self, window):
        """Create shopping list interface"""
        theme_colors = self.colors[self.current_theme]
        
        # Header
        header_frame = ctk.CTkFrame(window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="🛍️ Shopping List",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Stats
        if self.shopping_list:
            total_items = len(self.shopping_list)
            checked_items = sum(1 for item in self.shopping_list if item.get('checked', False))
            
            ctk.CTkLabel(
                header_frame,
                text=f"{checked_items}/{total_items} completed",
                font=ctk.CTkFont(size=14),
                text_color=theme_colors["text_secondary"]
            ).pack(side="right")
        
        # Shopping list content
        list_frame = ctk.CTkScrollableFrame(window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        if not self.shopping_list:
            ctk.CTkLabel(
                list_frame,
                text="Your shopping list is empty",
                font=ctk.CTkFont(size=16),
                text_color=theme_colors["text_secondary"]
            ).pack(pady=50)
            return
        
        # Group by aisle
        aisles = {}
        for item in self.shopping_list:
            aisle = item.get('aisle', 'Other')
            if aisle not in aisles:
                aisles[aisle] = []
            aisles[aisle].append(item)
        
        # Display by aisle
        for aisle, items in aisles.items():
            # Aisle header
            aisle_frame = ctk.CTkFrame(
                list_frame,
                fg_color=theme_colors["primary"],
                corner_radius=6
            )
            aisle_frame.pack(fill="x", pady=(10, 5))
            
            ctk.CTkLabel(
                aisle_frame,
                text=f"🛍️ {aisle}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(pady=8)
            
            # Items in aisle
            for item in items:
                item_frame = ctk.CTkFrame(
                    list_frame,
                    fg_color=theme_colors["card"],
                    corner_radius=4
                )
                item_frame.pack(fill="x", pady=2)
                item_frame.grid_columnconfigure(1, weight=1)
                
                # Checkbox
                checkbox = ctk.CTkCheckBox(
                    item_frame,
                    text="",
                    width=20
                )
                checkbox.grid(row=0, column=0, padx=15, pady=10)
                if item.get('checked', False):
                    checkbox.select()
                
                # Item name
                item_label = ctk.CTkLabel(
                    item_frame,
                    text=item['name'],
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                item_label.grid(row=0, column=1, sticky="ew", pady=10)
                
                # Recipe count
                if item.get('count', 1) > 1:
                    count_label = ctk.CTkLabel(
                        item_frame,
                        text=f"x{item['count']}",
                        font=ctk.CTkFont(size=10),
                        text_color=theme_colors["text_secondary"]
                    )
                    count_label.grid(row=0, column=2, padx=15, pady=10)
    
    def create_modern_main_content(self):
        """Create the main content area with modern Windows 11 styling"""
        theme_colors = self.colors[self.current_theme]
        
        # Main content frame with modern styling
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=theme_colors["surface"],
            corner_radius=12,
            border_width=1,
            border_color=theme_colors["border"]
        )
        self.main_frame.grid(row=0, column=1, sticky="nswe", padx=(8, 15), pady=15)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Modern header with search info and controls
        self.create_main_header()
        
        # Scrollable content area
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=theme_colors["background"],
            corner_radius=8
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nswe", padx=15, pady=(0, 15))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome message
        self.show_welcome_screen()
    
    def create_main_header(self):
        """Create the main content header"""
        theme_colors = self.colors[self.current_theme]
        
        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=0
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(20, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Results label with modern styling
        self.results_label = ctk.CTkLabel(
            header_frame,
            text="🏠 Welcome to Recipe Kitchen",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=theme_colors["text"]
        )
        self.results_label.grid(row=0, column=0, sticky="w")
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(
            header_frame,
            fg_color="transparent"
        )
        controls_frame.grid(row=0, column=1, sticky="e")
        
        # View toggle buttons
        self.view_buttons = ctk.CTkSegmentedButton(
            controls_frame,
            values=["Grid", "List"],
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            fg_color=theme_colors["hover"],
            selected_color=theme_colors["primary"],
            command=self.change_view_mode
        )
        self.view_buttons.set("Grid")
        self.view_buttons.pack(side="right", padx=(10, 0))
        
        # Sort dropdown
        self.sort_var = ctk.StringVar(value="Relevance")
        sort_menu = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.sort_var,
            values=["Relevance", "Popularity", "Health Score", "Cooking Time", "Alphabetical"],
            width=120,
            corner_radius=6,
            fg_color=theme_colors["hover"],
            button_color=theme_colors["primary"],
            command=self.resort_recipes
        )
        sort_menu.pack(side="right", padx=(10, 0))
    
    def show_welcome_screen(self):
        """Show welcome screen with modern design"""
        theme_colors = self.colors[self.current_theme]
        
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Welcome container
        welcome_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=theme_colors["card"],
            corner_radius=12,
            border_width=1,
            border_color=theme_colors["border"]
        )
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        # Welcome content
        welcome_content = ctk.CTkFrame(
            welcome_frame,
            fg_color="transparent"
        )
        welcome_content.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Large welcome emoji
        ctk.CTkLabel(
            welcome_content,
            text="👨‍🍳",
            font=ctk.CTkFont(size=80)
        ).pack(pady=(20, 30))
        
        # Welcome title
        ctk.CTkLabel(
            welcome_content,
            text="Welcome to Recipe Kitchen",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=theme_colors["text"]
        ).pack(pady=(0, 15))
        
        # Welcome subtitle
        ctk.CTkLabel(
            welcome_content,
            text="Discover amazing recipes with modern search and planning tools",
            font=ctk.CTkFont(size=16),
            text_color=theme_colors["text_secondary"]
        ).pack(pady=(0, 30))
        
        # Quick start buttons
        quick_start_frame = ctk.CTkFrame(
            welcome_content,
            fg_color="transparent"
        )
        quick_start_frame.pack()
        
        start_search_btn = ctk.CTkButton(
            quick_start_frame,
            text="🔍 Start Searching",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200,
            corner_radius=8,
            fg_color=theme_colors["primary"],
            hover_color=theme_colors["accent"],
            command=lambda: self.switch_view("search")
        )
        start_search_btn.pack(side="left", padx=(0, 15))
        
        browse_btn = ctk.CTkButton(
            quick_start_frame,
            text="🏷️ Browse Categories",
            font=ctk.CTkFont(size=16),
            height=50,
            width=200,
            corner_radius=8,
            fg_color=theme_colors["hover"],
            hover_color=theme_colors["primary"],
            text_color=theme_colors["text"],
            command=self.show_category_browser
        )
        browse_btn.pack(side="left")
    
    def change_view_mode(self, mode):
        """Change between grid and list view modes"""
        self.view_mode = mode.lower()
        if hasattr(self, 'recipes') and self.recipes:
            self.display_recipes()
    
    def resort_recipes(self, sort_option):
        """Resort current recipes based on selected option"""
        if not hasattr(self, 'recipes') or not self.recipes:
            return
        
        # Sort recipes based on option
        if sort_option == "Popularity":
            self.recipes.sort(key=lambda x: x.get('aggregateLikes', 0), reverse=True)
        elif sort_option == "Health Score":
            self.recipes.sort(key=lambda x: x.get('healthScore', 0), reverse=True)
        elif sort_option == "Cooking Time":
            self.recipes.sort(key=lambda x: x.get('readyInMinutes', 999))
        elif sort_option == "Alphabetical":
            self.recipes.sort(key=lambda x: x.get('title', '').lower())
        
        self.display_recipes()
    
    def show_category_browser(self):
        """Show category browser in main area"""
        theme_colors = self.colors[self.current_theme]
        
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.results_label.configure(text="🏷️ Browse Recipe Categories")
        
        # Category grid
        categories_grid = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="transparent"
        )
        categories_grid.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        for i in range(4):
            categories_grid.grid_columnconfigure(i, weight=1)
        
        # Create category cards
        categories = list(self.recipe_categories.items())
        for i, (name, category) in enumerate(categories):
            row = i // 4
            col = i % 4
            
            # Category card
            card = ctk.CTkFrame(
                categories_grid,
                fg_color=theme_colors["card"],
                corner_radius=12,
                border_width=1,
                border_color=theme_colors["border"]
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Category content
            ctk.CTkLabel(
                card,
                text=name.split()[0],  # Just the emoji
                font=ctk.CTkFont(size=40)
            ).pack(pady=(20, 10))
            
            ctk.CTkLabel(
                card,
                text=name.split(' ', 1)[1] if ' ' in name else name,  # Text without emoji
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=theme_colors["text"]
            ).pack(pady=(0, 15))
            
            # Browse button
            browse_cat_btn = ctk.CTkButton(
                card,
                text="Browse",
                width=100,
                height=35,
                corner_radius=6,
                fg_color=theme_colors["primary"],
                hover_color=theme_colors["accent"],
                command=lambda cat=category: self.search_by_category(cat)
            )
            browse_cat_btn.pack(pady=(0, 20))
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        self.results_label = ctk.CTkLabel(
            header_frame,
            text="Enter ingredients and click 'Search Recipes' to find delicious recipes!",
            font=ctk.CTkFont(size=16)
        )
        self.results_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Scrollable frame for recipes
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scrollable_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=(5, 10))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
    def add_ingredient(self, event=None):
        """Add ingredient with modern validation"""
        ingredient = self.ingredient_entry.get().strip()
        if ingredient and ingredient not in self.ingredients:
            self.ingredients.append(ingredient)
            self.ingredient_entry.delete(0, tk.END)
            self.refresh_ingredients_display()
            
            # Add to search history
            if ingredient not in self.search_history:
                self.search_history.insert(0, ingredient)
                self.search_history = self.search_history[:10]  # Keep last 10
                self.save_search_history()
        elif ingredient in self.ingredients:
            messagebox.showinfo("Info", "Ingredient already added!")
    
    def save_search_history(self):
        """Save search history to file"""
        try:
            with open('search_history.json', 'w') as f:
                json.dump(self.search_history, f)
        except Exception as e:
            print(f"Error saving search history: {e}")
    
    def remove_ingredient(self):
        """Legacy method for compatibility"""
        pass  # Now handled by remove_ingredient_by_index
        ingredient = self.ingredient_entry.get().strip()
        if ingredient and ingredient not in self.ingredients:
            self.ingredients.append(ingredient)
            self.ingredients_listbox.insert(tk.END, ingredient)
            self.ingredient_entry.delete(0, tk.END)
        elif ingredient in self.ingredients:
            messagebox.showinfo("Info", "Ingredient already added!")
            
    def remove_ingredient(self):
        selection = self.ingredients_listbox.curselection()
        if selection:
            index = selection[0]
            removed_ingredient = self.ingredients.pop(index)
            self.ingredients_listbox.delete(index)
            
    def search_recipes(self):
        """Enhanced search with modern loading and error handling"""
        if not self.ingredients:
            messagebox.showwarning("Warning", "Please add at least one ingredient!")
            return
            
        if not self.api_key:
            messagebox.showerror("Error", "Spoonacular API key not found! Please set SPOONACULAR_API_KEY environment variable.")
            return
        
        # Switch to main view and show loading
        self.switch_view("search")
        self.show_loading_screen("Searching for delicious recipes...")
        
        # Start search in background thread
        thread = threading.Thread(target=self._search_recipes_thread)
        thread.daemon = True
        thread.start()
    
    def show_loading_screen(self, message):
        """Show modern loading screen"""
        theme_colors = self.colors[self.current_theme]
        
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.results_label.configure(text="🔍 Searching Recipes")
        
        # Loading container
        loading_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=theme_colors["card"],
            corner_radius=12
        )
        loading_frame.pack(expand=True, fill="both", padx=50, pady=100)
        
        # Loading content
        ctk.CTkLabel(
            loading_frame,
            text="🍳",
            font=ctk.CTkFont(size=60)
        ).pack(pady=(40, 20))
        
        ctk.CTkLabel(
            loading_frame,
            text=message,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme_colors["text"]
        ).pack(pady=(0, 10))
        
        # Progress bar
        progress = ctk.CTkProgressBar(
            loading_frame,
            width=300,
            height=6,
            corner_radius=3,
            fg_color=theme_colors["hover"],
            progress_color=theme_colors["primary"]
        )
        progress.pack(pady=(20, 40))
        progress.set(0.7)  # Indeterminate progress
        if not self.ingredients:
            messagebox.showwarning("Warning", "Please add at least one ingredient!")
            return
            
        if not self.api_key:
            messagebox.showerror("Error", "Spoonacular API key not found! Please set SPOONACULAR_API_KEY environment variable.")
            return
            
        # Show loading message
        self.results_label.configure(text="Searching for recipes...")
        
        # Start search in background thread
        thread = threading.Thread(target=self._search_recipes_thread)
        thread.daemon = True
        thread.start()
        
    def _search_recipes_thread(self):
        """Enhanced search thread with better error handling"""
        try:
            # Use complexSearch API with enhanced parameters
            ingredients_str = ",".join(self.ingredients)
            params = {
                "apiKey": self.api_key,
                "includeIngredients": ingredients_str,
                "number": 20,  # Increased for better results
                "addRecipeInformation": True,
                "fillIngredients": True,
                "sort": self.advanced_filters.get("sort", "max-used-ingredients"),
                "maxReadyTime": self.advanced_filters.get("max_ready_time", 60)
            }
            
            # Add diet filter if selected
            diet_mapping = {
                "Vegetarian": "vegetarian",
                "Vegan": "vegan", 
                "Gluten Free": "gluten free",
                "Ketogenic": "ketogenic",
                "Paleo": "paleo"
            }
            if self.diet_var.get() != "None":
                params["diet"] = diet_mapping.get(self.diet_var.get(), self.diet_var.get().lower())
                
            # Add cuisine filter if selected
            if self.cuisine_var.get() != "None":
                params["cuisine"] = self.cuisine_var.get().lower()
            
            # Make API request with enhanced timeout
            response = requests.get(f"{self.base_url}/complexSearch", params=params, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                self.recipes = result.get('results', [])
                # Update UI in main thread
                self.root.after(0, self.display_recipes)
            elif response.status_code == 402:
                error_msg = "API quota exceeded. Please try again later or upgrade your Spoonacular plan."
                self.root.after(0, lambda: self.show_error(error_msg))
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f"API Error: {response.status_code}")
                except:
                    error_msg = f"API Error: {response.status_code}"
                self.root.after(0, lambda: self.show_error(error_msg))
                
        except Exception as e:
            error_msg = f"Error searching recipes: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
        try:
            # Use complexSearch API which supports diet and cuisine filters
            ingredients_str = ",".join(self.ingredients)
            params = {
                "apiKey": self.api_key,
                "includeIngredients": ingredients_str,
                "number": 12,
                "addRecipeInformation": True,
                "fillIngredients": True,
                "sort": "max-used-ingredients"
            }
            
            # Add diet filter if selected (map to correct API values)
            diet_mapping = {
                "Vegetarian": "vegetarian",
                "Vegan": "vegan", 
                "Gluten Free": "gluten free",
                "Ketogenic": "ketogenic",
                "Paleo": "paleo"
            }
            if self.diet_var.get() != "None":
                params["diet"] = diet_mapping.get(self.diet_var.get(), self.diet_var.get().lower())
                
            # Add cuisine filter if selected
            if self.cuisine_var.get() != "None":
                params["cuisine"] = self.cuisine_var.get().lower()
            
            # Make API request with timeout
            response = requests.get(f"{self.base_url}/complexSearch", params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.recipes = result.get('results', [])
                # Update UI in main thread
                self.root.after(0, self.display_recipes)
            elif response.status_code == 402:
                error_msg = "API quota exceeded. Please try again later or upgrade your Spoonacular plan."
                self.root.after(0, lambda: self.show_error(error_msg))
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f"API Error: {response.status_code}")
                except:
                    error_msg = f"API Error: {response.status_code}"
                self.root.after(0, lambda: self.show_error(error_msg))
                
        except Exception as e:
            error_msg = f"Error searching recipes: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
            
    def display_recipes(self):
        """Display recipes with modern Windows 11 styling"""
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.recipes:
            self.show_no_results()
            return
            
        self.results_label.configure(text=f"🍽️ Found {len(self.recipes)} delicious recipes")
        
        # Display recipes based on view mode
        if hasattr(self, 'view_mode') and self.view_mode == 'list':
            self.display_recipes_list()
        else:
            self.display_recipes_grid()
    
    def display_recipes_grid(self):
        """Display recipes in modern grid layout"""
        theme_colors = self.colors[self.current_theme]
        
        # Grid container
        grid_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="transparent"
        )
        grid_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configure grid columns (responsive)
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # Display each recipe as a modern card
        for i, recipe in enumerate(self.recipes):
            row = i // 3
            col = i % 3
            self.create_modern_recipe_card(recipe, grid_frame, row, col)
    
    def display_recipes_list(self):
        """Display recipes in modern list layout"""
        for i, recipe in enumerate(self.recipes):
            self.create_modern_recipe_list_item(recipe, i)
    
    def show_no_results(self):
        """Show modern no results screen"""
        theme_colors = self.colors[self.current_theme]
        
        self.results_label.configure(text="🔍 No Recipes Found")
        
        no_results_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=theme_colors["card"],
            corner_radius=12
        )
        no_results_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        ctk.CTkLabel(
            no_results_frame,
            text="🤔",
            font=ctk.CTkFont(size=60)
        ).pack(pady=(40, 20))
        
        ctk.CTkLabel(
            no_results_frame,
            text="No recipes found",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=theme_colors["text"]
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            no_results_frame,
            text="Try different ingredients or adjust your filters",
            font=ctk.CTkFont(size=14),
            text_color=theme_colors["text_secondary"]
        ).pack(pady=(0, 40))
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.recipes:
            self.results_label.configure(text="No recipes found. Try different ingredients!")
            return
            
        self.results_label.configure(text=f"Found {len(self.recipes)} recipes:")
        
        # Display each recipe
        for i, recipe in enumerate(self.recipes):
            self.create_recipe_card(recipe, i)
            
    def create_modern_recipe_card(self, recipe, parent, row, col):
        """Create a modern recipe card with Windows 11 styling"""
        theme_colors = self.colors[self.current_theme]
        
        # Main card frame with modern styling
        card_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["card"],
            corner_radius=12,
            border_width=1,
            border_color=theme_colors["border"]
        )
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Card content frame
        content_frame = ctk.CTkFrame(
            card_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Recipe image with modern styling
        image_frame = ctk.CTkFrame(
            content_frame,
            height=150,
            corner_radius=8,
            fg_color=theme_colors["hover"]
        )
        image_frame.pack(fill="x", pady=(0, 15))
        image_frame.pack_propagate(False)
        
        # Load image in background
        if recipe.get('image'):
            thread = threading.Thread(
                target=self.load_modern_recipe_image, 
                args=(recipe['image'], image_frame, (250, 150))
            )
            thread.daemon = True
            thread.start()
        else:
            self.display_modern_placeholder(image_frame)
        
        # Recipe title
        title_label = ctk.CTkLabel(
            content_frame,
            text=recipe['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme_colors["text"],
            wraplength=200
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Recipe info badges
        self.create_recipe_info_badges(content_frame, recipe)
        
        # Action buttons
        self.create_recipe_action_buttons(content_frame, recipe)
    
    def create_modern_recipe_list_item(self, recipe, index):
        """Create a modern list item for recipes"""
        theme_colors = self.colors[self.current_theme]
        
        # List item frame
        item_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        item_frame.pack(fill="x", padx=15, pady=5)
        
        # Content layout
        content_frame = ctk.CTkFrame(
            item_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=12)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Thumbnail image
        image_frame = ctk.CTkFrame(
            content_frame,
            width=80,
            height=60,
            corner_radius=6,
            fg_color=theme_colors["hover"]
        )
        image_frame.grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky="nw")
        image_frame.pack_propagate(False)
        
        if recipe.get('image'):
            thread = threading.Thread(
                target=self.load_modern_recipe_image,
                args=(recipe['image'], image_frame, (80, 60))
            )
            thread.daemon = True
            thread.start()
        
        # Recipe info
        info_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        info_frame.grid(row=0, column=1, sticky="ew")
        
        # Title
        title_label = ctk.CTkLabel(
            info_frame,
            text=recipe['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme_colors["text"],
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Quick info
        quick_info = self.get_recipe_quick_info(recipe)
        info_label = ctk.CTkLabel(
            info_frame,
            text=quick_info,
            font=ctk.CTkFont(size=12),
            text_color=theme_colors["text_secondary"],
            anchor="w"
        )
        info_label.pack(anchor="w", pady=(5, 0))
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        buttons_frame.grid(row=0, column=2, padx=(15, 0))
        
        self.create_compact_action_buttons(buttons_frame, recipe)
    
    def create_recipe_info_badges(self, parent, recipe):
        """Create modern info badges for recipe"""
        theme_colors = self.colors[self.current_theme]
        
        # Info container
        info_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        info_frame.pack(fill="x", pady=(0, 15))
        
        # Time badge
        ready_time = recipe.get('readyInMinutes', 'N/A')
        if ready_time != 'N/A':
            time_badge = ctk.CTkLabel(
                info_frame,
                text=f"⏱️ {ready_time}min",
                font=ctk.CTkFont(size=11),
                text_color=theme_colors["text_secondary"],
                fg_color=theme_colors["hover"],
                corner_radius=4,
                width=70,
                height=24
            )
            time_badge.pack(side="left", padx=(0, 5))
        
        # Health score badge
        health_score = recipe.get('healthScore', 0)
        if health_score > 0:
            score_color = theme_colors["success"] if health_score >= 70 else theme_colors["warning"] if health_score >= 40 else theme_colors["error"]
            health_badge = ctk.CTkLabel(
                info_frame,
                text=f"💪 {health_score}",
                font=ctk.CTkFont(size=11),
                text_color="white",
                fg_color=score_color,
                corner_radius=4,
                width=60,
                height=24
            )
            health_badge.pack(side="left", padx=(0, 5))
        
        # Servings badge
        servings = recipe.get('servings', 'N/A')
        if servings != 'N/A':
            servings_badge = ctk.CTkLabel(
                info_frame,
                text=f"🍽️ {servings}",
                font=ctk.CTkFont(size=11),
                text_color=theme_colors["text_secondary"],
                fg_color=theme_colors["hover"],
                corner_radius=4,
                width=50,
                height=24
            )
            servings_badge.pack(side="left")
    
    def create_recipe_action_buttons(self, parent, recipe):
        """Create modern action buttons for recipe"""
        theme_colors = self.colors[self.current_theme]
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        buttons_frame.pack(fill="x", pady=(10, 0))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # View details button
        details_btn = ctk.CTkButton(
            buttons_frame,
            text="👁️ View",
            height=35,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=theme_colors["primary"],
            hover_color=theme_colors["accent"],
            command=lambda: self.show_recipe_details(recipe)
        )
        details_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Favorite button
        is_favorite = recipe['id'] in self.favorites
        fav_icon = "❤️" if is_favorite else "🤍"
        fav_btn = ctk.CTkButton(
            buttons_frame,
            text=fav_icon,
            width=35,
            height=35,
            corner_radius=6,
            font=ctk.CTkFont(size=14),
            fg_color=theme_colors["error"] if is_favorite else theme_colors["hover"],
            hover_color=theme_colors["error"],
            text_color="white" if is_favorite else theme_colors["text"],
            command=lambda: self.toggle_favorite(recipe)
        )
        fav_btn.grid(row=0, column=1, padx=(5, 0))
    
    def create_compact_action_buttons(self, parent, recipe):
        """Create compact action buttons for list view"""
        theme_colors = self.colors[self.current_theme]
        
        # View button
        view_btn = ctk.CTkButton(
            parent,
            text="View",
            width=60,
            height=30,
            corner_radius=4,
            font=ctk.CTkFont(size=11),
            fg_color=theme_colors["primary"],
            command=lambda: self.show_recipe_details(recipe)
        )
        view_btn.pack(side="top", pady=(0, 5))
        
        # Favorite button
        is_favorite = recipe['id'] in self.favorites
        fav_icon = "❤️" if is_favorite else "🤍"
        fav_btn = ctk.CTkButton(
            parent,
            text=fav_icon,
            width=30,
            height=30,
            corner_radius=4,
            font=ctk.CTkFont(size=12),
            fg_color=theme_colors["error"] if is_favorite else theme_colors["hover"],
            text_color="white" if is_favorite else theme_colors["text"],
            command=lambda: self.toggle_favorite(recipe)
        )
        fav_btn.pack(side="top")
    
    def get_recipe_quick_info(self, recipe):
        """Get quick info string for recipe"""
        info_parts = []
        
        ready_time = recipe.get('readyInMinutes', 'N/A')
        if ready_time != 'N/A':
            info_parts.append(f"{ready_time} min")
        
        servings = recipe.get('servings', 'N/A')
        if servings != 'N/A':
            info_parts.append(f"{servings} servings")
        
        health_score = recipe.get('healthScore', 0)
        if health_score > 0:
            info_parts.append(f"Health: {health_score}")
        
        return " • ".join(info_parts) if info_parts else "Recipe details"
        # Recipe card frame
        card_frame = ctk.CTkFrame(self.scrollable_frame)
        card_frame.grid(row=index, column=0, sticky="ew", padx=5, pady=5)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Recipe image (placeholder for now)
        image_frame = ctk.CTkFrame(card_frame, width=120, height=80)
        image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        image_frame.grid_propagate(False)
        
        # Load image in background
        if recipe.get('image'):
            thread = threading.Thread(target=self.load_recipe_image, args=(recipe['image'], image_frame))
            thread.daemon = True
            thread.start()
        else:
            placeholder_label = ctk.CTkLabel(image_frame, text="No Image")
            placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Recipe info frame
        info_frame = ctk.CTkFrame(card_frame)
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Recipe title
        title_label = ctk.CTkLabel(
            info_frame,
            text=recipe['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Recipe info based on API response structure
        info_row = 1
        
        # Ready time and servings
        ready_time = recipe.get('readyInMinutes', 'N/A')
        servings = recipe.get('servings', 'N/A') 
        if ready_time != 'N/A' or servings != 'N/A':
            time_text = f"⏱️ {ready_time} min | 🍽️ {servings} servings"
            time_label = ctk.CTkLabel(
                info_frame,
                text=time_text,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w"
            )
            time_label.grid(row=info_row, column=0, sticky="ew", padx=10, pady=2)
            info_row += 1
        
        # Diet and cuisine tags
        tags = []
        if recipe.get('vegetarian'): tags.append("🌱 Vegetarian")
        if recipe.get('vegan'): tags.append("🌿 Vegan")
        if recipe.get('glutenFree'): tags.append("🌾 Gluten Free")
        if recipe.get('dairyFree'): tags.append("🥛 Dairy Free")
        
        if tags:
            tags_text = " | ".join(tags[:2])
            if len(tags) > 2:
                tags_text += f" (+{len(tags) - 2})"
            tags_label = ctk.CTkLabel(
                info_frame,
                text=tags_text,
                font=ctk.CTkFont(size=11),
                text_color="green",
                anchor="w"
            )
            tags_label.grid(row=info_row, column=0, sticky="ew", padx=10, pady=2)
            info_row += 1
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(info_frame)
        buttons_frame.grid(row=info_row, column=0, sticky="ew", padx=10, pady=(10, 10))
        
        # View details button
        details_btn = ctk.CTkButton(
            buttons_frame,
            text="View Details",
            width=100,
            command=lambda r=recipe: self.show_recipe_details(r)
        )
        details_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Favorite button
        is_favorite = recipe['id'] in self.favorites
        fav_text = "★ Favorite" if is_favorite else "☆ Add to Favorites"
        fav_btn = ctk.CTkButton(
            buttons_frame,
            text=fav_text,
            width=120,
            command=lambda r=recipe: self.toggle_favorite(r)
        )
        fav_btn.grid(row=0, column=1, padx=5, pady=5)
        
    def load_modern_recipe_image(self, image_url, image_frame, size=(250, 150)):
        """Load recipe image with modern styling and error handling"""
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                
                # Resize and crop to fit
                image = image.resize(size, Image.Resampling.LANCZOS)
                
                # Apply slight blur for modern look (optional)
                # image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
                
                photo = ImageTk.PhotoImage(image)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_modern_image(photo, image_frame))
            else:
                self.root.after(0, lambda: self.display_modern_placeholder(image_frame))
        except Exception as e:
            print(f"Error loading image: {e}")
            self.root.after(0, lambda: self.display_modern_placeholder(image_frame))
    
    def load_recipe_image(self, image_url, image_frame):
        """Legacy method for compatibility"""
        self.load_modern_recipe_image(image_url, image_frame, (100, 60))
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((100, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_image(photo, image_frame))
            else:
                self.root.after(0, lambda: self.display_placeholder(image_frame))
        except Exception as e:
            print(f"Error loading image: {e}")
            self.root.after(0, lambda: self.display_placeholder(image_frame))
            
    def display_modern_image(self, photo, image_frame):
        """Display image with modern styling"""
        # Clear frame and add image
        for widget in image_frame.winfo_children():
            widget.destroy()
            
        image_label = tk.Label(
            image_frame, 
            image=photo,
            bd=0,
            highlightthickness=0
        )
        # Keep a reference to prevent garbage collection
        image_label._image_ref = photo
        image_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def display_image(self, photo, image_frame):
        """Legacy method for compatibility"""
        self.display_modern_image(photo, image_frame)
        # Clear frame and add image
        for widget in image_frame.winfo_children():
            widget.destroy()
            
        image_label = tk.Label(image_frame, image=photo)
        # Keep a reference to prevent garbage collection
        image_label._image_ref = photo
        image_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def display_modern_placeholder(self, image_frame):
        """Display modern placeholder for missing images"""
        theme_colors = self.colors[self.current_theme]
        
        # Clear frame and add placeholder
        for widget in image_frame.winfo_children():
            widget.destroy()
            
        placeholder_label = ctk.CTkLabel(
            image_frame, 
            text="🍳",
            font=ctk.CTkFont(size=32),
            text_color=theme_colors["text_secondary"]
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def display_placeholder(self, image_frame):
        """Legacy method for compatibility"""
        self.display_modern_placeholder(image_frame)
        # Clear frame and add placeholder
        for widget in image_frame.winfo_children():
            widget.destroy()
            
        placeholder_label = ctk.CTkLabel(image_frame, text="🍽️", font=ctk.CTkFont(size=24))
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def show_recipe_details(self, recipe):
        """Show comprehensive recipe details with modern Windows 11 styling"""
        # Create modern details window
        details_window = ctk.CTkToplevel(self.root)
        details_window.title(f"🍳 {recipe['title']}")
        details_window.geometry("1000x700")
        details_window.transient(self.root)
        
        # Configure colors
        theme_colors = self.colors[self.current_theme]
        details_window.configure(fg_color=theme_colors["background"])
        
        # Get detailed recipe information with nutrition
        self.get_enhanced_recipe_details(recipe['id'], details_window, recipe)
        # Create details window
        details_window = ctk.CTkToplevel(self.root)
        details_window.title(f"Recipe Details - {recipe['title']}")
        details_window.geometry("800x600")
        details_window.transient(self.root)
        
        # Get detailed recipe information
        self.get_recipe_details(recipe['id'], details_window)
        
    def get_enhanced_recipe_details(self, recipe_id, window, basic_recipe):
        """Get enhanced recipe details with nutritional information"""
        theme_colors = self.colors[self.current_theme]
        
        # Show loading screen in details window
        loading_frame = ctk.CTkFrame(
            window,
            fg_color=theme_colors["card"],
            corner_radius=12
        )
        loading_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(
            loading_frame,
            text="🍳",
            font=ctk.CTkFont(size=60)
        ).pack(pady=(50, 20))
        
        ctk.CTkLabel(
            loading_frame,
            text="Loading recipe details...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme_colors["text"]
        ).pack()
        
        # Start loading in background
        thread = threading.Thread(
            target=self._get_enhanced_recipe_details_thread,
            args=(recipe_id, window, basic_recipe, loading_frame)
        )
        thread.daemon = True
        thread.start()
    
    def _get_enhanced_recipe_details_thread(self, recipe_id, window, basic_recipe, loading_frame):
        """Get enhanced recipe details in background thread"""
        try:
            params = {
                "apiKey": self.api_key,
                "includeNutrition": True
            }
            
            response = requests.get(f"{self.base_url}/{recipe_id}/information", params=params, timeout=15)
            
            if response.status_code == 200:
                recipe_data = response.json()
                # Update UI in main thread
                window.after(0, lambda: self.display_enhanced_recipe_details(recipe_data, window, loading_frame))
            else:
                error_msg = f"Error loading recipe details: {response.status_code}"
                window.after(0, lambda: self.show_recipe_error(window, loading_frame, error_msg))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            window.after(0, lambda: self.show_recipe_error(window, loading_frame, error_msg))
    
    def show_recipe_error(self, window, loading_frame, error_msg):
        """Show error in recipe details window"""
        loading_frame.destroy()
        
        error_label = ctk.CTkLabel(
            window,
            text=error_msg,
            font=ctk.CTkFont(size=16),
            text_color=self.colors[self.current_theme]["error"]
        )
        error_label.pack(pady=50)
    
    def get_recipe_details(self, recipe_id, window):
        """Legacy method for compatibility"""
        self.get_enhanced_recipe_details(recipe_id, window, {})
        try:
            params = {
                "apiKey": self.api_key,
                "includeNutrition": True
            }
            
            response = requests.get(f"{self.base_url}/{recipe_id}/information", params=params, timeout=10)
            
            if response.status_code == 200:
                recipe_data = response.json()
                self.display_recipe_details(recipe_data, window)
            else:
                error_label = ctk.CTkLabel(window, text=f"Error loading recipe details: {response.status_code}")
                error_label.pack(pady=20)
                
        except Exception as e:
            error_label = ctk.CTkLabel(window, text=f"Error: {str(e)}")
            error_label.pack(pady=20)
            
    def display_enhanced_recipe_details(self, recipe_data, window, loading_frame):
        """Display comprehensive recipe details with Windows 11 styling"""
        # Remove loading frame
        loading_frame.destroy()
        
        theme_colors = self.colors[self.current_theme]
        
        # Main container with modern styling
        main_container = ctk.CTkFrame(
            window,
            fg_color="transparent"
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left sidebar with quick info and actions
        self.create_recipe_sidebar(main_container, recipe_data)
        
        # Main content area with scrolling
        self.create_recipe_main_content(main_container, recipe_data)
    
    def create_recipe_sidebar(self, parent, recipe_data):
        """Create recipe details sidebar with quick info and actions"""
        theme_colors = self.colors[self.current_theme]
        
        sidebar = ctk.CTkFrame(
            parent,
            width=300,
            fg_color=theme_colors["surface"],
            corner_radius=12,
            border_width=1,
            border_color=theme_colors["border"]
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        sidebar.grid_propagate(False)
        
        # Recipe image
        image_frame = ctk.CTkFrame(
            sidebar,
            height=200,
            corner_radius=8,
            fg_color=theme_colors["hover"]
        )
        image_frame.pack(fill="x", padx=15, pady=(15, 20))
        image_frame.pack_propagate(False)
        
        if recipe_data.get('image'):
            thread = threading.Thread(
                target=self.load_modern_recipe_image,
                args=(recipe_data['image'], image_frame, (270, 200))
            )
            thread.daemon = True
            thread.start()
        else:
            self.display_modern_placeholder(image_frame)
        
        # Quick stats
        self.create_recipe_quick_stats(sidebar, recipe_data)
        
        # Nutritional information
        self.create_nutritional_panel(sidebar, recipe_data)
        
        # Action buttons
        self.create_recipe_detail_actions(sidebar, recipe_data)
    
    def create_recipe_quick_stats(self, parent, recipe_data):
        """Create quick stats panel with visual indicators"""
        theme_colors = self.colors[self.current_theme]
        
        stats_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Stats header
        ctk.CTkLabel(
            stats_frame,
            text="📊 Quick Stats",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme_colors["text"]
        ).pack(pady=(15, 10))
        
        # Stats grid
        stats_grid = ctk.CTkFrame(
            stats_frame,
            fg_color="transparent"
        )
        stats_grid.pack(fill="x", padx=15, pady=(0, 15))
        stats_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Ready time
        ready_time = recipe_data.get('readyInMinutes', 'N/A')
        prep_time = recipe_data.get('preparationMinutes', 'N/A')
        cook_time = recipe_data.get('cookingMinutes', 'N/A')
        
        self.create_stat_item(stats_grid, 0, 0, "⏱️", "Ready Time", f"{ready_time} min")
        self.create_stat_item(stats_grid, 0, 1, "👥", "Servings", str(recipe_data.get('servings', 'N/A')))
        
        if prep_time != 'N/A':
            self.create_stat_item(stats_grid, 1, 0, "🔪", "Prep Time", f"{prep_time} min")
        if cook_time != 'N/A':
            self.create_stat_item(stats_grid, 1, 1, "🍳", "Cook Time", f"{cook_time} min")
        
        # Health score with visual indicator
        health_score = recipe_data.get('healthScore', 0)
        self.create_health_score_indicator(stats_grid, health_score)
        
        # Difficulty indicator (estimated from various factors)
        difficulty = self.calculate_recipe_difficulty(recipe_data)
        self.create_difficulty_indicator(stats_grid, difficulty)
    
    def create_stat_item(self, parent, row, col, icon, label, value):
        """Create a single stat item"""
        theme_colors = self.colors[self.current_theme]
        
        item_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["hover"],
            corner_radius=6,
            height=60
        )
        item_frame.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        item_frame.pack_propagate(False)
        
        # Icon
        ctk.CTkLabel(
            item_frame,
            text=icon,
            font=ctk.CTkFont(size=20)
        ).pack(pady=(8, 0))
        
        # Label
        ctk.CTkLabel(
            item_frame,
            text=label,
            font=ctk.CTkFont(size=10),
            text_color=theme_colors["text_secondary"]
        ).pack()
        
        # Value
        ctk.CTkLabel(
            item_frame,
            text=str(value),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme_colors["text"]
        ).pack()
    
    def create_health_score_indicator(self, parent, health_score):
        """Create visual health score indicator"""
        theme_colors = self.colors[self.current_theme]
        
        # Determine color based on score
        if health_score >= 70:
            score_color = theme_colors["success"]
            score_text = "Excellent"
        elif health_score >= 50:
            score_color = theme_colors["warning"]
            score_text = "Good"
        elif health_score >= 30:
            score_color = theme_colors["warning"]
            score_text = "Fair"
        else:
            score_color = theme_colors["error"]
            score_text = "Poor"
        
        health_frame = ctk.CTkFrame(
            parent,
            fg_color=score_color,
            corner_radius=6,
            height=60
        )
        health_frame.grid(row=2, column=0, columnspan=2, padx=2, pady=5, sticky="ew")
        health_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            health_frame,
            text="💪 Health Score",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(pady=(8, 0))
        
        ctk.CTkLabel(
            health_frame,
            text=f"{health_score}/100 - {score_text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack()
    
    def create_difficulty_indicator(self, parent, difficulty):
        """Create difficulty level indicator"""
        theme_colors = self.colors[self.current_theme]
        
        difficulty_colors = {
            "Easy": theme_colors["success"],
            "Medium": theme_colors["warning"],
            "Hard": theme_colors["error"]
        }
        
        difficulty_frame = ctk.CTkFrame(
            parent,
            fg_color=difficulty_colors.get(difficulty, theme_colors["hover"]),
            corner_radius=6,
            height=50
        )
        difficulty_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=5, sticky="ew")
        difficulty_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            difficulty_frame,
            text=f"📈 Difficulty: {difficulty}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white" if difficulty != "Easy" else theme_colors["text"]
        ).pack(expand=True)
    
    def calculate_recipe_difficulty(self, recipe_data):
        """Calculate recipe difficulty based on various factors"""
        # Simple difficulty calculation based on:
        # - Number of ingredients
        # - Cooking time
        # - Number of steps
        
        ingredients_count = len(recipe_data.get('extendedIngredients', []))
        ready_time = recipe_data.get('readyInMinutes', 0)
        instructions = recipe_data.get('analyzedInstructions', [])
        steps_count = sum(len(inst.get('steps', [])) for inst in instructions)
        
        difficulty_score = 0
        
        # Factor in ingredients (more = harder)
        if ingredients_count > 15:
            difficulty_score += 2
        elif ingredients_count > 8:
            difficulty_score += 1
        
        # Factor in time (longer = harder)
        if ready_time > 120:
            difficulty_score += 2
        elif ready_time > 60:
            difficulty_score += 1
        
        # Factor in steps (more = harder)
        if steps_count > 10:
            difficulty_score += 2
        elif steps_count > 5:
            difficulty_score += 1
        
        # Return difficulty level
        if difficulty_score >= 4:
            return "Hard"
        elif difficulty_score >= 2:
            return "Medium"
        else:
            return "Easy"
    def create_nutritional_panel(self, parent, recipe_data):
        """Create comprehensive nutritional information panel"""
        theme_colors = self.colors[self.current_theme]
        
        nutrition_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        nutrition_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Nutrition header
        ctk.CTkLabel(
            nutrition_frame,
            text="🥗 Nutrition Facts",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme_colors["text"]
        ).pack(pady=(15, 10))
        
        # Get nutritional data
        nutrition = recipe_data.get('nutrition', {})
        nutrients = nutrition.get('nutrients', [])
        
        if not nutrients:
            ctk.CTkLabel(
                nutrition_frame,
                text="Nutritional information not available",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"]
            ).pack(pady=20)
            return
        
        # Create nutrition grid
        nutrition_grid = ctk.CTkFrame(
            nutrition_frame,
            fg_color="transparent"
        )
        nutrition_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        # Key nutrients to display
        key_nutrients = {
            'Calories': '🔥',
            'Protein': '🥩',
            'Carbohydrates': '🍞',
            'Fat': '🧈',
            'Fiber': '🌿',
            'Sugar': '🍬',
            'Sodium': '🧂',
            'Cholesterol': '❤️'
        }
        
        # Create nutrient items
        nutrients_dict = {n['name']: n for n in nutrients}
        row = 0
        
        for nutrient_name, icon in key_nutrients.items():
            if nutrient_name in nutrients_dict:
                nutrient = nutrients_dict[nutrient_name]
                amount = nutrient.get('amount', 0)
                unit = nutrient.get('unit', '')
                
                self.create_nutrition_item(
                    nutrition_grid, row, icon, nutrient_name, 
                    f"{amount:.1f} {unit}"
                )
                row += 1
    
    def create_nutrition_item(self, parent, row, icon, name, value):
        """Create a single nutrition item"""
        theme_colors = self.colors[self.current_theme]
        
        item_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["hover"],
            corner_radius=4,
            height=35
        )
        item_frame.grid(row=row, column=0, pady=1, sticky="ew")
        item_frame.pack_propagate(False)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        ctk.CTkLabel(
            item_frame,
            text=icon,
            font=ctk.CTkFont(size=14),
            width=30
        ).grid(row=0, column=0, padx=(10, 5), pady=8)
        
        # Name
        ctk.CTkLabel(
            item_frame,
            text=name,
            font=ctk.CTkFont(size=11),
            text_color=theme_colors["text"],
            anchor="w"
        ).grid(row=0, column=1, sticky="w", pady=8)
        
        # Value
        ctk.CTkLabel(
            item_frame,
            text=value,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme_colors["text"]
        ).grid(row=0, column=2, padx=(5, 10), pady=8)
    
    def create_recipe_detail_actions(self, parent, recipe_data):
        """Create action buttons for recipe details"""
        theme_colors = self.colors[self.current_theme]
        
        actions_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        actions_frame.pack(fill="x", padx=15, pady=15)
        
        # Favorite button
        is_favorite = recipe_data['id'] in self.favorites
        fav_text = "❤️ Remove from Favorites" if is_favorite else "🤍 Add to Favorites"
        fav_btn = ctk.CTkButton(
            actions_frame,
            text=fav_text,
            height=40,
            corner_radius=8,
            fg_color=theme_colors["error"] if is_favorite else theme_colors["primary"],
            hover_color=theme_colors["error"] if is_favorite else theme_colors["accent"],
            command=lambda: self.toggle_favorite_and_update(recipe_data, fav_btn)
        )
        fav_btn.pack(fill="x", pady=(0, 10))
        
        # Scale recipe button
        scale_btn = ctk.CTkButton(
            actions_frame,
            text="📎 Scale Recipe",
            height=40,
            corner_radius=8,
            fg_color=theme_colors["hover"],
            hover_color=theme_colors["primary"],
            text_color=theme_colors["text"],
            command=lambda: self.show_recipe_scaling(recipe_data)
        )
        scale_btn.pack(fill="x", pady=(0, 10))
        
        # Export options
        export_frame = ctk.CTkFrame(
            actions_frame,
            fg_color="transparent"
        )
        export_frame.pack(fill="x")
        export_frame.grid_columnconfigure((0, 1), weight=1)
        
        export_pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 PDF",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["success"],
            command=lambda: self.export_recipe_pdf(recipe_data)
        )
        export_pdf_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        export_text_btn = ctk.CTkButton(
            export_frame,
            text="📝 Text",
            height=35,
            corner_radius=6,
            fg_color=theme_colors["warning"],
            command=lambda: self.export_recipe_text(recipe_data)
        )
        export_text_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
    
    def toggle_favorite_and_update(self, recipe, button):
        """Toggle favorite and update button text"""
        theme_colors = self.colors[self.current_theme]
        
        self.toggle_favorite(recipe)
        
        # Update button
        is_favorite = recipe['id'] in self.favorites
        fav_text = "❤️ Remove from Favorites" if is_favorite else "🤍 Add to Favorites"
        button.configure(
            text=fav_text,
            fg_color=theme_colors["error"] if is_favorite else theme_colors["primary"]
        )
    
    def display_recipe_details(self, recipe_data, window):
        """Legacy method for compatibility"""
        # Use enhanced method instead
        loading_frame = ctk.CTkFrame(window)
        self.display_enhanced_recipe_details(recipe_data, window, loading_frame)
        
    def create_recipe_main_content(self, parent, recipe_data):
        """Create main content area with ingredients and instructions"""
        theme_colors = self.colors[self.current_theme]
        
        # Main content frame
        content_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color=theme_colors["surface"],
            corner_radius=12,
            border_width=1,
            border_color=theme_colors["border"]
        )
        content_frame.grid(row=0, column=1, sticky="nsew")
        
        # Recipe header
        header_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        # Recipe title
        title_label = ctk.CTkLabel(
            header_frame,
            text=recipe_data['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=theme_colors["text"],
            wraplength=600
        )
        title_label.pack(anchor="w")
        
        # Recipe summary/description
        summary = recipe_data.get('summary', '')
        if summary:
            # Clean HTML tags from summary
            clean_summary = re.sub('<.*?>', '', summary)
            summary_label = ctk.CTkLabel(
                header_frame,
                text=clean_summary[:300] + "..." if len(clean_summary) > 300 else clean_summary,
                font=ctk.CTkFont(size=14),
                text_color=theme_colors["text_secondary"],
                wraplength=600,
                justify="left"
            )
            summary_label.pack(anchor="w", pady=(10, 0))
        
        # Recipe metadata
        self.create_recipe_metadata(content_frame, recipe_data)
        
        # Ingredients section
        self.create_enhanced_ingredients_section(content_frame, recipe_data)
        
        # Instructions section
        self.create_enhanced_instructions_section(content_frame, recipe_data)
        
        # Wine pairing and additional info
        self.create_additional_info_section(content_frame, recipe_data)
        
    def create_recipe_metadata(self, parent, recipe_data):
        """Create recipe metadata section"""
        theme_colors = self.colors[self.current_theme]
        
        # Metadata badges
        metadata_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        metadata_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        badges_container = ctk.CTkFrame(
            metadata_frame,
            fg_color="transparent"
        )
        badges_container.pack(anchor="w")
        
        # Cuisine type
        cuisines = recipe_data.get('cuisines', [])
        if cuisines:
            cuisine_badge = ctk.CTkLabel(
                badges_container,
                text=f"🌍 {cuisines[0]}",
                font=ctk.CTkFont(size=11),
                text_color="white",
                fg_color=theme_colors["primary"],
                corner_radius=12,
                width=80,
                height=24
            )
            cuisine_badge.pack(side="left", padx=(0, 8))
        
        # Diet types
        diet_types = []
        if recipe_data.get('vegetarian'): diet_types.append('Vegetarian')
        if recipe_data.get('vegan'): diet_types.append('Vegan')
        if recipe_data.get('glutenFree'): diet_types.append('Gluten Free')
        
        for diet in diet_types[:2]:  # Show max 2 diet badges
            diet_badge = ctk.CTkLabel(
                badges_container,
                text=f"🌱 {diet}",
                font=ctk.CTkFont(size=11),
                text_color="white",
                fg_color=theme_colors["success"],
                corner_radius=12,
                height=24
            )
            diet_badge.pack(side="left", padx=(0, 8))
        
        # Source attribution
        source_url = recipe_data.get('sourceUrl', '')
        source_name = recipe_data.get('sourceName', '')
        if source_name:
            source_label = ctk.CTkLabel(
                metadata_frame,
                text=f"📚 Recipe from: {source_name}",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"]
            )
            source_label.pack(anchor="w", pady=(10, 0))
        
    def create_enhanced_ingredients_section(self, parent, recipe_data):
        """Create enhanced ingredients section with modern styling"""
        theme_colors = self.colors[self.current_theme]
        
        # Ingredients header
        ingredients_header = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        ingredients_header.pack(fill="x", padx=20, pady=(0, 10))
        ingredients_header.grid_columnconfigure(0, weight=1)
        
        ingredients_label = ctk.CTkLabel(
            ingredients_header,
            text="🥬 Ingredients",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=theme_colors["text"]
        )
        ingredients_label.grid(row=0, column=0, sticky="w")
        
        # Servings adjuster
        servings_frame = ctk.CTkFrame(
            ingredients_header,
            fg_color=theme_colors["hover"],
            corner_radius=8
        )
        servings_frame.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(
            servings_frame,
            text="Servings:",
            font=ctk.CTkFont(size=12),
            text_color=theme_colors["text"]
        ).pack(side="left", padx=(10, 5), pady=8)
        
        self.servings_var = tk.StringVar(value=str(recipe_data.get('servings', 4)))
        servings_entry = ctk.CTkEntry(
            servings_frame,
            textvariable=self.servings_var,
            width=50,
            height=30,
            corner_radius=4,
            font=ctk.CTkFont(size=12)
        )
        servings_entry.pack(side="left", padx=(0, 5), pady=8)
        
        scale_btn = ctk.CTkButton(
            servings_frame,
            text="🔄",
            width=30,
            height=30,
            corner_radius=4,
            fg_color=theme_colors["primary"],
            command=lambda: self.scale_ingredients(recipe_data)
        )
        scale_btn.pack(side="left", padx=(0, 10), pady=8)
        
        # Ingredients container
        ingredients_container = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        ingredients_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Store original servings for scaling
        self.original_servings = recipe_data.get('servings', 4)
        self.scaled_ingredients = recipe_data.get('extendedIngredients', [])
        
        # Create ingredients list
        self.ingredients_display_frame = ctk.CTkFrame(
            ingredients_container,
            fg_color="transparent"
        )
        self.ingredients_display_frame.pack(fill="x", padx=15, pady=15)
        
        self.display_ingredients_list(recipe_data.get('extendedIngredients', []))
    
    def display_ingredients_list(self, ingredients):
        """Display ingredients list with modern styling"""
        theme_colors = self.colors[self.current_theme]
        
        # Clear existing ingredients
        for widget in self.ingredients_display_frame.winfo_children():
            widget.destroy()
        
        if not ingredients:
            ctk.CTkLabel(
                self.ingredients_display_frame,
                text="No ingredients information available",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"]
            ).pack(pady=10)
            return
        
        # Group ingredients by aisle (if available) or show as list
        for i, ingredient in enumerate(ingredients):
            ingredient_item = ctk.CTkFrame(
                self.ingredients_display_frame,
                fg_color=theme_colors["hover"],
                corner_radius=4,
                height=40
            )
            ingredient_item.pack(fill="x", pady=2)
            ingredient_item.pack_propagate(False)
            ingredient_item.grid_columnconfigure(1, weight=1)
            
            # Checkbox for shopping list
            checkbox = ctk.CTkCheckBox(
                ingredient_item,
                text="",
                width=20,
                corner_radius=3
            )
            checkbox.grid(row=0, column=0, padx=(15, 10), pady=10)
            
            # Ingredient text
            ingredient_text = ingredient.get('original', ingredient.get('name', 'Unknown ingredient'))
            ing_label = ctk.CTkLabel(
                ingredient_item,
                text=f"• {ingredient_text}",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text"],
                anchor="w"
            )
            ing_label.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
            
            # Amount/unit info
            amount = ingredient.get('amount', '')
            unit = ingredient.get('unit', '')
            if amount and unit:
                amount_label = ctk.CTkLabel(
                    ingredient_item,
                    text=f"{amount} {unit}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=theme_colors["primary"]
                )
                amount_label.grid(row=0, column=2, padx=(10, 15), pady=10)
        
    def scale_ingredients(self, recipe_data):
        """Scale ingredients based on servings"""
        try:
            new_servings = int(self.servings_var.get())
            if new_servings <= 0:
                raise ValueError("Servings must be positive")
            
            scale_factor = new_servings / self.original_servings
            
            # Scale ingredients
            scaled_ingredients = []
            for ingredient in recipe_data.get('extendedIngredients', []):
                scaled_ingredient = ingredient.copy()
                if 'amount' in scaled_ingredient and scaled_ingredient['amount']:
                    scaled_ingredient['amount'] = round(scaled_ingredient['amount'] * scale_factor, 2)
                    
                    # Update original text with new amount
                    original = ingredient.get('original', '')
                    if original and 'amount' in ingredient:
                        old_amount = str(ingredient['amount'])
                        new_amount = str(scaled_ingredient['amount'])
                        scaled_ingredient['original'] = original.replace(old_amount, new_amount, 1)
                
                scaled_ingredients.append(scaled_ingredient)
            
            # Update display
            self.display_ingredients_list(scaled_ingredients)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of servings")
            self.servings_var.set(str(self.original_servings))
        
    def create_enhanced_instructions_section(self, parent, recipe_data):
        """Create enhanced instructions section with step-by-step styling"""
        theme_colors = self.colors[self.current_theme]
        
        # Instructions header
        instructions_label = ctk.CTkLabel(
            parent,
            text="📄 Instructions",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=theme_colors["text"]
        )
        instructions_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Instructions container
        instructions_container = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["card"],
            corner_radius=8,
            border_width=1,
            border_color=theme_colors["border"]
        )
        instructions_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Get and display instructions
        instructions = recipe_data.get('instructions', '')
        analyzed_instructions = recipe_data.get('analyzedInstructions', [])
        
        if analyzed_instructions:
            # Use analyzed instructions for better formatting
            for instruction_group in analyzed_instructions:
                steps = instruction_group.get('steps', [])
                for step in steps:
                    self.create_instruction_step(
                        instructions_container,
                        step['number'],
                        step['step']
                    )
        elif instructions:
            # Fallback to raw instructions
            clean_instructions = re.sub('<.*?>', '', instructions)
            steps = clean_instructions.split('. ')
            for i, step in enumerate(steps, 1):
                if step.strip():
                    self.create_instruction_step(instructions_container, i, step.strip())
        else:
            # No instructions available
            ctk.CTkLabel(
                instructions_container,
                text="No instructions available",
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"]
            ).pack(pady=20)
    
    def create_instruction_step(self, parent, step_number, step_text):
        """Create a single instruction step with modern styling"""
        theme_colors = self.colors[self.current_theme]
        
        step_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_colors["hover"],
            corner_radius=6
        )
        step_frame.pack(fill="x", padx=15, pady=5)
        step_frame.grid_columnconfigure(1, weight=1)
        
        # Step number
        number_frame = ctk.CTkFrame(
            step_frame,
            width=40,
            height=40,
            corner_radius=20,
            fg_color=theme_colors["primary"]
        )
        number_frame.grid(row=0, column=0, padx=15, pady=15, sticky="n")
        number_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            number_frame,
            text=str(step_number),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Step text
        step_label = ctk.CTkLabel(
            step_frame,
            text=step_text,
            font=ctk.CTkFont(size=13),
            text_color=theme_colors["text"],
            wraplength=500,
            anchor="w",
            justify="left"
        )
        step_label.grid(row=0, column=1, sticky="ew", padx=(10, 15), pady=15)
    
    def create_additional_info_section(self, parent, recipe_data):
        """Create additional information section"""
        theme_colors = self.colors[self.current_theme]
        
        # Wine pairing
        wine_pairing = recipe_data.get('winePairing', {})
        if wine_pairing and wine_pairing.get('pairingText'):
            wine_section = ctk.CTkFrame(
                parent,
                fg_color=theme_colors["card"],
                corner_radius=8,
                border_width=1,
                border_color=theme_colors["border"]
            )
            wine_section.pack(fill="x", padx=20, pady=(0, 20))
            
            ctk.CTkLabel(
                wine_section,
                text="🍷 Wine Pairing",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=theme_colors["text"]
            ).pack(anchor="w", padx=15, pady=(15, 10))
            
            wine_text = wine_pairing.get('pairingText', '')
            ctk.CTkLabel(
                wine_section,
                text=wine_text,
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"],
                wraplength=600,
                anchor="w",
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Equipment needed (if available)
        equipment = recipe_data.get('equipment', [])
        if equipment:
            equipment_section = ctk.CTkFrame(
                parent,
                fg_color=theme_colors["card"],
                corner_radius=8,
                border_width=1,
                border_color=theme_colors["border"]
            )
            equipment_section.pack(fill="x", padx=20, pady=(0, 20))
            
            ctk.CTkLabel(
                equipment_section,
                text="🔧 Equipment Needed",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=theme_colors["text"]
            ).pack(anchor="w", padx=15, pady=(15, 10))
            
            equipment_text = ", ".join([eq.get('name', '') for eq in equipment if eq.get('name')])
            ctk.CTkLabel(
                equipment_section,
                text=equipment_text,
                font=ctk.CTkFont(size=12),
                text_color=theme_colors["text_secondary"],
                wraplength=600,
                anchor="w"
            ).pack(anchor="w", padx=15, pady=(0, 15))
        
    def show_recipe_scaling(self, recipe_data):
        """Show recipe scaling dialog"""
        scaling_window = ctk.CTkToplevel(self.root)
        scaling_window.title("Scale Recipe")
        scaling_window.geometry("400x300")
        scaling_window.transient(self.root)
        
        theme_colors = self.colors[self.current_theme]
        scaling_window.configure(fg_color=theme_colors["background"])
        
        # Scaling content
        content_frame = ctk.CTkFrame(
            scaling_window,
            fg_color=theme_colors["surface"]
        )
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content_frame,
            text="📎 Scale Recipe",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Current servings
        current_servings = recipe_data.get('servings', 4)
        ctk.CTkLabel(
            content_frame,
            text=f"Current servings: {current_servings}",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        # New servings input
        ctk.CTkLabel(
            content_frame,
            text="New servings:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(20, 5))
        
        new_servings_var = tk.StringVar(value=str(current_servings))
        servings_entry = ctk.CTkEntry(
            content_frame,
            textvariable=new_servings_var,
            width=100,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        servings_entry.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Apply Scaling",
            width=120,
            height=40,
            fg_color=theme_colors["primary"],
            command=lambda: self.apply_scaling(recipe_data, new_servings_var.get(), scaling_window)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=40,
            fg_color=theme_colors["hover"],
            text_color=theme_colors["text"],
            command=scaling_window.destroy
        ).pack(side="left")
    
    def apply_scaling(self, recipe_data, new_servings_str, window):
        """Apply recipe scaling"""
        try:
            new_servings = int(new_servings_str)
            if new_servings <= 0:
                raise ValueError()
            
            # Update servings in the recipe details window
            self.servings_var.set(new_servings_str)
            self.scale_ingredients(recipe_data)
            
            window.destroy()
            messagebox.showinfo("Success", f"Recipe scaled to {new_servings} servings!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of servings")
    
    def export_recipe_pdf(self, recipe_data):
        """Export recipe to PDF (placeholder for now)"""
        messagebox.showinfo("Export PDF", "PDF export feature coming soon!")
    
    def export_recipe_text(self, recipe_data):
        """Export recipe to text file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Recipe"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write recipe title
                    f.write(f"{recipe_data['title']}\n")
                    f.write("=" * len(recipe_data['title']) + "\n\n")
                    
                    # Write basic info
                    f.write(f"Servings: {recipe_data.get('servings', 'N/A')}\n")
                    f.write(f"Ready in: {recipe_data.get('readyInMinutes', 'N/A')} minutes\n")
                    f.write(f"Health Score: {recipe_data.get('healthScore', 'N/A')}/100\n\n")
                    
                    # Write ingredients
                    f.write("INGREDIENTS:\n")
                    f.write("-" * 12 + "\n")
                    for ingredient in recipe_data.get('extendedIngredients', []):
                        ing_text = ingredient.get('original', ingredient.get('name', 'Unknown ingredient'))
                        f.write(f"• {ing_text}\n")
                    
                    f.write("\n")
                    
                    # Write instructions
                    f.write("INSTRUCTIONS:\n")
                    f.write("-" * 13 + "\n")
                    
                    instructions = recipe_data.get('instructions', '')
                    if recipe_data.get('analyzedInstructions'):
                        for instruction_group in recipe_data['analyzedInstructions']:
                            for step in instruction_group.get('steps', []):
                                f.write(f"{step['number']}. {step['step']}\n\n")
                    elif instructions:
                        clean_instructions = re.sub('<.*?>', '', instructions)
                        f.write(clean_instructions + "\n")
                    else:
                        f.write("No instructions available.\n")
                
                messagebox.showinfo("Success", f"Recipe saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recipe: {str(e)}")
        
    def toggle_favorite(self, recipe):
        """Enhanced toggle favorite with better state management"""
        recipe_id = recipe['id']
        if recipe_id in self.favorites:
            self.favorites.remove(recipe_id)
            # If viewing favorites, remove from current display
            if self.current_view == "favorites":
                self.recipes = [r for r in self.recipes if r['id'] != recipe_id]
        else:
            self.favorites.append(recipe_id)
        
        self.save_favorites()
        
        # Refresh the appropriate display only if we're in the main view
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
            if self.current_view == "favorites":
                self.display_favorites()
            elif self.recipes:  # Only refresh if we have recipes to display
                self.display_recipes()
        recipe_id = recipe['id']
        if recipe_id in self.favorites:
            self.favorites.remove(recipe_id)
            # If viewing favorites, remove from current display
            if self.current_view == "favorites":
                self.recipes = [r for r in self.recipes if r['id'] != recipe_id]
        else:
            self.favorites.append(recipe_id)
        
        self.save_favorites()
        # Refresh the appropriate display
        if self.current_view == "favorites":
            self.display_favorites()
        else:
            self.display_recipes()
        
    def load_favorites(self):
        try:
            if os.path.exists('favorites.json'):
                with open('favorites.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
        
    def save_favorites(self):
        try:
            with open('favorites.json', 'w') as f:
                json.dump(self.favorites, f)
        except Exception as e:
            print(f"Error saving favorites: {e}")
            
    def show_favorites(self):
        if not self.favorites:
            self.results_label.configure(text="No favorite recipes saved yet!")
            # Clear the scrollable frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            return
            
        self.current_view = "favorites"
        self.results_label.configure(text="Loading your favorite recipes...")
        
        # Start loading favorites in background
        thread = threading.Thread(target=self._load_favorites_thread)
        thread.daemon = True
        thread.start()
        
    def _load_favorites_thread(self):
        try:
            if not self.favorites:
                self.root.after(0, self.display_favorites)
                return
                
            # Use bulk API for efficiency
            params = {
                "apiKey": self.api_key,
                "ids": ",".join(map(str, self.favorites)),
                "includeNutrition": False
            }
            
            response = requests.get(f"{self.base_url}/informationBulk", params=params, timeout=10)
            
            if response.status_code == 200:
                self.recipes = response.json()
                self.root.after(0, self.display_favorites)
            elif response.status_code == 402:
                error_msg = "API quota exceeded. Please try again later or upgrade your Spoonacular plan."
                self.root.after(0, lambda: self.show_error(error_msg))
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f"API Error: {response.status_code}")
                except:
                    error_msg = f"API Error: {response.status_code}"
                self.root.after(0, lambda: self.show_error(error_msg))
            
        except Exception as e:
            error_msg = f"Error loading favorites: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
            
    def display_favorites(self):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.recipes:
            self.results_label.configure(text="No favorite recipes found!")
            return
            
        self.results_label.configure(text=f"Your {len(self.recipes)} favorite recipes:")
        
        # Display each favorite recipe
        for i, recipe in enumerate(self.recipes):
            self.create_recipe_card(recipe, i)
        
    def show_error(self, message):
        self.results_label.configure(text="Error occurred while searching.")
        messagebox.showerror("Error", message)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RecipeSearchApp()
    app.run()