const fs = require('fs');
const path = require('path');

const filePath = decodeURI(process.argv[2]); // Le chemin du fichier texte
const outputJsPath = path.join(__dirname, 'fileContent.js'); // Le fichier JS à générer

if (!filePath) {
    console.error('Aucun chemin de fichier fourni.');
    process.exit(1);
}

fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
        console.error(`Erreur lors de la lecture du fichier: ${err.message}`);
        process.exit(1);
    }

    const content = JSON.stringify(data.replace(/</g, '\\u003c').replace(/>/g, '\\u003e'));
    const jsContent = `const fileContent = ${content};`;

    fs.writeFile(outputJsPath, jsContent, 'utf8', (err) => {
        if (err) {
            console.error(`Erreur lors de l'écriture du fichier JS: ${err.message}`);
            process.exit(1);
        }
        console.log(`Fichier JS généré: ${outputJsPath}`);
    });
});
