import streamlit as st

# Set page config
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html, body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(to right, #dbeafe, #f0f9ff);
      color: #222;
    }

    .marquee {
      background-color: #003b5c;
      color: white;
      padding: 0.5rem 0;
      text-align: center;
      font-weight: bold;
      font-size: 2.5rem;
    }

    header {
      background-color: #003b5c;
      padding: 1rem 2rem;
      color: white;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    .navbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
    }

    .nav-links {
      list-style: none;
      display: flex;
      gap: 1.5rem;
    }

    .nav-links a {
      color: white;
      text-decoration: none;
      font-weight: 500;
      transition: color 0.3s ease;
    }

    .nav-links a:hover {
      color: #00c3ff;
    }

    .hero {
      background: url('https://images.unsplash.com/photo-1589884490000-5fc209c56a4b') no-repeat center center/cover;
      height: 70vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }

    .hero-content {
      background-color: rgba(0, 0, 0, 0.55);
      padding: 3rem;
      border-radius: 16px;
      color: white;
      max-width: 700px;
    }

    .hero h1 {
      font-size: 2.5rem;
      margin-bottom: 1rem;
      font-weight: 700;
    }

    .hero p {
      font-size: 1.25rem;
    }

    .cta-button {
      display: inline-block;
      margin-top: 2rem;
      padding: 0.75rem 1.5rem;
      background-color: #00c3ff;
      color: white;
      border: none;
      border-radius: 25px;
      text-decoration: none;
      font-weight: bold;
      transition: background-color 0.3s ease;
    }

    .cta-button:hover {
      background-color: #008fb3;
    }

    .dashboard {
      padding: 4rem 2rem;
      background-color: #f9fbfc;
      text-align: center;
    }

    .dashboard h2 {
      font-size: 2rem;
      margin-bottom: 2rem;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 2rem;
      padding: 1rem 0;
    }

    .card {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
      font-size: 1.25rem;
      font-weight: 600;
      transition: transform 0.2s ease;
    }

    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }

    footer {
      background-color: #003b5c;
      color: white;
      text-align: center;
      padding: 1rem;
      font-size: 0.9rem;
      margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Marquee
st.markdown("""<div class="marquee"><marquee>WELCOME TO KENYA WRF WEATHER EXPLORER</marquee></div>""", unsafe_allow_html=True)


# Hero Section
st.markdown("""
<section class="hero">
  <div class="hero-content">
    <h1>KENYA WRF WEATHER EXPLORER</h1>
    <p>Visualize temperature, rainfall, humidity, and wind data over your region.</p>
  </div>
</section>
""", unsafe_allow_html=True)

# Dashboard
st.markdown("""
<section id="dashboard" class="dashboard">
  <h2>Dashboard Overview</h2>
  <div class="cards">
    <div class="card">🌡 Temperature</div>
    <div class="card">🌧 Rainfall</div>
    <div class="card">💧 Humidity</div>
    <div class="card">🌬 Wind Speed</div>
  </div>
</section>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<footer>
  <p>&copy; 2025 Weather Dashboard. All rights reserved.</p>
</footer>
""", unsafe_allow_html=True)
