from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                "message": "Telegram Bot is running",
                "status": "OK",
                "method": "GET"
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        try:
            # อ่าน content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # อ่าน request body
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    # Parse JSON data จาก Telegram webhook
                    webhook_data = json.loads(post_data.decode('utf-8'))
                    print(f"Received webhook data: {webhook_data}")
                    
                    # ประมวลผล Telegram update ที่นี่
                    # webhook_data จะมีข้อมูลจาก Telegram
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    webhook_data = {}
            else:
                webhook_data = {}
            
            # ส่ง response กลับ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                "ok": True,
                "status": "received",
                "method": "POST"
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in POST handler: {str(e)}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
