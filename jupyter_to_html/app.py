import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import nbformat
from nbconvert import HTMLExporter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        
        if file and file.filename.endswith('.ipynb'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook_content = nbformat.read(f, as_version=4)
            
            html_exporter = HTMLExporter()
            (body, _) = html_exporter.from_notebook_node(notebook_content)
            
            output_filename = os.path.splitext(filename)[0] + '.html'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(body)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

