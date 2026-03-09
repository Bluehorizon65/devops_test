# view_model.py
from flask import Flask, render_template_string
import os
import trimesh
import plotly.graph_objects as go

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar Panel Designer Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 50%, #1e88e5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.8;
            color: #b0bec5;
        }
        
        .main-content {
            display: flex;
            justify-content: center;
            align-items: start;
        }
        
        .viewer-card {
            background: rgba(30, 30, 46, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
            min-height: 800px;
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 1200px;
        }
        
        .viewer-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: #e0e0e0;
        }
        
        .model-viewer {
            flex: 1;
            border-radius: 12px;
            overflow: hidden;
            background: rgba(255,255,255,0.02);
            min-height: 700px;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 1rem;
            }
            
            .viewer-card {
                min-height: 600px;
            }
            
            .model-viewer {
                min-height: 500px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
        </div>
        
        <div class="main-content">
            <div class="viewer-card">
                <h2 class="viewer-title">3D Solar Panel Model Visualization</h2>
                <div class="model-viewer">
                    {{ fig|safe }}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    fig_html = ""
    
    # Load the output_model.glb file directly
    try:
        mesh = trimesh.load_mesh("output_model.glb")
        vertices = mesh.vertices
        faces = mesh.faces
        
        if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
            vertex_colors = mesh.visual.vertex_colors
            colors = [f'rgb({c[0]},{c[1]},{c[2]})' for c in vertex_colors]
        else:
            colors = 'orange'
            
        fig = go.Figure(
            data=[
                go.Mesh3d(
                    x=vertices[:, 0],
                    y=vertices[:, 1],
                    z=vertices[:, 2],
                    i=faces[:, 0],
                    j=faces[:, 1],
                    k=faces[:, 2],
                    vertexcolor=colors,
                    opacity=1.0
                )
            ]
        )
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Length (X)',
                yaxis_title='Width (Y)',
                zaxis_title='Height (Z)',
                aspectmode='data',
                bgcolor='rgba(30,30,46,1)',
                xaxis=dict(backgroundcolor='rgba(30,30,46,1)', gridcolor='rgba(255,255,255,0.1)', showbackground=True),
                yaxis=dict(backgroundcolor='rgba(30,30,46,1)', gridcolor='rgba(255,255,255,0.1)', showbackground=True),
                zaxis=dict(backgroundcolor='rgba(30,30,46,1)', gridcolor='rgba(255,255,255,0.1)', showbackground=True)
            ),
            title={
                'text': '3D Solar Panel Model',
                'font': {'color': '#e0e0e0'}
            },
            paper_bgcolor='rgba(30,30,46,1)',
            plot_bgcolor='rgba(30,30,46,1)',
            font=dict(color='#e0e0e0'),
            height=700,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        fig_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
    except Exception as e:
        fig_html = f"<p style='color:#f44336;'>Error loading model: {str(e)}</p>"
    
    return render_template_string(HTML_FORM, fig=fig_html)

if __name__ == '__main__':
    print("🚀 Flask server running at: http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)