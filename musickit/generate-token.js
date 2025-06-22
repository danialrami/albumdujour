const jwt = require('jsonwebtoken');
const fs = require('fs');

// First install the required package
// Run: npm init -y
// Then: npm install jsonwebtoken

const privateKey = fs.readFileSync('AuthKey_NZPSNMM9D8.p8').toString();
const teamId = 'H4N6QXWZW9'; // Replace with your 10-digit Team ID from Developer Console
const keyId = 'NZPSNMM9D8';

const token = jwt.sign({}, privateKey, {
    algorithm: 'ES256',
    expiresIn: '180d',
    issuer: teamId,
    header: {
        alg: 'ES256',
        kid: keyId
    }
});

console.log('Developer Token:', token);