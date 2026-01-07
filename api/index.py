# api/index.py - Root endpoint
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = {
            "status": "running",
            "message": "QR Code API is operational",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "endpoints": {
                "qr_generator": {
                    "path": "/api/qr",
                    "method": "GET",
                    "description": "Generate QR codes with custom parameters",
                    "parameters": {
                        "data": {
                            "type": "string",
                            "required": True,
                            "description": "Text or URL to encode"
                        },
                        "size": {
                            "type": "integer",
                            "required": False,
                            "default": 300,
                            "max": 2000,
                            "description": "QR code size in pixels"
                        },
                        "fg": {
                            "type": "string",
                            "required": False,
                            "default": "black",
                            "description": "Foreground color (name or hex)"
                        },
                        "bg": {
                            "type": "string",
                            "required": False,
                            "default": "white",
                            "description": "Background color (name or hex)"
                        },
                        "format": {
                            "type": "string",
                            "required": False,
                            "default": "png",
                            "options": ["png", "svg"],
                            "description": "Output format"
                        }
                    },
                    "example": "/api/qr?data=https://example.com&size=400&fg=blue&bg=yellow"
                }
            },
            "features": [
                "CORS enabled for all origins",
                "Permanent QR codes with 1-year cache",
                "PNG and SVG format support",
                "Custom colors and sizes",
                "High error correction",
                "No rate limits"
            ],
            "developed_by": "zerodev",
            "documentation": "https://link-to-qr-api.vercel.app/docs",
            "support": "https://github.com/zerodev"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# ============================================
# api/qr.py - QR Code Generator
# ============================================
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import qrcode
from io import BytesIO
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        # Get parameters
        data = params.get('data', [''])[0]
        size = min(int(params.get('size', ['300'])[0]), 2000)
        fg_color = params.get('fg', ['black'])[0]
        bg_color = params.get('bg', ['white'])[0]
        format_type = params.get('format', ['png'])[0].lower()
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if not data:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'error': 'Missing required parameter: data',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'usage': {
                    'endpoint': '/api/qr',
                    'method': 'GET',
                    'parameters': {
                        'data': 'Required - Text or URL to encode',
                        'size': 'Optional - Size in pixels (default: 300, max: 2000)',
                        'fg': 'Optional - Foreground color (default: black)',
                        'bg': 'Optional - Background color (default: white)',
                        'format': 'Optional - png or svg (default: png)'
                    },
                    'examples': [
                        '/api/qr?data=https://example.com',
                        '/api/qr?data=Hello%20World&size=400&fg=blue&bg=yellow',
                        '/api/qr?data=Contact&format=svg&fg=%23FF5733'
                    ]
                },
                'developed_by': 'zerodev'
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            if format_type == 'svg':
                from qrcode.image.svg import SvgPathImage
                img = qr.make_image(
                    image_factory=SvgPathImage,
                    fill_color=fg_color,
                    back_color=bg_color
                )
                buffer = BytesIO()
                img.save(buffer)
                self.send_header('Content-type', 'image/svg+xml')
                self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
                self.send_header('X-Developed-By', 'zerodev')
                self.end_headers()
                self.wfile.write(buffer.getvalue())
            else:
                img = qr.make_image(fill_color=fg_color, back_color=bg_color)
                if size != 300:
                    img = img.resize((size, size))
                
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
                self.send_header('X-Developed-By', 'zerodev')
                self.end_headers()
                self.wfile.write(buffer.getvalue())
                
        except Exception as e:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'developed_by': 'zerodev'
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
"""


# ============================================
# requirements.txt
# ============================================
"""
qrcode[pil]==7.4.2
pillow==10.1.0
"""


# ============================================
# vercel.json
# ============================================
"""
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "api/qr.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/",
      "dest": "api/index.py"
    },
    {
      "src": "/api/qr",
      "dest": "api/qr.py"
    }
  ]
}
"""
