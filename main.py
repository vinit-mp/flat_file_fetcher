from flask import Flask, send_file, abort, jsonify, request
import os 
from pathlib import Path
import mimetypes






app = Flask(__name__)
DOWNLOAD_DIRECTORY = "downloads"
FILE_SIZE = 10*1024*1024
ALLOWED_EXTENSIONS = {".txt"}

#Does the directory exists check

os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)



def is_safe_path(basedir, path , has_symlinks): # new concept dir traversal attacks prevention
    if has_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((basedir, matchpath))



def is_allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS



@app.route('/')
def index():
    """List available files"""
    try:
        files = []
        download_path = os.path.abspath(DOWNLOAD_DIRECTORY)
        
        for filename in os.listdir(DOWNLOAD_DIRECTORY):
            file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
            
            if os.path.isfile(file_path) and is_allowed_file(filename):
                file_size = os.path.getsize(file_path)
                files.append({
                    'name': filename,
                    'size': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2),
                    'download_url': f'/download/{filename}'
                })
        
        return jsonify({
            'available_files': files,
            'total_files': len(files)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a specific file"""
    try:
        if not filename or '..' in filename or '/' in filename:
            abort(400, "Invalid filename")
        
        if not is_allowed_file(filename):
            abort(400, "File type not allowed")
        
        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        abs_file_path = os.path.abspath(file_path)
        abs_download_dir = os.path.abspath(DOWNLOAD_DIRECTORY)
        
        if not is_safe_path(abs_download_dir, abs_file_path):
            abort(400, "Invalid file path")
        
        if not os.path.exists(abs_file_path):
            abort(404, "File not found")
        
        file_size = os.path.getsize(abs_file_path)
        if file_size > FILE_SIZE:
            abort(413, "File too large")
        
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        return send_file(
            abs_file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_type
        )
    
    except Exception as e:
        if hasattr(e, 'code'):  # HTTP exception
            raise e
        return jsonify({'error': str(e)}), 500

@app.route('/info/<filename>')
def file_info(filename):
    """Get information about a specific file"""
    try:
        if not filename or '..' in filename or '/' in filename:
            abort(400, "Invalid filename")
        
        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        abs_file_path = os.path.abspath(file_path)
        abs_download_dir = os.path.abspath(DOWNLOAD_DIRECTORY)
        
        if not is_safe_path(abs_download_dir, abs_file_path):
            abort(400, "Invalid file path")
        
        if not os.path.exists(abs_file_path):
            abort(404, "File not found")
        
        if not is_allowed_file(filename):
            abort(400, "File type not allowed")
        
        stat = os.stat(abs_file_path)
        mime_type, _ = mimetypes.guess_type(filename)
        
        return jsonify({
            'name': filename,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': stat.st_mtime,
            'mime_type': mime_type or 'application/octet-stream',
            'extension': Path(filename).suffix.lower(),
            'download_url': f'/download/{filename}'
        })
    
    except Exception as e: 
        if hasattr(e, 'code'):
            raise e
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error.description)}), 400

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    print(f"File Download Server starting...")
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIRECTORY)}")
    print(f"Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"Max file size: {FILE_SIZE / (1024 * 1024):.1f} MB")
    print(f"Access the server at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


 
















