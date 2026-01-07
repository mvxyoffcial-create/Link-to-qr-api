"""
Vercel QR Code Generator API with CORS
File structure:
/api/qr.py (this file)
/requirements.txt
/vercel.json
"""

# api/qr.py
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import qrcode
from io import BytesIO
import base64
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        # Get parameters with defaults
        data = params.get('data', [''])[0]
        size = int(params.get('size', ['300'])[0])
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
                'error': 'Missing required parameter: data',
                'usage': {
                    'endpoint': '/api/qr',
                    'parameters': {
                        'data': 'Required - Text or URL to encode',
                        'size': 'Optional - QR code size in pixels (default: 300)',
                        'fg': 'Optional - Foreground color (default: black)',
                        'bg': 'Optional - Background color (default: white)',
                        'format': 'Optional - png or svg (default: png)'
                    },
                    'example': '/api/qr?data=https://example.com&size=400&fg=blue&bg=yellow'
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            if format_type == 'svg':
                # SVG format
                from qrcode.image.svg import SvgPathImage
                img = qr.make_image(
                    image_factory=SvgPathImage,
                    fill_color=fg_color,
                    back_color=bg_color
                )
                buffer = BytesIO()
                img.save(buffer)
                self.send_header('Content-type', 'image/svg+xml')
                self.end_headers()
                self.wfile.write(buffer.getvalue())
            else:
                # PNG format (default)
                img = qr.make_image(fill_color=fg_color, back_color=bg_color)
                
                # Resize if needed
                if size != 300:
                    img = img.resize((size, size))
                
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=31536000')
                self.end_headers()
                self.wfile.write(buffer.getvalue())
                
        except Exception as e:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# requirements.txt content:
"""
qrcode[pil]==7.4.2
pillow==10.1.0
"""

# vercel.json content:
"""
{
  "version": 2,
  "builds": [
    {
      "src": "api/qr.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/qr",
      "dest": "api/qr.py"
    }
  ]
}
"""
