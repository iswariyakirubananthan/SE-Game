"""
routes/home.py - Public Landing Page Blueprint
=============================================
Demonstrates:
  - Module 1: Home Page
  - Colorful gaming-themed introduction
  - Seamless navigation to Register, Login, and Play
"""

from flask import Blueprint, render_template, session, redirect, url_for

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    """
    Renders the public landing page.
    If the player is already logged in, provides quick links directly to the dashboard.
    """
    return render_template('index.html')
