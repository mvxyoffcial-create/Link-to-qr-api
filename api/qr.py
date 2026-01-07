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
