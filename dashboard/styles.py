import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

def apply_page_styling():
    """Injects high-end, premium SaaS styling to make the Streamlit app feel human-designed."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Font rules */
        html, body, [class*="css"], .stText, .stMarkdown {
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Clean background and container alignment */
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Glassmorphism sidebar customization */
        [data-testid="stSidebar"] {
            background-color: #0d1222 !important;
            border-right: 1px solid #1e293b !important;
        }
        
        /* Styled subheaders and title tags */
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
            color: #ffffff !important;
        }
        
        /* Custom card elements */
        .custom-card {
            background: rgba(21, 29, 48, 0.6) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .custom-card:hover {
            transform: translateY(-2px);
            border-color: rgba(96, 165, 250, 0.3);
            box-shadow: 0 12px 40px 0 rgba(96, 165, 250, 0.1);
        }

        /* Style native Streamlit container borders */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(21, 29, 48, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 24px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15) !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(96, 165, 250, 0.3) !important;
            box-shadow: 0 12px 40px 0 rgba(96, 165, 250, 0.1) !important;
        }
        
        /* Clean metrics override */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #60a5fa !important;
        }
        
        /* Premium custom warning & alerts */
        .alert-box {
            border-left: 4px solid #3b82f6;
            background-color: #1e293b;
            padding: 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 20px;
        }
        
        /* Styled tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #151d30 !important;
            border: 1px solid #1e293b !important;
            border-radius: 6px 6px 0 0 !important;
            padding: 10px 20px !important;
            color: #94a3b8 !important;
            font-weight: 500 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1d4ed8 !important;
            color: #ffffff !important;
            border-color: #3b82f6 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_plotly_theme(fig):
    """Applies a professional, high-contrast Slate color scheme and removes default chart clutter."""
    colors = ['#6366f1', '#10b981', '#f59e0b', '#3b82f6', '#ec4899', '#f43f5e', '#8b5cf6']
    
    # Update chart colors if it's a bar, pie, line, etc.
    if hasattr(fig, 'data'):
        for i, trace in enumerate(fig.data):
            if trace.type == 'pie':
                if hasattr(trace, 'marker') and trace.marker:
                    trace.marker.colors = colors
            else:
                if hasattr(trace, 'marker') and trace.marker:
                    try:
                        # Only assign individual colors if not already defined
                        if not getattr(trace.marker, 'color', None):
                            trace.marker.color = colors[i % len(colors)]
                    except Exception:
                        pass
                
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Outfit, sans-serif",
            size=12,
            color="#94a3b8"
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1e293b",
            zeroline=False,
            title_font=dict(color="#f3f4f6", size=13),
            tickfont=dict(color="#94a3b8")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1e293b",
            zeroline=False,
            title_font=dict(color="#f3f4f6", size=13),
            tickfont=dict(color="#94a3b8")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.05)",
            font=dict(color="#94a3b8")
        )
    )
    return fig

def render_kpi_card(title, value, trend_text, trend_direction="up", icon_svg=""):
    """Generates an extremely premium custom glassmorphic KPI card with trend badges."""
    trend_color = "#10b981" if trend_direction == "up" else "#ef4444"
    trend_arrow = "▲" if trend_direction == "up" else "▼"
    
    html = f"""<div class="custom-card" style="position: relative; overflow: hidden; margin-bottom: 0px;"><div style="display: flex; justify-content: space-between; align-items: flex-start;"><div><div style="font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 500;">{title}</div><div style="font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 6px;">{value}</div><div style="font-size: 11px; color: {trend_color}; font-weight: 600; display: flex; align-items: center; gap: 4px;"><span>{trend_arrow} {trend_text}</span></div></div><div style="background: rgba(99, 102, 241, 0.1); border-radius: 8px; padding: 10px; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px;">{icon_svg.strip()}</div></div></div>"""
    return html

# Reusable SVG Icons for metrics
SVG_REVENUE = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
"""

SVG_PROFIT = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
"""

SVG_ORDERS = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
"""

SVG_CUSTOMERS = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
"""
