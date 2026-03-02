@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Process the CSV file here (e.g., run analysis, update cache/history)
        # Example: df = pd.read_csv(filepath)
        # analysis_cache[filename] = analyze(df)
        flash('File uploaded and analyzed successfully!')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type')
        return redirect(url_for('index'))