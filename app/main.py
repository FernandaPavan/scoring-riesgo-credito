import streamlit as st
import os  # <--- Faltava este!
import sys
import pandas as pd
import numpy as np
import scorecardpy as sc
import plotly.graph_objects as go

# Ajuste de caminho para localizar a pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles import apply_custom_styles
from src.loader import load_assets
from src.policy import get_score, apply_business_policy