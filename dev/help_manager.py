'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        help_manager.py

 Author:      Diego Pérez

 Created:     09/07/2025
 Copyright:   (c) perez 2025
-------------------------------------------------------------------------------
'''
import settings
import os
# Now, import language and assets
from pathlib import Path
if settings.LANGUAGE == 'English':
    HELP_PATH = Path(__file__).parent / Path(r".\help\User guide EN.pdf")
elif settings.LANGUAGE == 'Castellano':
    HELP_PATH = Path(__file__).parent / Path(r".\help\User guide ES.pdf")

def open_help():
    p = Path(HELP_PATH)
    if not p.exists():
        raise FileNotFoundError(p)
    # On Windows this will open the PDF in the user's default PDF viewer
    os.startfile(str(p))  # non-blocking

# import http.server
# import socketserver
# import threading
# import webbrowser
# import os
# import socket
# import ssl
# from tkinter import messagebox
# from pathlib import Path
# import datetime
# import ipaddress
#
# # cryptography is required (install with pip if missing)
# from cryptography import x509
# from cryptography.x509.oid import NameOID
# from cryptography.hazmat.primitives import hashes, serialization
# from cryptography.hazmat.primitives.asymmetric import rsa
#
# PORT = 8000
# _server_thread = None
# # class helpserver:
# def is_port_in_use(port):
#     """Check if the port is already open (indicates server is running)."""
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         return s.connect_ex(('localhost', port)) == 0
#
# def open_help():
#     global _server_thread
#
#     if is_port_in_use(PORT):
#         print(f"[Info] Manual already running at http://localhost:{PORT}/help/index.html")
#         webbrowser.open(f"http://localhost:{PORT}/help/index.html")
#         return
#
#     # Serve from the root directory (must include "help/" folder inside it)
#     manual_root = Path(__file__).parent.resolve()
#     os.chdir(manual_root)
#
#     handler = http.server.SimpleHTTPRequestHandler
#
#     def run():
#         with socketserver.TCPServer(("localhost", PORT), handler) as httpd:
#             print(f"[Started] Manual server at http://localhost:{PORT}/help/index.html")
#             httpd.serve_forever()
#
#     _server_thread = threading.Thread(target=run, daemon=True)
#     _server_thread.start()
#
#     webbrowser.open(f"http://localhost:{PORT}/help/index.html")
#
# # def _create_self_signed_cert(certfile: Path, valid_days: int = 365) -> bool:
# #     """
# #     Create a self-signed certificate (PEM) containing the private key and certificate.
# #     Returns True on success, False on failure.
# #     """
# #     try:
# #         if certfile.exists():
# #             return True
# #
# #         # Generate private key
# #         key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
# #
# #         # Subject and issuer (self-signed)
# #         subject = issuer = x509.Name([
# #             x509.NameAttribute(NameOID.COMMON_NAME, u'localhost'),
# #         ])
# #
# #         now = datetime.datetime.utcnow()
# #         cert_builder = (
# #             x509.CertificateBuilder()
# #             .subject_name(subject)
# #             .issuer_name(issuer)
# #             .public_key(key.public_key())
# #             .serial_number(x509.random_serial_number())
# #             .not_valid_before(now - datetime.timedelta(minutes=1))
# #             .not_valid_after(now + datetime.timedelta(days=valid_days))
# #             .add_extension(
# #                 x509.SubjectAlternativeName([
# #                     x509.DNSName(u'localhost'),
# #                     x509.IPAddress(ipaddress.IPv4Address('127.0.0.1')),
# #                     x509.IPAddress(ipaddress.IPv6Address('::1'))
# #                 ]),
# #                 critical=False
# #             )
# #         )
# #
# #         cert = cert_builder.sign(private_key=key, algorithm=hashes.SHA256())
# #
# #         # Ensure parent directory exists
# #         certfile.parent.mkdir(parents=True, exist_ok=True)
# #
# #         # Write key + cert in one PEM file (key first)
# #         pem_bytes = key.private_bytes(
# #             encoding=serialization.Encoding.PEM,
# #             format=serialization.PrivateFormat.TraditionalOpenSSL,
# #             encryption_algorithm=serialization.NoEncryption()
# #         ) + cert.public_bytes(serialization.Encoding.PEM)
# #
# #         # Write file with restrictive permissions where possible
# #         with open(certfile, 'wb') as f:
# #             f.write(pem_bytes)
# #         try:
# #             os.chmod(certfile, 0o600)
# #         except Exception:
# #             # ignore chmod failures on platforms that don't support it
# #             pass
# #
# #         return True
# #     except Exception as e:
# #         messagebox.showerror('[Error] Certificate creation failed', f'Failed to create HTTPS certificate: {e}')
# #         return False
# #
# # def open_help():
# #     global _server_thread
# #
# #     if is_port_in_use(PORT):
# #         # print(f"[Info] Manual already running at https://localhost:{PORT}/help/index.html")
# #         webbrowser.open(f"https://localhost:{PORT}/help/index.html")
# #         return
# #
# #     # Serve from the root directory (must include "help/" folder inside it)
# #     manual_root = Path(__file__).parent.resolve()
# #     os.chdir(manual_root)
# #
# #     handler = http.server.SimpleHTTPRequestHandler
# #
# #     # certificate file (key+cert in one PEM)
# #     certfile = manual_root / "help_server.pem"
# #
# #     https_ready = _create_self_signed_cert(certfile)
# #     if not https_ready or not certfile.exists():
# #         messagebox.showerror('[Error] HTTPS unavailable', 'Could not create HTTPS certificate; help cannot be served.')
# #         return
# #
# #     def run():
# #         try:
# #             # prefer a threaded server
# #             ServerClass = getattr(http.server, "ThreadingHTTPServer", None)
# #             if ServerClass is None:
# #                 ServerClass = socketserver.TCPServer
# #
# #             with ServerClass(("localhost", PORT), handler) as httpd:
# #                 # configure SSL
# #                 context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# #                 context.load_cert_chain(str(certfile))
# #                 httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
# #                 # print(f"[Started] Manual HTTPS server at https://localhost:{PORT}/help/index.html")
# #                 httpd.serve_forever()
# #         except Exception as e:
# #             messagebox.showerror('[Error] Failed to start server', 'Failed to start help server: ' + str(e))
# #
# #     _server_thread = threading.Thread(target=run, daemon=True)
# #     _server_thread.start()
# #
# #     webbrowser.open(f"https://localhost:{PORT}/help/index.html")
