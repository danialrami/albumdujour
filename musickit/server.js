const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const tokenPath = '/Users/danielramirez/Obsidian/ore/Notes/Life/utilities/musickit/music_user_token.txt';

app.post('/save-token', (req, res) => {
    const { token } = req.body;
    fs.writeFileSync(tokenPath, token);
    res.json({ success: true });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
