const { exec } = require('child_process');

exports.searchFaq = (req, res, next) => {
    const { search } = req.query;
    if (!search) return res.send('');
    
    // VULNERABLE: Reflected XSS (No sanitization before returning HTML)
    const responseHtml = `
      <div class="text-red-800 p-2 bg-red-50 border border-red-200 mt-2">
        <p>Aucun résultat trouvé pour votre requête : <strong>${search}</strong></p>
        <p>Veuillez vérifier l'orthographe ou essayer d'autres mots-clés.</p>
      </div>
    `;
    res.send(responseHtml);
};

exports.checkServerStatus = (req, res, next) => {
    const { server_ip } = req.body;
    if (!server_ip) return res.status(400).json({ error: 'IP required' });

    // VULNERABLE: Command Injection. Expected format: '8.8.8.8'
    exec(`ping -c 1 ${server_ip}`, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ success: false, output: stderr || error.message });
        }
        res.json({ success: true, output: stdout });
    });
};

exports.getFaqDocument = (req, res, next) => {
    const { file } = req.query;
    if (!file) return res.status(400).json({ error: 'File name required' });

    // VULNERABLE: Path Traversal. Can be exploited with ../../../etc/passwd
    const path = require('path');
    const filePath = path.join(__dirname, '../../public/faq', file);
    
    res.sendFile(filePath, (err) => {
        if (err) {
            res.status(404).json({ error: 'File not found' });
        }
    });
};
